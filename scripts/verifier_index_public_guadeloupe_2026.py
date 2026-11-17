#!/usr/bin/env python3
"""Vérifier les 35 épisodes publics Guadeloupe et les MOD contre le COG original."""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

EXPECTED={("1946-03-21","20"):34,("1976-06-04","10"):1,
          ("2007-02-23","30"):2}
OLD={"97123","97127"}

def verifier(audit:dict,public:dict)->dict:
    if audit.get("schema")!="adlfi.lieux.guadeloupe.audit.cog-pactols-geom.v1":
        raise ValueError("Audit COG source Guadeloupe non reconnu")
    if public.get("schema")!="adlfi.lieux.guadeloupe.etats_cog_public.v1":
        raise ValueError("Chronologie publique 971 non reconnue")
    expected=sorted((r["code"],r["libelle"],r["debut_inclus"],r["fin_exclue"] or "")
                    for r in audit["historique_codes_971"])
    actual=sorted(tuple(line.split("|")) for line in public["episodes"].splitlines())
    if expected!=actual or len(actual)!=35:
        raise ValueError("Les 35 épisodes COG publics ne correspondent pas aux fichiers officiels")
    codes={x[0] for x in actual}
    if len(codes)!=34:
        raise ValueError("Les codes communaux historiques ne sont pas distincts")
    current={x["code_COG_2026"]:x["libelle_COG_2026"] for x in audit["communes"]}
    active={c:l for c,l,start,end in actual
            if start<="2026-01-01" and (not end or end>"2026-01-01")}
    if len(active)!=32 or active!=current or set(codes)-set(current)!=OLD:
        raise ValueError("Les 32 codes COG 2026 ou les deux anciens codes ont changé")
    event=collections.Counter((x["DATE_EFF"],x["MOD"])
                              for x in audit["mouvements_source_avec_code_971"])
    if event!=EXPECTED:
        raise ValueError("Les mouvements COG de Guadeloupe ont changé")
    printed={(x["date_effet"],x["modalite"]):x["lignes"]
             for x in public["mouvements_decompte"]}
    if printed!=EXPECTED:
        raise ValueError("Le résumé des mouvements COG est incomplet")
    exit07=[x for x in audit["mouvements_source_avec_code_971"]
            if x["DATE_EFF"]=="2007-02-23"]
    if len(exit07)!=2 or {e["COM_AV"] for e in exit07}!=OLD or any(
       e["MOD"]!="30" or e["COM_AP"]!="" for e in exit07):
        raise ValueError("Destination COG 2007 artificiellement renseignée")
    rename=[x for x in audit["mouvements_source_avec_code_971"]
            if x["DATE_EFF"]=="1976-06-04"]
    if len(rename)!=1 or rename[0]["COM_AV"]!="97107" or rename[0]["COM_AP"]!="97107" or (
       rename[0]["LIBELLE_AV"]!="Capesterre-de-Guadeloupe" or
       rename[0]["LIBELLE_AP"]!="Capesterre-Belle-Eau"):
        raise ValueError("Le renommage de Capesterre n'est pas celui du COG")
    for old in public["anciens_codes"]:
        if old["code"] not in OLD or old["destination_com_ap"] is not None or (
           old["ark_pactols_uri_insee_atteste"] is not None):
            raise ValueError("Lien historique ou Pactols inventé")
    if len(public["anciens_codes"])!=2 or public["nouveaux_alignements_pactols"]!=0 or (
       public["nouvelles_relations_successions_inferrees"]!=0) or (
       public["contours_historiques_publies"]!=0):
        raise ValueError("Publication de relations historiques interdites")
    if audit["bilan"]["source_Pactols_stats"]["liens_insee_non_courants"]:
        raise ValueError("Le RDF ne doit pas citer d'ARK lié aux anciennes URI 971")
    return {"episodes_valides":35,"codes_historiques":34,
            "codes_actuels":32,"anciens_codes":2,"mouvements":37,
            "anciennes_destinations_COG_non_renseignees":2,
            "nouveaux_alignements_ARK":0,"contours_publies":0}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit",type=Path,required=True)
    p.add_argument("--public",type=Path,required=True)
    args=p.parse_args()
    a=json.loads(args.audit.read_text(encoding="utf8"))
    b=json.loads(args.public.read_text(encoding="utf8"))
    print(json.dumps(verifier(a,b),ensure_ascii=False,sort_keys=True,indent=2))
