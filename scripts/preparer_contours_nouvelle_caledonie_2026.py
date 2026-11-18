#!/usr/bin/env python3
"""Préparer sans publier les 32 contours communaux néo-calédoniens de référence 2026.

Dumbéa (98805) est strictement exclue : géométrie invalide dans l'édition source.
Aucun ARK, tracé historique ni statut d'homologation n'est inféré.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
SOURCE_URL = "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-100m.geojson.gz"
EXCLUSION = "98805"
EXPECTED = 33
SCHEMA = "adlfi.lieux.contours.nouvelle-caledonie-2026.recette.v1"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def preparer(source, index):
    from shapely.geometry import shape
    from shapely.validation import explain_validity
    if index.get("schema") != "adlfi.lieux.recherche.outremer.public.v1" or index.get("cog_ref") != "2026-01-01":
        raise ValueError("Index COG 2026 inattendu")
    if index.get("contours_invalides") != ["98745", "98805"]:
        raise ValueError("Signalements topologiques de référence modifiés")
    records = {}
    for line in index["communes"]["988"].splitlines():
        code, separator, name = line.partition("|")
        if not separator or not name or len(code) != 5 or not code.startswith("988") or code in records:
            raise ValueError("Code communal COG invalide ou dupliqué : " + line)
        records[code] = name
    if len(records) != EXPECTED or EXCLUSION not in records:
        raise ValueError("Couverture COG Nouvelle-Calédonie inattendue")
    if source.get("type") != "FeatureCollection" or not isinstance(source.get("features"), list):
        raise ValueError("Source géométrique non GeoJSON")
    matches = {}
    for feat in source["features"]:
        code = str((feat.get("properties") or {}).get("code") or "")
        if code in records:
            if code in matches:
                raise ValueError("Géométrie en double : " + code)
            matches[code] = feat
    if set(matches) != set(records):
        raise ValueError("Couverture de 33 géométries incomplète : " + str(sorted(set(records)-set(matches))))
    # La géométrie exclue doit effectivement rester invalide ; ne jamais la réparer silencieusement.
    excluded = shape(matches[EXCLUSION]["geometry"])
    if excluded.is_valid:
        raise ValueError("Dumbéa n'est plus invalide : nouvelle instruction nécessaire")
    features = []
    for code in sorted(set(records) - {EXCLUSION}):
        geometry = matches[code]["geometry"]
        g = shape(geometry)
        if g.geom_type not in ("Polygon", "MultiPolygon") or g.is_empty or not g.is_valid or g.area <= 0:
            raise ValueError("Géométrie invalide : " + code + " : " + explain_validity(g))
        minx, miny, maxx, maxy = g.bounds
        if not (160 < minx < maxx < 170 and -24 < miny < maxy < -18):
            raise ValueError("Emprise néo-calédonienne inattendue : " + code)
        features.append({"type": "Feature", "properties": {
            "code": code, "nom": records[code], "zone": "nouvelle-caledonie",
            "ref_cog": "COMER:COM:" + code, "niveau": "commune", "annee": 2026,
            "millesime_cog": "2026-01-01", "edition_geometrie": "2026-05-04",
            "qualification_geometrie": "controle_topologique_2026",
            "limite_juridique_homologuee": False, "ark_pactols": None
        }, "geometry": geometry})
    if len(features) != 32:
        raise ValueError("32 contours attendus")
    return {"type": "FeatureCollection", "features": features, "provenance": {
        "schema": SCHEMA, "statut": "recette_non_publiee",
        "source_geometrique": SOURCE_URL, "sha256_source_geometrique": SOURCE_SHA256,
        "cog_ref": "2026-01-01", "edition_geometrie": "2026-05-04",
        "generalisation_m": 100, "nombre_contours": 32,
        "exclusion": {"code": EXCLUSION, "motif": "auto_intersection_source_2026",
                      "diagnostic": explain_validity(excluded)},
        "contours_sans_ARK": True, "limites_juridiques_homologuees": False,
        "restitutions_historiques": 0,
        "note": "Poya 98827 : ne pas inférer une province unique à partir du contour communal."
    }}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--geometries", type=Path, required=True)
    p.add_argument("--index-cog", type=Path, required=True)
    p.add_argument("--sortie", type=Path, required=True)
    a = p.parse_args()
    if "docs" in a.sortie.resolve().parts or a.sortie.exists():
        raise ValueError("Sortie de recette neuve hors docs/ uniquement")
    if sha256(a.geometries) != SOURCE_SHA256:
        raise ValueError("SHA-256 de la source Etalab incorrect")
    raw = a.geometries.read_bytes()
    source = json.loads(gzip.decompress(raw) if raw[:2] == b"\\x1f\\x8b" else raw)
    index = json.loads(a.index_cog.read_text(encoding="utf-8"))
    output = preparer(source, index)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\\n", encoding="utf-8")
    print(json.dumps({"contours": 32, "exclu": EXCLUSION,
                      "sha256": sha256(a.sortie), "octets": a.sortie.stat().st_size},
                     ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
