#!/usr/bin/env python3
"""Polynésie française : auditer les 48 communes COG 2026 et les épisodes historiques.

Le COG 2026 définit les communes, mais non une hiérarchie exhaustive des
98 communes associées définies par l'ISPF. Les subdivisions administratives,
les îles et les communes associées sont des nomenclatures distinctes.
Dates du COG = attestations de couples code–libellé, non dates de création.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,collections
from pathlib import Path

SHAS={
 "v_comer_2026.csv":"d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed",
 "v_commune_comer_2026.csv":"9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8",
 "v_tom_depuis_1943.csv":"6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd",
 "v_commune_outremer_depuis_1943.csv":"d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748",
 "v_commune_2026.csv":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
 "v_commune_depuis_1943.csv":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee"
}
INSEE_SOURCE="https://www.insee.fr/fr/information/8740222"
INSEE_CODIFICATION="https://www.insee.fr/fr/information/7929495"
LOI_1971="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000693681"
ISPF="https://www.ispf.pf/ispf/referentiels"
ETAT="https://www.polynesie-francaise.gouv.fr/Actions-de-l-Etat/Accompagnement-des-communes/Presentation"

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()

def read(path:Path)->list[dict]:
 with path.open("r",encoding="utf-8-sig",newline="") as f:
  first=f.readline();f.seek(0)
  rows=list(csv.DictReader(f,delimiter=";" if first.count(";")>first.count(",") else ","))
 if not rows or any(None in r or None in r.values() for r in rows):
  raise ValueError("Table COG manquante ou mal formée : "+path.name)
 return rows

def episode(r:dict,code_field:str,category:str)->dict:
 debut=r["DATE_DEBUT"];fin=r["DATE_FIN"] or None
 if len(debut)!=10 or (fin and (len(fin)!=10 or fin<=debut)):
  raise ValueError("Dates d'épisode COG anormales "+str(r))
 return {"code":r[code_field],"libelle":r["LIBELLE"],
         "debut_inclus":debut,"fin_exclue":fin,
         "nature_zonage_COG":r.get("NATURE_ZONAGE"),
         "famille_COG":category}

def codes_publics(path:Path)->dict[str,str]:
 data=json.loads(path.read_text(encoding="utf-8"))
 if data.get("schema")!="adlfi.lieux.recherche.outremer.public.v1":
  raise ValueError("Référentiel public ultramarin inattendu")
 raw=data["communes"]["987"]
 pairs=[line.split("|") for line in raw.splitlines()]
 if len(pairs)!=48 or any(len(p)!=2 for p in pairs):
  raise ValueError("48 couples publics 987 attendus")
 codes=dict(pairs)
 if len(codes)!=48 or set(codes)!=set(f"987{x}" for x in range(11,59)):
  raise ValueError("Les codes communaux publics 987 sont incomplets")
 if any(code in data["pactols_valides"] for code in codes):
  raise ValueError("Un ARK 987 est déjà publié, audit à revoir")
 return codes

def analyser(folder:Path,public:Path)->dict:
 for filename,digest in SHAS.items():
  if sha(folder/filename)!=digest:
   raise ValueError("Empreinte COG différente : "+filename)
 t={filename:read(folder/filename) for filename in SHAS}
 pub=codes_publics(public)
 current=[r for r in t["v_commune_comer_2026.csv"] if r["COMER"]=="987"]
 listed=[r for r in current if r["NATURE_ZONAGE"]=="COM"]
 others=[r for r in current if r["NATURE_ZONAGE"]!="COM"]
 actual={r["COM_COMER"]:r["LIBELLE"] for r in listed}
 if len(listed)!=48 or len(actual)!=48 or actual!=pub:
  raise ValueError("Les 48 communes publiques divergent du COG 2026")
 if any(r["COM"].startswith("987") for r in t["v_commune_2026.csv"]):
  raise ValueError("Commune DROM 987 inattendue")
 if any(r["COM"].startswith("987") for r in t["v_commune_depuis_1943.csv"]):
  raise ValueError("Commune historique DROM 987 inattendue")
 territo=[r for r in t["v_comer_2026.csv"] if r["COMER"]=="987"]
 if len(territo)!=1 or territo[0]["LIBELLE"]!="Polynésie française":
  raise ValueError("Territoire COG 987 non conforme")
 hist=[episode(r,"COM_COMER","COMMUNE_HISTORIQUE_COMER")
   for r in t["v_commune_outremer_depuis_1943.csv"]
   if r["COM_COMER"] in actual]
 noncommunes=[episode(r,"COM_COMER","ZONAGE_COG_A_QUALIFIER")
   for r in t["v_commune_outremer_depuis_1943.csv"]
   if r["COM_COMER"].startswith("987") and r["COM_COMER"] not in actual]
 territories=[episode(r,"COMER","TERRITOIRE_COG")
   for r in t["v_tom_depuis_1943.csv"] if r["COMER"]=="987"]
 if not territories:
  raise ValueError("Aucun épisode historique du territoire 987")
 if {x["code"] for x in hist}!=set(pub):
  raise ValueError("Historique COG incomplet pour les 48 communes 2026")
 if not all(x["nature_zonage_COG"]=="COM" for x in hist):
  raise ValueError("Des épisodes associés ne sont pas des communes COM")
 if len(others)>0:
  raise ValueError("Zonage distinct en 2026 à traiter séparément : "+
                   repr([(r["COM_COMER"],r["NATURE_ZONAGE"]) for r in others]))
 starts=collections.Counter(x["debut_inclus"] for x in hist)
 percode=collections.Counter(x["code"] for x in hist)
 end=len([x for x in hist if x["fin_exclue"] is not None])
 return {
   "schema":"adlfi.lieux.polynesie.audit.cog2026.v1",
   "statut":"RECETTE_DOCUMENTAIRE_NON_VALIDANTE",
   "sources":{"edition":"COG 2026","insee":INSEE_SOURCE,"sha256":SHAS,
     "codification_COMER":INSEE_CODIFICATION},
   "autres_sources":{"loi_1971":LOI_1971,"ispf_nomenclature":ISPF,
       "etat_48_communes":ETAT},
   "territoire_2026":{"code":"987","libelle":"Polynésie française",
       "categorie":"COLLECTIVITE_OUTREMER"},
   "communes_2026":[{"code":c,"libelle":pub[c],"famille":"COMER","nature_zonage":"COM"}
                     for c in sorted(pub)],
   "episodes_communes_COG":sorted(hist,key=lambda x:(x["code"],x["debut_inclus"])),
   "episodes_collectivite_COG":sorted(territories,key=lambda x:(x["code"],x["debut_inclus"])),
   "autres_codes_historiques_a_instruire":sorted(noncommunes,key=lambda x:(x["code"],x["debut_inclus"])),
   "autres_zonages_COG_2026":[],"debut_episodes_par_date_COG":dict(sorted(starts.items())),
   "nombre_episodes_par_code":dict(sorted(percode.items())),
   "rapport":{"communes_COG_2026":48,
      "communes_associees_ISPF_a_documenter_separement":98,
      "communes_avec_associees_ISPF":30,
      "communes_sans_associees_ISPF":18,
      "subdivisions_administratives_etat":5,
      "episodes_communes_COG":len(hist),"episodes_termines":end,
      "codes_historique_distincts":len(percode),
      "autres_zonages_courants_COG":len(others),
      "autres_codes_historiques_COG":len(noncommunes),
      "episodes_collectivite_COG":len(territories),
      "nouveaux_alignements_Pactols":0,"nouveaux_contours_historiques":0,
      "historique_des_communes_associees_COG_inferre":False,
      "creation_de_toutes_les_communes_en_1972_inferree":False,
      "publication_docs":False}
 }
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--sources",required=True,type=Path)
 ap.add_argument("--index-public",required=True,type=Path)
 ap.add_argument("--sortie",required=True,type=Path)
 a=ap.parse_args()
 if "docs" in a.sortie.resolve().parts or a.sortie.exists():
  raise ValueError("Écriture sous docs/ ou écrasement interdits")
 d=analyser(a.sources,a.index_public)
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"rapport":d["rapport"],"debut_episodes_par_date_COG":d["debut_episodes_par_date_COG"],
   "territoire":d["episodes_collectivite_COG"],
   "autres_historiques":d["autres_codes_historiques_a_instruire"]},ensure_ascii=False))
if __name__=="__main__":main()
