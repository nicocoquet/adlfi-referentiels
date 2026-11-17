#!/usr/bin/env python3
"""Préinstruction Wallis-et-Futuna : territoire 986 et 3 circonscriptions COG.

Les circonscriptions ont un fondement juridique dans l'art. 17 de la loi
n° 61-814 (1961), indépendamment de la date initiale des épisodes du COG.
Ne jamais qualifier 98611/98612/98613 de communes, ni inférer leur création
depuis le premier millésime du COG où elles apparaissent.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
SHAS={
 "v_comer_2026.csv":"d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed",
 "v_commune_comer_2026.csv":"9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8",
 "v_tom_depuis_1943.csv":"6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd",
 "v_commune_outremer_depuis_1943.csv":"d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748",
 "v_commune_2026.csv":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
 "v_commune_depuis_1943.csv":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
}
EXPECTED={"98611":"Alo","98612":"Sigave","98613":"Uvea"}
LEGAL={
 "source":"https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000684031",
 "loi":"Loi n° 61-814 du 29 juillet 1961",
 "article_circonscriptions":"17",
 "article_personnalite_morale":"18",
 "en_vigueur_depuis":"1961-07-30",
 "circonscriptions_legales":["Uvea","Alo","Sigave"]
}
INSEE="https://www.insee.fr/fr/information/7929495"

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as s:
  for block in iter(lambda:s.read(1024*1024),b""):
   h.update(block)
 return h.hexdigest()
def read(path:Path)->list[dict]:
 with path.open("r",encoding="utf-8-sig",newline="") as s:
  line=s.readline();s.seek(0)
  rows=list(csv.DictReader(s,delimiter=";" if line.count(";")>line.count(",") else ","))
 if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
  raise ValueError("Table COG absente/invalide "+path.name)
 return rows
def to_episode(r:dict,code_field:str,category:str)->dict:
 start=r["DATE_DEBUT"];end=r["DATE_FIN"] or None
 if not start or len(start)!=10 or (end and (len(end)!=10 or end<=start)):
  raise ValueError("Période COG non conforme : "+repr(r))
 return {"code":r[code_field],"libelle":r["LIBELLE"],
         "debut_inclus":start,"fin_exclue":end,"famille":category,
         **({"nature_zonage_COG":r["NATURE_ZONAGE"]}
            if "NATURE_ZONAGE" in r else {})}
def analyser(folder:Path)->dict:
 for name,expected in SHAS.items():
  if sha(folder/name)!=expected:raise ValueError("SHA-256 officiel incorrect : "+name)
 t={key:read(folder/key) for key in SHAS}
 current_cir=[r for r in t["v_commune_comer_2026.csv"]
              if r["COMER"]=="986" and r["NATURE_ZONAGE"]=="CIR"]
 actual={r["COM_COMER"]:r["LIBELLE"] for r in current_cir}
 if len(current_cir)!=3 or actual!=EXPECTED:
  raise ValueError("Les trois circonscriptions COG 2026 ne correspondent plus aux sources")
 current_territory=[r for r in t["v_comer_2026.csv"] if r["COMER"]=="986"]
 if len(current_territory)!=1 or current_territory[0]["LIBELLE"]!="Wallis-et-Futuna":
  raise ValueError("Collectivité territoriale actuelle 986 non concordante")
 if any(r["COM"].startswith("986") for r in t["v_commune_2026.csv"]):
  raise ValueError("Une commune courante 986 a été trouvée : audit à revoir")
 if any(r["COM"].startswith("986") for r in t["v_commune_depuis_1943.csv"]):
  raise ValueError("Un épisode communal DROM 986 a été trouvé : audit à revoir")
 hist_cir=[to_episode(r,"COM_COMER","CIRCONSCRIPTION_COG")
   for r in t["v_commune_outremer_depuis_1943.csv"]
   if r["COM_COMER"] in EXPECTED and r["NATURE_ZONAGE"]=="CIR"]
 hist_other=[to_episode(r,"COM_COMER","AUTRE_ZONAGE_COG")
   for r in t["v_commune_outremer_depuis_1943.csv"]
   if r["COM_COMER"] in EXPECTED and r["NATURE_ZONAGE"]!="CIR"]
 territory=[to_episode(r,"COMER","TERRITOIRE_COG")
   for r in t["v_tom_depuis_1943.csv"] if r["COMER"]=="986"]
 old_candidates=[to_episode(r,"COMER","ANCIEN_CODE_COG_A_QUALIFIER")
   for r in t["v_tom_depuis_1943.csv"] if r["COMER"] in ("98607","98609")]
 if not territory or {x["code"] for x in hist_cir}!=set(EXPECTED):
  raise ValueError("Épisodes historiques des 3 CIR ou de la collectivité 986 incomplets")
 if any(r["code"] not in EXPECTED for r in hist_cir):
  raise ValueError("Circonscription historique inattendue")
 return {
  "schema":"adlfi.lieux.wallis-futuna.preinstruction.cog2026.v1",
  "statut":"PREINSTRUCTION_NON_VALIDANTE_SANS_PUBLICATION",
  "sources":{"edition":"INSEE Code officiel géographique 2026","url":"https://www.insee.fr/fr/information/8740222","sha256":SHAS},
  "source_histoire_codification":{"url":INSEE,"note":"La notice Insee mentionne 98607, 98609, puis 986 en 1985 ; les codes ne sont pas reliés automatiquement."},
  "source_loi_1961":LEGAL,
  "territoire_2026":{"code":"986","libelle":"Wallis-et-Futuna",
       "nature":"TERRITOIRE_NON_COMMUNAL","nombre_communes":0,"nombre_circonscriptions":3},
  "circonscriptions_2026":[{"code":code,"libelle":EXPECTED[code],
      "type":"CIRCONSCRIPTION_TERRITORIALE_NON_COMMUNALE",
      "nature_zonage_COG":"CIR","territoire":"986"} for code in sorted(EXPECTED)],
  "episodes_circonscriptions_COG":sorted(hist_cir,key=lambda r:(r["code"],r["debut_inclus"])),
  "episodes_autres_zonages_de_codes_identiques_a_qualifier":sorted(hist_other,key=lambda r:(r["code"],r["debut_inclus"])),
  "episodes_territoire_COG":sorted(territory,key=lambda r:(r["code"],r["debut_inclus"])),
  "anciens_codes_territoriaux_a_qualifier":sorted(old_candidates,key=lambda r:(r["code"],r["debut_inclus"])),
  "distinctions":{"annee_loi_1961_n_est_pas_date_premier_episode_COG":True,
    "communes_creees":0,"equivalence_98607_98609_986_inferree":False,
    "distinction_territoire_circonscription":True,
    "distinction_circonscription_royaume_coutumier":True},
  "bilan":{"codes_circonscriptions_2026":3,"codes_communes_2026":0,
    "nouveaux_alignements_Pactols":0,"geometries_historiques":0,
    "successions_de_codes_inferrees":0,"publication_docs":False}
 }
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--sources",required=True,type=Path)
 p.add_argument("--sortie",required=True,type=Path)
 args=p.parse_args()
 if "docs" in args.sortie.resolve().parts or args.sortie.exists():
  raise ValueError("Sortie de préinstruction hors docs/ uniquement")
 result=analyser(args.sources)
 args.sortie.parent.mkdir(parents=True,exist_ok=True)
 args.sortie.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
if __name__=="__main__":main()
