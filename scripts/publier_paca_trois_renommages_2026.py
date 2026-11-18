#!/usr/bin/env python3
"""Troisième alignement Pactols PACA : Céreste, UUID INSEE officiellement résolu.

Le générateur v2 conserve bit à bit les deux entrées approuvées par le
générateur v1 ; seule l'entrée du code 04045 s'ajoute, avec provenance RDF
Pactols + triplet INSEE d'un sujet URI UUID + MOD10 COG + décret.
Aucun alignement n'est ajouté aux périodes antérieures à 2026.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from publier_paca_deux_renommages_2026 import publier as publier_deux
from auditer_paca_trois_renommages_rdf_2026 import SOURCES, RDF_SHA

SCHEMA="adlfi.lieux.pactols.paca.renommages.2026.public.v2"
PREUVE_FICHIER="recette/lieux/PACA-CERESTE-UUID-INSEE-AUDIT-2026.json"
UUID="3cb419d3-63ba-4e7c-be42-2640cf521de8"
URI="http://id.insee.fr/geo/commune/"+UUID
CODE_PRED="http://rdf.insee.fr/def/geo#codeINSEE"
ARK="26678/pcrtHxveTzUMik"
CODE="04045"

def verifier_preuve_insee(proof:dict)->None:
    source=proof.get("sources",{})
    if (proof.get("schema")!="adlfi.lieux.paca.cereste.uuid-insee.audit.v1"
        or proof.get("statut")!="AUDIT_NON_PUBLIANT"
        or source.get("uri_canonique")!=URI
        or source.get("rdf_pactols_sha256")!=RDF_SHA
        or source.get("pactols")!=ARK
        or proof.get("code_COG_2026_officiel")!=CODE
        or proof.get("libelle_COG_2026_officiel")!="Céreste-en-Luberon"
        or proof.get("preuve_par_triplet_insee") is not True
        or proof.get("decision_documentaire")!="URI_UUID_CONFIRME_COG_04045_PAR_TRIPLET_INSEE"
        or proof.get("nouvel_ARK_publie") is not False
        or proof.get("nouvel_etat_historique") is not False):
        raise ValueError("Rapport officiel de résolution de l'UUID Insee invalide")
    rdfxml=any(
        x.get("status")==200 and
        x.get("preuve_directe_code_04045") is True and
        x.get("codeINSEE_du_sujet_UUID")==[CODE] and
        "rdf+xml" in (x.get("content_type") or "").lower()
        for x in proof.get("appels_dereferencement",[])
    )
    sparql=any(
        x.get("status")==200 and
        x.get("preuve",{}).get("preuve_directe_code_04045") is True and
        any(t.get("s")==URI and t.get("p")==CODE_PRED and
            t.get("o")==CODE and t.get("type")=="literal"
            for t in x.get("preuve",{}).get("triples",[]))
        for x in proof.get("appels_sparql",[])
    )
    if not rdfxml or not sparql:
        raise ValueError("Absence de double preuve Insee RDF et SPARQL pour l'UUID 04045")

def publier(audit:dict,preuve_uuid:dict,pilote:dict,complet:dict,cog:dict)->dict:
    base=publier_deux(audit,pilote,complet,cog)
    if (base.get("schema")!="adlfi.lieux.pactols.paca.renommages.2026.public.v1"
        or base.get("liens_renommages_ajoutes")!=2
        or base.get("total_alignements_PACA_2026")!=937
        or base.get("communes_a_instruire")!=9
        or base.get("reserve_Cereste_UUID")!=CODE
        or base.get("geometries_modifiees")!=0
        or base.get("autres_renommages_historiques_inferes")!=0):
        raise ValueError("Deux correspondances antérieures PACA altérées")
    verifier_preuve_insee(preuve_uuid)
    rows={x["code_COG"]:x for x in audit["dossiers"]}
    record=rows.get(CODE,{})
    if (record.get("nom_ancien")!="Céreste"
        or record.get("nom_2026")!="Céreste-en-Luberon"
        or record.get("date_effet")!="2024-01-01"
        or record.get("nature_COG")!="MOD10_RENOMMAGE_CODE_CONSERVE"
        or record.get("decret")!="2023-959"
        or record.get("decret_url")!=SOURCES[CODE]["url_decret"]
        or record.get("ARK_directement_assertes_vers_code_2026")!=[]
        or record.get("nombre_candidats")!=1):
        raise ValueError("Dossier Pactols Céreste ou événement COG altéré")
    concept=record["concepts_pactols_a_examiner"][0]
    french=[x["texte"] for x in concept["prefLabel"] if x["lang"]=="fr"]
    old=[x["texte"] for x in concept["altLabel"] if x["lang"]=="fr"]
    uris=[x for x in concept["exactMatch"] if
        x.lower().startswith(("http://id.insee.fr/geo/","https://id.insee.fr/geo/"))]
    if (concept["ark"]!=ARK or french!=["Céreste-en-Luberon"] or old!=["Céreste"]
        or concept["owl_deprecated"] or concept["dct_isReplacedBy"]
        or uris!=[URI] or len(concept["exactMatch_INSEE"])!=1
        or concept["exactMatch_INSEE"][0]!={
            "est_UUID":True,"famille":"commune","identifiant":UUID,"uri":URI}
        or "PREF_LIBELLE_NOUVEAU_EXACT" not in concept["motifs_de_recuperation"]):
        raise ValueError("Le concept Pactols Céreste n'atteste pas l'URI UUID attendue")
    old_codes={x["correspondances"][0]["code_insee"] for x in pilote["autorites"]}
    old_arks={x["ark_pactols"] for x in pilote["autorites"]}
    old_codes.update(x["code_insee"] for x in complet["alignements_Pactols_COG_valides_2026"])
    old_arks.update(x["ark_pactols"] for x in complet["alignements_Pactols_COG_valides_2026"])
    for x in base["alignements_Pactols_COG_valides_2026"]:
        old_codes.add(x["code_insee"]);old_arks.add(x["ark_pactols"])
    if len(old_codes)!=937 or len(old_arks)!=937 or CODE in old_codes or ARK in old_arks:
        raise ValueError("Collision ou base PACA 937 altérée")
    entry={
        "code_insee":CODE,"libelle_COG_2026":"Céreste-en-Luberon",
        "libelle_ancien_COG":"Céreste","date_effet_renommage":"2024-01-01",
        "decret":"2023-959","decret_url":SOURCES[CODE]["url_decret"],
        "ark_pactols":ARK,"libelle_pactols":"Céreste-en-Luberon",
        "uri_insee":URI,"predicat_source":"skos:exactMatch",
        "code_insee_resolu":"04045","predicat_resolution":CODE_PRED,
        "source_preuve_uuid":PREUVE_FICHIER,
        "source_rdf_sha256":RDF_SHA,"millesime_validation":2026,
        "date_validation":"2026-11-18",
        "statut":"correspondance_PACA_renommage_validee_par_preuves_2026",
        "type_validation":"exactMatch_UUID_resolu_INSEE_plus_MOD10_plus_decret",
        "portee_chronologique":"2026_SEULEMENT"
    }
    return {
        **{k:v for k,v in base.items() if k not in (
            "schema","liens_renommages_ajoutes","total_alignements_PACA_2026",
            "communes_a_instruire","reserve_Cereste_UUID",
            "alignements_Pactols_COG_valides_2026")},
        "schema":SCHEMA,"liens_renommages_ajoutes":3,
        "total_alignements_PACA_2026":938,"communes_a_instruire":8,
        "Cereste_UUID_resolu_code_COG":CODE,
        "preuve_Cereste_UUID":PREUVE_FICHIER,
        "alignements_Pactols_COG_valides_2026":sorted(
            [*base["alignements_Pactols_COG_valides_2026"],entry],
            key=lambda x:x["code_insee"]),
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("audit","preuve-uuid","pilote","complement","cog","sortie"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    inputs=[a.audit,a.preuve_uuid,a.pilote,a.complement,a.cog]
    if a.sortie.exists() or a.sortie.resolve() in [x.resolve() for x in inputs]:
        raise ValueError("Sortie neuve et distincte des sources")
    source=[json.loads(x.read_text(encoding="utf-8")) for x in inputs]
    result=publier(*source)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,
                                  separators=(",",":"))+"\n",encoding="utf-8")
    print("PACA_TROIS_RENOMMAGES_PREPARES",json.dumps({
      "renommages":3,"identites_2026":938,"exceptions":8,
      "preuve_uuid_insee":True,"geometries_modifiees":0,
    },sort_keys=True))

if __name__=="__main__":
    main()
