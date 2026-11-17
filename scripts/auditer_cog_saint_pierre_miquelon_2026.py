#!/usr/bin/env python3
"""Saint-Pierre-et-Miquelon : préinstruction COG 2026 de deux communes et du territoire.

Ne pas identifier les périodes code-libellé aux périodes de statut juridique.
L'année 1976 (DOM), 1985 (collectivité territoriale) et 2003 (COM) ne sont
pas, à elles seules, des dates de création ou de suppression de communes.
Aucun ARK Pactols, contour ancien ou lien de succession ne peut être inféré.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

SHAS={
 "v_comer_2026.csv":"d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed",
 "v_commune_comer_2026.csv":"9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8",
 "v_tom_depuis_1943.csv":"6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd",
 "v_commune_outremer_depuis_1943.csv":"d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748",
 "v_commune_depuis_1943.csv":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
 "v_commune_2026.csv":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
}
CODES={"97501","97502"}
NOMS={"97501":"Miquelon-Langlade","97502":"Saint-Pierre"}
CIBLE="975"

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as stream:
  for block in iter(lambda:stream.read(1<<20),b""):
   h.update(block)
 return h.hexdigest()

def lire(path:Path)->list[dict]:
 with path.open(encoding="utf-8-sig",newline="") as stream:
  header=stream.readline()
  stream.seek(0)
  r=csv.DictReader(stream,delimiter=";" if header.count(";")>header.count(",") else ",")
  rows=list(r)
 if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
  raise ValueError("CSV officiel absent ou mal formé : "+path.name)
 return rows

def episode(row:dict,famille:str,code:str,kind:str)->dict:
 start=row["DATE_DEBUT"]
 end=row["DATE_FIN"] or None
 if (len(start)!=10 or (end and (len(end)!=10 or end<=start))):
  raise ValueError("Période historique COG invalide : "+str(row))
 return {"code":code,"libelle":row["LIBELLE"],"famille":famille,
         "nature":kind,"debut_inclus":start,"fin_exclue":end}

def analyser(dossier:Path)->dict:
 for name,digest in SHAS.items():
  if sha(dossier/name)!=digest:
   raise ValueError("SHA-256 COG 2026 inattendu : "+name)
 tab={key:lire(dossier/key) for key in SHAS}
 cur={r["COM_COMER"]:r for r in tab["v_commune_comer_2026.csv"]
      if r["COMER"]==CIBLE and r["NATURE_ZONAGE"]=="COM"}
 if set(cur)!=CODES or {code:row["LIBELLE"] for code,row in cur.items()}!=NOMS:
  raise ValueError("Le COG 2026 n'atteste plus exactement les deux communes attendues")
 ter={r["COMER"]:r for r in tab["v_comer_2026.csv"] if r["COMER"]==CIBLE}
 if len(ter)!=1 or ter[CIBLE]["LIBELLE"]!="Saint-Pierre-et-Miquelon":
  raise ValueError("Collectivité 975 courante différente")
 # Table française des communes (DROM) : vérifier explicitement les épisodes
 # de 97501/97502 pour ne pas escamoter une éventuelle période DOM 1976-1985.
 hist_drom=[
  episode(r,"DROM",""+r["COM"],"COM")
  for r in tab["v_commune_depuis_1943.csv"]
  if r["COM"] in CODES and r["TYPECOM"]=="COM"
 ]
 hist_comer=[
  episode(r,"COMER",r["COM_COMER"],r["NATURE_ZONAGE"])
  for r in tab["v_commune_outremer_depuis_1943.csv"]
  if r["COM_COMER"] in CODES and r["NATURE_ZONAGE"]=="COM"
 ]
 collectif=[
  episode(r,"COLLECTIVITE",r["COMER"],"COMER")
  for r in tab["v_tom_depuis_1943.csv"] if r["COMER"]==CIBLE
 ]
 if len(hist_comer)<2 or not collectif:
  raise ValueError("Séries historiques insuffisantes pour une préinstruction 975")
 if {e["code"] for e in hist_comer}!=CODES:
  raise ValueError("L'historique COMER ne couvre pas les deux communes 2026")
 for r in hist_drom+hist_comer:
  if r["code"] not in CODES:raise ValueError("Code historique étranger à 975")
 for items in (hist_drom,hist_comer,collectif):
  if len(items)!=len({(r["code"],r["libelle"],r["debut_inclus"],r["fin_exclue"]) for r in items}):
   raise ValueError("Episode COG historique dupliqué")
 report={
  "schema":"adlfi.lieux.spm.audit.cog2026.v1",
  "statut":"PREINSTRUCTION_COG_NON_VALIDANTE",
  "sources":{"producteur":"INSEE, Code officiel géographique au 1er janvier 2026",
             "url":"https://www.insee.fr/fr/information/8740222","sha256":SHAS},
  "collectivite_actuelle":{"code":CIBLE,"libelle":ter[CIBLE]["LIBELLE"],
                          "code_communal":False,"nombre_communes":2},
  "communes_2026":[{"code":code,"libelle":cur[code]["LIBELLE"],
                    "nature":cur[code]["NATURE_ZONAGE"],"collectivite":CIBLE}
                   for code in sorted(CODES)],
  "episodes_collectivite_COG":sorted(collectif,key=lambda r:(r["debut_inclus"],r["code"])),
  "episodes_communes_COMER_COG":sorted(hist_comer,key=lambda r:(r["code"],r["debut_inclus"])),
  "episodes_communes_DROM_COG":sorted(hist_drom,key=lambda r:(r["code"],r["debut_inclus"])),
  "periodes_juridiques_a_ne_pas_confondre":[
    {"nature":"departement_d_outre_mer","texte":"Loi 76-664 du 19 juillet 1976",
     "date_loi":"1976-07-19","transition_communes_inferree":False},
    {"nature":"collectivite_territoriale","texte":"Loi 85-595 du 11 juin 1985",
     "date_loi":"1985-06-11","transition_communes_inferree":False},
    {"nature":"collectivite_d_outre_mer_article_74",
     "texte":"Loi constitutionnelle 2003-276 du 28 mars 2003",
     "date_loi":"2003-03-28","transition_communes_inferree":False}],
  "couverture_pactols_2026_dans_index_public":0,
  "nouveaux_alignements_pactols":0,
  "nouvelles_relations_successions_inferrees":0,
  "geometries_historiques_adoptees":0,
  "publication_docs":False
 }
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--sources",type=Path,required=True)
 p.add_argument("--sortie",type=Path,required=True)
 args=p.parse_args()
 if "docs" in args.sortie.resolve().parts or args.sortie.exists():
  raise ValueError("Écriture refusée dans docs/ ou sur rapport existant")
 obj=analyser(args.sources)
 args.sortie.parent.mkdir(parents=True,exist_ok=True)
 args.sortie.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(obj,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
