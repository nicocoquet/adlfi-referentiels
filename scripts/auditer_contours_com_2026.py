#!/usr/bin/env python3
"""Audit sans publication des 83 communes des COM du socle ultramarin 2026.

Fournit une première qualification géométrique Etalab par code COG ;
ne conclut ni à l'authenticité juridique des limites, ni à leur identité
dans les sources ISPF / GEO PF. Aucun polygone n'est diffusé.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
from pathlib import Path

from shapely.geometry import shape
from shapely.validation import explain_validity

from publier_contours_drom_2026 import EXPECTED_SOURCE, SOURCE_URL, sha

SCHEMA = "adlfi.lieux.com.83-communes.2026.audit.v1"
EXPECTED = {"975": 2, "987": 48, "988": 33}


def codes_communaux(index: dict) -> dict[str, dict]:
    if (index.get("schema") != "adlfi.lieux.recherche.outremer.public.v1"
        or index.get("cog_ref") != "2026-01-01"
        or index.get("edition_geom") != "2026-05-04"
        or index.get("source_audit_sha256") !=
        "5aa79d28ab3d7dcf5952937b90e2beb4a558afc1f1b05c9c697b30682ae60b33"):
        raise ValueError("Index COG ultramarin non conforme à la recette")
    records = {}
    for prefix, count in EXPECTED.items():
        rows = index["communes"].get(prefix, "").split("\n")
        if len(rows) != count:
            raise ValueError("Nombre de communes COG incorrect : " + prefix)
        for line in rows:
            code, sep, name = line.partition("|")
            if (not sep or not code.startswith(prefix) or len(code) != 5
                or not name or code in records):
                raise ValueError("Identifiant communal ambigu : " + line)
            records[code] = {"code": code, "libelle_COG": name, "territoire": prefix}
    if len(records) != 83 or sorted(index["contours_invalides"]) != ["98745", "98805"]:
        raise ValueError("Les diagnostics 2026 de Tahaa / Dumbéa ont été modifiés")
    return records


def inventorier(fc: dict, codes: dict[str, dict], index: dict) -> dict:
    if fc.get("type") != "FeatureCollection" or not isinstance(fc.get("features"), list):
        raise ValueError("Source non GeoJSON")
    geom = {}
    for f in fc["features"]:
        code = str((f.get("properties") or {}).get("code") or "")
        if code not in codes:
            continue
        if code in geom:
            raise ValueError("Code de géométrie COM dupliqué : " + code)
        geom[code] = f
    rows = []
    for code, c in sorted(codes.items()):
        f = geom.get(code)
        shape_type = None
        valide = False
        cause = "ABSENT"
        if f and isinstance(f.get("geometry"), dict):
            g = shape(f["geometry"])
            shape_type = g.geom_type
            valide = (shape_type in ("Polygon", "MultiPolygon")
                      and g.is_valid and not g.is_empty and g.area > 0)
            cause = "VALIDE" if valide else explain_validity(g)[:200]
        rows.append({
            **c,
            "geometrie_presente": f is not None,
            "type_geometrie": shape_type,
            "geometrie_topologiquement_valide": bool(valide),
            "diagnostic_geometrique": cause,
            "signalement_index_public_invalide": code in index["contours_invalides"],
            "evaluation_limite_juridique": "NON_EFFECTUEE",
            "identite_ARK_geometrique": "NON_INFEREE",
            "publication": "NON_PUBLIE",
        })
    counts = collections.Counter(r["territoire"] for r in rows if r["geometrie_topologiquement_valide"])
    missing = [r["code"] for r in rows if not r["geometrie_presente"]]
    invalid = [r["code"] for r in rows if r["geometrie_presente"] and
               not r["geometrie_topologiquement_valide"]]
    signalements = sorted(index["contours_invalides"])
    return {
        "schema": SCHEMA,
        "statut": "RECETTE_GEOMETRIQUE_NON_VALIDANTE",
        "source_geometrie": {
            "url": SOURCE_URL,
            "sha256": EXPECTED_SOURCE,
            "edition": "2026-05-04",
            "generalisation": "100m",
        },
        "source_COG": {
            "index": "docs/data/lieux-outremer/recherche-2026.json",
            "millesime": "2026-01-01",
            "statut": "projection du COG public, sans géométrie"
        },
        "bilan": {
            "communes_COG": len(rows), "geometries_presentes": len(geom),
            "geometries_valides": sum(r["geometrie_topologiquement_valide"] for r in rows),
            "valides_par_territoire": dict(sorted(counts.items())),
            "codes_absents": missing,
            "codes_invalides": invalid,
            "signalements_geometriques_preexistants": signalements,
            "signalements_conformes_aux_invalides": invalid == signalements,
            "nouvelles_geometries_publiees": 0,
            "ark_pactols_inferes": 0,
            "contours_historiques_inferes": 0,
        },
        "communes": rows,
        "limites": [
            "Validité GEOS seule : elle n'atteste pas le périmètre légal ou la date de production du tracé.",
            "La source Etalab peut utiliser des contributions OSM dans les COM.",
            "Les différences ISPF / GEO PF en Polynésie restent en instruction.",
            "Le code COG d'une commune ne valide ni son ARK ni un état administratif ancien.",
            "Aucune publication des polygones ne découle de cet audit."
        ],
    }


def audit(geo: Path, index_file: Path) -> dict:
    if sha(geo) != EXPECTED_SOURCE:
        raise ValueError("SHA-256 du GeoJSON Etalab 2026 non conforme")
    index = json.loads(index_file.read_text(encoding="utf-8"))
    codes = codes_communaux(index)
    raw = geo.read_bytes()
    fc = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    return inventorier(fc, codes, index)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--geometries", required=True, type=Path)
    p.add_argument("--index", required=True, type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    a = p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Le rapport doit être neuf et hors du dossier public docs")
    data = audit(a.geometries, a.index)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print("COM_83_CONTOURS_BILAN", json.dumps(data["bilan"], ensure_ascii=False, sort_keys=True))
    for r in data["communes"]:
        if not r["geometrie_topologiquement_valide"]:
            print("COM_83_EXCEPTION", json.dumps(r, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
