#!/usr/bin/env python3
"""Publier uniquement les deux géométries de référence 2026 de Saint-Pierre-et-Miquelon.

Source géométrique Etalab/IGN (édition 4 mai 2026), généralisation 100 m.
Index COG/COMER du module Lieux : codes et libellés strictement vérifiés.
Aucune réparation, inférence de limite historique ou correspondance ARK nouvelle.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
INDEX_AUDIT_SHA256 = "5aa79d28ab3d7dcf5952937b90e2beb4a558afc1f1b05c9c697b30682ae60b33"
SOURCE_URL = ("https://etalab-datasets.geo.data.gouv.fr/"
              "contours-administratifs/2026/geojson/communes-100m.geojson.gz")
SCHEMA = "adlfi.lieux.contours.spm-2026.v1"
CODES = {"97501": "Miquelon-Langlade", "97502": "Saint-Pierre"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verifier_index(index: dict) -> None:
    if (index.get("schema") != "adlfi.lieux.recherche.outremer.public.v1"
        or index.get("cog_ref") != "2026-01-01"
        or index.get("edition_geom") != "2026-05-04"
        or index.get("source_audit_sha256") != INDEX_AUDIT_SHA256
        or index.get("communes", {}).get("975") !=
            "97501|Miquelon-Langlade\n97502|Saint-Pierre"
        or index.get("contours_invalides") != ["98745", "98805"]):
        raise ValueError("COG/COMER ultramarin 2026 différent de l'index approuvé")
    # Les ARK sont déjà validés dans l'index documentaire, jamais repris dans le GeoJSON.
    if (index.get("pactols_valides", {}).get("97501") != "26678/pcrtQAMzeGHldU"
        or index.get("pactols_valides", {}).get("97502") != "26678/pcrtYQmFfwxLq8"):
        raise ValueError("Les deux décisions Pactols SPM existantes ont été modifiées")


def construire(source: dict) -> dict:
    from shapely.geometry import shape
    from shapely.validation import explain_validity
    if source.get("type") != "FeatureCollection" or not isinstance(source.get("features"), list):
        raise ValueError("Source cartographique non GeoJSON")
    geoms = {}
    formes = {}
    for f in source["features"]:
        props = f.get("properties") or {}
        code = str(props.get("code") or "")
        if code not in CODES:
            continue
        if code in geoms:
            raise ValueError("Géométrie dupliquée pour " + code)
        geometry = f.get("geometry")
        if not isinstance(geometry, dict) or geometry.get("type") not in ("Polygon", "MultiPolygon"):
            raise ValueError("Géométrie surfacique absente : " + code)
        geom = shape(geometry)
        if geom.is_empty or not geom.is_valid or geom.area <= 0:
            raise ValueError("Géométrie topologiquement invalide "+code+": "+explain_validity(geom))
        minlon, minlat, maxlon, maxlat = geom.bounds
        if not (-59 < minlon < maxlon < -53 and 45 < minlat < maxlat < 49):
            raise ValueError("Emprise géographique hors de Saint-Pierre-et-Miquelon : " + code)
        geoms[code] = {
            "type": "Feature",
            "properties": {
                "code": code, "nom": CODES[code], "zone": "spm",
                "ref_cog": "COMER:COM:" + code,
                "niveau": "commune", "annee": 2026,
                "millesime_cog": "2026-01-01",
                "edition_geometrie": "2026-05-04",
                "qualification_geometrie": "controle_topologique_2026",
                "limite_juridique_homologuee": False,
                "ark_pactols": None,
            },
            "geometry": geometry,
        }
        formes[code] = geom
    if set(geoms) != set(CODES):
        raise ValueError("Couverture des deux communes incomplète : "+repr(sorted(geoms)))
    if formes["97501"].intersection(formes["97502"]).area > 1e-9:
        raise ValueError("Chevauchement des contours communaux SPM au-delà de la tolérance")
    return {
        "type": "FeatureCollection",
        "features": [geoms[c] for c in sorted(CODES)],
        "provenance": {
            "schema": SCHEMA,
            "millesime": 2026, "cog_ref": "2026-01-01",
            "edition_geometrie": "2026-05-04", "generalisation_m": 100,
            "source_geometrique": SOURCE_URL,
            "sha256_source_geometrique": SOURCE_SHA256,
            "index_communes_COG": "docs/data/lieux-outremer/recherche-2026.json",
            "sha256_audit_COG": INDEX_AUDIT_SHA256,
            "contours_sans_ARK": True,
            "limites_juridiques_homologuees": False,
            "restitutions_historiques": 0,
            "nombre_contours": 2,
            "statut": "contours_cartographiques_reference_2026",
        },
    }


def generer(geometries: Path, index_cog: Path) -> dict:
    if sha(geometries) != SOURCE_SHA256:
        raise ValueError("Empreinte SHA-256 du GeoJSON Etalab non conforme")
    verifier_index(json.loads(index_cog.read_text(encoding="utf-8")))
    raw = geometries.read_bytes()
    fc = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    return construire(fc)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometries", required=True, type=Path)
    parser.add_argument("--index-cog", required=True, type=Path)
    parser.add_argument("--sortie", required=True, type=Path)
    args = parser.parse_args()
    d = generer(args.geometries, args.index_cog)
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(
        json.dumps(d, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("SPM_2_CONTOURS_2026", json.dumps({
        "codes": sorted(x["properties"]["code"] for x in d["features"]),
        "geojson_sha256": sha(args.sortie),
        "octets": args.sortie.stat().st_size,
        "ark_inferes": 0, "etats_historiques_inferes": 0,
        "limites_juridiques_homologuees": False,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
