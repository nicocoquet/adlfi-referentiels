#!/usr/bin/env python3
"""Certifier les trois épisodes publics SPM à partir des 6 fichiers INSEE originaux.

La famille COG d'un épisode n'est pas une qualification constitutionnelle
historique : DOM 1976–1985 et collectivités 1985/2003 sont documentés à part.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from auditer_cog_saint_pierre_miquelon_2026 import SHAS, analyser

SCHEMA="adlfi.lieux.spm.etats_cog_public.v1"
def to_compact(rows):
 return "\n".join("|".join((r["code"],r["libelle"],r["debut_inclus"],r["fin_exclue"] or ""))
                  for r in sorted(rows,key=lambda r:(r["code"],r["debut_inclus"])))
def verifier(dossier:Path,data:dict)->dict:
 source=analyser(dossier)
 if data.get("schema")!=SCHEMA or data["statut"]!="ETATS_DOCUMENTAIRES_SANS_GEOMETRIES":
  raise ValueError("Schéma public SPM inattendu")
 if data.get("cog_sha256")!=SHAS:
  raise ValueError("Sources COG 2026 non identiques à la provenance authentifiée")
 current="\n".join(f'{x["code"]}|{x["libelle"]}' for x in source["communes_2026"])
 if data["communes_2026"]!=current:
  raise ValueError("Communes actuelles 975 non conformes")
 compara={
  "episodes_communes_COMER":source["episodes_communes_COMER_COG"],
  "episodes_communes_DROM":source["episodes_communes_DROM_COG"],
  "episodes_collectivite_COG":source["episodes_collectivite_COG"]
 }
 for k,v in compara.items():
  if data[k]!=to_compact(v):
   raise ValueError("Épisodes publics divergents du COG INSEE : "+k)
 if len(source["episodes_communes_COMER_COG"])!=2 or (
    len(source["episodes_communes_DROM_COG"])!=0) or (
    len(source["episodes_collectivite_COG"])!=1):
  raise ValueError("Structure historique SPM différente du rapport de préinstruction")
 if data.get("famille_COG_non_equivalente_au_statut_juridique") is not True:
  raise ValueError("Confusion entre famille COMER et statut DOM/COM")
 for k in ("nouveaux_alignements_pactols","relations_successions_inferrees",
           "contours_historiques_publies","identites_historiques_retroprojetees",
           "correspondances_Pactols_COG_2026_conservees"):
  if data.get(k)!=0:
   raise ValueError("Une relation/limite historique non approuvée a été publiée : "+k)
 if data["code_collectivite_2026"]!="975" or (
    data["start_year"]!=1943) or data["end_year"]!=2026:
  raise ValueError("Code ou période SPM publique incohérents")
 laws=data["statuts_juridiques_reperes_annuels"]
 if len(laws)!=4 or [
    (x["date_loi"],x["preuve"],x["date_effet_precise_deduite"]) for x in laws]!=[
    ("1976-07-19","Loi n° 76-664",False),
    ("1985-06-11","Loi n° 85-595",False),
    ("2003-03-28","Loi constitutionnelle n° 2003-276",False),
    ("2007-02-21","Loi organique n° 2007-223",False),
   ]:
  raise ValueError("Jalons statutaires juridiques incorrects")
 return {"communes_2026":2,"episodes_COG_communes_COMER":2,
         "episodes_COG_communes_DROM":0,"episodes_COG_collectivite":1,
         "code_collectivite":"975","nouveaux_Pactols":0,"geometries_historiques":0,
         "sources_SHA256":SHAS}
if __name__=="__main__":
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--cog-dir",type=Path,required=True)
 parser.add_argument("--public",type=Path,required=True)
 args=parser.parse_args()
 print(json.dumps(verifier(args.cog_dir,json.loads(args.public.read_text(encoding="utf-8"))),
                  ensure_ascii=False,indent=2))
