#!/usr/bin/env python3
"""Exporter les seuls 129 contours communaux des cinq DROM au COG 2026.

Le découpage cartographique Etalab/IGN du 4 mai 2026 n'est ni un contour
historique, ni une preuve de l'alignement ARK. Sources officielles épinglées,
contrôle Shapely de chaque géométrie, sans réparation automatique.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

from shapely.geometry import shape

EXPECTED_SOURCE = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
EXPECTED_COG = "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3"
SOURCE_URL = ("https://etalab-datasets.geo.data.gouv.fr/"
              "contours-administratifs/2026/geojson/communes-100m.geojson.gz")
EXPECTED = {"971": 32, "972": 34, "973": 22, "974": 24, "976": 17}
REGIONS = {"971": "01", "972": "02", "973": "03", "974": "04", "976": "06"}
SCHEMA = "adlfi.lieux.contours.drom-2026.v1"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fd:
        for block in iter(lambda: fd.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def lire_cog(path: Path) -> dict[str, dict]:
    if sha(path) != EXPECTED_COG:
        raise ValueError("COG 2026 incompatible avec le snapshot Insee épinglé")
    communes = {}
    with path.open(encoding="utf-8-sig", newline="") as fd:
        reader = csv.DictReader(fd)
        if not {"TYPECOM", "COM", "REG", "DEP", "LIBELLE"}.issubset(reader.fieldnames or ()):
            raise ValueError("Champs Insee du COG 2026 incomplets")
        for row in reader:
            code = row["COM"]
            prefix = code[:3]
            if prefix not in EXPECTED or row["TYPECOM"] != "COM":
                continue
            if code in communes or row["REG"] != REGIONS[prefix] or row["DEP"] != prefix:
                raise ValueError("Commune DROM hors région, département ou dupliquée : " + code)
            communes[code] = {"nom": row["LIBELLE"], "region": row["REG"], "territoire": prefix}
    effectifs = Counter(r["territoire"] for r in communes.values())
    if effectifs != Counter(EXPECTED):
        raise ValueError("Dénombrement communal des cinq DROM incohérent : " + str(effectifs))
    return communes


def verifier_index(index: dict, cog: dict) -> None:
    if (index.get("schema") != "adlfi.lieux.recherche.outremer.public.v1"
        or index.get("cog_ref") != "2026-01-01"
        or len(index.get("pactols_valides", {})) != 212):
        raise ValueError("Index documentaire COG ultramarin non conforme")
    seen = set()
    for prefix, expected in EXPECTED.items():
        rows = index["communes"].get(prefix, "").split("\n")
        if len(rows) != expected:
            raise ValueError("Index COG incomplet pour le territoire " + prefix)
        for line in rows:
            code, sep, nom = line.partition("|")
            if not sep or code not in cog or nom != cog[code]["nom"] or code in seen:
                raise ValueError("Libellé ou identifiant COG divergent dans l'index : " + code)
            seen.add(code)
    if seen != set(cog):
        raise ValueError("Index documentaire et COG officiel ne couvrent pas les mêmes communes")


def construire(fc: dict, communes: dict) -> dict:
    if fc.get("type") != "FeatureCollection" or not isinstance(fc.get("features"), list):
        raise ValueError("Source géographique non GeoJSON")
    vues = {}
    for item in fc["features"]:
        props = item.get("properties") or {}
        code = str(props.get("code") or "")
        if code not in communes:
            continue
        if code in vues:
            raise ValueError("Géométrie dupliquée pour " + code)
        geodata = item.get("geometry")
        if not geodata or geodata.get("type") not in ("Polygon", "MultiPolygon"):
            raise ValueError("Contour non surfacique pour " + code)
        geom = shape(geodata)
        if geom.is_empty or not geom.is_valid or geom.area <= 0:
            raise ValueError("Contour invalide : " + code)
        if any(abs(v) > limit for v, limit in zip(geom.bounds, (180, 90, 180, 90))):
            raise ValueError("Coordonnées hors WGS84 : " + code)
        vues[code] = {"type": "Feature", "properties": {
            "code": code, "nom": communes[code]["nom"],
            "zone": "drom", "niveau": "commune", "annee": 2026,
            "ref_cog": "DROM:COM:" + code,
            "edition_geometrie": "2026-05-04",
            "millesime_cog": "2026-01-01",
            "qualification_geometrie": "controle_topologique_2026",
            "ark_pactols": None,
        }, "geometry": geodata}
    manque = set(communes) - set(vues)
    if manque:
        raise ValueError("Contours DROM manquants : " + ",".join(sorted(manque)))
    if len(vues) != 129:
        raise ValueError("Nombre inattendu de contours DROM")
    return {"type": "FeatureCollection", "features": [vues[k] for k in sorted(vues)],
            "provenance": {
                "schema": SCHEMA, "millesime": 2026,
                "edition_geometrie": "2026-05-04", "cog_ref": "2026-01-01",
                "generalisation_m": 100, "source": SOURCE_URL,
                "sha256_source_geometrique": EXPECTED_SOURCE,
                "sha256_source_cog": EXPECTED_COG,
                "origine_geometrie": "Etalab / Contours administratifs",
                "contours_sans_ARK": True, "restitutions_historiques": 0,
                "nombre_contours": 129,
                "effectifs_drom": EXPECTED
            }}


def generer(geo_path: Path, cog_path: Path, index_path: Path) -> dict:
    if sha(geo_path) != EXPECTED_SOURCE:
        raise ValueError("GeoJSON source du 4 mai 2026 non conforme au SHA-256 épinglé")
    communes = lire_cog(cog_path)
    verifier_index(json.loads(index_path.read_text(encoding="utf-8")), communes)
    raw = geo_path.read_bytes()
    data = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    return construire(data, communes)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--geometries", required=True, type=Path)
    p.add_argument("--cog", required=True, type=Path)
    p.add_argument("--index", required=True, type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    a = p.parse_args()
    data = generer(a.geometries, a.cog, a.index)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8"
    )
    print("DROM_CONTOURS_2026", json.dumps({
        "nombre": len(data["features"]),
        "effectifs": data["provenance"]["effectifs_drom"],
        "source_sha256": EXPECTED_SOURCE,
        "json_sha256": sha(a.sortie),
        "octets": a.sortie.stat().st_size,
        "identites_pactols_inferees": 0,
        "restitutions_historiques": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
