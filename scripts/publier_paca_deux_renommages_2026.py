#!/usr/bin/env python3
"""Ajouter deux exactMatch PACA 2026 documentés par renommage COG et décret.

Rousset-Serre-Ponçon et Esparron-de-Pallières : les concepts Pactols ont un
exactMatch explicite au code INSEE en vigueur. Aucun alignement n'est inféré
pour Céreste-en-Luberon dont le concept cite une URI UUID à résoudre.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from auditer_paca_trois_renommages_rdf_2026 import (
    RDF_SHA, SCHEMA as AUDIT_SCHEMA, SOURCES, verifier_cog
)

SCHEMA="adlfi.lieux.pactols.paca.renommages.2026.public.v1"
SOURCE_AUDIT="recette/lieux/PACA-TROIS-RENOMMAGES-RDF-2026.json"
SOURCES_PACA={
    "05127":("26678/pcrtla4EHGDgDd","Rousset (Hautes-Alpes)"),
    "83052":("26678/pcrt7B7bs9P5g2","Esparron (Var)"),
}
EXCEPTION_UUID="04045"

def publier(audit:dict, pilote:dict, complet:dict, cog:dict)->dict:
    events={x["code_COG"]:x for x in verifier_cog(cog)}
    if (audit.get("schema")!=AUDIT_SCHEMA or
        audit.get("sources",{}).get("pactols",{}).get("sha256")!=RDF_SHA or
        audit.get("bilan",{}).get("renommages_officiels_controles")!=3 or
        audit.get("bilan",{}).get("ARK_directs_vers_codes_2026")!=2 or
        audit.get("bilan",{}).get("nouveaux_ARK_valides")!=0 or
        audit.get("bilan",{}).get("index_public_modifie") is not False):
        raise ValueError("Preuve de recette des renommages altérée")
    dossier={x["code_COG"]:x for x in audit["dossiers"]}
    if set(dossier)!=set(SOURCES):
        raise ValueError("Les trois dossiers du RDF sont obligatoires")
    pilot=pilote.get("autorites",[])
    pilot_codes={x["correspondances"][0]["code_insee"] for x in pilot}
    pilot_arks={x["ark_pactols"] for x in pilot}
    if (len(pilot)!=103 or len(pilot_codes)!=103 or len(pilot_arks)!=103 or
        pilote.get("totaux",{}).get("autorites_pactols")!=103):
        raise ValueError("Le pilote PACA de 103 correspondances a changé")
    complement=complet.get("alignements_Pactols_COG_valides_2026",[])
    codes832={x["code_insee"] for x in complement}
    arks832={x["ark_pactols"] for x in complement}
    if (complet.get("schema")!="adlfi.lieux.pactols.paca.complement.2026.public.v1"
        or len(complement)!=832 or len(codes832)!=832 or len(arks832)!=832
        or complet.get("nombre_total_alignements_2026")!=935
        or complet.get("communes_a_instruire")!=11
        or pilot_codes & codes832 or pilot_arks & arks832):
        raise ValueError("832 compléments PACA ou 103 validations du pilote modifiés")
    if (set(SOURCES_PACA)|{EXCEPTION_UUID}) & (pilot_codes|codes832):
        raise ValueError("Un renommage se trouve déjà dans l'index public")
    uuid=dossier[EXCEPTION_UUID]
    if (uuid["ARK_directement_assertes_vers_code_2026"]!=[] or
        uuid["nombre_candidats"]!=1):
        raise ValueError("Céreste ne doit pas être promue sans résolution UUID")
    c=uuid["concepts_pactols_a_examiner"][0]
    if (c["ark"]!="26678/pcrtHxveTzUMik" or
        len(c["exactMatch_INSEE"])!=1 or
        not c["exactMatch_INSEE"][0]["est_UUID"] or
        c["exactMatch_INSEE"][0]["identifiant"]!="3cb419d3-63ba-4e7c-be42-2640cf521de8"):
        raise ValueError("La réserve UUID Céreste a été modifiée")
    entries=[]
    for code,(ark,old_label) in SOURCES_PACA.items():
        row=dossier[code]
        event=events[code]
        if (row["nature_COG"]!="MOD10_RENOMMAGE_CODE_CONSERVE" or
            row["date_effet"]!=event["date_effet"] or
            row["nom_ancien"]!=event["nom_ancien"] or
            row["nom_2026"]!=event["nom_2026"] or
            row["decret"]!=event["decret"] or
            row["decret_url"]!=event["decret_url"] or
            row["ARK_directement_assertes_vers_code_2026"]!=[ark] or
            row["qualification"]!="COG_RENOMMAGE_CONFIRME_PACTOLS_A_INSTRUIRE"):
            raise ValueError("L'événement ou la preuve Pactols a divergé : "+code)
        hits=[x for x in row["concepts_pactols_a_examiner"] if x["ark"]==ark]
        if len(hits)!=1:
            raise ValueError("Concept attendu absent ou dupliqué : "+code)
        p=hits[0]
        uri="http://id.insee.fr/geo/commune/"+code
        french=[x["texte"] for x in p["prefLabel"] if x["lang"]=="fr"]
        if (french!=[old_label] or p["owl_deprecated"] or p["dct_isReplacedBy"]
            or uri not in p["exactMatch"] or len(p["exactMatch_INSEE"])!=1
            or p["exactMatch_INSEE"][0]["est_UUID"]
            or p["exactMatch_INSEE"][0]["identifiant"]!=code
            or p["exactMatch_INSEE"][0]["famille"]!="commune"
            or "EXACTMATCH_INSEE_CODE_COURANT" not in p["motifs_de_recuperation"]):
            raise ValueError("Preuve RDF insuffisante pour "+code)
        if code=="83052" and "Esparron-de-Pallières" not in [
            x["texte"] for x in p["altLabel"] if x["lang"]=="fr"]:
            raise ValueError("Variante Pactols 2026 Esparron absente")
        entries.append({
            "code_insee":code,"libelle_COG_2026":event["nom_2026"],
            "libelle_ancien_COG":event["nom_ancien"],
            "date_effet_renommage":event["date_effet"],
            "decret":event["decret"],"decret_url":event["decret_url"],
            "ark_pactols":ark,"libelle_pactols":old_label,
            "uri_insee":uri,"predicat_source":"skos:exactMatch",
            "source_rdf_sha256":RDF_SHA,"millesime_validation":2026,
            "date_validation":"2026-11-18",
            "statut":"correspondance_PACA_renommage_validee_par_preuves_2026",
            "type_validation":"exactMatch_code_2026_plus_MOD10_plus_decret",
            "portee_chronologique":"2026_SEULEMENT",
        })
    return {
        "schema":SCHEMA,"region":"paca","millesime_cog":"2026-01-01",
        "source_rdf_sha256":RDF_SHA,"source_audit":SOURCE_AUDIT,
        "liens_renommages_ajoutes":2,"pilotage_valide_conserve":103,
        "complements_existants_conserves":832,
        "total_alignements_PACA_2026":937,"communes_a_instruire":9,
        "reserve_Cereste_UUID":"04045","autres_renommages_historiques_inferes":0,
        "geometries_modifiees":0,
        "alignements_Pactols_COG_valides_2026":sorted(entries,key=lambda x:x["code_insee"]),
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("audit","pilote","complement","cog","sortie"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    if a.sortie.exists() or a.sortie.resolve() in [
        x.resolve() for x in (a.audit,a.pilote,a.complement,a.cog)]:
        raise ValueError("Sortie neuve et distincte des sources")
    result=publier(
        json.loads(a.audit.read_text(encoding="utf-8")),
        json.loads(a.pilote.read_text(encoding="utf-8")),
        json.loads(a.complement.read_text(encoding="utf-8")),
        json.loads(a.cog.read_text(encoding="utf-8"))
    )
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                  separators=(",",":"))+"\n",encoding="utf-8")
    print("PACA_DEUX_RENOMMAGES_PREPARES",json.dumps({
        "nouvelles_identites_2026":2,"total_avec_pilote":937,"exceptions":9,
        "cereste_UUID_non_publie":True,"aucune_geometrie_modifiee":True,
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
