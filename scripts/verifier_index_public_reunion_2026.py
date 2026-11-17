#!/usr/bin/env python3
"""Contrôler chaque épisode 974 et les mouvements 1965 contre le COG Insee original."""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

SHAS={
 "v_commune_2026.csv":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
 "v_commune_depuis_1943.csv":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
 "v_mvt_commune_2026.csv":"8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1"
}
CODES={f"974{i:02d}" for i in range(1,25)}

def digest(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1<<20),b""):h.update(block)
 return h.hexdigest()

def rows(path:Path)->list[dict]:
 with path.open(encoding="utf-8-sig",newline="") as f:
  entries=list(csv.DictReader(f))
 if not entries or any(None in r or any(v is None for v in r.values()) for r in entries):
  raise ValueError("CSV Insee COG absent, vide ou mal structuré : "+path.name)
 return entries

def verifier(cog_dir:Path,public:dict)->dict:
 if public.get("schema")!="adlfi.lieux.reunion.etats_cog_public.v1":
  raise ValueError("Schéma de publication Réunion inconnu")
 for file,sha in SHAS.items():
  if digest(cog_dir/file)!=sha:raise ValueError("Source Insee non épinglée : "+file)
 actuel={r["COM"]:r["LIBELLE"] for r in rows(cog_dir/"v_commune_2026.csv")
          if r["TYPECOM"]=="COM" and r["DEP"]=="974"}
 if set(actuel)!=CODES:raise ValueError("COG courant 974 incomplet")
 historiques=sorted([
  (r["COM"],r["LIBELLE"],r["DATE_DEBUT"],r["DATE_FIN"])
  for r in rows(cog_dir/"v_commune_depuis_1943.csv")
  if r["TYPECOM"]=="COM" and r["COM"].startswith("974")
 ])
 publies=sorted(tuple(x.split("|")) for x in public["episodes"].splitlines())
 if historiques!=publies or len(historiques)!=24:
  raise ValueError("Épisodes historiques publics distincts des 24 observations officielles")
 if {code:nom for code,nom,_,end in historiques if not end}!=actuel:
  raise ValueError("Libellés historiques courants différents des états 2026")
 mouvements=[
  r for r in rows(cog_dir/"v_mvt_commune_2026.csv")
  if r["COM_AV"].startswith("974") or r["COM_AP"].startswith("974")
 ]
 comptes=collections.Counter((r["DATE_EFF"],r["MOD"]) for r in mouvements)
 recap={(r["date_effet"],r["modalite"]):r["lignes"]
        for r in public["mouvements_decompte"]}
 if comptes!=recap or len(mouvements)!=25:
  raise ValueError("Les 25 mouvements COG diffèrent du récapitulatif publié")
 division=[r for r in mouvements if r["DATE_EFF"]=="1965-02-05"]
 if len(division)!=2 or {r["MOD"] for r in division}!={"20"} or (
    {r["COM_AV"] for r in division}!={"97414"}) or (
    {r["COM_AP"] for r in division}!={"97414","97424"}):
  raise ValueError("Division Saint-Louis/Cilaos non conforme aux mouvements originaux")
 noms=sorted((r["COM_AP"],r["LIBELLE_AP"]) for r in division)
 if noms!=[("97414","Saint-Louis"),("97424","Cilaos")]:
  raise ValueError("Noms des communes issues de la division non attestés")
 d=public["mouvement_division_1965"]
 if d["code_avant"]!="97414" or d["date_effet"]!="1965-02-05" or (
  d["codes_apres"]!=["97414","97424"]) or (
  d["contour_avant_1965"] is not None or d["contour_apres_1965"] is not None):
  raise ValueError("Reconstitution géométrique ou transfert non documenté")
 if any(public.get(k)!=0 for k in (
    "nouveaux_alignements_pactols",
    "contours_historiques_publies",
    "nouvelles_relations_successions_inferrees"
 )) or public["correspondances_pactols_COG_2026_conservees"]!=24:
  raise ValueError("Inférence historique ou correspondance nouvelle interdite")
 return {"communes_COG_2026":24,"episodes_officiels":24,"mouvements_officiels":25,
         "division_1965_lignes":2,"nouveaux_ARK":0,"contours_historiques":0}

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--cog-dir",type=Path,required=True)
 p.add_argument("--public",type=Path,required=True)
 args=p.parse_args()
 data=json.loads(args.public.read_text(encoding="utf-8"))
 print(json.dumps(verifier(args.cog_dir,data),sort_keys=True,ensure_ascii=False,indent=2))
