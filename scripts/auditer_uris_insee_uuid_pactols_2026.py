#!/usr/bin/env python3
"""Recette non validante des exactMatch Pactols vers des URI INSEE de type UUID.

Le segment UUID ne désigne pas un code COG. Même avec un nom compatible, la
résolution de la ressource et de sa temporalité doit provenir de l'INSEE.
Aucun ARK n'est publié et aucune succession géographique n'est inférée.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from auditer_pactols_polynesie_2026 import (
    ARK, DCT, OWL, RDF, RDF_COMMIT, RDF_SHA, SKOS, XML, norm,
)
from auditer_pactols_cog_regions_prioritaires_2026 import (
    communes_actuelles, sha,
)

UUID_URI = re.compile(
    r"^https?://id\.insee\.fr/geo/commune/"
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/?$",
    re.I,
)
CODE_URI = re.compile(r"^https?://id\.insee\.fr/geo/commune/([0-9A-Z]{5})/?$")
SCHEMA = "adlfi.lieux.pactols.insee-uuid.bfc.2026.recette.v1"


def scanner_uuid(rdf: Path, communes_bfc: dict[str, str]) -> dict:
    """Inventorier toutes les URI UUID ; rapprocher les noms sans conclure."""
    codes_par_nom = collections.defaultdict(set)
    for code, nom in communes_bfc.items():
        codes_par_nom[norm(nom)].add(code)

    concepts_examines = 0
    records = []
    parser = ET.iterparse(rdf, events=("start", "end"))
    _, root = next(parser)
    if root.tag != RDF + "RDF":
        raise ValueError("Source XML qui n'est pas rdf:RDF")
    for event, el in parser:
        if event != "end" or el.tag not in (SKOS + "Concept", RDF + "Description"):
            continue
        match_ark = ARK.fullmatch(el.get(RDF + "about", ""))
        if not match_ark:
            el.clear()
            root.clear()
            continue
        if el.tag == RDF + "Description" and not any(
            x.get(RDF + "resource") == "http://www.w3.org/2004/02/skos/core#Concept"
            for x in el.findall(RDF + "type")
        ):
            el.clear()
            root.clear()
            continue
        concepts_examines += 1
        exact = sorted({
            x.get(RDF + "resource", "")
            for x in el.findall(SKOS + "exactMatch")
            if x.get(RDF + "resource")
        })
        uuid = sorted(x for x in exact if UUID_URI.fullmatch(x))
        if uuid:
            pref = sorted({
                x.text.strip() for x in el.findall(SKOS + "prefLabel")
                if x.text and x.get(XML + "lang", "").lower().startswith("fr")
            })
            alt = sorted({
                x.text.strip() for x in el.findall(SKOS + "altLabel")
                if x.text and x.get(XML + "lang", "").lower().startswith("fr")
            })
            candidats = sorted({
                code for label in pref + alt
                for code in codes_par_nom.get(norm(label), ())
            })
            codes_directs = sorted({
                m.group(1) for uri in exact
                if (m := CODE_URI.fullmatch(uri))
                and m.group(1) in communes_bfc
            })
            deprecie = any(
                (x.text or "").strip().lower() in ("1", "true")
                for x in el.findall(OWL + "deprecated")
            )
            records.append({
                "ark": match_ark.group(1),
                "prefLabels_fr": pref,
                "altLabels_fr": alt,
                "uris_insee_uuid_exactMatch": uuid,
                "autres_exactMatch": sorted(set(exact) - set(uuid)),
                "codes_bfc_directement_assertes": codes_directs,
                "codes_bfc_par_libelle_non_validants": candidats,
                "concerne_potentiellement_bfc": bool(candidats or codes_directs),
                "deprecie": deprecie,
                "remplace": bool(el.findall(DCT + "isReplacedBy")),
                "statut": "A_INSTRUIRE_RESOLUTION_URI_INSEE_UUID",
                "code_cog_resolu_par_uuid": None,
                "decision_editoriale": "NON_PRISE",
                "publication": "NON_PUBLIE",
            })
        el.clear()
        root.clear()
    records.sort(key=lambda p: p["ark"])
    return {"concepts_RDF_examines": concepts_examines, "concepts_uuid": records}


def audit(rdf: Path, cog: Path) -> dict:
    if sha(rdf) != RDF_SHA:
        raise ValueError("Source RDF Pactols différente du snapshot épinglé")
    noms = communes_actuelles(cog)
    bfc = {code: p["nom"] for code, p in noms.items() if p["region"] == "27"}
    scan = scanner_uuid(rdf, bfc)
    records = scan["concepts_uuid"]
    concernes = [r for r in records if r["concerne_potentiellement_bfc"]]
    val = [r for r in concernes if "25060" in (
        r["codes_bfc_directement_assertes"] +
        r["codes_bfc_par_libelle_non_validants"]
    )]
    return {
        "schema": SCHEMA,
        "statut": "RECETTE_NON_VALIDANTE",
        "source_pactols": {"commit": RDF_COMMIT, "sha256": RDF_SHA},
        "source_cog": {"millesime": "2026-01-01", "sha256": sha(cog)},
        "communes_bfc_COG_2026": len(bfc),
        "concepts_RDF_examines": scan["concepts_RDF_examines"],
        "concepts_avec_exactMatch_uuid_INSEE": len(records),
        "concepts_uuid_concernant_potentiellement_BFC": len(concernes),
        "candidats_val_d_usiers_25060": val,
        "concepts": records,
        "nouvelles_validations": 0,
        "modifications_index_public": 0,
        "geometries_historiques_inferrees": 0,
        "limites": [
            "Un UUID de ressource INSEE n'est pas un code de commune.",
            "Les correspondances lexicales, même uniques, ne valident aucun code.",
            "Résoudre le type, le code et la période de la ressource INSEE dans le RDF officiel avant toute décision.",
            "Le code 25060 de Val-d'Usiers est hérité de Bians-les-Usiers en 2024 : le code seul ne prouve pas l'identité historique.",
            "Les exactMatch à UUID sont conservés même s'ils coexistent avec une URI de code COG.",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf", required=True, type=Path)
    p.add_argument("--cog", required=True, type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    a = p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Nouveau rapport seulement, hors du dossier public docs")
    result = audit(a.rdf, a.cog)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print("BFC_INSEE_UUID", json.dumps({
        "concepts_RDF_examines": result["concepts_RDF_examines"],
        "uuid": result["concepts_avec_exactMatch_uuid_INSEE"],
        "potentiellement_bfc": result["concepts_uuid_concernant_potentiellement_BFC"],
        "val_d_usiers": result["candidats_val_d_usiers_25060"],
        "validations": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
