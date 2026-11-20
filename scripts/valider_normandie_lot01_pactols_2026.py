#!/usr/bin/env python3
"""Registre de neuf identités communales normandes actuelles, validées pour 2026 seulement.

À partir du RDF Pactols épinglé et de la recette non publiante #155,
vérifie les notes historiques et les anciens ARK concurrents. Aucun
reclassement d'une opération ancienne ni inférence d'un contour historique.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from auditer_normandie_lot01_identites_2026 import CASES, produire, RDF_SHA

SCHEMA = "adlfi.lieux.pactols.normandie.lot01.2026.public.v1"
DATE_VALIDATION = "2026-11-20"


def construire(rapport: dict) -> dict:
    if (rapport.get("schema") != "adlfi.lieux.normandie.communes-nouvelles.lot01.2026.audit.v1"
            or rapport.get("statut") != "RECETTE_NON_PUBLIANTE"
            or rapport.get("bilan", {}).get("dossiers") != 10
            or rapport.get("bilan", {}).get("candidats_Pactols") != 19
            or rapport.get("sources", {}).get("rdf_Pactols_sha256") != RDF_SHA):
        raise ValueError("Rapport d'instruction non conforme ou de provenance différente")
    dossiers = {d["code_COG_2026"]: d for d in rapport["dossiers"]}
    if set(dossiers) != set(CASES):
        raise ValueError("Périmètre des dix dossiers modifié")
    # La seule exception reste Port-Bail-sur-Mer (50412).
    if dossiers["50412"]["statut"] != "INDECIDABLE_ARK_COMMUNE_ACTUELLE":
        raise ValueError("Port-Bail-sur-Mer ne doit pas être promu")
    alignements = []
    for code, spec in sorted(CASES.items()):
        if code == "50412":
            continue
        dossier = dossiers[code]
        candidates = dossier["candidats_Pactols"]
        if (dossier["nom_COG_2026"] != spec["nom"]
                or dossier["date_creation_INSEE"] != spec["date"]
                or dossier["statut"] != "CANDIDAT_EDITION_2026_SANS_PUBLICATION"
                or dossier["decision_editoriale"] != "NON_PRISE"
                or dossier["nouveaux_alignements_publies"] != 0):
            raise ValueError("Dossier 2026 insuffisamment qualifié : " + code)
        current = [c for c in candidates if c["classification"] ==
                   "CANDIDAT_COMMUNE_NOUVELLE_2026_A_ARBITRER"]
        old = [c for c in candidates if c["ark"] == spec["ancien"]]
        if len(current) != 1 or len(old) != 1 or current[0]["ark"] != spec["actuel"]:
            raise ValueError("Identité ancienne/contemporaine ambiguë : " + code)
        c = current[0]
        if (c["prefLabels_fr"] != [spec["nom"]] or c["owl_deprecated"]
                or c["dct_isReplacedBy"]
                or c["exactMatch"].count("http://id.insee.fr/geo/commune/" + code) != 1):
            raise ValueError("Le concept contemporain n'est pas assez documenté : " + code)
        # Interdit : promotion d'ARK ancien et homonymie non résolue.
        if any(a["ark_pactols"] == old[0]["ark"] for a in alignements):
            raise ValueError("Ancien ARK déjà promu")
        if old[0]["ark"] == c["ark"]:
            raise ValueError("Même ARK pour identité ancienne et contemporaine")
        notes = [(n["type"], n["texte"].casefold()) for n in c["notes"]]
        if code == "27467":
            if (not any(t == "definition" and
                        "pont-audemer est une commune française" in v for t, v in notes)
                    or "http://www.wikidata.org/entity/Q47067820" not in c["exactMatch"]
                    or "http://www.wikidata.org/entity/Q367667" not in old[0]["exactMatch"]
                    or not any(n["type"] == "definition" and
                               "ancienne commune" in n["texte"].casefold()
                               for n in old[0]["notes"])):
                raise ValueError("Pont-Audemer : distinction actuelle/ancienne non prouvée")
            nature = "exactMatch_INSEE_plus_definitions_distinctes_et_Wikidata"
        elif code == "27022":
            if not any(t == "definition" and "commune nouvelle" in v and "2016" in v
                       for t, v in notes):
                raise ValueError("Le Val d'Hazey : création non attestée dans la définition")
            nature = "exactMatch_INSEE_plus_definition_et_COG_2016"
        else:
            if not any(t == "historyNote" and "commune nouvelle" in v
                       and spec["date"] in v and
                       "création de la commune nouvelle" in v for t, v in notes):
                raise ValueError("Création de commune nouvelle non attestée dans le RDF : " + code)
            nature = "exactMatch_INSEE_plus_historyNote_COG"
        alignements.append({
            "code_insee": code,
            "libelle_COG_2026": spec["nom"],
            "ark_pactols": c["ark"],
            "libelle_pactols": c["prefLabels_fr"][0],
            "uri_insee": "http://id.insee.fr/geo/commune/" + code,
            "predicat_source": "skos:exactMatch",
            "millesime_validation": 2026,
            "date_validation": DATE_VALIDATION,
            "date_creation_commune_nouvelle": spec["date"],
            "statut": "correspondance_NORMANDIE_validee_pour_2026",
            "type_validation": nature,
            "source_insee": dossier["source_INSEE"],
            "ancien_ark_non_promu": old[0]["ark"],
        })
    if len(alignements) != 9 or len({a["ark_pactols"] for a in alignements}) != 9:
        raise ValueError("Neuf correspondances univoques attendues")
    return {
        "schema": SCHEMA,
        "region": "normandie",
        "code_region_COG_2026": "28",
        "millesime_cog": "2026-01-01",
        "source_rdf": "Pactols_Lieux_th17_20260722.rdf",
        "source_rdf_sha256": RDF_SHA,
        "source_registre": "recette/lieux/NORMANDIE-LOT01-IDENTITES-2026.md",
        "nombre_communes": 9,
        "communes_lot01_a_instruire": 1,
        "couverture_region_entiere": False,
        "active_dans_interface": False,
        "nouvelles_geometries": 0,
        "liens_historiques_inferes": 0,
        "alignements_Pactols_COG_valides_2026": alignements,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rdf", type=Path, required=True)
    parser.add_argument("--sortie", type=Path, required=True)
    parser.add_argument("--comparer", type=Path)
    args = parser.parse_args()
    doc = construire(produire(args.rdf))
    if args.comparer is not None:
        existing = json.loads(args.comparer.read_text(encoding="utf-8"))
        if existing != doc:
            raise ValueError("Registre publié différent de l'audit reproductible")
    dest = args.sortie.resolve()
    if "docs" in dest.parts or dest.exists():
        raise ValueError("Sortie de recette neuve hors docs/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
                    encoding="utf-8")
    print("NORMANDIE_LOT01_VALIDATIONS_2026",
          json.dumps({"nombre_communes": doc["nombre_communes"],
                      "communes_lot01_a_instruire": doc["communes_lot01_a_instruire"],
                      "nouvelles_geometries": doc["nouvelles_geometries"],
                      "active_dans_interface": doc["active_dans_interface"]},
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
