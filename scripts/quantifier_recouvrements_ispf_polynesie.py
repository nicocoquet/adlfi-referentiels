#!/usr/bin/env python3
"""Quantifier les recouvrements ISPF sur l'ellipsoïde du RGPF, sans correction.

La géométrie est opérée sur les coordonnées natives RGPF EPSG:4687.
Seules les surfaces de leur intersection sont mesurées géodésiquement avec
l'ellipsoïde du CRS (GRS 1980). Aucun classement arbitraire par seuil.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

from auditer_recouvrements_ispf_polynesie import (
    auditer as inventaire_precedent, normaliser_code, SOURCE_SHA, CRS
)

def quantifier(archive: Path):
    from pyproj import CRS as ProjectionCRS
    from shapely.geometry import shape

    precedent = inventaire_precedent(archive)
    crs = ProjectionCRS.from_epsg(4687)
    if not crs.is_geographic or crs.ellipsoid.name != "GRS 1980":
        raise ValueError("Ellipsoïde RGPF inattendu")
    geod = crs.get_geod()
    with ZipFile(archive) as z:
        fc = json.loads(z.read("Comas.GeoJSON"))
    if fc.get("crs", {}).get("properties", {}).get("name") != CRS:
        raise ValueError("CRS source différent du RGPF")
    lookup = {}
    for feat in fc["features"]:
        ident = normaliser_code(feat["properties"]["IDComas"])
        if ident in lookup:
            raise ValueError("IDComas dupliqué")
        lookup[ident] = shape(feat["geometry"])

    def aire(geom):
        # pyproj calcule une aire signée, l'abs permet les orientations
        # différentes des anneaux ; ne pas ignorer les grandes surfaces.
        a, _ = geod.geometry_area_perimeter(geom)
        if not math.isfinite(a):
            raise ValueError("Surface géodésique non finie")
        return abs(a)

    observations = []
    parents = {x["code_a"] + "|" + x["code_b"]: x
               for x in precedent["couches"]["Comas.GeoJSON"]["paires_recouvrements_a_instruire"]}
    for key, pair in sorted(parents.items()):
        a, b = lookup[pair["code_a"]], lookup[pair["code_b"]]
        inter = a.intersection(b)
        area = aire(inter)
        if inter.area <= 0 or area <= 0:
            raise ValueError("Recouvrement sans surface positive : " + key)
        area_a, area_b = aire(a), aire(b)
        if not area_a or not area_b:
            raise ValueError("Surface nulle pour une unité fine : " + key)
        observations.append({
            "idcomas_a": pair["code_a"], "idcomas_b": pair["code_b"],
            "meme_commune_parente": pair["meme_commune_parente"],
            "communes_parentes_ispf": pair["communes_parentes_ISPF"],
            "aire_intersection_m2": round(area, 6),
            "part_surface_a": round(area / area_a, 12),
            "part_surface_b": round(area / area_b, 12),
            "part_de_la_plus_petite_unite": round(area / min(area_a, area_b), 12),
            "relation_geometrique": pair["intersection_geometrique"],
        })
    if len(observations) != 65:
        raise ValueError("L'inventaire PR81 n'est plus celui de 65 paires")
    ranked = sorted(observations, key=lambda x: (-x["aire_intersection_m2"], x["idcomas_a"], x["idcomas_b"]))
    by_type = {
        name: [x for x in ranked if x["meme_commune_parente"] == same]
        for name, same in (("intra_communale", True), ("inter_communale", False))
    }
    return {
        "schema": "adlfi.lieux.polynesie.recouvrements.aires.geodesiques.v1",
        "statut": "AUDIT_NON_VALIDANT",
        "source_sha256": SOURCE_SHA,
        "crs_source": CRS,
        "ellipsoide": "GRS 1980",
        "methode": "pyproj.Geod.geometry_area_perimeter / Shapely intersection",
        "bilan": {
            "paires": len(observations),
            "paires_intra_commune": len(by_type["intra_communale"]),
            "paires_inter_communes": len(by_type["inter_communale"]),
            "total_des_aires_paires_m2": round(sum(x["aire_intersection_m2"] for x in observations), 3),
            "total_aire_paires_intra_m2": round(sum(x["aire_intersection_m2"] for x in by_type["intra_communale"]), 3),
            "total_aire_paires_inter_m2": round(sum(x["aire_intersection_m2"] for x in by_type["inter_communale"]), 3),
            "nombre_de_contours_crees": 0,
        },
        "paires_classees_par_aire_decroissante": ranked,
        "limites": [
            "Somme des aires par paire : ce total peut compter plusieurs fois des intersections triples.",
            "Les surfaces sont calculées sur ellipsoïde, sans échelle de précision des contours attestée.",
            "Aucun seuil ne déclare automatiquement un recouvrement acceptable ou erroné.",
            "Comparaison à une source indépendante non encore réalisée.",
            "Aucune publication ni correction de polygone.",
        ],
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", required=True, type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    a = p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("La recette n'écrit jamais dans docs ni sur un fichier existant")
    report = quantifier(a.archive)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("ISPF_AIRES_BILAN", json.dumps(report["bilan"], ensure_ascii=False, sort_keys=True))
    print("ISPF_AIRES_TOP10", json.dumps(report["paires_classees_par_aire_decroissante"][:10], ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
