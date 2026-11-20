#!/usr/bin/env python3
"""Inventorier sans modification toutes les références à SER-0063 dans le maître XLSX.

Exemple :
 python3 scripts/auditer_reclassement_grasm.py chemin/maitre.xlsx \
   --rapport /tmp/audit-grasm.json

Le rapport est LOCAL : il peut contenir des extraits des cellules privées du maître.
Aucune nouvelle ORG n'est attribuée et aucune cellule n'est modifiée.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOCREL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKGREL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"x": MAIN}
IDENT = "SER-0063"
EXPECTED_RELATION = "RSE-0083"
EXPECTED_FEDERATION = "ORG-0120"
REFERENCE_RE = re.compile(r"(?<![A-Z0-9])SER-0063(?![A-Z0-9])", re.I)


def normalize_name(value: object) -> str:
    value = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(c for c in value if c.isalnum()).casefold()


def column_index(column_letters: str) -> int:
    index = 0
    for char in column_letters:
        index = index * 26 + ord(char) - 64
    return index - 1


def read_workbook(path: Path) -> dict[str, list[dict]]:
    """Lire toutes les feuilles, y compris les feuilles hors schéma d'export.

    Les formules ne sont pas recalculées : seul leur résultat mis en cache est
    lisible. Les noms de feuilles sont ceux du classeur, sans hypothèse sur leur
    ordre. Le nombre de ligne physique est conservé pour la relecture Excel.
    """
    sheets: dict[str, list[dict]] = {}
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            item.attrib["Id"]: item.attrib["Target"]
            for item in rels.findall(f"{{{PKGREL}}}Relationship")
        }
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in strings.findall(f"{{{MAIN}}}si"):
                shared.append("".join(n.text or "" for n in item.findall(f".//{{{MAIN}}}t")))
        for sheet in workbook.findall("x:sheets/x:sheet", NS):
            name = sheet.get("name") or ""
            relationship = sheet.get(f"{{{DOCREL}}}id")
            if relationship not in targets:
                raise ValueError(f"Relation OOXML absente pour la feuille {name!r}")
            target = targets[relationship]
            if target.startswith("/"):
                member = target.lstrip("/")
            else:
                member = posixpath.normpath(posixpath.join("xl", target))
            if not member.startswith("xl/"):
                raise ValueError(f"Chemin OOXML de feuille inattendu : {member}")
            root = ET.fromstring(archive.read(member))
            rows = []
            for node in root.findall("x:sheetData/x:row", NS):
                number = int(node.get("r") or len(rows) + 1)
                cells: dict[str, str] = {}
                for cell in node.findall("x:c", NS):
                    addr = cell.get("r") or ""
                    matched = re.match(r"([A-Z]+)[1-9][0-9]*$", addr)
                    if not matched:
                        continue
                    col = matched.group(1)
                    kind = cell.get("t")
                    val = cell.find("x:v", NS)
                    value = val.text if val is not None else None
                    if kind == "inlineStr":
                        inline = cell.find("x:is", NS)
                        value = "".join(
                            t.text or "" for t in inline.findall(".//x:t", NS)
                        ) if inline is not None else None
                    elif kind == "s" and value is not None:
                        value = shared[int(value)]
                    elif kind == "e":
                        value = None
                    if value is not None:
                        cells[col] = str(value)
                if cells:
                    rows.append({"row": number, "cells": cells})
            sheets[name] = rows
    return sheets


def tabular_rows(sheets: dict[str, list[dict]], name: str) -> list[dict]:
    """Associer aux cellules des en-têtes de la première ligne non vide."""
    rows = sheets.get(name) or []
    if not rows:
        return []
    headers = {col: text.strip() for col, text in rows[0]["cells"].items()}
    return [{
        "row": item["row"],
        "data": {
            headers[col]: value for col, value in item["cells"].items()
            if col in headers and headers[col]
        },
    } for item in rows[1:]]


def audit(sheets: dict[str, list[dict]], *, filename: str, sha256: str) -> dict:
    """Auditer un classeur, sans écrire ni attribuer d'identifiant."""
    services = tabular_rows(sheets, "Services")
    organismes = tabular_rows(sheets, "Organismes")
    service_rows = [
        item["row"] for item in services
        if item["data"].get("service_id", "").strip().upper() == IDENT
    ]
    candidates = []
    for item in organismes:
        data = item["data"]
        name = normalize_name(data.get("nom_normalise"))
        acronym = normalize_name(data.get("acronyme"))
        if acronym == "grasm" or name == normalize_name("Groupe de recherche archéologique sous-marine"):
            candidates.append({
                "row": item["row"], "id": data.get("organisme_id"),
                "nom_normalise": data.get("nom_normalise"),
                "acronyme": data.get("acronyme"),
            })

    relation_rows = tabular_rows(sheets, "Relations_services")
    matching_relations = [{
        "row": item["row"],
        "relation_service_id": item["data"].get("relation_service_id"),
        "source": item["data"].get("service_source_id"),
        "target": item["data"].get("organisme_cible_id")
            or item["data"].get("service_cible_id"),
        "type": item["data"].get("type_relation"),
        "validation": item["data"].get("statut_validation"),
    } for item in relation_rows if
        item["data"].get("relation_service_id") == EXPECTED_RELATION
        or item["data"].get("service_source_id") == IDENT
        or item["data"].get("service_cible_id") == IDENT]

    occurrences = []
    counts = Counter()
    for name, rows in sheets.items():
        headers = (rows[0]["cells"] if rows else {})
        for item in rows:
            for column, value in item["cells"].items():
                if not REFERENCE_RE.search(value):
                    continue
                field = headers.get(column) if item is not rows[0] else "(en-tête)"
                occurrence = {
                    "sheet": name, "row": item["row"],
                    "column": column, "field": field,
                    "value_excerpt": value[:180],
                }
                occurrences.append(occurrence)
                counts[name] += 1

    expected = [
        item for item in matching_relations
        if item["relation_service_id"] == EXPECTED_RELATION
        and item["source"] == IDENT
        and item["target"] == EXPECTED_FEDERATION
        and item["type"] == "rattachement_service"
    ]
    checks = {
        "ser_0063_unique_dans_services": len(service_rows) == 1,
        "aucune_org_homonyme_deja_creee": not candidates,
        "rse_0083_rattachement_attendu_present": len(expected) == 1,
        "relations_avec_ser_0063_toutes_recensees": True,
        "relecture_toutes_feuilles": True,
    }
    return {
        "nature": "préflight en lecture seule, sans conversion d'identifiants",
        "source": {"filename": filename, "sha256": sha256},
        "sheets_scanned": list(sheets),
        "ser_0063_service_rows": service_rows,
        "potential_organisme_duplicates": candidates,
        "relations_services_implicated": matching_relations,
        "occurrences_by_sheet": dict(sorted(counts.items())),
        "occurrences": occurrences,
        "checks": checks,
        "ready_for_editorial_arbitrage": all(checks.values()),
        "proposed_actions": [
            "Attribuer un ORG libre depuis le dernier maître, après recherche de doublons.",
            "Créer une correspondance pérenne de SER-0063 vers le nouvel ORG ; ne pas simuler une succession historique.",
            "Reprendre chaque référence de toutes les feuilles, notamment les correspondances d'affiliations éditoriales.",
            "Remplacer RSE-0083 (rattachement_service) par une relation d'affiliation fédérale ORG vers ORG-0120.",
            "Reprendre le logo canonique et tester les liens entrants vers SER-0063.",
            "Régénérer le JSON et vérifier l'absence de références orphelines, les contrôles CI et la fiche navigateur.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("maitre", type=Path)
    parser.add_argument("--rapport", type=Path,
                        help="Chemin local du rapport JSON (par défaut : stdout)")
    args = parser.parse_args(argv)
    path = args.maitre.resolve()
    if not path.is_file():
        parser.error(f"Classeur introuvable : {path}")
    if not zipfile.is_zipfile(path):
        parser.error(f"Fichier non OOXML : {path}")
    if args.rapport and args.rapport.resolve() == path:
        parser.error("Le rapport ne peut jamais écraser le maître")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    result = audit(read_workbook(path), filename=path.name, sha256=digest)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.rapport:
        args.rapport.parent.mkdir(parents=True, exist_ok=True)
        args.rapport.write_text(payload, encoding="utf-8")
        print(f"Audit écrit : {args.rapport}")
        print(f"Feuilles : {len(result['sheets_scanned'])} ; occurrences : {len(result['occurrences'])}")
        print(f"Préflight : {'OK' if result['ready_for_editorial_arbitrage'] else 'À INSTRUIRE'}")
    else:
        print(payload, end="")
    return 0 if result["ready_for_editorial_arbitrage"] else 2


if __name__ == "__main__":
    sys.exit(main())
