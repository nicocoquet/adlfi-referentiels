#!/usr/bin/env python3
"""Premier lot normand : distinguer dix communes nouvelles de leurs anciennes identités.

Audit non publiant, à partir d'un RDF Pactols strictement épinglé. Les dates de
création et noms des communes anciennes proviennent des fiches INSEE citées dans
CASES ; l'audit ne prétend pas rejouer les mouvements COG depuis le fichier brut.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from auditer_pactols_polynesie_2026 import (
    RDF, SKOS, OWL, DCT, XML, ARK, RDF_SHA, RDF_COMMIT,
    analyser_rdf,
)

SCHEMA = "adlfi.lieux.normandie.communes-nouvelles.lot01.2026.audit.v1"
INSEE_DOSSIER = "https://www.insee.fr/fr/statistiques/2011101?geo=COM-"

# Codes historiques conservés. Les sources INSEE sont indépendantes de la
# présence d'un exactMatch RDF, et ne transfèrent aucune identité Pactols.
CASES = {
    "50129": {
        "nom": "Cherbourg-en-Cotentin", "date": "2016-01-01",
        "ancienne": "Cherbourg-Octeville",
        "actuel": "26678/pcrt4Ft3j507NA", "ancien": "26678/pcrtKpjSHTRIyK",
    },
    "50412": {
        "nom": "Port-Bail-sur-Mer", "date": "2019-01-01",
        "ancienne": "Portbail",
        "actuel": None, "ancien": "26678/pcrtouI45wMnJl",
    },
    "14456": {
        "nom": "Moult-Chicheboville", "date": "2017-01-01",
        "ancienne": "Moult",
        "actuel": "26678/pcrtNAhK2vpwPa", "ancien": "26678/pcrtetxgQaGZ5H",
    },
    "61194": {
        "nom": "Monts-sur-Orne", "date": "2018-01-01",
        "ancienne": "Goulet",
        "actuel": "26678/pcrtZtrHp1bjSL", "ancien": "26678/pcrtinAdI9l885",
    },
    "14762": {
        "nom": "Vire Normandie", "date": "2016-01-01",
        "ancienne": "Vire",
        "actuel": "26678/pcrt78ZZg0wMbU", "ancien": "26678/pcrtkeqj9I3nbw",
    },
    "27467": {
        "nom": "Pont-Audemer", "date": "2018-01-01",
        "ancienne": "Pont-Audemer", "cas_homonyme": True,
        "actuel": "26678/pcrttaqrTGrSS9",
        "candidats": ["26678/pcrttaqrTGrSS9", "26678/pcrtFmM1SUxsz6"],
        "ancien": "26678/pcrtFmM1SUxsz6",
    },
    "27022": {
        "nom": "Le Val d'Hazey", "date": "2016-01-01",
        "ancienne": "Aubevoye",
        "actuel": "26678/pcrt5SNyKsPv04", "ancien": "26678/pcrtABogj7gxSP",
    },
    "14098": {
        "nom": "Thue et Mue", "date": "2017-01-01",
        "ancienne": "Bretteville-l'Orgueilleuse",
        "actuel": "26678/pcrt32xA0aWOKZ", "ancien": "26678/pcrt37IBobgENS",
    },
    "14014": {
        "nom": "Colomby-Anguerny", "date": "2016-01-01",
        "ancienne": "Anguerny",
        "actuel": "26678/pcrtAHatdH8M5h", "ancien": "26678/pcrtqhCH2knMXr",
    },
    "14200": {
        "nom": "Creully sur Seulles", "date": "2017-01-01",
        "ancienne": "Creully",
        "actuel": "26678/pcrtEU57VjwLxi", "ancien": "26678/crtHlZfEWxn98",
    },
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def arks_attendus(code: str) -> set[str]:
    spec = CASES[code]
    return set(spec["candidats"]) if spec.get("cas_homonyme") else {
        a for a in (spec["actuel"], spec["ancien"]) if a
    }


def rdf_complementaire(path: Path, wanted: set[str]) -> dict:
    """Extraire les notes, liens et statuts des seuls concepts déjà identifiés."""
    found = {}
    parser = ET.iterparse(path, events=("start", "end"))
    _, root = next(parser)
    if root.tag != RDF + "RDF":
        raise ValueError("RDF/XML attendu")
    for event, el in parser:
        if event != "end" or el.tag not in (SKOS + "Concept", RDF + "Description"):
            continue
        m = ARK.fullmatch(el.get(RDF + "about", ""))
        if not m or m.group(1) not in wanted:
            el.clear()
            root.clear()
            continue
        ark = m.group(1)
        if ark in found:
            raise ValueError("Concept Pactols dupliqué : " + ark)
        exact = sorted({n.get(RDF + "resource", "") for n in el.findall(SKOS + "exactMatch")
                        if n.get(RDF + "resource")})
        notes = []
        for kind in ("historyNote", "changeNote", "scopeNote", "definition"):
            for n in el.findall(SKOS + kind):
                if (n.text or "").strip():
                    notes.append({"type": kind, "texte": n.text.strip()[:1600]})
        found[ark] = {
            "exactMatch": exact,
            "prefLabels_fr": sorted({n.text.strip() for n in el.findall(SKOS + "prefLabel")
                                    if n.text and (n.get(XML + "lang") or "").lower().startswith("fr")}),
            "altLabels_fr": sorted({n.text.strip() for n in el.findall(SKOS + "altLabel")
                                   if n.text and (n.get(XML + "lang") or "").lower().startswith("fr")}),
            "notes": notes,
            "owl_deprecated": any((n.text or "").strip().lower() in ("true", "1")
                                  for n in el.findall(OWL + "deprecated")),
            "dct_isReplacedBy": sorted({n.get(RDF + "resource") or (n.text or "").strip()
                                       for n in el.findall(DCT + "isReplacedBy")}),
            "dct_replaces": sorted({n.get(RDF + "resource") or (n.text or "").strip()
                                   for n in el.findall(DCT + "replaces")}),
        }
        el.clear()
        root.clear()
    if set(found) != wanted:
        raise ValueError("ARK absents du RDF : " + repr(sorted(wanted - set(found))))
    return found


def classer(code: str, ark: str, details: dict) -> str:
    spec = CASES[code]
    if details["owl_deprecated"] or details["dct_isReplacedBy"]:
        return "A_INSTRUIRE_CONCEPT_REMPLACE"
    if spec.get("cas_homonyme"):
        # Même libellé et même code, mais identifiants Wikidata indépendants :
        # Q367667 = ancienne commune ; Q47067820 = commune actuelle.
        # La définition doit également distinguer l'identité.
        definitions = [n["texte"].casefold() for n in details["notes"]
                       if n["type"] == "definition"]
        if ark == spec["ancien"]:
            if ("http://www.wikidata.org/entity/Q367667" in details["exactMatch"]
                    and any("ancienne commune" in d for d in definitions)):
                return "ANCIENNE_COMMUNE_DELEGUEE_IDENTIFIEE"
            return "HOMONYMIE_PERSISTANTE_A_INSTRUIRE"
        if (ark == spec["actuel"] and
                "http://www.wikidata.org/entity/Q47067820" in details["exactMatch"]
                and any("pont-audemer est une commune française" in d for d in definitions)):
            return "CANDIDAT_COMMUNE_NOUVELLE_2026_A_ARBITRER"
        return "HOMONYMIE_PERSISTANTE_A_INSTRUIRE"
    if ark == spec["ancien"]:
        return "IDENTITE_ANCIENNE_COMMUNE_A_PRESERVER"
    if ark == spec["actuel"]:
        return "CANDIDAT_COMMUNE_NOUVELLE_2026_A_ARBITRER"
    raise ValueError("ARK non attendu : " + ark)


def produire(rdf: Path) -> dict:
    if sha256(rdf) != RDF_SHA:
        raise ValueError("Source Pactols différente du snapshot RDF épinglé")
    names = {code: spec["nom"] for code, spec in CASES.items()}
    scan = analyser_rdf(rdf, names)
    expected = set().union(*(arks_attendus(code) for code in CASES))
    detailed = rdf_complementaire(rdf, expected)
    dossiers = []
    for code, spec in sorted(CASES.items()):
        hits = scan["explicites"][code]
        if set(h["ark"] for h in hits) != arks_attendus(code):
            raise ValueError("Changement des ARK concurrents au code COG : " + code)
        candidates = []
        for hit in hits:
            ark = hit["ark"]
            item = detailed[ark]
            if (item["prefLabels_fr"] != hit["prefLabels_fr"] or
                    item["altLabels_fr"] != hit["altLabels_fr"] or
                    item["owl_deprecated"] != hit["deprecie"]):
                raise ValueError("Preuves Pactols incohérentes : " + ark)
            uris = [i for i in hit["insee_exactMatch"] if i["famille"] == "commune"]
            if len(uris) != 1 or uris[0]["code"] != code or len(hit["codes_communaux_cites"]) != 1:
                raise ValueError("exactMatch concurrent ou absent pour " + ark)
            if len(item["prefLabels_fr"]) != 1:
                raise ValueError("prefLabel non univoque : " + ark)
            expected_label = (spec["nom"] if ark == spec["actuel"]
                              else (spec["ancienne"] if ark == spec["ancien"] else spec["nom"]))
            if spec.get("cas_homonyme") and ark == spec["ancien"]:
                expected_label = "Pont-Audemer (commune déléguée)"
            if item["prefLabels_fr"][0] != expected_label:
                raise ValueError("Identité lexicale inattendue : " + ark)
            candidates.append({
                "ark": ark,
                "classification": classer(code, ark, item),
                **item,
            })
        if not spec.get("cas_homonyme") and spec["actuel"] is None:
            if len(candidates) != 1:
                raise ValueError("Cas sans ARK nouveau non univoque : " + code)
        dossiers.append({
            "code_COG_2026": code,
            "nom_COG_2026": spec["nom"],
            "date_creation_INSEE": spec["date"],
            "ancienne_commune_porteuse_code": spec["ancienne"],
            "source_INSEE": INSEE_DOSSIER + code,
            "statut": ("CANDIDAT_EDITION_2026_SANS_PUBLICATION"
                       if any(c["classification"] == "CANDIDAT_COMMUNE_NOUVELLE_2026_A_ARBITRER"
                              for c in candidates)
                       else "INDECIDABLE_ARK_COMMUNE_ACTUELLE"),
            "candidats_Pactols": candidates,
            "decision_editoriale": "NON_PRISE",
            "nouveaux_alignements_publies": 0,
            "contours_historiques_inferes": 0,
        })
    tally = Counter(c["classification"] for d in dossiers for c in d["candidats_Pactols"])
    return {
        "schema": SCHEMA,
        "statut": "RECETTE_NON_PUBLIANTE",
        "sources": {
            "rdf_Pactols_commit": RDF_COMMIT,
            "rdf_Pactols_sha256": RDF_SHA,
            "cog": "COG Insee 2026 (REG=28), attestations officielles par code dans chaque dossier",
            "date_consultation_sources_officielles": "2026-11-20",
        },
        "bilan": {
            "dossiers": len(dossiers),
            "candidats_Pactols": len(expected),
            "codes_avec_candidat_distinct_commune_actuelle": sum(
                d["statut"] == "CANDIDAT_EDITION_2026_SANS_PUBLICATION" for d in dossiers),
            "codes_sans_arbitrage_identite_actuelle": sum(
                d["statut"] == "INDECIDABLE_ARK_COMMUNE_ACTUELLE" for d in dossiers),
            "classes_RDF": dict(sorted(tally.items())),
            "nouvelles_validations_publiees": 0,
            "limites_historiques_inferrees": 0,
        },
        "dossiers": dossiers,
        "limitations": [
            "La qualification des ARK en concept de commune nouvelle n'est pas une validation éditoriale.",
            "Un même code INSEE avant et après la création ne prouve pas une identité persistante.",
            "Les notices AdlFI sont indexées avec un thésaurus actuel ; l'année d'opération ne prouve pas la validité historique d'un ARK.",
            "À Pont-Audemer, le concept actuel n'est candidat que grâce aux URI Wikidata distinctes et aux définitions RDF, corroborées par le COG 2018 ; le seul libellé ne suffit pas.",
            "Le concept Portbail, seul concept RDF exactMatch au code 50412, ne doit pas représenter automatiquement Port-Bail-sur-Mer.",
            "Les dates INSEE sont des attestations documentées, non déduites du RDF.",
            "Aucun contour ni nouvelle association Pactols–COG n'est publié par ce rapport.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rdf", type=Path, required=True)
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    out = args.sortie.resolve()
    if "docs" in out.parts or out.exists():
        raise ValueError("Sortie de recette neuve hors docs/ uniquement")
    report = produire(args.rdf)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                   encoding="utf-8")
    print("NORMANDIE_LOT01", json.dumps(report["bilan"], sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
