#!/usr/bin/env python3
"""Vérifier les deux transitions publiques 2007 contre sept CSV COG 2026.

Les successions juridiques sont sourcées à la loi organique 2007-223, et
ne sont PAS des destinations du mouvement COG (COM_AP doit rester vide).
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from auditer_transition_saint_barthelemy_saint_martin_2007 import SHAS,ENTITES,analyser

def verifier(cog_dir:Path,public:dict)->dict:
 r=analyser(cog_dir)
 if public.get("schema")!="adlfi.lieux.antilles2007.etats_cog_juridique_public.v1":
  raise ValueError("Schéma public Antilles 2007 inattendu")
 if public.get("statut")!="ETATS_COG_DOCUMENTAIRES_ET_SUCCESSIONS_JURIDIQUES_SANS_GEOMETRIES":
  raise ValueError("Confusion entre preuve COG et preuve juridique")
 if public.get("cog_sha256")!=SHAS:
  raise ValueError("Provenance COG 2026 publique incohérente")
 if public.get("date_cog_reforme")!="2007-02-23" or (
    public.get("date_entree_vigueur_loi_organique")!="2007-02-22"):
  raise ValueError("Dates COG / date d'entrée en vigueur confondues")
 if public.get("source_codification_977_978")!="https://www.insee.fr/fr/information/7929495" or (
    public.get("source_loi_succession")!="https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006399955"):
  raise ValueError("Sources juridiques et codification absentes")
 if public.get("start_year")!=1943 or public.get("end_year")!=2026:
  raise ValueError("Fenêtre annuelle non conforme")
 rows=r["lignes"]
 old="\n".join("|".join((x["ancienne_commune_971"]["code"],
  x["ancienne_commune_971"]["libelle"],
  x["ancienne_commune_971"]["date_debut_COG"],
  x["ancienne_commune_971"]["date_fin_exclue_COG"])) for x in rows)
 coll="\n".join("|".join((y["code"],y["libelle"],z["debut"],z["fin"] or ""))
  for x in rows for y in [x["nouvelle_collectivite_2026"]]
  for z in y["couples_code_libelle_historiques"])
 five="\n".join("|".join((x["code_application_5_positions"]["code"],
  x["code_application_5_positions"]["libelle"],
  z["nature_zonage_COG"],z["debut"],z["fin"] or ""))
  for x in rows for z in x["code_application_5_positions"]["episodes_COG"])
 if public.get("episodes_anciens")!=old or (
    public.get("episodes_collectivites")!=coll) or (
    public.get("episodes_codes_cinq_positions")!=five):
  raise ValueError("États COG publiés différents des sept sources originales")
 pub=public.get("relations")
 if not isinstance(pub,list) or len(pub)!=2:
  raise ValueError("Relations juridiques incomplètes")
 for source,relation in zip(rows,pub):
  old=source["ancienne_commune_971"]["code"]
  ref=ENTITES[old]
  if (relation["ancienne_commune"]!={
      "code":old,"libelle":ref["nom"],"type":"COMMUNE","famille_COG":"DROM"} or
      relation["collectivite"]!={"code":ref["collectivite"],"libelle":ref["nom"],
                                 "type":"COLLECTIVITE_OUTREMER"} or
      relation["code_cinq_positions"]!={"code":ref["code_cinq"],
       "nature_zonage_COG":source["code_application_5_positions"]["nature_zonage_COG"],
       "type":"CODE_APPLICATION_5_POSITIONS_NON_COMMUNE"} or
      relation["mouvement_COG"]!={"modalite":"30","date_effet":"2007-02-23","COM_AP":None}):
   raise ValueError("Entités COG ou MOD 30 incompatibles : "+old)
  legal=relation["succession_juridique"]
  if (legal.get("type")!="SUCCESSION_DROITS_ET_OBLIGATIONS" or
      legal.get("source")!="Loi organique n° 2007-223, article "+ref["article_transitoire"] or
      legal.get("source_legifrance")!="https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006399955" or
      legal.get("fondement_CGCT")!=ref["lo"] or
      legal.get("date_effet_relation_precise_deduite") is not None or
      legal.get("identite_pactols_deduite") is not False):
   raise ValueError("Succession juridique ou identité Pactols non attestée : "+old)
 if (public.get("relations_successions_juridiques_documentees")!=2 or
     public.get("nouvelles_relations_successions_COG_inferrees")!=0 or
     public.get("codes_communes_actuelles_creees")!=0 or
     public.get("correspondances_pactols_guadeloupe_2026_conservees")!=32 or
     any(public.get(x)!=0 for x in (
       "nouveaux_alignements_pactols","nouveaux_contours_historiques",
       "retroprojections_anciennes_communes"))):
  raise ValueError("Invariants éditoriaux Antilles non conservés")
 return {"anciennes_communes":2,"collectivites":2,"codes_cinq_positions":2,
  "successions_juridiques_attestees":2,"destinations_COG_COM_AP":0,
  "alignements_Pactols_nouveaux":0,"contours_historiques":0}

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--cog-dir",type=Path,required=True)
 p.add_argument("--public",type=Path,required=True)
 args=p.parse_args()
 data=json.loads(args.public.read_text(encoding="utf-8"))
 print(json.dumps(verifier(args.cog_dir,data),ensure_ascii=False,sort_keys=True,indent=2))
