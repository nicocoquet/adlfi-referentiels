#!/usr/bin/env python3
"""Valider sept identités communales 2026 du lot 02 ; réserver trois cas incohérents.

Le RDF Pactols est épinglé SHA256. L'histoire de Saint-Pierre-en-Auge est relue
INTÉGRALEMENT dans le RDF source (non à partir de la note tronquée à 1600
caractères de l'audit #158). Le rapport ne réécrit aucune identité historique.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from auditer_pactols_polynesie_2026 import RDF, SKOS, ARK, RDF_SHA, RDF_COMMIT
from auditer_normandie_lot02_rdf_2026 import CASES, produire

SCHEMA="adlfi.lieux.pactols.normandie.lot02.2026.public.v1"
VALIDATIONS={
    "14035":"2016-01-01",  # Balleroy-sur-Drôme
    "14654":"2017-01-01",  # Saint-Pierre-en-Auge : note XML complète
    "27471":"2018-01-01",  # Porte-de-Seine
    "50239":"2016-01-01",  # Thèreval
    "61211":"2016-01-01",  # Juvigny Val d'Andaine
    "61341":"2016-01-01",  # Écouves
    "76258":"2017-01-01",  # Terres-de-Caux
}
EXCEPTIONS={
    "14342":{
        "nom":"Isigny-sur-Mer",
        "statut":"DEFINITION_RDF_ET_LIENS_EXTERIEURS_AMBIGUS",
        "justification":"Le candidat 2026 porte une histoire de création 2017, mais aussi une définition d'ancienne commune et des liens de l'ancienne identité.",
        "insee":"https://www.insee.fr/fr/statistiques/2011101?geo=COM-14342",
    },
    "27112":{
        "nom":"Breteuil",
        "statut":"EXACTMATCH_WIKIDATA_COMMUN_ANCIEN_ACTUEL",
        "justification":"Les deux ARK concurrents partagent Q467162 comme skos:exactMatch malgré des libellés et définitions distincts.",
        "insee":"https://www.insee.fr/fr/statistiques/2011101?geo=COM-27112",
    },
    "50546":{
        "nom":"Bourgvallées",
        "statut":"DEUX_CREATIONS_COG_2016_ET_2019",
        "justification":"Le RDF du candidat documente 2016, mais le COG documente une nouvelle création au 1er janvier 2019 incluant Le Mesnil-Herman et Soulles.",
        "insee":"https://www.insee.fr/fr/statistiques/2011101?geo=COM-50546",
    },
}
SOURCE_INSEE="https://www.insee.fr/fr/statistiques/2011101?geo=COM-"


def preuves_creation_rdf(rdf:Path)->dict:
    """Lire sans troncature la note de création des sept concepts sélectionnés."""
    wanted={CASES[code]["actuel"]: (CASES[code]["nom"],date,code)
            for code,date in VALIDATIONS.items()}
    found={}
    parser=ET.iterparse(rdf,events=("start","end"))
    _,root=next(parser)
    if root.tag!=RDF+"RDF":
        raise ValueError("RDF/XML attendu")
    for event,el in parser:
        if event!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):
            continue
        match=ARK.fullmatch(el.get(RDF+"about",""))
        ark=match.group(1) if match else None
        if ark in wanted:
            if ark in found:
                raise ValueError("Concept contemporain dupliqué dans le RDF : "+ark)
            name,date,code=wanted[ark]
            phrase=re.compile(
                r"Création de la commune nouvelle (?:de |d['’])"+
                re.escape(name)+
                r"\b[\s\S]{0,4000}?\[date d'effet : "+
                re.escape(date)+r"\]",re.IGNORECASE)
            notes=[(n.text or "").strip() for n in el.findall(SKOS+"historyNote")
                   if (n.text or "").strip()]
            matches=[note for note in notes if phrase.search(note)]
            if len(matches)!=1:
                raise ValueError("Note complète de création INSEE introuvable ou ambiguë : "+code)
            note=matches[0]
            found[ark]={
                "ark":ark,
                "code_COG_2026":code,
                "source":"skos:historyNote",
                "date_creation_RDF":date,
                "sha256_note_complete":hashlib.sha256(note.encode("utf-8")).hexdigest(),
                "longueur_note_complete":len(note),
            }
        el.clear()
        root.clear()
    if set(found)!=set(wanted):
        raise ValueError("Concepts de communes nouvelles absents : "+str(sorted(set(wanted)-set(found))))
    return found


def qualifier_exceptions(dossiers:dict)->list:
    """Le changement des preuves litigieuses doit interrompre l'arbitrage figé."""
    results=[]
    for code,spec in sorted(EXCEPTIONS.items()):
        item=dossiers[code]
        current=next(c for c in item["candidats_Pactols"] if c["ark"]==CASES[code]["actuel"])
        old=next(c for c in item["candidats_Pactols"] if c["ark"]==CASES[code]["ancien"])
        if code=="14342":
            definitions=[n["texte"].lower() for n in current["notes"]
                         if n["type"]=="definition"]
            external=" ".join(current["exactMatch"]).lower()
            if (not any("ancienne commune" in x for x in definitions) or
                    "commune_déléguée" not in external):
                raise ValueError("Isigny-sur-Mer : les contradictions RDF ont changé, réexaminer")
        elif code=="27112":
            # Les deux écritures Wikidata (entity/Q... et wiki/Q...) pointent
            # vers le même identifiant ; comparer les QID, non les URL brutes.
            def qids(links):
                found=set()
                for uri in links:
                    m=re.search(r"https?://(?:www\.)?wikidata\.org/(?:entity|wiki)/(Q[0-9]+)$",uri)
                    if m:found.add(m.group(1))
                return found
            shared=qids(current["exactMatch"]) & qids(old["exactMatch"])
            if "Q467162" not in shared:
                raise ValueError("Breteuil : intersection des Wikidata RDF modifiée")
        elif code=="50546":
            notes=" ".join(n["texte"] for n in current["notes"] if n["type"]=="historyNote")
            if "2016-01-01" not in notes or "2019-01-01" in notes:
                raise ValueError("Bourgvallées : histoire RDF modifiée, réexaminer le COG 2019")
        results.append({
            "code_insee":code,"libelle_COG_2026":spec["nom"],
            "statut":spec["statut"],"justification":spec["justification"],
            "source_insee":spec["insee"],
            "ark_candidat_non_valide":current["ark"],
            "ark_ancien_distinct":old["ark"],
            "decision_editoriale":"SUSPENDUE",
            "alignement_publie":False,
        })
    return results


