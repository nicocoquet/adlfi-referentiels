#!/usr/bin/env python3
"""Comparer deux contours ODS millésimés 2015 à l'IGN GEOFLA départements 2015.

Entrées : le SHP IGN extrait d'une archive dont SHA256 est contrôlé séparément
et le GeoJSON ODS 2015 déjà contrôlé par code/millésime.
Sorties non publiées : deux régions *reconstituées* par union de quatre
départements 2015 et métriques d'écart avec les contours ODS dérivés.
Ne jamais attribuer ces contours au 1er janvier si la livraison est du 4 mars
sans préciser séparément dates COG et de production géométrique.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from geopandas import read_file
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform, unary_union

HASH_ARCHIVE="7831ad942f3c0646d7b9ebf9ba480dcf746d6f69d46834b38e36fa6681c1060e"
ARCHIVE_URL=("https://data.geopf.fr/telechargement/download/GEOFLA/"
 "GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04/"
 "GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04.7z")
CODES={
    "26":("Bourgogne",("21","58","71","89")),
    "43":("Franche-Comté",("25","39","70","90")),
}
COLUMNS=("code_region","nom","departements","surface_ign_km2","surface_ods_km2",
         "surface_difference_symetrique_km2","taux_recouvrement_iou_pct",
         "distance_hausdorff_km")

def hash_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as fd:
        for b in iter(lambda:fd.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def verifier_archive(archive: Path):
    got=hash_file(archive)
    if got!=HASH_ARCHIVE:
        raise ValueError(f"Paquet IGN différent de l'édition contrôlée : {got}")
    return got

def comparer(shp:Path, ods:Path, sortie:Path, archive:Path | None):
    if "docs" in Path(sortie).resolve().parts:
        raise ValueError("Veto : ne pas publier ces résultats de recette sous docs/")
    source_sha=verifier_archive(archive) if archive else None
    deps=read_file(shp)
    if len(deps)!=96 or deps.crs is None or deps.crs.to_epsg()!=2154:
        raise ValueError("Il faut les 96 départements métropolitains GEOFLA en EPSG:2154")
    for key in ("CODE_DEPT","CODE_REG"):
        if key not in deps.columns:
            raise ValueError("Colonne IGN manquante : "+key)
    if deps["CODE_DEPT"].duplicated().any():
        raise ValueError("Codes départements IGN non uniques")
    od=json.loads(Path(ods).read_text(encoding="utf8"))
    if od["type"]!="FeatureCollection" or od["provenance"].get("annee")!=2015:
        raise ValueError("ODS doit porter le millésime géométrique 2015")
    actual={f["properties"]["code_region"]:f for f in od["features"]}
    if set(actual)!=set(CODES):
        raise ValueError("L'ODS 2015 doit couvrir exactement Bourgogne et Franche-Comté")
    to_l93=Transformer.from_crs(4326,2154,always_xy=True).transform
    to_wgs=Transformer.from_crs(2154,4326,always_xy=True).transform
    stats=[];features=[]
    for code,(name,parts) in CODES.items():
        sub=deps[deps["CODE_DEPT"].isin(parts)]
        if len(sub)!=4 or set(sub["CODE_DEPT"])!=set(parts) or set(sub["CODE_REG"])!={code}:
            raise ValueError(f"Les quatre départements 2015 de {name} ne concordent pas")
        native=unary_union(sub.geometry.tolist())
        o=actual[code]
        if o["properties"]["millesime_geometrie"]!=2015 or o["properties"]["nom"]!=name:
            raise ValueError("Nom/millésime ODS incompatible")
        derived=transform(to_l93,shape(o["geometry"]))
        if not native.is_valid or not derived.is_valid:
            raise ValueError("Géométrie invalide")
        intersection=native.intersection(derived)
        union=native.union(derived)
        if union.area <=0 or intersection.area<=0:
            raise ValueError("Polygones manifestement disjoints")
        metrics={
            "code_region":code,"nom":name,"departements":",".join(parts),
            "surface_ign_km2":round(native.area/1e6,4),
            "surface_ods_km2":round(derived.area/1e6,4),
            "surface_difference_symetrique_km2":round(native.symmetric_difference(derived).area/1e6,4),
            "taux_recouvrement_iou_pct":round(100*intersection.area/union.area,6),
            "distance_hausdorff_km":round(native.hausdorff_distance(derived)/1000,5),
        }
        if not (95<metrics["taux_recouvrement_iou_pct"]<100):
            raise ValueError("Écart spatial inattendu : "+name)
        stats.append(metrics)
        features.append({"type":"Feature",
            "geometry":mapping(transform(to_wgs,native)),
            "properties":{
                "code_region":code,"nom":name,
                "millesime_geometrie":2015,
                "date_edition_archive_ign":"2015-03-04",
                "date_reference_cog":"2015-01-01",
                "source_producteur":"IGN GEOFLA 2.0 — DEPARTEMENT",
                "type_contour":"reconstitution_union_4_departements_du_meme_millesime",
                "departements_sources":list(parts),
                "contour_region_natif_IGN":False,
                "alignement_pactols_approuve":False,
            }})
    sortie=Path(sortie);sortie.mkdir(parents=True,exist_ok=True)
    with (sortie/"comparaison-geometries-IGN-ODS-2015.csv").open("w",encoding="utf-8-sig",newline="") as fp:
        w=csv.DictWriter(fp,fieldnames=COLUMNS,delimiter=";")
        w.writeheader();w.writerows(stats)
    geo={"type":"FeatureCollection","provenance":{
        "source":ARCHIVE_URL,
        "source_hash_sha256":source_sha,
        "edition_IGN":"2015-03-04",
        "millesime_representation":2015,
        "date_reference_administrative_COG":"2015-01-01",
        "methode":"union des quatre départements GEOFLA 2015",
        "geometrie_regionale_native_IGN":False,
        "geometrie_2026_utilisee":False,
    },"features":features}
    (sortie/"regions-2015-bfc-reconstituees-IGN.geojson").write_text(
        json.dumps(geo,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
    report={
        "schema":"adlfi.lieux.bfc.geo.source_ign.2015.v1",
        "statut":"RECETTE_SOURCES_DIFFERENTES_NON_PUBLIEE",
        "archive_IGN_sha256":source_sha,"source_URL":ARCHIVE_URL,
        "departements_metropole":len(deps),
        "departements_retenus":8,
        "comparaisons":stats,
        "alignements_Pactols_crees":0,
        "geometries_retroprojetees_depuis_2026":0,
        "reserve":"La divergence entre contours produits avec des généralisations différentes ne mesure pas un déplacement historique de frontière.",
    }
    (sortie/"rapport-comparaison-IGN-ODS-2015.json").write_text(
        json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for x in ("shp","ods","sortie"):
        p.add_argument("--"+x,required=True,type=Path)
    p.add_argument("--archive",type=Path)
    a=p.parse_args()
    print(json.dumps(comparer(a.shp,a.ods,a.sortie,a.archive),ensure_ascii=False,indent=2))
