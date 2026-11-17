#!/usr/bin/env python3
"""Nouvelle-Calédonie : 33 communes COG et histoire des codes distincte des provinces.

La commune de Poya est répartie entre provinces Nord et Sud, donc
une province unique ne saurait être inférée à partir du code communal.
Les 8 aires coutumières relèvent d'un autre référentiel.
La codification COG n'établit ni limites géométriques ni création juridique.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
from auditer_cog_polynesie_2026 import SHAS,sha,read,episode
SOURCE_COG="https://www.insee.fr/fr/information/8740222"
SOURCE_INSEE="https://www.insee.fr/fr/information/7929495"
SOURCE_LOI="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000393606/"
CODES_PARTAGES={"98827"} # Poya : vérifier impérativement code et libellé COG

def analyser(folder:Path,index:Path)->dict:
 for filename,digest in SHAS.items():
  if sha(folder/filename)!=digest:
   raise ValueError("Empreinte de source COG 2026 différente : "+filename)
 t={n:read(folder/n) for n in SHAS}
 published=json.loads(index.read_text(encoding="utf-8"))
 if published.get("schema")!="adlfi.lieux.recherche.outremer.public.v1" or (
     len(published.get("pactols_valides",{}))!=176 or
     len(published.get("pactols_collectivites_valides",{}))!=4):
  raise ValueError("Socle AdlFI 176+4 non conforme")
 current=published["communes"]["988"].split("\n")
 public=dict(r.split("|",1) for r in current)
 if len(current)!=33 or len(public)!=33 or any(
    len(c)!=5 or not c.startswith("988") for c in public):
  raise ValueError("33 identifiants COG 988 attendus dans le site")
 actual=[r for r in t["v_commune_comer_2026.csv"] if r["COMER"]=="988"]
 actual_codes={r["COM_COMER"]:r["LIBELLE"] for r in actual}
 if len(actual)!=33 or actual_codes!=public or any(
    r["NATURE_ZONAGE"]!="COM" for r in actual):
  raise ValueError("Communes NC COG 2026 non concordantes avec le site")
 territory=[r for r in t["v_comer_2026.csv"] if r["COMER"]=="988"]
 if len(territory)!=1 or territory[0]["LIBELLE"]!="Nouvelle-Calédonie":
  raise ValueError("Collectivité COG 988 manquante")
 if any(r["COM"].startswith("988") for r in t["v_commune_2026.csv"]):
  raise ValueError("Commune COMER 988 traitée à tort comme DROM")
 if any(r["COM"].startswith("988") for r in t["v_commune_depuis_1943.csv"]):
  raise ValueError("Commune historique COMER 988 dans table DROM")
 hist=[episode(r,"COM_COMER","COMMUNE_HISTORIQUE_COMER")
       for r in t["v_commune_outremer_depuis_1943.csv"]
       if r["COM_COMER"].startswith("988")]
 territorial=[episode(r,"COMER","TERRITOIRE_COG")
       for r in t["v_tom_depuis_1943.csv"] if r["COMER"]=="988"]
 if not territorial or not {x["code"] for x in hist}.issuperset(public):
  raise ValueError("Historique COG NC incomplet")
 current_hist=[r for r in hist if r["code"] in public]
 autres=[r for r in hist if r["code"] not in public]
 if any(r["nature_zonage_COG"]!="COM" for r in current_hist):
  raise ValueError("Historique des 33 communes contient un zonage non communal")
 poya=[(code,name) for code,name in public.items() if name.casefold()=="poya"]
 if len(poya)!=1:raise ValueError("Poya absente des 33 communes COG")
 if any(code in published["pactols_valides"] for code in public):
  raise ValueError("Alignements NC nouveaux non encore instruits")
 per=collections.Counter(r["code"] for r in current_hist)
 starts=collections.Counter(r["debut_inclus"] for r in current_hist)
 return {"schema":"adlfi.lieux.nouvelle-caledonie.audit.cog2026.v1",
  "statut":"RECETTE_COG_NON_VALIDANTE",
  "sources":{"insee_COG":SOURCE_COG,"insee_codification":SOURCE_INSEE,
    "loi_organique_1999":SOURCE_LOI,"sha256_COG":SHAS},
  "territoire_COG_2026":{"code":"988","libelle":"Nouvelle-Calédonie"},
  "communes_COG_2026":[{"code":c,"libelle":public[c]} for c in sorted(public)],
  "episodes_communes_COG":sorted(current_hist,key=lambda x:(x["code"],x["debut_inclus"])),
  "anciens_codes_ou_zonages_COG_a_qualifier":sorted(autres,key=lambda x:(x["code"],x["debut_inclus"])),
  "episodes_territoire_COG":sorted(territorial,key=lambda x:x["debut_inclus"]),
  "Poya":{"code_COG":poya[0][0],"libelle":poya[0][1],
       "provinces_juridiques":["Nord","Sud"],
       "commune_entierement_dans_une_seule_province":False,
       "code_COG_province_unique":None,
       "parts_provinciales_geometrie_non_qualifiees":True},
  "provinces":{"nombre":3,"noms":["Nord","Sud","Îles Loyauté"],
       "rattachement_commune_vers_province_unique_publie":False},
  "aires_coutumieres":{"nombre":8,"noms":["Hoot Ma Whaap","Paicî-Cèmuhi",
       "Ajië Aro","Xârâcùù","Drubea-Kapumë","Nengone","Drehu","Iaai"],
       "confondues_avec_provinces":False},
  "debut_episodes_par_date_COG":dict(sorted(starts.items())),
  "episodes_par_code":dict(sorted(per.items())),
  "bilan":{"communes_2026":33,"episodes_communes_existantes":len(current_hist),
     "anciens_codes_ou_zonages":len(autres),
     "episodes_territoire":len(territorial),
     "communes_Poya_a_double_province":1,
     "rattachements_provinces_deduits":0,
     "aires_coutumieres_deduites_des_communes":0,
     "nouveaux_ARK":0,"nouveaux_contours":0,"publication_docs":False}}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--sources',type=Path,required=True)
 p.add_argument('--index-public',type=Path,required=True)
 p.add_argument('--sortie',type=Path,required=True)
 a=p.parse_args()
 if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
  raise ValueError("Recette NC à produire hors docs sans écrasement")
 out=analyser(a.sources,a.index_public)
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n',
   encoding="utf-8")
 print("NOUVELLE_CALEDONIE_BILAN",json.dumps(out["bilan"],ensure_ascii=False))
 print("NOUVELLE_CALEDONIE_POYA",json.dumps(out["Poya"],ensure_ascii=False))
 print("NOUVELLE_CALEDONIE_EPISODES_DATES",json.dumps(out["debut_episodes_par_date_COG"],ensure_ascii=False))
 print("NOUVELLE_CALEDONIE_ANCIENS",json.dumps(out["anciens_codes_ou_zonages_COG_a_qualifier"],ensure_ascii=False))
 print("NOUVELLE_CALEDONIE_EPISODES_POUR_CANA_KOUAOUA",
    json.dumps([e for e in out["episodes_communes_COG"] if
      "Canala" in e["libelle"] or "Kouaoua" in e["libelle"]],ensure_ascii=False))
if __name__=="__main__":main()
