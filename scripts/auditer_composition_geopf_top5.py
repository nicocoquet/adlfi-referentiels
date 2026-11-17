#!/usr/bin/env python3
"""Recette : composition des cinq plus grands écarts de contours GEO PF–ISPF.

Les unités sont explicitement ciblées à partir du résultat PR84. On conserve
les codes géographiques et les modes d'acquisition par pièce, on confronte
leurs emprises au contour ISPF, sans décider quelle source est correcte.
Aucune géométrie ni coordonnée de personne n'est publiée.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from comparer_contours_geopf_ispf import (
    aire, lire_source_geopf, XLSX_SHA, ISPF_GEO_SHA, GEO_PF_SHA
)
from qualifier_jointures_geopf_ispf import code
from qualifier_communes_associees_ispf import rows
from inspecter_nomenclature_geographique_ispf import read_xlsx

CIBLES = ("190", "202", "112", "263", "264")
CRS_ISPF = "urn:ogc:def:crs:EPSG::4687"

def ratio(numerateur, denominateur):
    if denominateur <= 0:
        raise ValueError("Surface de référence nulle")
    return round(numerateur / denominateur, 10)

def profiler_piece(ident, attributs, geom, contour, geod):
    if not geom.is_valid or geom.is_empty:
        raise ValueError("Pièce GEO PF invalide : " + ident)
    surface = aire(geom, geod)
    part_dans_ispf = aire(geom.intersection(contour), geod)
    return {
        "IDGeo": ident,
        "nom_geographique": str(attributs.get("nom_geogra") or ""),
        "nom_GEO_PF": str(attributs.get("nom") or ""),
        "code_ile_GEO_PF": str(attributs.get("id_ile") or ""),
        "mode_acquisition": str(attributs.get("mode_acq") or ""),
        "organisme_acquisition": str(attributs.get("org_acq") or ""),
        "detail_mode_acquisition": str(attributs.get("d_mode_acq") or ""),
        "detail_organisme_acquisition": str(attributs.get("d_org_acq") or ""),
        "nombre_composantes": len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1,
        "surface_geopf_m2": round(surface, 3),
        "surface_piece_dans_ISPF_m2": round(part_dans_ispf, 3),
        "part_piece_couverte_par_ISPF": ratio(part_dans_ispf, surface),
    }

def auditer(xlsx, ispf_geojson, geopf):
    from shapely.geometry import shape
    from shapely.ops import unary_union
    from pyproj import CRS
    sources = (
        ("xlsx", xlsx, XLSX_SHA),
        ("ispf_geojson", ispf_geojson, ISPF_GEO_SHA),
        ("geopf", geopf, GEO_PF_SHA),
    )
    for name, path, digest in sources:
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("SHA-256 incorrect : " + name)
    sheets = {s["feuille"]: s for s in read_xlsx(xlsx)}
    lignes = rows(sheets["Geo"])
    source_by_geo = {code(r["IDGeo"], 5): r for r in lignes}
    if len(lignes) != 179 or len(source_by_geo) != 179:
        raise ValueError("Nomenclature ISPF Geo incomplète ou dupliquée")
    attendu = {unit: {
        ident for ident, r in source_by_geo.items()
        if code(r["IDComas"], 3) == unit
    } for unit in CIBLES}

    with ZipFile(ispf_geojson) as z:
        layer = json.loads(z.read("Comas.GeoJSON"))
    if layer.get("crs", {}).get("properties", {}).get("name") != CRS_ISPF:
        raise ValueError("CRS ISPF modifié")
    contours = {}
    for feature in layer["features"]:
        unit = code(feature["properties"]["IDComas"], 3)
        if unit in CIBLES:
            if unit in contours: raise ValueError("Unité ISPF dupliquée")
            contours[unit] = shape(feature["geometry"])
    if set(contours) != set(CIBLES): raise ValueError("Cibles ISPF manquantes")
    geod = CRS.from_epsg(4687).get_geod()

    parts_by_unit = {unit: [] for unit in CIBLES}
    for attrib, geom in lire_source_geopf(geopf):
        unit = code(attrib["code_com_1"], 3)
        if unit not in parts_by_unit: continue
        ident = code(attrib["code_geogr"], 5)
        ligne = source_by_geo.get(ident)
        if ligne is None: raise ValueError("Code GEO PF non apparié : " + ident)
        for col,other,width in (
            ("IDComas","code_com_1",3),("IDCom","code_commu",2),
            ("IDSub","code_subdi",None),("IDIle","id_ile",None)
        ):
            if code(ligne[col],width) != code(attrib.get(other),width):
                raise ValueError("Hiérarchie GEO PF non concordante : "+ident+" "+col)
        parts_by_unit[unit].append((ident,attrib,geom))

    result = {}
    for unit in CIBLES:
        parts = sorted(parts_by_unit[unit], key=lambda x:x[0])
        actual = {p[0] for p in parts}
        if actual != attendu[unit]:
            raise ValueError("Couverture géographique incomplète : "+unit)
        base = contours[unit]
        if not base.is_valid or base.is_empty: raise ValueError("Contour ISPF invalide")
        grouped = unary_union([p[2] for p in parts])
        if not grouped.is_valid or grouped.is_empty:
            raise ValueError("Union GEO PF invalide")
        geom_in_ispf = aire(grouped.intersection(base),geod)
        geom_out_ispf = aire(grouped.difference(base),geod)
        ispf_out_geopf = aire(base.difference(grouped),geod)
        aire_ispf = aire(base,geod)
        aire_geopf = aire(grouped,geod)
        observations = [profiler_piece(ident,attributs,geom,base,geod)
                        for ident,attributs,geom in parts]
        result[unit] = {
            "codes_IDGeo": sorted(actual),
            "nombre_pieces_geographiques_GEO_PF":len(parts),
            "nombre_composantes_GEO_PF":sum(x["nombre_composantes"] for x in observations),
            "nombre_composantes_ISPF":len(base.geoms) if base.geom_type=="MultiPolygon" else 1,
            "surface_ISPF_m2":round(aire_ispf,3),
            "surface_GEO_PF_m2":round(aire_geopf,3),
            "surface_GEO_PF_hors_ISPF_m2":round(geom_out_ispf,3),
            "surface_ISPF_hors_GEO_PF_m2":round(ispf_out_geopf,3),
            "surface_commune_m2":round(geom_in_ispf,3),
            "part_ISPF_hors_GEO_PF":ratio(ispf_out_geopf,aire_ispf),
            "part_GEO_PF_hors_ISPF":ratio(geom_out_ispf,aire_geopf),
            "modes_acquisition_GEO_PF":dict(sorted(Counter(
                str(a.get("mode_acq") or "NON_RENSEIGNE") for _,a,_ in parts
            ).items())),
            "organismes_acquisition_GEO_PF":dict(sorted(Counter(
                str(a.get("org_acq") or "NON_RENSEIGNE") for _,a,_ in parts
            ).items())),
            "pieces":observations,
        }
    return {
        "schema":"adlfi.lieux.polynesie.geopf.ispf.composition.top5.audit.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "sources_sha256":{n:d for n,_,d in sources},
        "crs":"EPSG:4687 RGPF / GRS 1980",
        "cibles":list(CIBLES),
        "unites":result,
        "comparaison_dependance_sources":"NON_ETABLIE",
        "precision_acquisition":"NON_ATTESTEE",
        "publication":{"geometries":0,"autorites":0,"ark":0},
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--xlsx",required=True,type=Path)
    ap.add_argument("--ispf-geojson",required=True,type=Path)
    ap.add_argument("--geopf",required=True,type=Path)
    ap.add_argument("--sortie",required=True,type=Path)
    args=ap.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Sortie de recette hors docs et sans écrasement")
    report=auditer(args.xlsx,args.ispf_geojson,args.geopf)
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    for unit,record in report["unites"].items():
        print("GEO_PF_COMPOSITION",json.dumps({
            "code":unit,
            "pieces":record["nombre_pieces_geographiques_GEO_PF"],
            "composantes_ispf":record["nombre_composantes_ISPF"],
            "composantes_geopf":record["nombre_composantes_GEO_PF"],
            "modes":record["modes_acquisition_GEO_PF"],
            "organismes":record["organismes_acquisition_GEO_PF"],
            "ispf_hors_geopf_m2":record["surface_ISPF_hors_GEO_PF_m2"],
            "geopf_hors_ispf_m2":record["surface_GEO_PF_hors_ISPF_m2"],
            "pieces_top":sorted(record["pieces"],key=lambda p:-p["surface_geopf_m2"])[:5],
        },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
