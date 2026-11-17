#!/usr/bin/env python3
"""Préparer les correspondances PDL 2026 validables, sans publication.

Audit exhaustif des liens INSEE de chaque concept sélectionné : une URI
INSEE inconnue du parseur régional bloque la génération, même si un
exactMatch à code paraît par ailleurs univoque.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from auditer_pactols_cog_regions_prioritaires_2026 import audit
from auditer_pactols_polynesie_2026 import ARK, RDF, SKOS
from preparer_validations_pactols_corse_2026 import FIELDS, ecrire_csv

STATUTS_ATTENDUS = {
    "ELIGIBLE_SELON_REGLE": 1140,
    "A_INSTRUIRE_PLUSIEURS_ARK": 60,
    "A_INSTRUIRE_LIBELLE_STATUT_OU_URI": 24,
    "SANS_EXACTMATCH": 4,
}
INSEE_GEO = re.compile(r"^https?://id\.insee\.fr/geo/", re.I)


def preparer_depuis_rapport(rapport: dict, attendus: dict | None = None) -> tuple[list, list, dict]:
    attendus = STATUTS_ATTENDUS if attendus is None else attendus
    pdl = sorted((r for r in rapport["communes"] if r["region"] == "52"),
                 key=lambda r: r["code"])
    counts = collections.Counter(r["etat"] for r in pdl)
    if dict(counts) != attendus:
        raise ValueError("Cardinalités PDL différentes de l'audit contrôlé : " + str(dict(counts)))
    selection = []
    exceptions = []
    arks = set()
    for r in pdl:
        if r["etat"] != "ELIGIBLE_SELON_REGLE":
            exceptions.append({
                "code_insee": r["code"], "libelle_COG_2026": r["nom"],
                "etat_a_instruire": r["etat"],
                "arks_exactMatch": sorted(x["ark"] for x in r["preuves_RDF_exactMatch"]),
                "decision_editoriale": "NON_PRISE",
            })
            continue
        matches = r["preuves_RDF_exactMatch"]
        if len(matches) != 1:
            raise ValueError("Sélection non univoque : " + r["code"])
        p = matches[0]
        uris = [x["uri"] for x in p["insee_exactMatch"]
                if x["famille"] == "commune" and x["code"] == r["code"]]
        if len(uris) != 1 or len(p["insee_exactMatch"]) != 1 or p["ark"] in arks:
            raise ValueError("URI ou ARK ambigu : " + r["code"])
        arks.add(p["ark"])
        selection.append(dict(zip(FIELDS, (
            r["code"], r["nom"], r["region"], r["departement"],
            p["ark"], uris[0], "skos:exactMatch", p["prefLabels_fr"][0],
            rapport["pactols"]["sha256"], "VALIDE_ADLFI_2026",
            "2026-01-01", "REGLE_EXACTMATCH_UNIVOQUE",
            "EN_ATTENTE_RECETTE_PUBLICATION",
        ))))
    if len(arks) != len(selection) or len(set(x["code_insee"] for x in selection)) != len(selection):
        raise ValueError("Identifiants dupliqués dans le registre PDL")
    return selection, exceptions, dict(sorted(counts.items()))


def verifier_toutes_uris_insee(rdf: Path, records: list[dict]) -> None:
    """Détecter toutes les URI INSEE, même non reconnues dans l'audit régional."""
    attendues = {x["ark_pactols"]: x["uri_insee"] for x in records}
    vues = set()
    parser = ET.iterparse(rdf, events=("start", "end"))
    _, root = next(parser)
    if root.tag != RDF + "RDF":
        raise ValueError("Format du RDF Pactols inattendu")
    for event, el in parser:
        if event != "end" or el.tag not in (SKOS + "Concept", RDF + "Description"):
            continue
        match = ARK.fullmatch(el.get(RDF + "about", ""))
        if not match or match.group(1) not in attendues:
            el.clear()
            root.clear()
            continue
        ark = match.group(1)
        if ark in vues:
            raise ValueError("Concept ARK dupliqué dans le RDF : " + ark)
        vues.add(ark)
        exact_insee = sorted({
            x.get(RDF + "resource", "")
            for x in el.findall(SKOS + "exactMatch")
            if INSEE_GEO.match(x.get(RDF + "resource", ""))
        })
        if exact_insee != [attendues[ark]]:
            raise ValueError(
                "Un exactMatch INSEE non reconnu ou contradictoire est présent : "
                + ark + " : " + repr(exact_insee)
            )
        el.clear()
        root.clear()
    if vues != set(attendues):
        raise ValueError("ARK sélectionnés absents du RDF : " + str(len(set(attendues) - vues)))


def produire(rdf: Path, cog: Path) -> tuple[dict, list, list, dict]:
    r = audit(rdf, cog)
    selection, exceptions, states = preparer_depuis_rapport(r)
    verifier_toutes_uris_insee(rdf, selection)
    if len(selection) != 1140 or len(exceptions) != 88:
        raise ValueError("Lot PDL incomplet")
    return r, selection, exceptions, states


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf", required=True, type=Path)
    p.add_argument("--cog", required=True, type=Path)
    p.add_argument("--sortie-csv", required=True, type=Path)
    p.add_argument("--sortie-exceptions", required=True, type=Path)
    args = p.parse_args()
    for sortie in (args.sortie_csv, args.sortie_exceptions):
        if sortie.exists() or "docs" in sortie.resolve().parts:
            raise ValueError("Sortie nouvelle, exclusivement hors dossier docs")
    if args.sortie_csv.resolve() == args.sortie_exceptions.resolve():
        raise ValueError("Les deux sorties doivent être distinctes")

    report, records, exceptions, etats = produire(args.rdf, args.cog)
    ecrire_csv(records, args.sortie_csv)
    args.sortie_exceptions.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "schema": "adlfi.lieux.pactols.pdl.2026.exceptions.v1",
        "millesime_cog": "2026-01-01",
        "pactols_sha256": report["pactols"]["sha256"],
        "cog_sha256": report["cog"]["sha256"],
        "statuts": etats,
        "exceptions": exceptions,
        "liens_historiques_inferes": 0,
        "validations_exceptions": 0,
        "publication": "NON_PUBLIE",
    }
    args.sortie_exceptions.write_text(
        json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print("PDL_REGISTRE_2026", json.dumps({
        "validations_par_regle": len(records),
        "exceptions": len(exceptions),
        "etats": etats,
        "csv_sha256": hashlib.sha256(args.sortie_csv.read_bytes()).hexdigest(),
        "publication": "NON_PUBLIE",
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
