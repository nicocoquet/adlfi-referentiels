#!/usr/bin/env python3
"""Publier en 2026 trois liens Pactols dont les UUID sont résolus par RDF Insee.

Ne pas présenter ces liens comme des exactMatch Pactols vers les codes : le
skos:exactMatch vise une URI UUID et c'est le RDF de l'Insee qui établit
l'identité codeINSEE / owl:sameAs. Les épisodes historiques ne sont pas liés.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from auditer_pdl_trois_uuid_insee_2026 import (
  CASES, SCHEMA as AUDIT_SCHEMA, URI_BASE, GEO, source_uri,
)
from auditer_pactols_polynesie_2026 import RDF_SHA

SCHEMA="adlfi.lieux.pactols.pdl.trois_uuid_resolus.2026.public.v1"
OFFICIAL="INSEE_RDF_UUID_codeINSEE_owl_sameAs"
UUID_SHA={
 "44066":"2a74630bb7d7e13460a47e8d8e93cdbb963ced97ddfee9c86a1ab2274648a93f",
 "85165":"82756c6fe552045c995b33d4e565b21dff065ced4d5dc552fb4fcc50a4b531e7",
 "85212":"cfff49e3a18ed56e5ea9aefd5a2265d504f839338dfdfdc4082549c10d73af9e",
}
def publier(audit,previous,cog,preflight):
 if (audit.get("schema")!=AUDIT_SCHEMA or audit.get("statut")!="RECETTE_NON_PUBLIANTE" or
     audit.get("bilan",{}).get("dossiers")!=3 or
     audit.get("bilan",{}).get("preuves_officielles_positives")!=3 or
     audit.get("bilan",{}).get("liens_PDL_deja_publies")!=1140 or
     audit.get("bilan",{}).get("nouveaux_ARK_publies")!=0 or
     audit.get("bilan",{}).get("geometries_modifiees")!=0):
  raise ValueError("Rapport de résolution UUID Insee altéré")
 if (previous.get("schema")!="adlfi.lieux.pactols.pdl.2026.public.v1" or
     previous.get("nombre_communes")!=1140 or
     previous.get("communes_a_instruire")!=88 or
     len(previous.get("alignements_Pactols_COG_valides_2026",[]))!=1140):
  raise ValueError("Index des 1140 couples PDL altéré")
 if cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026:
  raise ValueError("COG PDL inattendu")
 if (preflight.get("schema")!="adlfi.lieux.pdl.quatre_sans_exactmatch.2026.audit.v1" or
     preflight.get("bilan",{}).get("quatre_cas_sans_exactMatch")!=4):
  raise ValueError("Rapport initial des quatre exceptions absent")
 prev_arks={x["ark_pactols"] for x in previous["alignements_Pactols_COG_valides_2026"]}
 prev_codes={x["code_insee"] for x in previous["alignements_Pactols_COG_valides_2026"]}
 if len(prev_arks)!=1140 or len(prev_codes)!=1140 or set(CASES)&prev_codes:
  raise ValueError("Doublons avec les correspondances PDL précédentes")
 current={}
 for p in cog["periodes_com"]:
  if (p["typecom"]=="COM" and p["debut_inclus"]<="2026-01-01"
      and (not p["fin_exclue"] or p["fin_exclue"]>"2026-01-01")):
   if p["code_insee"] in current:raise ValueError("Code PDL dupliqué")
   current[p["code_insee"]]=p["libelle"]
 if len(current)!=1228:raise ValueError("Le COG PDL n'a pas 1228 communes en 2026")
 docs={x["code_COG_2026"]:x for x in audit["dossiers"]}
 candidates={x["code_COG_2026"]:x for x in preflight["dossiers"]}
 if set(docs)!=set(CASES):
  raise ValueError("Au moins une des trois résolutions manque")
 entries=[]
 for code,sp in CASES.items():
  d=docs[code];rdf=d["rdf_insee"];source=d["provenance_reponse"]
  pre=candidates[code]
  pref=[p for p in pre["candidats_Pactols"] if p["ark_pactols"]==sp["ark"]]
  if len(pref)!=1:raise ValueError("ARK lexical Pactols non unique : "+code)
  older=pref[0]
  if (older["exactMatch_INSEE"]!=[source_uri(code)] or older["deprecated"] or
      older["isReplacedBy"] or any(x in prev_arks for x in [sp["ark"]])):
   raise ValueError("URI UUID Pactols ou validité du concept modifiée : "+code)
  if (not d["validation_documentaire_possible_2026"] or
      d["validation_editoriale_prononcee"] is not False or
      d["publication"]!="AUCUNE" or
      d["code_COG_2026"]!=code or d["ARK_Pactols"]!=sp["ark"] or
      d["skos_exactMatch_Pactols_URI_UUID"]!=source_uri(code) or
      d["URI_INSEE_code_COG"]!=URI_BASE+code or
      d["nom_COG_2026"]!=sp["nom"] or
      d["date_effet_evenement_COG"]!=sp["date"] or
      d["portee_chronologique"]!="2026_SEULEMENT" or
      rdf["assertions_code_2026_concordantes"] is not True or
      rdf["codeINSEE"]!=[code] or rdf["owl_sameAs"]!=[URI_BASE+code] or
      rdf["type_RDF"]!=[GEO+"Commune"] or
      rdf["sujet_URI_UUID"]!=source_uri(code) or
      rdf["nom_officiel_dans_RDF"]!=[sp["nom"]] or
      rdf["sha256_du_corps_RDF"]!=UUID_SHA[code] or
      source["sha256"]!=UUID_SHA[code] or
      source["status_http"]!=200 or
      current[code]!=sp["nom"]):
   raise ValueError("La triple preuve officielle est insuffisante : "+code)
  if code in ("85165","85212"):
   if rdf["dates_metadonnees"]["created"]!=["2024-01-30T17:51:56.207524"]:
    raise ValueError("Création RDF après défusion divergente : "+code)
   prev_com=sorted((p for p in cog["periodes_com"] if
                    p["code_insee"]==code and p["typecom"]=="COM"),
                   key=lambda p:p["debut_inclus"])
   if len(prev_com)!=2 or prev_com[0]["fin_exclue"]!="2016-01-01" or prev_com[1]["debut_inclus"]!="2024-01-01":
    raise ValueError("Défusion COG 2016/2024 incohérente : "+code)
  if code=="44066":
   movements=[x for x in cog["lignes_mouvements_cog"] if
              x["mod"]=="10" and x["code_avant"]==code and
              x["code_apres"]==code and x["date_effet"]=="2023-01-01"]
   if len(movements)!=1 or movements[0]["libelle_avant"]!=sp["ancien"] or movements[0]["libelle_apres"]!=sp["nom"]:
    raise ValueError("Renommage COG Grandchamp non établi")
  entries.append({
   "code_insee":code,"libelle_COG_2026":sp["nom"],
   "libelle_pactols":next((p["texte"] for p in older["prefLabel"] if p["lang"]=="fr"),sp["nom"]),
   "ark_pactols":sp["ark"],
   "uri_insee_UUID_Pactols_exactMatch":source_uri(code),
   "uri_insee_courante_resolue":URI_BASE+code,
   "predicat_Pactols":"skos:exactMatch",
   "predicat_resolution_INSEE_code":"geo:codeINSEE",
   "predicat_resolution_INSEE_URI":"owl:sameAs",
   "nature_validation":OFFICIAL,
   "source_RDF_INSEE_sha256":UUID_SHA[code],
   "source_RDF_Pactols_sha256":RDF_SHA,
   "source_audit":"recette/lieux/PDL-TROIS-UUID-INSEE-RESOLUTIONS-2026.json",
   "date_evenement_COG":sp["date"],
   "type_evenement_COG":d["type_evenement_COG"],
   "millesime_validation":2026,
   "date_validation":"2026-11-18",
   "statut":"correspondance_PDL_UUID_resolue_par_INSEE_validee_2026",
   "portee_chronologique":"2026_SEULEMENT",
   "relations_historiques_inferees":0
  })
 if len(entries)!=3 or len(prev_codes|set(CASES))!=1143:
  raise ValueError("Compte des trois nouvelles identités incohérent")
 return {
  "schema":SCHEMA,"region":"pdl","millesime_cog":"2026-01-01",
  "source_audit":"recette/lieux/PDL-TROIS-UUID-INSEE-RESOLUTIONS-2026.json",
  "alignements_publies_precedemment":1140,
  "alignements_UUID_resolus_ajoutes":3,
  "total_alignements_PDL_2026":1143,
  "communes_PDL_COG_2026":1228,
  "communes_a_instruire":85,
  "cas_Rives_du_Fougerais_exclu":"85292",
  "geometries_ajoutees":0,"identites_historiques_inferees":0,
  "alignements_Pactols_COG_valides_2026":sorted(entries,key=lambda e:e["code_insee"])
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ("audit","previous","cog","preflight","sortie"):
  p.add_argument("--"+name,required=True,type=Path)
 a=p.parse_args()
 if a.sortie.exists():raise ValueError("Ne pas écraser une publication ou sa source")
 load=lambda f:json.loads(f.read_text(encoding="utf-8"))
 d=publier(load(a.audit),load(a.previous),load(a.cog),load(a.preflight))
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
 print("PDL_1143_UUID_PUBLICATION",json.dumps({"new":3,"total":1143,"exceptions":85,
  "rives_85292":"NON_PUBLIE","geometries":0},ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
