#!/usr/bin/env python3
"""Qualification non validante des 60 collisions d'ARK Pactols des Pays de la Loire."""
from __future__ import annotations
import argparse
import collections
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from auditer_pactols_polynesie_2026 import (
    ARK, RDF, SKOS, DCT, label_compatible,
)

SCHEMA = "adlfi.lieux.pdl.ark-multiples.triage.2026.v1"

def completer_rdf(rdf: Path, attendus: set[str]) -> dict:
    preuves = {}
    parseur = ET.iterparse(rdf, events=("start", "end"))
    _, racine = next(parseur)
    if racine.tag != RDF+"RDF":
        raise ValueError("Fichier source non RDF/XML")
    for evenement, element in parseur:
        if evenement != "end" or element.tag not in (SKOS+"Concept", RDF+"Description"):
            continue
        match = ARK.fullmatch(element.get(RDF+"about", ""))
        if match and match.group(1) in attendus:
            ark = match.group(1)
            if ark in preuves:
                raise ValueError("Concept dupliqué dans le RDF : "+ark)
            def ressources(tag):
                return sorted({x.get(RDF+"resource") for x in element.findall(tag)
                               if x.get(RDF+"resource")})
            def textes(tag):
                return sorted({(x.text or "").strip() for x in element.findall(tag)
                               if (x.text or "").strip()})
            preuves[ark] = {
                "exactMatch_tous": ressources(SKOS+"exactMatch"),
                "closeMatch_tous": ressources(SKOS+"closeMatch"),
                "remplacements_explicites": ressources(DCT+"isReplacedBy"),
                "definitions": textes(SKOS+"definition"),
                "notes_histoire": textes(SKOS+"historyNote"),
                "notes_portee": textes(SKOS+"scopeNote"),
                "notes": textes(SKOS+"note"),
            }
        element.clear()
        racine.clear()
    absents = attendus-set(preuves)
    if absents:
        raise ValueError("ARK absents du RDF : "+repr(sorted(absents)))
    return preuves

def libelle_contemporain_compatible(nom_cog: str, libelle: str) -> bool:
    """Un qualificatif administratif historique ne vaut pas identité COM 2026."""
    if not label_compatible(nom_cog, libelle):
        return False
    historique = ("ancienne commune", "commune déléguée",
                  "commune deleguee", "commune associée",
                  "commune associee", "ancien territoire")
    return not any(terme in libelle.casefold() for terme in historique)

