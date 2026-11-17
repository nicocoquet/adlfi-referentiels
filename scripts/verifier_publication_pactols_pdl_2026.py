#!/usr/bin/env python3
"""Contrôle hors RDF de la publication Pactols PDL 2026 (CSV/JSON/COG/manifeste)."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from preparer_validations_pactols_pdl_2026 import STATUTS_ATTENDUS
from preparer_validations_pactols_corse_2026 import FIELDS
from publier_alignements_pactols_pdl_2026 import (
    CSV_SHA, DATE_VALIDATION, SCHEMA, SOURCE_REGISTRE, index_public,
)

ROOT = Path(__file__).resolve().parents[1]
DEP = re.compile(r"^(?:44|49|53|72|85)\d{3}$")
SOURCE_SHA = "3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"


def verifier(root=ROOT):
    csv_path = root / SOURCE_REGISTRE
    json_path = root / "docs/data/lieux-chronologie/pactols-pdl-2026.json"
    cog_path = root / "docs/data/lieux-chronologie/cog-pdl.json"
    manifest_path = root / "docs/data/manifest.json"
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("Colonnes registre PDL incompatibles")
        decisions = list(reader)
    import hashlib
    if hashlib.sha256(csv_path.read_bytes()).hexdigest() != CSV_SHA:
        raise ValueError("Registre PDL différent du CSV source PR 102")
    pub = json.loads(json_path.read_text(encoding="utf-8"))
    cog = json.loads(cog_path.read_text(encoding="utf-8"))
    man = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(decisions) != 1140 or len(pub.get("alignements_Pactols_COG_valides_2026", [])) != 1140:
        raise ValueError("Nombre d'alignements PDL incompatible")
    current = {
        p["code_insee"]: p["libelle"] for p in cog["periodes_com"]
        if p["typecom"] == "COM" and p["debut_inclus"] <= "2026-01-01"
        and (not p["fin_exclue"] or p["fin_exclue"] > "2026-01-01")
    }
    if len(current) != 1228 or cog["alignements_Pactols_COG_valides_2026"] != [] or cog["geometries_historiques"] != []:
        raise ValueError("COG PDL historique modifié ou incomplet")
    codes = set()
    arks = set()
    for r in decisions:
        code,ark=r["code_insee"],r["ark_pactols"]
        if (not DEP.fullmatch(code) or code not in current or code in codes or ark in arks
            or current[code] != r["libelle_COG_2026"]
            or not re.fullmatch(r"26678/[A-Za-z0-9]+", ark)
            or r["uri_insee"] != "http://id.insee.fr/geo/commune/" + code
            or r["source_rdf_sha256"] != SOURCE_SHA
            or r["predicat_source"] != "skos:exactMatch"
            or r["statut_validation"] != "VALIDE_ADLFI_2026"
            or r["portee_COG"] != "2026-01-01"
            or r["type_decision"] != "REGLE_EXACTMATCH_UNIVOQUE"
            or r["publication_site"] != "EN_ATTENTE_RECETTE_PUBLICATION"):
            raise ValueError("Décision de publication PDL invalide : "+code)
        codes.add(code)
        arks.add(ark)
    if bool(codes & {"44066", "85165", "85212", "85292"}) or len(codes) != 1140 or len(current.keys() - codes) != 88:
        raise ValueError("les quatre communes sans exactMatch ou les autres exceptions ont été publiées")
    expected = index_public(
        {"pactols":{"sha256":SOURCE_SHA}}, decisions
    )
    if pub != expected:
        raise ValueError("Index public PDL divergent du registre vérifié")
    meta = man["modules"]["lieux"]["pactols_pdl_2026"]
    if (meta["fichier"] != "data/lieux-chronologie/pactols-pdl-2026.json"
        or meta["communes"] != 1140 or meta["relations_validees"] != 1140
        or meta["communes_a_instruire"] != 88
        or meta["source_registre"] != SOURCE_REGISTRE
        or meta["portee_COG"] != "2026-01-01"
        or meta["geometries_historiques_validees"] != 0
        or meta["retroprojections"] != 0):
        raise ValueError("Manifeste PDL non conforme")
    return {"liens_pactols":len(decisions),"exceptions":len(current.keys()-codes),
            "ark_uniques":len(arks),"liens_historiques_inferes":0,
            "geometries_historiques_modifiees":0}


if __name__ == "__main__":
    print("PDL_1140_PUBLICATION_OK",
          json.dumps(verifier(),ensure_ascii=False,sort_keys=True))
