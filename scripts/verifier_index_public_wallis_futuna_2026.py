#!/usr/bin/env python3
"""Certifier les dates publiques COG Wallis-et-Futuna à partir des six CSV INSEE.

98607 = Nouvelle-Calédonie dans les séries historiques ; n'est pas érigé
en Wallis-et-Futuna 1943. Les trois circonscriptions de droit (1961)
n'ont pas de code COG documenté avant 1985 dans l'édition consultée.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from auditer_cog_wallis_futuna_2026 import SHAS,analyser

def compact(rows,with_nature=False):
 return "\n".join("|".join((r["code"],r["libelle"])+
            ((r["nature_zonage_COG"],) if with_nature else tuple())+
            (r["debut_inclus"],r["fin_exclue"] or ""))
        for r in sorted(rows,key=lambda r:(r["code"],r["debut_inclus"])))
def verifier(folder:Path,pub:dict)->dict:
 source=analyser(folder)
 if pub.get("schema")!="adlfi.lieux.wallis-futuna.etats_cog_public.v1":
  raise ValueError("Schéma public Wallis-et-Futuna inconnu")
 if pub.get("cog_sha256")!=SHAS:
  raise ValueError("Provenance COG 2026 différente")
 expected_cur="\n".join(f'{x["code"]}|{x["libelle"]}|{x["nature_zonage_COG"]}'
    for x in source["circonscriptions_2026"])
 if pub.get("circonscriptions_2026")!=expected_cur:
  raise ValueError("Liste des 3 CIR 2026 différente")
 if pub.get("episodes_circonscriptions")!=compact(
    source["episodes_circonscriptions_COG"],with_nature=True):
  raise ValueError("Épisodes des CIR différents du COG")
 if pub.get("episodes_territoire")!=compact(source["episodes_territoire_COG"]):
  raise ValueError("Épisode territorial 986 différent du COG")
 old=[x for x in source["anciens_codes_territoriaux_a_qualifier"] if x["code"]=="98609"]
 if len(old)!=1 or pub.get("code_territorial_ancien_documente")!=compact(old):
  raise ValueError("Période du code 98609 différente du COG")
 newcal=[x for x in source["anciens_codes_territoriaux_a_qualifier"] if x["code"]=="98607"]
 if len(newcal)!=1 or newcal[0]["libelle"]!="Nouvelle-Calédonie":
  raise ValueError("Ancien code 98607 inattendu")
 ctx=pub.get("ancien_code_contextuel_non_adopte",{})
 if ctx.get("code")!="98607" or ctx.get("libelle")!=newcal[0]["libelle"] or (
    ctx.get("debut_cog")!=newcal[0]["debut_inclus"]) or (
    ctx.get("fin_exclue_cog")!=newcal[0]["fin_exclue"]):
  raise ValueError("98607 attribué à Wallis contrairement au COG")
 if source["episodes_autres_zonages_de_codes_identiques_a_qualifier"]:
  raise ValueError("Zonages supplémentaires 986 à instruire")
 law=pub.get("loi_circonscriptions",{})
 if law.get("entree_en_vigueur")!="1961-07-30" or law.get("articles")!=["17","18"] or (
    law.get("personnalite_morale") is not True) or (
    law.get("lien")!="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000684031"):
  raise ValueError("Fondement légal de 1961 incohérent")
 if pub.get("territoire_courant")!={"code":"986","libelle":"Wallis-et-Futuna",
    "type":"TERRITOIRE_COMER_NON_COMMUNAL","circonscriptions":3,"communes":0}:
  raise ValueError("Wallis-et-Futuna ne doit pas contenir de communes")
 if pub.get("start_year")!=1943 or pub.get("end_year")!=2026 or (
    pub.get("famille_COG_distincte_statut_juridique") is not True):
  raise ValueError("Fenêtre temporelle ou distinction juridique incohérente")
 for key in ("nouveaux_alignements_pactols","contours_historiques_publies",
             "codes_communes_creees","correspondances_pactols_2026_validees_pour_les_3_circonscriptions"):
  if pub.get(key)!=0:raise ValueError("Publication d'autorités non homologuées : "+key)
 for key in ("creation_circonscriptions_inferree_de_1985",
             "succession_juridique_98609_986_inferree",
             "lien_de_identite_98607_986_inferre",
             "trois_circonscriptions_sont_les_3_royaumes_coutumiers",
             "publication_autorites_pactols"):
  if pub.get(key) is not False:raise ValueError("Identité juridique/coutumière ou publication inférée : "+key)
 return {"codes_circonscriptions":3,"episodes_COG_circonscriptions":3,
   "episodes_territoire_986":1,"episodes_ancien_code_98609":1,
   "ancien_code_98607_Nouvelle_Caledonie":1,"communes":0,
   "nouveaux_Pactols":0,"contours_historiques":0}
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--sources",required=True,type=Path)
 p.add_argument("--public",required=True,type=Path)
 args=p.parse_args()
 d=json.loads(args.public.read_text(encoding="utf-8"))
 print(json.dumps(verifier(args.sources,d),ensure_ascii=False,sort_keys=True,indent=2))
