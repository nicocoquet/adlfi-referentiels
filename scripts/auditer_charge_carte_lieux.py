#!/usr/bin/env python3
"""Mesurer, sans publier ni modifier de données, le coût statique des contours communaux.

Le résultat est reproductible (pas d'horodatage) et distingue poids des sources,
poids gzip estimé et nombre de sommets. Ni la mémoire Leaflet ni les coûts réseau
réels ne sont inférés à partir des tailles des fichiers.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "adlfi.lieux.audit-charge-contours-2026.v1"
FILES = (
    ("paca", "lieux-chronologie/contours-2026-paca.geojson"),
    ("corse", "lieux-chronologie/contours-2026-corse.geojson"),
    ("pdl", "lieux-chronologie/contours-2026-pdl.geojson"),
    ("bfc", "lieux-chronologie/contours-2026-bfc.geojson"),
    ("drom", "lieux-outremer/contours-communes-drom-2026.geojson"),
    ("spm", "lieux-outremer/contours-communes-spm-2026.geojson"),
    ("nouvelle-caledonie", "lieux-outremer/contours-communes-nc-2026.geojson"),
    ("polynesie", "lieux-outremer/contours-communes-pf-28-2026.geojson"),
)


def points(coordinates):
    """Parcourir les positions d'un Polygon ou MultiPolygon GeoJSON."""
    if not isinstance(coordinates, list) or not coordinates:
        raise ValueError("Coordonnées GeoJSON absentes ou invalides")
    if len(coordinates) >= 2 and all(
        isinstance(v, (int, float)) and not isinstance(v, bool)
        for v in coordinates[:2]
    ):
        lon, lat = coordinates[:2]
        if not (math.isfinite(lon) and math.isfinite(lat)
                and -180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError("Coordonnée hors bornes WGS84")
        yield lon, lat
    else:
        for child in coordinates:
            yield from points(child)


def auditer_couche(data_root: Path, zone: str, name: str) -> dict:
    path = data_root / name
    raw = path.read_bytes()
    obj = json.loads(raw)
    if obj.get("type") != "FeatureCollection" or not isinstance(obj.get("features"), list):
        raise ValueError(f"GeoJSON inattendu : {name}")
    provenance = obj.get("provenance") or {}
    if not isinstance(provenance, dict):
        raise ValueError(f"Provenance illisible : {name}")
    if provenance.get("millesime") not in (None, 2026):
        raise ValueError(f"Millésime incompatible : {name}")
    if not obj["features"]:
        raise ValueError(f"Couche vide : {name}")

    codes = set()
    vertices = 0
    bbox = [180.0, 90.0, -180.0, -90.0]
    for feature in obj["features"]:
        props = feature.get("properties") or {}
        code = props.get("code") or props.get("code_insee")
        if not isinstance(code, str) or len(code) != 5 or code in codes:
            raise ValueError(f"Code communal absent, dupliqué ou invalide dans {name} : {code}")
        codes.add(code)
        geom = feature.get("geometry") or {}
        if geom.get("type") not in ("Polygon", "MultiPolygon"):
            raise ValueError(f"Géométrie inattendue pour {code} dans {name}")
        current = 0
        for lon, lat in points(geom.get("coordinates")):
            bbox[0] = min(bbox[0], lon)
            bbox[1] = min(bbox[1], lat)
            bbox[2] = max(bbox[2], lon)
            bbox[3] = max(bbox[3], lat)
            current += 1
        if not current:
            raise ValueError(f"Géométrie vide pour {code} dans {name}")
        vertices += current

    declared = provenance.get("nombre_contours")
    if declared is not None and declared != len(codes):
        raise ValueError(f"Effectif de provenance incohérent : {name}")
    return {
        "zone": zone,
        "fichier": "docs/data/" + name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "communes_cartographiees": len(codes),
        "sommets_coordonnees": vertices,
        "octets_bruts": len(raw),
        "octets_gzip_simules": len(gzip.compress(raw, compresslevel=9, mtime=0)),
        "emprise_lon_lat": bbox,
        "provenance_schema": provenance.get("schema"),
        "provenance_millesime": provenance.get("millesime"),
    }


def audit(root: Path, files=FILES) -> dict:
    data_root = root / "docs" / "data"
    items = [auditer_couche(data_root, zone, name) for zone, name in files]
    return {
        "schema": SCHEMA,
        "statut": "MESURE_STATIQUE_NON_PUBLIANTE",
        "couches": items,
        "total": {
            "fichiers": len(items),
            "communes_cartographiees": sum(i["communes_cartographiees"] for i in items),
            "sommets_coordonnees": sum(i["sommets_coordonnees"] for i in items),
            "octets_bruts": sum(i["octets_bruts"] for i in items),
            "octets_gzip_simules": sum(i["octets_gzip_simules"] for i in items),
        },
        "limites": [
            "Gzip simulé en mémoire : n'est pas une mesure du transfert HTTP GitHub Pages.",
            "Nombre de sommets : n'est pas une mesure du temps de rendu ou de la mémoire Leaflet.",
            "Une commune est comptée dans sa couche GeoJSON actuelle, sans inférer un ARK Pactols.",
            "Les géométries contemporaines de référence ne valent pas délimitation historique.",
            "L'inventaire porte uniquement sur les huit couches actuellement chargées en Commune 2026.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--racine", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    root = args.racine.resolve()
    output = args.sortie.resolve()
    if output == root / "docs" or root / "docs" in output.parents:
        raise ValueError("La mesure ne doit pas être publiée dans docs/")
    result = audit(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("LIEUX_CHARGE_2026", json.dumps(result["total"], ensure_ascii=False, sort_keys=True))
    for row in result["couches"]:
        print("LIEUX_COUCHE", json.dumps({k: row[k] for k in (
            "zone", "communes_cartographiees", "sommets_coordonnees",
            "octets_bruts", "octets_gzip_simules"
        )}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