def construire(audit:dict,notes_complete:dict,lot01:dict)->dict:
    if (audit.get("schema")!="adlfi.lieux.normandie.lot02.candidats.2026.audit.v1"
            or audit.get("statut")!="RECETTE_NON_VALIDANTE"
            or audit.get("source_rdf",{}).get("sha256")!=RDF_SHA
            or audit.get("bilan",{}).get("communes_COG_a_instruire")!=10
            or audit.get("bilan",{}).get("ARK_candidats")!=20
            or audit.get("bilan",{}).get("nouvelles_validations")!=0):
        raise ValueError("Préflight lot 02 insuffisant ou source RDF modifiée")
    if (lot01.get("schema")!="adlfi.lieux.pactols.normandie.lot01.2026.public.v1"
            or lot01.get("source_rdf_sha256")!=RDF_SHA
            or lot01.get("nombre_communes")!=9):
        raise ValueError("Registre du premier lot incompatible")
    existing={x["code_insee"] for x in lot01["alignements_Pactols_COG_valides_2026"]}
    if len(existing)!=9 or existing & set(CASES):
        raise ValueError("Doublon avec une commune du premier lot")
    dossiers={d["code_COG_2026"]:d for d in audit["dossiers"]}
    if set(dossiers)!=set(CASES) or set(VALIDATIONS) | set(EXCEPTIONS)!=set(CASES):
        raise ValueError("Périmètre non exhaustif du lot 02")
    if set(notes_complete)!={CASES[c]["actuel"] for c in VALIDATIONS}:
        raise ValueError("Notes du RDF non exhaustives")
    validations=[]
    for code,date in sorted(VALIDATIONS.items()):
        spec=CASES[code]
        dossier=dossiers[code]
        if (dossier["nom_COG_2026"]!=spec["nom"] or
                dossier["decision_editoriale"]!="NON_PRISE" or
                dossier["nouvelles_geometries"]!=0 or
                dossier["liens_historiques_inferes"]!=0):
            raise ValueError("Dossier Pactols/COG modifié : "+code)
        curr=[c for c in dossier["candidats_Pactols"] if c["ark"]==spec["actuel"]]
        old=[c for c in dossier["candidats_Pactols"] if c["ark"]==spec["ancien"]]
        if len(curr)!=1 or len(old)!=1 or spec["actuel"]==spec["ancien"]:
            raise ValueError("Identités anciennes non distinctes pour "+code)
        c=curr[0]
        if (c["role_preliminaire"]!="CANDIDAT_COMMUNE_ACTUELLE_A_INSTRUIRE"
                or c["prefLabels_fr"]!=[spec["label_actuel"]]
                or c["owl_deprecated"] or c["dct_isReplacedBy"]
                or c["exactMatch"].count("http://id.insee.fr/geo/commune/"+code)!=1):
            raise ValueError("Preuve Pactols actuelle insuffisante : "+code)
        old_case=old[0]
        if old_case["role_preliminaire"]!="IDENTITE_ANTERIEURE_OU_DELEGUEE_A_INSTRUIRE":
            raise ValueError("Identité ancienne non qualifiée : "+code)
        if not any(n["type"]=="historyNote" and
                   ("commune déléguée" in n["texte"].lower() or
                    "commune nouvelle" in n["texte"].lower())
                   for n in old_case["notes"]):
            raise ValueError("Histoire de l'ancien concept absente : "+code)
        proof=notes_complete[c["ark"]]
        if (proof["date_creation_RDF"]!=date or proof["code_COG_2026"]!=code or
                proof["source"]!="skos:historyNote" or
                len(proof["sha256_note_complete"])!=64):
            raise ValueError("Preuve intégrale de création RDF non conforme : "+code)
        validations.append({
            "code_insee":code,"libelle_COG_2026":spec["nom"],
            "libelle_pactols":spec["label_actuel"],
            "ark_pactols":c["ark"],
            "ancien_ark_non_promu":old_case["ark"],
            "uri_insee":"http://id.insee.fr/geo/commune/"+code,
            "predicat_source":"skos:exactMatch",
            "date_creation_commune_nouvelle":date,
            "source_insee":SOURCE_INSEE+code,
            "preuve_creation_RDF":proof,
            "millesime_validation":2026,"date_validation":"2026-11-20",
            "statut":"correspondance_NORMANDIE_validee_pour_2026",
        })
    exceptions=qualifier_exceptions(dossiers)
    if len(validations)!=7 or len(exceptions)!=3:
        raise ValueError("Attendu 7 validations et 3 suspensions")
    return {
        "schema":SCHEMA,"region":"normandie","code_region_COG_2026":"28",
        "millesime_cog":"2026-01-01","source_rdf":"Pactols_Lieux_th17_20260722.rdf",
        "source_rdf_commit":RDF_COMMIT,"source_rdf_sha256":RDF_SHA,
        "source_registre":"recette/lieux/NORMANDIE-LOT02-VALIDATIONS-PRUDENTES-2026.md",
        "nombre_communes":7,"communes_lot02_suspendues":3,
        "cumule_avec_lot01":16,"couverture_region_entiere":False,
        "active_dans_interface":False,
        "nouvelles_geometries":0,"liens_historiques_inferes":0,
        "alignements_Pactols_COG_valides_2026":validations,
        "exceptions_non_validees":exceptions,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rdf",required=True,type=Path)
    parser.add_argument("--lot01",required=True,type=Path)
    parser.add_argument("--sortie",required=True,type=Path)
    parser.add_argument("--comparer",type=Path)
    args=parser.parse_args()
    dest=args.sortie.resolve()
    if dest.exists() or "docs" in dest.parts:
        raise ValueError("La sortie de recette doit être neuve et hors docs/")
    report=construire(
        produire(args.rdf),
        preuves_creation_rdf(args.rdf),
        json.loads(args.lot01.read_text(encoding="utf8")))
    if args.comparer and json.loads(args.comparer.read_text(encoding="utf8"))!=report:
        raise ValueError("Le registre du lot 02 ne concorde pas avec la source RDF")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,
                               separators=(",",":"))+"\n",encoding="utf8")
    print("NORMANDIE_LOT02_VALIDATION",json.dumps({
        "validations":report["nombre_communes"],
        "exceptions":report["communes_lot02_suspendues"],
        "cumule":report["cumule_avec_lot01"],"geometries":report["nouvelles_geometries"],
        "activation":report["active_dans_interface"]
    },ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()
