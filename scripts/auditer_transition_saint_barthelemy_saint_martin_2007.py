#!/usr/bin/env python3
"""Auditer le passage 2007 : anciennes communes 97123/97127 vers COM 977/978.

COG : codes et dates documentaires ; Légifrance : succession juridique
explicitement attestée, distincte de COM_AP (vide dans les deux mouvements).
97701/97801 sont codes d'application à cinq positions : PAS des communes
créées par le changement de statut. Aucune équivalence Pactols déduite.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

SHAS={
 "v_commune_depuis_1943.csv":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
 "v_mvt_commune_2026.csv":"8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
 "v_commune_2026.csv":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
 "v_comer_2026.csv":"d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed",
 "v_tom_depuis_1943.csv":"6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd",
 "v_commune_comer_2026.csv":"9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8",
 "v_commune_outremer_depuis_1943.csv":"d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748",
}
ENTITES={
 "97123":{"nom":"Saint-Barthélemy","collectivite":"977","code_cinq":"97701",
          "lo":"LO6211-1","article_transitoire":"18-X"},
 "97127":{"nom":"Saint-Martin","collectivite":"978","code_cinq":"97801",
          "lo":"LO6311-1","article_transitoire":"18-XI"}
}
SOURCE_LEGALE="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000465963"
SOURCE_INSEE="https://www.insee.fr/fr/information/7929495"

def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()

def lire(path):
 with path.open("r",encoding="utf-8-sig",newline="") as f:
  header=f.readline();f.seek(0)
  rows=list(csv.DictReader(f,delimiter=";" if header.count(";")>header.count(",") else ","))
 if not rows or any(None in x or None in x.values() for x in rows):
  raise ValueError("Fichier COG absent ou mal formé : "+path.name)
 return rows

def analyser(folder):
 for name,digest in SHAS.items():
  if sha(folder/name)!=digest:
   raise ValueError("SHA COG 2026 incorrect : "+name)
 t={name:lire(folder/name) for name in SHAS}
 courant=t["v_commune_2026.csv"]
 histor=t["v_commune_depuis_1943.csv"]
 mvts=t["v_mvt_commune_2026.csv"]
 coll=t["v_comer_2026.csv"]
 coll_hist=t["v_tom_depuis_1943.csv"]
 codes5=t["v_commune_comer_2026.csv"]
 codes5_hist=t["v_commune_outremer_depuis_1943.csv"]
 lines=[]
 for ancien,ref in ENTITES.items():
  nom,code,code5=ref["nom"],ref["collectivite"],ref["code_cinq"]
  old=[r for r in histor if r["TYPECOM"]=="COM" and r["COM"]==ancien]
  if len(old)!=1 or old[0]["LIBELLE"]!=nom or old[0]["DATE_DEBUT"]!="1946-03-21" or old[0]["DATE_FIN"]!="2007-02-23":
   raise ValueError("Épisode communal 971 inattendu : "+ancien)
  if any(r["COM"]==ancien and r["TYPECOM"]=="COM" for r in courant):
   raise ValueError("Ancienne commune toujours courante : "+ancien)
  movement=[r for r in mvts if r["COM_AV"]==ancien and r["DATE_EFF"]=="2007-02-23"]
  if len(movement)!=1 or movement[0]["MOD"]!="30" or movement[0]["COM_AP"]!="":
   raise ValueError("Mouvement MOD 30 2007 ou destination COG inattendue : "+ancien)
  collectivite=[r for r in coll if r["COMER"]==code]
  if len(collectivite)!=1 or collectivite[0]["LIBELLE"]!=nom:
   raise ValueError("Collectivité 2026 absente ou autre libellé : "+code)
  historie=[r for r in coll_hist if r["COMER"]==code]
  if not historie:raise ValueError("Absence de l'historique de la collectivité : "+code)
  five=[r for r in codes5 if r["COMER"]==code and r["COM_COMER"]==code5]
  if len(five)!=1 or five[0]["LIBELLE"]!=nom:
   raise ValueError("Code 5 positions 2026 absent : "+code5)
  fivehist=[r for r in codes5_hist if r["COM_COMER"]==code5]
  if not fivehist:raise ValueError("Absence d'historique du code 5 positions : "+code5)
  # Le champ nature du COG est une catégorie de zonage statistique.
  # L'Insee qualifie 97701/97801 de codes sur cinq positions, non de communes.
  lines.append({
   "ancienne_commune_971":{"code":ancien,"libelle":nom,
      "date_debut_COG":old[0]["DATE_DEBUT"],"date_fin_exclue_COG":old[0]["DATE_FIN"],
      "present_dans_communes_2026":False},
   "mouvement_communal_COG":{"date_effet":movement[0]["DATE_EFF"],
      "mod":movement[0]["MOD"],"com_av":ancien,"com_ap":None,
      "successeur_code_COG_atteste_par_mouvement":False},
   "nouvelle_collectivite_2026":{"code":code,"libelle":nom,
      "couples_code_libelle_historiques":[
        {"code":r["COMER"],"libelle":r["LIBELLE"],"debut":r["DATE_DEBUT"],
         "fin":r["DATE_FIN"] or None}
        for r in sorted(historie,key=lambda x:x["DATE_DEBUT"])]},
   "code_application_5_positions":{"code":code5,"libelle":nom,
      "nature_zonage_COG":five[0]["NATURE_ZONAGE"],"equivalent_a_commune_actuelle":False,
      "episodes_COG":[{"code":r["COM_COMER"],"libelle":r["LIBELLE"],
          "debut":r["DATE_DEBUT"],"fin":r["DATE_FIN"] or None,
          "nature_zonage_COG":r["NATURE_ZONAGE"]}
         for r in sorted(fivehist,key=lambda x:x["DATE_DEBUT"])]},
   "succession_juridique":{
      "predecesseur":"COMMUNE:"+ancien,"successeur":"COLLECTIVITE:"+code,
      "nature":"SUCCESSION_DROITS_OBLIGATIONS_EXPRESSÉMENT_PREVUE_PAR_LOI",
      "source":SOURCE_LEGALE,"loi_organique":"2007-223 du 21 février 2007",
      "article":ref["article_transitoire"],"code_general_collectivites":ref["lo"],
      "date_effet_relation_precise_inferree":None,
      "identite_conceptuelle_Pactols_inferree":False,
      "geometrie_historique_inferree":False}
  })
 return {
  "schema":"adlfi.lieux.antilles2007.audit.cog2026.v1",
  "statut":"PREINSTRUCTION_COG_ET_SUCCESSION_LEGALE_SANS_PUBLICATION",
  "sources_COG_SHA256":SHAS,
  "sources_juridiques":{"insee_codification":SOURCE_INSEE,
      "legifrance":SOURCE_LEGALE},
  "transition_codification_INSEE":"2007-02-23",
  "date_entree_vigueur_loi_organique":"2007-02-22",
  "lignes":lines,
  "bilan":{"anciennes_communes":2,"collectivites":2,
           "codes_applications_cinq_positions":2,
           "nouvelles_relations_successions_juridiques_attestees":2,
           "destinations_COM_AP_COG":0,
           "nouveaux_alignements_pactols":0,
           "contours_historiques_publies":0,
           "publication_docs":False}
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--cog-dir",type=Path,required=True)
 p.add_argument("--sortie",type=Path,required=True)
 args=p.parse_args()
 if "docs" in args.sortie.resolve().parts or args.sortie.exists():
  raise ValueError("Interdiction d'écriture dans docs/ ou d'écrasement")
 r=analyser(args.cog_dir)
 args.sortie.parent.mkdir(parents=True,exist_ok=True)
 args.sortie.write_text(json.dumps(r,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"lignes":r["lignes"],"bilan":r["bilan"]},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
