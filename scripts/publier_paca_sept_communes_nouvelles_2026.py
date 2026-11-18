#!/usr/bin/env python3
"""PACA 2026 : publier les sept communes nouvelles prouvées, sans leurs anciens ARK.

Sept codes réutilisés par des fusions MOD32, deux concepts Pactols chacun.
Seul le concept dont le prefLabel est le nom de la *commune nouvelle*, dont
l'exactMatch INSEE est exclusif et dont la note retrace la création datée,
est retenu pour le COG 2026. La huitième commune, Abriès-Ristolas, attend
la preuve de correspondance du concept contemporain.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from auditer_paca_huit_communes_nouvelles_2026 import (
    SCHEMA as AUDIT_SCHEMA,CASES,reconstruire_cog
)
from auditer_pactols_polynesie_2026 import RDF_SHA

SCHEMA="adlfi.lieux.pactols.paca.communes_nouvelles.2026.public.v1"
SOURCE_AUDIT="recette/lieux/PACA-HUIT-COMMUNES-NOUVELLES-RDF-2026.json"
CODES={
    "04033":("26678/pcrtDcVUj2Mdw9","26678/pcrtC1Vi7jqzBS"),
    "04120":("26678/pcrtjDzQ2Y9N5o","26678/pcrtjMIYKdPaHG"),
    "05024":("26678/pcrtAUevxwngAh","26678/pcrteug78RKN9a"),
    "05039":("26678/pcrtFGmyycRjcC","26678/pcrtp9Ljm1lvVd"),
    "05053":("26678/pcrtKc33Ttmi9L","26678/pcrtYB42tOKsY7"),
    "05101":("26678/pcrt2BsRDBxggr","26678/pcrt6KSOx6bX7u"),
    "05118":("26678/pcrtjKbaVOnEjn","26678/pcrth0vgSHba4G"),
}
ABRIES_CODE="05001"
ABRIES_CANDIDAT="26678/pcrtm96gvvfnwmggc9z0wrxn"
ABRIES_ARK_ANCIEN="26678/pcrtGQ7nGPZN7K"

def construire(audit:dict,pilote:dict,complement:dict,renommages:dict,cog:dict)->dict:
    summary=audit.get("bilan",{})
    sources=audit.get("sources",{}).get("pactols",{})
    if (audit.get("schema")!=AUDIT_SCHEMA or
        audit.get("statut")!="RECETTE_NON_PUBLIANTE" or
        sources.get("sha256")!=RDF_SHA or
        summary.get("communes_nouvelles_a_instruire")!=8 or
        summary.get("ARK_vers_codes_contemporains")!=15 or
        summary.get("nouvelles_validations_2026")!=0 or
        summary.get("etats_historiques_inferes")!=0 or
        summary.get("geometries_modifiees")!=0):
        raise ValueError("Preuve des huit fusions Pactols non conforme")
    if set(CODES)|{ABRIES_CODE}!=set(CASES):
        raise ValueError("Périmètre des huit fusions modifié")
    dossier={x["code_COG_2026"]:x for x in audit["dossiers"]}
    if set(dossier)!=set(CASES):raise ValueError("Huit dossiers COG requis")
    histories=reconstruire_cog(cog)
    for code,doc in dossier.items():
        if doc["historique_COG"]!=histories[code] or doc["publication"]!="AUCUNE":
            raise ValueError("Incohérence de succession COG : "+code)
    current={}
    for a in pilote["autorites"]:
        corr=a["correspondances"]
        if len(corr)!=1:raise ValueError("Pilote PACA ambigu")
        code=corr[0]["code_insee"]
        if code in current:raise ValueError("Code du pilote dupliqué")
        current[code]=a["ark_pactols"]
    if len(current)!=103:raise ValueError("Pilote 103 PACA altéré")
    if (complement.get("schema")!="adlfi.lieux.pactols.paca.complement.2026.public.v1"
        or complement.get("nombre_ajouts")!=832
        or len(complement.get("alignements_Pactols_COG_valides_2026",[]))!=832):
        raise ValueError("Index des 832 PACA altéré")
    if (renommages.get("schema")!="adlfi.lieux.pactols.paca.renommages.2026.public.v2"
        or renommages.get("liens_renommages_ajoutes")!=3
        or renommages.get("total_alignements_PACA_2026")!=938
        or len(renommages.get("alignements_Pactols_COG_valides_2026",[]))!=3):
        raise ValueError("Les 3 renommages PACA ont changé")
    for pack in (complement["alignements_Pactols_COG_valides_2026"],
                 renommages["alignements_Pactols_COG_valides_2026"]):
        for row in pack:
            code=row["code_insee"]
            if code in current:raise ValueError("Collision d'identité PACA antérieure : "+code)
            current[code]=row["ark_pactols"]
    if len(current)!=938 or len(set(current.values()))!=938:
        raise ValueError("Les 938 identités actuelles ne sont pas uniques")
    if (set(CODES)|{ABRIES_CODE}) & set(current):
        raise ValueError("Commune nouvelle déjà validée ailleurs")
    abries=dossier[ABRIES_CODE]
    if (len(abries["candidats_Pactols"])!=1
        or abries["candidats_Pactols"][0]["ark_pactols"]!=ABRIES_ARK_ANCIEN
        or abries["candidats_Pactols"][0]["qualification_de_recette"]!="IDENTITE_ANCIENNE_COMMUNE_PORTEUSE_CODE"
        or not any(x["ark"]==ABRIES_CANDIDAT and
                   x["prefLabels_fr"]==["Abriès-Ristolas"] and
                   x["exactMatch_INSEE"]==[]
                   for x in abries["concepts_lexicaux_non_validants"])):
        raise ValueError("Abriès-Ristolas sans preuve Pactols reste une exception")
    links=[]
    anciens_exclus=[]
    for code,(ark_new,ark_old) in CODES.items():
        d=dossier[code]
        if (len(d["candidats_Pactols"])!=2 or
            d["libelle_COG_2026"]!=CASES[code]["nom"]):
            raise ValueError("Concepts multiples ou identité COG modifiés : "+code)
        lookup={x["ark_pactols"]:x for x in d["candidats_Pactols"]}
        if set(lookup)!={ark_new,ark_old}:raise ValueError("ARK inattendus pour "+code)
        new,old=lookup[ark_new],lookup[ark_old]
        hist=histories[code]
        uri="http://id.insee.fr/geo/commune/"+code
        if (new["qualification_de_recette"]!="CANDIDAT_IDENTITE_COMMUNE_NOUVELLE_SELON_LIBELLE"
            or new["prefLabels_fr"]!=[d["libelle_COG_2026"]]
            or new["owl_deprecated"] or new["dct_isReplacedBy"]
            or new["insee_exactMatch"]!=[{"famille":"commune","identifiant":code,"uri":uri}]
            or not any("Création de la commune nouvelle" in x["texte"] and
                       "[date d'effet : "+hist["date_creation_commune_nouvelle"]+"]" in x["texte"]
                       for x in new["notes"])
            or old["qualification_de_recette"]!="IDENTITE_ANCIENNE_COMMUNE_PORTEUSE_CODE"
            or old["prefLabels_fr"]!=[hist["ancienne_commune_porteuse_code"]]
            or old["insee_exactMatch"]!=[{"famille":"commune","identifiant":code,"uri":uri}]):
            raise ValueError("Les preuves d'identité de la commune nouvelle sont insuffisantes : "+code)
        if ark_new in current.values() or ark_old in current.values():
            raise ValueError("ARK ancien ou actuel déjà réemployé : "+code)
        anciens_exclus.append({"code_insee_reutilise":code,
            "ark_ancienne_commune":ark_old,
            "nom_ancienne_commune":hist["ancienne_commune_porteuse_code"],
            "periode_ancienne_commune_fin":hist["date_creation_commune_nouvelle"],
            "decision":"NE_PAS_ALIGNER_ARK_ANCIEN_A_LA_COMMUNE_NOUVELLE"})
        links.append({
            "code_insee":code,"libelle_COG_2026":d["libelle_COG_2026"],
            "ark_pactols":ark_new,"libelle_pactols":new["prefLabels_fr"][0],
            "uri_insee":uri,"predicat_source":"skos:exactMatch",
            "date_creation_commune_nouvelle":hist["date_creation_commune_nouvelle"],
            "nature_COG":hist["nature_evenement"],
            "communes_sources_COG":hist["communes_sources"],
            "ark_ancien_exclu":ark_old,
            "source_rdf_sha256":RDF_SHA,
            "millesime_validation":2026,"date_validation":"2026-11-18",
            "type_validation":"exactMatch_2026_plus_prefLabel_commune_nouvelle_plus_historyNote_MOD32",
            "statut":"correspondance_PACA_commune_nouvelle_validee_par_preuves_2026",
            "portee_chronologique":"2026_SEULEMENT",
        })
    return {
        "schema":SCHEMA,"region":"paca","millesime_cog":"2026-01-01",
        "source_rdf_sha256":RDF_SHA,"source_audit":SOURCE_AUDIT,
        "nombre_ajouts":7,"pilote_valide_conserve":103,"complements_conserves":832,
        "renommages_conserves":3,"total_alignements_PACA_2026":945,
        "communes_a_instruire":1,"reserve_abries_ristolas":ABRIES_CODE,
        "candidat_lexical_abries_ristolas":ABRIES_CANDIDAT,
        "identites_historiques_inferees":0,"geometries_modifiees":0,
        "anciens_ARK_exclus":anciens_exclus,
        "alignements_Pactols_COG_valides_2026":sorted(links,key=lambda x:x["code_insee"]),
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("audit","pilote","complement","renommages","cog","sortie"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    paths=[a.audit,a.pilote,a.complement,a.renommages,a.cog]
    if a.sortie.exists() or a.sortie.resolve() in [x.resolve() for x in paths]:
        raise ValueError("Sortie neuve distincte des entrées")
    vals=[json.loads(x.read_text(encoding="utf-8")) for x in paths]
    out=construire(*vals)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("PACA_SEPT_COMMUNES_NOUVELLES_PREPAREES",json.dumps({
        "nouvelles_validations":7,"identites_PACA_2026":945,
        "anciens_ARK_exclus":7,"reserve_Abriès_Ristolas":True,
        "geometries_modifiees":0
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