def qualifier(audit: dict, rdf: Path) -> dict:
    lignes = audit["communes"]
    if len(lignes) != 60 or len({x["code_COG_2026"] for x in lignes}) != 60:
        raise ValueError("L'audit source doit contenir exactement 60 codes distincts")
    attendus = {c["ark"] for x in lignes for c in x["candidats_RDF"]}
    complements = completer_rdf(rdf, attendus)
    resultats = []
    for entree in lignes:
        code = entree["code_COG_2026"]
        nom = entree["libelle_COG_2026"]
        episodes = sorted({m["date_effet"] for m in entree["mouvements_COG_documentes"]
                           if m["mod"] == "32" and m["code_apres"] == code})
        candidats = []
        for candidat in entree["candidats_RDF"]:
            ark = candidat["ark"]
            autres = [u for u in complements[ark]["exactMatch_tous"]
                      if "id.insee.fr/geo/" in u
                      and u not in {v["uri"] for v in candidat["insee_exactMatch"]}]
            candidat_compatible = (
                any(libelle_contemporain_compatible(nom, lab) for lab in candidat["prefLabels_fr"])
                and not candidat["deprecie"] and not candidat["remplace"]
            )
            candidats.append({
                "ark": ark, "prefLabels_fr": candidat["prefLabels_fr"],
                "altLabels_fr": candidat["altLabels_fr"],
                "deprecie": candidat["deprecie"], "remplace": candidat["remplace"],
                "compatibilite_libelle_sans_validation": candidat_compatible,
            "intitule_statut_historique": any(
                "ancienne commune" in l.casefold() or "commune déléguée" in l.casefold()
                for l in candidat["prefLabels_fr"]),
                "insee_exactMatch_codes": candidat["insee_exactMatch"],
                "insee_exactMatch_non_codes": autres,
                "autres_preuves_RDF": complements[ark],
            })
        compatibles = [c for c in candidats if c["compatibilite_libelle_sans_validation"]]
        if len(episodes) > 1:
            groupe = "CREATIONS_SUCCESSIVES"
        elif any(c["intitule_statut_historique"] for c in candidats):
            groupe = "STATUT_HISTORIQUE_EXPLICITE"
        elif len(compatibles) > 1:
            groupe = "PLUSIEURS_LIBELLES_COMPATIBLES"
        elif not compatibles:
            groupe = "AUCUN_LIBELLE_COMPATIBLE"
        else:
            groupe = "UN_LIBELLE_COMPATIBLE"
        resultats.append({
            "code_COG_2026": code, "nom_COG_2026": nom,
            "departement": entree["departement"],
            "dates_MOD32": episodes, "groupe_instruction": groupe,
            "nombre_ARK": len(candidats),
            "nombre_libelles_compatibles": len(compatibles),
            "candidats": candidats,
            "mouvements_COG_documentes": entree["mouvements_COG_documentes"],
            "ark_retenu": None, "decision_editoriale": "NON_PRISE",
            "publication": "NON_PUBLIE",
        })
    priorites = {"CREATIONS_SUCCESSIVES": 0,
                 "STATUT_HISTORIQUE_EXPLICITE": 1,
                 "PLUSIEURS_LIBELLES_COMPATIBLES": 2,
                 "AUCUN_LIBELLE_COMPATIBLE": 3,
                 "UN_LIBELLE_COMPATIBLE": 4}
    resultats.sort(key=lambda x: (priorites[x["groupe_instruction"]],
                                   x["code_COG_2026"]))
    compte = collections.Counter(x["groupe_instruction"] for x in resultats)
    return {"schema": SCHEMA, "statut": "RECETTE_NON_VALIDANTE",
            "sources": audit["sources"],
            "bilan": {"codes": 60, "ark_distincts": len(attendus),
                      "groupes": dict(sorted(compte.items())),
                      "validations": 0, "geometries": 0,
                      "liens_historiques_inferes": 0},
            "communes": resultats,
            "limites": [
                "La compatibilité lexicale ne valide pas une identité administrative.",
                "Un même code COG peut être réemployé pour plusieurs épisodes de commune.",
                "Les URI INSEE UUID doivent être résolues auprès de l'INSEE avant validation.",
                "Les liens RDF concurrents ne prouvent pas l'équivalence entre ARK.",
            ]}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit", required=True, type=Path)
    p.add_argument("--rdf", required=True, type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    a = p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette nouvelle et hors docs uniquement")
    audit = json.loads(a.audit.read_text(encoding="utf-8"))
    resultat = qualifier(audit, a.rdf)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(json.dumps(resultat, sort_keys=True, indent=2,
                                    ensure_ascii=False)+"\n", encoding="utf-8")
    print("PDL_TRIAGE_BILAN", json.dumps(resultat["bilan"], ensure_ascii=False))
    for ligne in resultat["communes"][:12]:
        print("PDL_TRIAGE_PREMIER_LOT", json.dumps({
            "code": ligne["code_COG_2026"], "nom": ligne["nom_COG_2026"],
            "groupe": ligne["groupe_instruction"], "dates": ligne["dates_MOD32"],
            "candidats": [{"ark": c["ark"], "pref": c["prefLabels_fr"],
                           "alt": c["altLabels_fr"],
                           "deprecie": c["deprecie"], "remplace": c["remplace"],
                           "insee": c["insee_exactMatch_codes"],
                           "uri_non_codes": c["insee_exactMatch_non_codes"],
                           "definitions": c["autres_preuves_RDF"]["definitions"]}
                          for c in ligne["candidats"]]},
            ensure_ascii=False, sort_keys=True))
if __name__ == "__main__":
    main()
