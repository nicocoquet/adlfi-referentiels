#!/usr/bin/env python3
"""Comparer les enveloppes BFC des DEUX millésimes de géométrie ODS.

Ces chiffres mesurent l'écart de représentations dérivées et simplifiées,
PAS un changement administratif de surface. Les géométries d'entrée ne
doivent provenir ni de 2026 ni d'une intersection/union rétrodictive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union

EXPECTED={"2015":{"26","43"},"2016":{"27"}}
PROJECTION="EPSG:2154"

def geom_load(path:Path,year:str):
    document=json.loads(Path(path).read_text(encoding="utf-8"))
    if document.get("type")!="FeatureCollection":
        raise ValueError("GeoJSON FeatureCollection attendu")
    if document.get("provenance",{}).get("annee")!=int(year):
        raise ValueError("Millésime géographique différent de l'année de référence")
    if document.get("provenance",{}).get("absence_de_retroprojection") is not True:
        raise ValueError("Garantie de non-rétroprojection absente")
    feat=document.get("features")
    if not isinstance(feat,list) or len(feat)!=len(EXPECTED[year]):
        raise ValueError("Cardinalité des contours BFC incorrecte")
    actual={str(f.get("properties",{}).get("code_region")) for f in feat}
    if actual!=EXPECTED[year]:raise ValueError("Code régional/millésime inattendu")
    for f in feat:
        p=f.get("properties",{})
        if p.get("millesime_geometrie")!=int(year):
            raise ValueError("Le millésime du contour est incompatible")
        if p.get("pactols_valide") is not False:
            raise ValueError("Une validation Pactols a été inférée sans approbation")
    geoms=[shape(f["geometry"]) for f in feat]
    for g in geoms:
        if g.is_empty or not g.is_valid or g.geom_type not in ("Polygon","MultiPolygon"):
            raise ValueError("Contour régional vide ou non valide")
    return geoms

def comparer(p2015:Path,p2016:Path):
    tr=Transformer.from_crs("EPSG:4326",PROJECTION,always_xy=True).transform
    anciennes=unary_union([transform(tr,g) for g in geom_load(p2015,"2015")])
    nouvelle=unary_union([transform(tr,g) for g in geom_load(p2016,"2016")])
    intersection=anciennes.intersection(nouvelle)
    reunion=anciennes.union(nouvelle)
    sym=anciennes.symmetric_difference(nouvelle)
    if not anciennes.is_valid or not nouvelle.is_valid:
        raise ValueError("Géométrie projetée non valide")
    if reunion.area<=0:raise ValueError("Superficie globale nulle")
    rapport={
      "schema":"adlfi.lieux.geo.bfc.comparaison_2015_2016.v1",
      "statut":"RECETTE_COMPARAISON_REPRESENTATIONS_NON_GEOMETRIE_OFFICIELLE",
      "description":"Différences géométriques des jeux dérivés et simplifiés, pas des mutations administratives",
      "projection_superficies":"EPSG:2154 Lambert-93, unités m puis km²",
      "source_geometrie":"Opendatasoft georef-france-region-millesime",
      "sha256_geometries":{
        "2015":hashlib.sha256(Path(p2015).read_bytes()).hexdigest(),
        "2016":hashlib.sha256(Path(p2016).read_bytes()).hexdigest(),
      },
      "surface_union_2015_km2":round(anciennes.area/1e6,4),
      "surface_polygone_2016_km2":round(nouvelle.area/1e6,4),
      "surface_difference_symetrique_km2":round(sym.area/1e6,4),
      "surface_dintersection_km2":round(intersection.area/1e6,4),
      "taux_recouvrement_iou_pourcent":round(100*intersection.area/reunion.area,6),
      "distance_hausdorff_km":round(anciennes.hausdorff_distance(nouvelle)/1000,5),
      "precision_limites_reconstituees":"NON_ETABLIE_PAR_CET_AUDIT",
      "changement_reel_de_surface":"NON_INFERABLE",
      "geom_2015_sous_cog_2016":False,
      "geometries_historiques_reconstruites":0,
      "nouveaux_alignements_pactols":0,
      "limites":[
       "La géométrie 2015 n'est pas la géométrie 2016.",
       "Un écart de sommets/aire peut résulter de simplifications cartographiques.",
       "Une comparaison avec les départements GEOFLA 2015 originaux reste à mener.",
       "La distance de Hausdorff dépend de la simplification; ne pas l'assimiler à une erreur de frontière.",
       "Un jeu de données millésimé ne prouve pas la géométrie à toutes les dates intra-annuelles."
      ],
    }
    return rapport

def ecrire(rapport:dict,out:Path):
    out=Path(out)
    if "docs" in out.resolve().parts:raise ValueError("Sortie de recette non autorisée dans docs")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(rapport,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contours2015",required=True,type=Path)
    ap.add_argument("--contours2016",required=True,type=Path)
    ap.add_argument("--sortie",required=True,type=Path)
    x=ap.parse_args()
    r=comparer(x.contours2015,x.contours2016)
    ecrire(r,x.sortie)
    print(json.dumps(r,ensure_ascii=False,indent=2))
