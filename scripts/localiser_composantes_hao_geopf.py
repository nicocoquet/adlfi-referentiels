#!/usr/bin/env python3
"""Localiser les cinq principales pièces de GEO PF Hao hors ISPF île 23.

Les mesures s'appliquent à la géométrie intersection/différence native RGPF.
Sortie de recette numérique et géographique, sans qualification automatique
(motu / récif / lagon), sans nouveau contour diffusé sur GitHub Pages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from auditer_hao_ispf_geopf import (
    HAO_GEO, HAO_ILE, ISPF_CRS, polygones
)
from comparer_contours_geopf_ispf import (
    XLSX_SHA, ISPF_GEO_SHA, GEO_PF_SHA, aire, lire_source_geopf
)
from qualifier_jointures_geopf_ispf import code

def classer_pieces(diff, geod):
    """Détails de localisation, avec conservation du total avant arrondi."""
    records=[]
    for poly in polygones(diff):
        area=aire(poly,geod)
        if area<=0:continue
        marker=poly.representative_point()
        records.append({
            "surface_m2":round(area,3),
            "emprise_lon_lat":[round(x,7) for x in poly.bounds],
            "point_interieur_lon_lat":[round(marker.x,7),round(marker.y,7)],
            "composantes":1,
            "anneaux_interieurs":len(poly.interiors),
            "interpretation_geographique":"NON_QUALIFIEE",
        })
    records.sort(key=lambda r:(-r["surface_m2"],r["point_interieur_lon_lat"]))
    return records

def auditer(geopf:Path,ispf:Path):
    from shapely.geometry import shape
    from pyproj import CRS
    for name,path,expected in (("GEO PF",geopf,GEO_PF_SHA),
                               ("ISPF SIG",ispf,ISPF_GEO_SHA)):
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError("Empreinte source non conforme : "+name)
    matches=[(props,g) for props,g in lire_source_geopf(geopf)
             if code(props.get("code_geogr"),5)==HAO_GEO]
    if len(matches)!=1:raise ValueError("Hao GEO PF absent ou dupliqué")
    props,hao=matches[0]
    if code(props.get("id_ile"))!=HAO_ILE:
        raise ValueError("Rattachement insulaire GEO PF inattendu")
    with ZipFile(ispf) as archive:
        layer=json.loads(archive.read("Ile.GeoJSON"))
    if layer.get("crs",{}).get("properties",{}).get("name")!=ISPF_CRS:
        raise ValueError("CRS ISPF non conforme")
    features=[feat for feat in layer.get("features",[])
              if code(feat["properties"]["IDIle"])==HAO_ILE]
    if len(features)!=1:raise ValueError("Île 23 absente ou dupliquée")
    isle=shape(features[0]["geometry"])
    if not hao.is_valid or not isle.is_valid or hao.is_empty or isle.is_empty:
        raise ValueError("Géométrie source non valide")
    geod=CRS.from_epsg(4687).get_geod()
    difference=hao.difference(isle)
    if difference.is_empty:raise ValueError("Aucune différence géographique détectée")
    pieces=classer_pieces(difference,geod)
    top=pieces[:5]
    total=aire(difference,geod)
    return {
        "schema":"adlfi.lieux.polynesie.hao.pieces-hors-ile.audit.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "sources_sha256":{"geopf":GEO_PF_SHA,"ispf_geojson":ISPF_GEO_SHA},
        "crs_source":"RGPF EPSG:4687",
        "ellipsoide":"GRS 1980",
        "selection":{"code_geogr_GEO_PF":HAO_GEO,"IDIle_ISPF":HAO_ILE},
        "nombre_pieces_positives":len(pieces),
        "aire_totale_hors_ile_ISPF_m2":round(total,3),
        "aire_cinq_pieces_m2":round(sum(aire_part["surface_m2"] for aire_part in top),3),
        "part_cinq_pieces":round(sum(aire_part["surface_m2"] for aire_part in top)/total,10),
        "cinq_pieces_classees":top,
        "precision_localisation":"Coordonnées natives en degrés, arrondies à 7 décimales ; un point intérieur n'identifie pas un toponyme.",
        "identification_nature_objets":"NON_ETABLIE",
        "provenance_independante":"NON_ETABLIE",
        "publication":{"contours":0,"autorites":0,"ark":0},
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--geopf",required=True,type=Path)
    p.add_argument("--ispf-geojson",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Rapport de recette hors docs et sans écrasement")
    record=auditer(a.geopf,a.ispf_geojson)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("HAO_PIECES_TOP5",json.dumps({
        "total":record["aire_totale_hors_ile_ISPF_m2"],
        "pieces":record["cinq_pieces_classees"],
        "nombre":record["nombre_pieces_positives"],
        "fraction_top5":record["part_cinq_pieces"],
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
