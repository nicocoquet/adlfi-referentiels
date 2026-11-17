#!/usr/bin/env python3
"""Construire le registre et l'index PDL 2026, distincts du COG historique.

La génération exige les sources officielles épinglées, les 1 140 liens
univoques et le contrôle exhaustif des URI exactMatch INSEE dans le RDF.
N'écrit jamais dans les fichiers de chronologie/contours.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from preparer_validations_pactols_pdl_2026 import produire
from preparer_validations_pactols_corse_2026 import ecrire_csv

SOURCE_REGISTRE = "recette/lieux/PDL-VALIDATIONS-PACTOLS-COG-2026.csv"
SCHEMA = "adlfi.lieux.pactols.pdl.2026.public.v1"
CSV_SHA = "81c49e32e5a443a1dd2e9f40e2d82c842a72ab1f82d81833fd51f02ae9d71335"
DATE_VALIDATION = "2026-11-17"


def index_public(rapport: dict, registres: list[dict]) -> dict:
    if len(registres) != 1140:
        raise ValueError("Le registre PDL doit comporter 1140 décisions")
    return {
        "schema": SCHEMA,
        "region": "pdl",
        "millesime_cog": "2026-01-01",
        "source_rdf": "Pactols_Lieux_th17_20260722.rdf",
        "source_rdf_sha256": rapport["pactols"]["sha256"],
        "source_registre": SOURCE_REGISTRE,
        "nombre_communes": 1140,
        "communes_a_instruire": 88,
        "nouvelles_geometries": 0,
        "liens_historiques_inferes": 0,
        "alignements_Pactols_COG_valides_2026": [
            {
                "code_insee": row["code_insee"],
                "libelle_COG_2026": row["libelle_COG_2026"],
                "ark_pactols": row["ark_pactols"],
                "libelle_pactols": row["prefLabel_fr_pactols"],
                "uri_insee": row["uri_insee"],
                "predicat_source": "skos:exactMatch",
                "millesime_validation": 2026,
                "date_validation": DATE_VALIDATION,
                "statut": "correspondance_PDL_validee_2026",
            }
            for row in registres
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rdf", required=True, type=Path)
    parser.add_argument("--cog", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    args = parser.parse_args()
    if args.csv.resolve() == args.json.resolve():
        raise ValueError("CSV et JSON doivent être distincts")
    audit, decisions, exceptions, _ = produire(args.rdf, args.cog)
    if len(exceptions) != 88 or any(x["code_insee"] in {"44066", "85165", "85212", "85292"} for x in decisions):
        raise ValueError("Exceptions PDL ou les quatre communes sans assertion promues")
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    ecrire_csv(decisions, args.csv)
    import hashlib
    csv_sha = hashlib.sha256(args.csv.read_bytes()).hexdigest()
    if csv_sha != CSV_SHA:
        raise ValueError("Registre PDL divergent de la recette PR 104 : " + csv_sha)
    published = index_public(audit, decisions)
    args.json.write_text(
        json.dumps(published, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("PDL_1140_PUBLICATION_GENEREE", json.dumps({
        "registres": len(decisions), "exceptions_exclues": len(exceptions),
        "csv_sha256": csv_sha,
        "taille_json": args.json.stat().st_size,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
