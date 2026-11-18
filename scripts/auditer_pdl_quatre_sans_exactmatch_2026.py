#!/usr/bin/env python3
"""Pays de la Loire : quatre codes sans exactMatch Pactols reconnu en 2026.

Audit documentaire non validant : un renommage, deux communes rétablies
après défusion et une commune nouvelle. Les ARK lexicaux et liens non INSEE
sont des pistes, jamais des identités automatiquement publiées.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from auditer_pactols_polynesie_2026 import ARK, RDF, SKOS, OWL, DCT, XML, RDF_SHA, RDF_COMMIT, norm
from auditer_paca_trois_renommages_rdf_2026 import sha256

SCHEMA="adlfi.lieux.pdl.quatre_sans_exactmatch.2026.audit.v1"
CASES={
 "44066":{"nom":"Grandchamp-des-Fontaines","ancien":"Grandchamps-des-Fontaines",
          "date":"2023-01-01","mod":"10","type":"RENOMMAGE_CODE_CONSERVE",
          "ark_lexical":"26678/pcrt99dzcmxdhR",
          "insee":"https://www.insee.fr/fr/metadonnees/geographie/commune/44066-grandchamp-des-fontaines"},
 "85165":{"nom":"L'Oie","ancien":"L'Oie","date":"2024-01-01","mod":"21",
          "type":"RETABLISSEMENT_APRES_DEFUSION",
          "ark_lexical":"26678/pcrtsn4IGEserS",
          "insee":"https://www.insee.fr/fr/metadonnees/geographie/commune/85165-loie"},
 "85212":{"nom":"Sainte-Florence","ancien":"Sainte-Florence","date":"2024-01-01",
          "mod":"21","type":"RETABLISSEMENT_APRES_DEFUSION",
          "ark_lexical":None,
          "insee":"https://www.insee.fr/fr/metadonnees/geographie/commune/85212-sainte-florence"},
 "85292":{"nom":"Rives-du-Fougerais","ancien":"Thouarsais-Bouildroux",
          "date":"2024-01-01","mod":"32","type":"CREATION_COMMUNE_NOUVELLE",
          "ark_lexical":"26678/pcrtjr01c5sg25ngf5hq8898",
          "insee":"https://www.insee.fr/fr/metadonnees/geographie/commune/85292-rives-du-fougerais"},
}
EXACT_SOURCE="https://github.com/frantiq/PACTOLS/tree/69bf9697e24cefd645a69465bbd271702786285a"
def verifier_cog(cog:dict,previous:dict)->dict:
 if (cog.get("schema")!="adlfi.lieux.chronologie.4regions.public-recette.v1" or
     cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026):
  raise ValueError("Chronologie COG PDL inattendue")
 if (previous.get("schema")!="adlfi.lieux.pactols.pdl.2026.public.v1" or
     previous.get("nombre_communes")!=1140 or previous.get("communes_a_instruire")!=88 or
     len(previous.get("alignements_Pactols_COG_valides_2026",[]))!=1140):
  raise ValueError("Les 1140 alignements PDL existants ont changé")
 used={x["code_insee"] for x in previous["alignements_Pactols_COG_valides_2026"]}
 if len(used)!=1140 or set(CASES)&used:
  raise ValueError("L'un des quatre codes PDL est déjà validé")
 out={}
 for code,spec in CASES.items():
  periods=sorted([x for x in cog["periodes_com"] if x["code_insee"]==code and x["typecom"]=="COM"],
                  key=lambda x:x["debut_inclus"])
  if len(periods)!=2 or periods[0]["libelle"]!=spec["ancien"] or periods[1]["libelle"]!=spec["nom"] or periods[1]["debut_inclus"]!=spec["date"] or periods[1]["fin_exclue"] is not None:
   raise ValueError("Épisodes COG 2026 invalides : "+code)
  if spec["mod"]=="10":
   if periods[0]["fin_exclue"]!=spec["date"]:
    raise ValueError("Date de changement de nom incohérente")
  elif spec["mod"]=="21":
   if periods[0]["fin_exclue"]!="2016-01-01":
    raise ValueError("Ancienne date de fusion 2016 incohérente : "+code)
  elif periods[0]["fin_exclue"]!=spec["date"]:
   raise ValueError("Ancienne commune et nouvelle commune non distinguées")
  ev=[x for x in cog["lignes_mouvements_cog"]
      if x["code_apres"]==code and x["date_effet"]==spec["date"]
      and x["mod"]==spec["mod"]]
  if not ev or not any(x["libelle_apres"]==spec["nom"] for x in ev):
   raise ValueError("Mouvement officiel de transition absent : "+code)
  if spec["mod"]=="21" and not any(x["code_avant"]=="85084" for x in ev):
   raise ValueError("Rétablissement depuis Essarts en Bocage absent")
  if spec["mod"]=="32" and {x["code_avant"] for x in ev}!={"85041","85271","85292"}:
   raise ValueError("Fusion historique des trois communes du Fougerais altérée")
  out[code]={
   "code_COG_2026":code,"nom_COG_2026":spec["nom"],
   "ancienne_identite_ou_denomination":spec["ancien"],
   "date_effet":spec["date"],"type_transition":spec["type"],
   "mode_COG":spec["mod"],
   "periode_anterieure_COM":periods[0],
   "periode_actuelle_COM":periods[1],
   "evenements_COG":[{k:x.get(k) for k in ("id","code_avant","code_apres","date_effet","mod","libelle_avant","libelle_apres","typecom_avant","typecom_apres")} for x in ev],
   "url_fiche_officielle_INSEE":spec["insee"]
  }
 return out

def compatible(label,sp):
 name=norm(label)
 return any(name==norm(x) or name.startswith(norm(x)+" ")
            for x in (sp["nom"],sp["ancien"]))

def extraire_rdf(rdf:Path):
 if sha256(rdf)!=RDF_SHA:raise ValueError("RDF Pactols non conforme au snapshot épinglé")
 targets={sp["ark_lexical"] for sp in CASES.values() if sp["ark_lexical"]}
 found={}
 count=0
 parser=ET.iterparse(rdf,events=("start","end"))
 _,root=next(parser)
 if root.tag!=RDF+"RDF":raise ValueError("RDF mal formé")
 for event,el in parser:
  if event!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):continue
  match=ARK.fullmatch(el.get(RDF+"about",""))
  if not match:
   el.clear();root.clear();continue
  if el.tag==RDF+"Description" and not any(
      x.get(RDF+"resource")=="http://www.w3.org/2004/02/skos/core#Concept"
      for x in el.findall(RDF+"type")):
   el.clear();root.clear();continue
  count+=1
  ark=match.group(1)
  pref=[{"texte":(x.text or "").strip(),"lang":x.get(XML+"lang")}
        for x in el.findall(SKOS+"prefLabel") if (x.text or "").strip()]
  alt=[{"texte":(x.text or "").strip(),"lang":x.get(XML+"lang")}
       for x in el.findall(SKOS+"altLabel") if (x.text or "").strip()]
  fr=[x["texte"] for x in pref+alt if x["lang"] in ("fr","fr-FR",None)]
  labels={code:sorted({x for x in fr if compatible(x,sp)})
          for code,sp in CASES.items()}
  cases={code for code,v in labels.items() if v}
  if ark in targets or cases:
   if ark in found:raise ValueError("ARK dupliqué dans le RDF")
   def links(ns,tag):
    return sorted({x.get(RDF+"resource") or (x.text or "").strip()
                   for x in el.findall(ns+tag)
                   if x.get(RDF+"resource") or (x.text or "").strip()})
   exact=links(SKOS,"exactMatch")
   found[ark]={
     "ark_pactols":ark,"prefLabel":pref,"altLabel":alt,
     "definition":[{"texte":(x.text or "").strip(),"lang":x.get(XML+"lang")}
                   for x in el.findall(SKOS+"definition") if (x.text or "").strip()],
     "notes":[{"type":k,"texte":(x.text or "").strip()}
              for k in ("historyNote","changeNote","scopeNote")
              for x in el.findall(SKOS+k) if (x.text or "").strip()],
     "exactMatch":exact,
     "exactMatch_INSEE":[u for u in exact if u.lower().startswith(("http://id.insee.fr/geo/","https://id.insee.fr/geo/"))],
     "broader":links(SKOS,"broader"),
     "related":links(SKOS,"related"),
     "owl_sameAs":links(OWL,"sameAs"),
     "isReplacedBy":links(DCT,"isReplacedBy"),
     "replaces":links(DCT,"replaces"),
     "deprecated":any((x.text or "").strip().lower() in ("true","1")
                      for x in el.findall(OWL+"deprecated")),
     "labels_correspondant_a":labels
   }
  el.clear();root.clear()
 if count!=50556:
  raise ValueError("Nombre de concepts RDF inattendu : "+str(count))
 if not targets.issubset(found):
  raise ValueError("Les trois ARK lexicaux déjà repérés manquent du RDF")
 return {"total_concepts_rdf":count,"concepts":found}

def construire(cog,previous,rdf):
 history=verifier_cog(cog,previous)
 scanned=extraire_rdf(rdf)
 d=[]
 for code,spec in CASES.items():
  matches=[p for p in scanned["concepts"].values()
           if p["labels_correspondant_a"][code] or p["ark_pactols"]==spec["ark_lexical"]]
  matches.sort(key=lambda x:x["ark_pactols"])
  d.append({
   **history[code],
   "ark_lexical_signalé_audit_precedent":spec["ark_lexical"],
   "candidats_Pactols":matches,
   "nombre_de_candidats":len(matches),
   "decision_editoriale":"NON_PRISE",
   "publication":"AUCUNE",
  })
 return {
  "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
  "sources":{
   "pactols":{"commit":RDF_COMMIT,"sha256":RDF_SHA,"url":EXACT_SOURCE},
   "cog":{"fichier":"docs/data/lieux-chronologie/cog-pdl.json","millesime":"2026-01-01"},
   "publication_PDL_existante":"docs/data/lieux-chronologie/pactols-pdl-2026.json"
  },
  "bilan":{"communes_COG_PDL_2026":1228,
           "alignements_PDL_2026_conserves":1140,
           "exceptions_PDL_2026_conservees":88,
           "quatre_cas_sans_exactMatch":4,
           "concepts_RDF_examines":scanned["total_concepts_rdf"],
           "nouveaux_ARK_valides":0,"geometries_modifiees":0,
           "identites_historiques_inferrees":0},
  "dossiers":d,
  "limites":[
   "Un lien lexical vers un concept Pactols, même unique, n'est pas une validation de correspondance COG.",
   "Le cas des communes rétablies après défusion exige une décision temporelle : rétablissement ne signifie pas automatiquement conservation d'une autorité ontologique.",
   "Les noms identiques à plusieurs époques ne prouvent pas un exactMatch vers l'identité 2026.",
   "Aucune géométrie ancienne ni relation de succession d'ARK n'est inférée."
  ]
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for a in ("rdf","cog","publie","sortie"):p.add_argument("--"+a,type=Path,required=True)
 a=p.parse_args()
 if a.sortie.exists() or "docs" in a.sortie.resolve().parts:raise ValueError("Sortie neuve hors docs")
 result=construire(json.loads(a.cog.read_text(encoding="utf-8")),
                  json.loads(a.publie.read_text(encoding="utf-8")),a.rdf)
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("PDL_QUATRE_SANS_EXACTMATCH",json.dumps({
   **result["bilan"],
   "dossiers":[{"code":x["code_COG_2026"],"nom":x["nom_COG_2026"],
               "candidats":[{"ark":p["ark_pactols"],"pref":p["prefLabel"],
                             "exactMatch_INSEE":p["exactMatch_INSEE"]}
                            for p in x["candidats_Pactols"]]}
              for x in result["dossiers"]]
 },ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
