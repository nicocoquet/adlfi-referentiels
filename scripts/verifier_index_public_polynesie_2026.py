#!/usr/bin/env python3
"""Comparer les périodes 987 publiées aux six fichiers COG officiels.

Les dates COG sont des attestations de codes ; les communes associées
relèvent de l'ISPF et ne sont pas inférées des 48 enregistrements communaux.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from auditer_cog_polynesie_2026 import SHAS,analyser

def render_current(xs):
 return "\n".join(f'{x["code"]}|{x["libelle"]}' for x in xs)

def render_hist(xs):
 return "\n".join(f'{r["code"]}|{r["libelle"]}|{r["debut_inclus"]}|{r["fin_exclue"] or ""}'
  for r in sorted(xs,key=lambda r:(r["code"],r["debut_inclus"])))

def verifier(folder:Path,existing_index:Path,published:dict)->dict:
 a=analyser(folder,existing_index)
 if published.get("schema")!="adlfi.lieux.polynesie.etats_cog_public.v1" or (
    published.get("statut")!="ETATS_COG_DOCUMENTAIRES_SANS_GEOMETRIES_NI_RELATIONS_ASSOCIEES"):
  raise ValueError("Schéma public Polynésie incompatible")
 if published.get("cog_sha256")!=SHAS:
  raise ValueError("Sources COG SHA-256 publiques non vérifiées")
 if published.get("communes_actuelles_2026")!=render_current(a["communes_2026"]):
  raise ValueError("Les 48 codes/libellés communaux publics diffèrent du COG")
 if published.get("episodes_communes_COG")!=render_hist(a["episodes_communes_COG"]):
  raise ValueError("Les épisodes COG 987 publiés diffèrent des fichiers INSEE")
 if published.get("episode_territoire_COG")!=render_hist(a["episodes_collectivite_COG"]):
  raise ValueError("L'épisode territorial 987 est différent du COG")
 extra=a["autres_codes_historiques_a_instruire"]
 clip=published.get("ancien_code_Clipperton_COG",{})
 if len(extra)!=1 or extra[0]["code"]!="98799":
  raise ValueError("Un code historique autre que Clipperton est à instruire")
 old=extra[0]
 if not all((clip.get("code")==old["code"],clip.get("libelle")==old["libelle"],
    clip.get("debut_inclus")==old["debut_inclus"],
    clip.get("fin_exclue")==old["fin_exclue"],clip.get("code_actuel") is False)):
  raise ValueError("Clipperton historique 98799 est mal documenté")
 if len(a["episodes_communes_COG"])!=48 or a["rapport"]["episodes_termines"]!=0:
  raise ValueError("L'historique du COG 987 exige une nouvelle qualification")
 if {x["debut_inclus"] for x in a["episodes_communes_COG"]}!={"1972-05-21"}:
  raise ValueError("Date d'attestation COG communale changée")
 if published.get("start_year")!=1943 or published.get("end_year")!=2026:
  raise ValueError("Fenêtre annuelle non conforme")
 r=published.get("recette_COG",{})
 if r.get("nombre_communes")!=48 or r.get("nombre_episodes")!=48 or (
    r.get("premiere_attestation_COG")!="1972-05-21" or
    r.get("nombre_changements_code_libelle_ulterieurs")!=0):
  raise ValueError("Comptage d'épisodes éditorialement différent")
 ispf=published.get("decoupage_ISPF",{})
 if any(ispf.get(k)!=v for k,v in {
   "nombre_communes_associees":98,"nombre_communes_avec_associees":30,
   "nombre_communes_sans_associees":18,"nombre_unites_de_nomenclature_fine":116,
   "nombre_subdivisions_administratives":5}.items()) or (
    ispf.get("liste_codes_associes_incluse") is not False or
    ispf.get("correspondance_automatique_commune_ile") is not False):
  raise ValueError("Découpage ISPF déduit à tort des tables COG")
 law=published.get("historique_juridique",{})
 if (law.get("communes_preexistantes_avant_1971")!=4 or
     law.get("communes_ajoutees_reforme")!=44 or
     law.get("creation_juridique_toutes_communes_deduite_1972") is not False):
  raise ValueError("Date de création des communes non attestée")
 for key in ("alignements_pactols_2026_valides","nouveaux_alignements_pactols",
             "contours_historiques_publies","communes_associees_creees",
             "subdivisions_mises_dans_communes","relations_historiques_inferrees"):
  if published.get(key)!=0:raise ValueError("Inférence historique / Pactols interdite : "+key)
 return {"communes":48,"episodes":48,"premiere_attestation_COG":"1972-05-21",
     "Clipperton_98799_exclu":True,"associations_ISPF_sans_codes_inventes":98,
     "nouvelles_relations_Pactols":0,"contours_historiques":0}

if __name__=="__main__":
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--sources",type=Path,required=True)
 parser.add_argument("--index-public",type=Path,required=True)
 parser.add_argument("--public",type=Path,required=True)
 args=parser.parse_args()
 d=json.loads(args.public.read_text(encoding="utf-8"))
 print(json.dumps(verifier(args.sources,args.index_public,d),ensure_ascii=False,sort_keys=True,indent=2))
