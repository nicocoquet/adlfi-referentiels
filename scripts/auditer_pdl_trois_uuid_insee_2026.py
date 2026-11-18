#!/usr/bin/env python3
"""Résoudre trois UUID INSEE cités par Pactols dans les Pays de la Loire.

Source probante : RDF/XML servi par le point d'accès officiel Insee au sujet
précis de chaque URI UUID. Il faut codeINSEE, owl:sameAs du code et rdf:type
geo:Commune concordants. Deux phases : acquisition figée puis audit hors-ligne
reproductible, sans publication ni extrapolation de période historique.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

SCHEMA="adlfi.lieux.pdl.trois_uuid_insee.2026.audit.v1"
SOURCE_RDF="recette/lieux/PDL-QUATRE-SANS-EXACTMATCH-RDF-2026.json"
CASES={
 "44066":{"nom":"Grandchamp-des-Fontaines",
          "ancien":"Grandchamps-des-Fontaines",
          "ark":"26678/pcrt99dzcmxdhR",
          "uuid":"493ed29c-e150-4c2e-9880-f94d7002f1f5",
          "date":"2023-01-01","mod":"10"},
 "85165":{"nom":"L'Oie","ancien":"L'Oie",
          "ark":"26678/pcrtsn4IGEserS",
          "uuid":"c518cde7-3eed-4d8a-add5-d603a502dace",
          "date":"2024-01-01","mod":"21"},
 "85212":{"nom":"Sainte-Florence","ancien":"Sainte-Florence",
          "ark":"26678/pcrt3AUfSktjqj",
          "uuid":"80c14c7d-5f43-4927-8877-3031578366a5",
          "date":"2024-01-01","mod":"21"}
}
RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
GEO="http://rdf.insee.fr/def/geo#"
OWL="http://www.w3.org/2002/07/owl#"
DCT="http://purl.org/dc/terms/"
URI_BASE="http://id.insee.fr/geo/commune/"
MAX_BYTES=1_000_000

def sha256(b:bytes)->str:
 return hashlib.sha256(b).hexdigest()

def source_uri(code:str)->str:
 return URI_BASE+CASES[code]["uuid"]

def endpoint(code:str)->str:
 return "https://rdf.insee.fr/sparql?query="+quote(
    "describe<"+source_uri(code)+">",safe="")

def verifier_xml(data:bytes,code:str)->dict:
 if len(data)>MAX_BYTES:raise ValueError("RDF officiel trop volumineux")
 root=ET.fromstring(data)
 if root.tag!=f"{{{RDF}}}RDF":raise ValueError("Réponse reçue non RDF/XML")
 uri=source_uri(code)
 nodes=[n for n in root if n.attrib.get(f"{{{RDF}}}about")==uri]
 if len(nodes)!=1:raise ValueError("Sujet UUID officiel absent, ambigu ou redirigé")
 n=nodes[0]
 def literal(tag):
  return sorted({(e.text or "").strip() for e in n.findall(f"{{{GEO}}}"+tag)
                 if e.text and e.text.strip()})
 def resources(ns,key):
  return sorted({e.attrib.get(f"{{{RDF}}}resource","")
                 for e in n.findall(f"{{{ns}}}"+key)
                 if e.attrib.get(f"{{{RDF}}}resource")})
 types=resources(RDF,"type")
 sameas=resources(OWL,"sameAs")
 codes=literal("codeINSEE")
 noms=literal("nom")
 dates={
  k:sorted({(e.text or "").strip() for e in n.findall(f"{{{DCT}}}"+k) if e.text})
  for k in ("created","modified")
 }
 expected_uri=URI_BASE+code
 success=(types==[GEO+"Commune"] and codes==[code]
          and sameas==[expected_uri] and
          len(noms)==1 and noms[0].casefold().replace("’","'").replace("-"," ")
            in [CASES[code]["nom"].casefold().replace("’","'").replace("-"," "),
                CASES[code]["ancien"].casefold().replace("’","'").replace("-"," ")])
 return {
  "sujet_URI_UUID":uri,"type_RDF":types,
  "codeINSEE":codes,"owl_sameAs":sameas,
  "nom_officiel_dans_RDF":noms,"dates_metadonnees":dates,
  "assertions_code_2026_concordantes":success,
  "sha256_du_corps_RDF":sha256(data),
  "octets_corps_RDF":len(data),
  "nombre_noeuds_RDF":len(list(root))
 }

def collecter(repertoire:Path)->dict:
 if repertoire.exists() and any(repertoire.iterdir()):
  raise ValueError("Répertoire de sources déjà rempli : pas de réacquisition implicite")
 repertoire.mkdir(parents=True,exist_ok=True)
 sources={}
 for code in CASES:
  url=endpoint(code)
  last_error=None
  for attempt in range(3):
   try:
    req=Request(url,headers={
      "Accept":"application/rdf+xml",
      "User-Agent":"AdlFI-Referentiels/1.0 (scientific edition; INSEE RDF audit)",
      "Cache-Control":"no-cache"
    })
    with urlopen(req,timeout=30) as resp:
     data=resp.read(MAX_BYTES+1)
     content_type=resp.headers.get("Content-Type","")
     response_url=resp.geturl()
     status=resp.status
    if status!=200 or not response_url.startswith("https://rdf.insee.fr/"):
     raise ValueError("Réponse hors point d'accès INSEE")
    parsed=verifier_xml(data,code)
    fname=f"INSEE-UUID-PDL-{code}.rdf"
    (repertoire/fname).write_bytes(data)
    sources[code]={
      "fichier":fname,"requete":url,"reponse_url":response_url,
      "content_type":content_type,"status_http":status,
      "sha256":parsed["sha256_du_corps_RDF"],
      "octets":len(data)
    }
    break
   except (ET.ParseError,ValueError,HTTPError,URLError,TimeoutError,OSError) as exc:
    last_error=str(exc)[:300]
    if attempt<2:time.sleep(2*(attempt+1))
  else:
   raise RuntimeError(f"Impossible de recueillir la preuve RDF Insee pour {code}: {last_error}")
 report={"schema":"adlfi.lieux.pdl.trois_uuid_insee.sources.v1","sources":sources,
         "source_institutionnelle":"INSEE RDF, données expérimentales",
         "methode":"DESCRIBE sur URI UUID exact citée dans skos:exactMatch Pactols"}
 (repertoire/"provenance.json").write_text(
     json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 return report

def auditer(repertoire:Path,rapport_pactols:dict,cog:dict)->dict:
 provenance=json.loads((repertoire/"provenance.json").read_text(encoding="utf-8"))
 if (provenance.get("schema")!="adlfi.lieux.pdl.trois_uuid_insee.sources.v1" or
     set(provenance.get("sources",{}))!=set(CASES)):
  raise ValueError("Registre de provenance INSEE absent ou incomplet")
 if rapport_pactols.get("schema")!="adlfi.lieux.pdl.quatre_sans_exactmatch.2026.audit.v1":
  raise ValueError("Audit Pactols des quatre communes absent")
 dossiers={x["code_COG_2026"]:x for x in rapport_pactols["dossiers"]}
 if set(dossiers)!={"44066","85165","85212","85292"}:
  raise ValueError("Les quatre dossiers de recette Pactols ont changé")
 if (cog.get("schema")!="adlfi.lieux.chronologie.4regions.public-recette.v1" or
     cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026):
  raise ValueError("COG PDL absent ou altéré")
 out=[]
 for code,sp in CASES.items():
  src=provenance["sources"][code]
  path=repertoire/src["fichier"]
  b=path.read_bytes()
  if (src["sha256"]!=sha256(b) or src["octets"]!=len(b)
      or src["status_http"]!=200 or src["requete"]!=endpoint(code)):
   raise ValueError("Source INSEE non reproductible : "+code)
  row=verifier_xml(b,code)
  x=dossiers[code]
  matches=[m for m in x["candidats_Pactols"] if m["ark_pactols"]==sp["ark"]]
  if len(matches)!=1 or (matches[0]["exactMatch_INSEE"]!=[source_uri(code)]
                         or matches[0]["deprecated"] or matches[0]["isReplacedBy"]):
   raise ValueError("Lien exactMatch UUID Pactols altéré : "+code)
  hist=sorted([p for p in cog["periodes_com"] if p["code_insee"]==code and
               p["typecom"]=="COM"],key=lambda p:p["debut_inclus"])
  if len(hist)!=2 or hist[-1]["libelle"]!=sp["nom"] or hist[-1]["debut_inclus"]!=sp["date"] or hist[-1]["fin_exclue"] is not None:
   raise ValueError("Situation administrative 2026 non confirmée : "+code)
  if (x["date_effet"]!=sp["date"] or x["mode_COG"]!=sp["mod"] or
      x["decision_editoriale"]!="NON_PRISE" or x["publication"]!="AUCUNE"):
   raise ValueError("Recette initiale COG altérée : "+code)
  out.append({
   "code_COG_2026":code,
   "nom_COG_2026":sp["nom"],
   "date_effet_evenement_COG":sp["date"],
   "type_evenement_COG":x["type_transition"],
   "ARK_Pactols":sp["ark"],
   "skos_exactMatch_Pactols_URI_UUID":source_uri(code),
   "URI_INSEE_code_COG":URI_BASE+code,
   "rdf_insee":row,
   "provenance_reponse":src,
   "validation_documentaire_possible_2026":row["assertions_code_2026_concordantes"],
   "validation_editoriale_prononcee":False,
   "publication":"AUCUNE",
   "portee_chronologique":"2026_SEULEMENT"
  })
 return {
  "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIANTE",
  "source_Pactols":SOURCE_RDF,
  "source_COG":"docs/data/lieux-chronologie/cog-pdl.json",
  "source_INSEE_provenance":"provenance.json",
  "bilan":{
   "dossiers":3,"preuves_officielles_positives":sum(
      r["validation_documentaire_possible_2026"] for r in out),
   "nouveaux_ARK_publies":0,
   "liens_PDL_deja_publies":1140,
   "geometries_modifiees":0,
   "retrocessions_historiques_inferees":0
  },
  "dossiers":out,
  "limites":[
   "La confirmation de l'URI UUID par l'Insee est une preuve de code, pas une attribution rétroactive de l'ARK aux périodes antérieures.",
   "L'Oie et Sainte-Florence ont été rétablies comme COM en 2024 après une période COMD : ne pas écraser les épisodes antérieurs.",
   "Un renommage à code constant ne constitue pas une fusion.",
   "La source RDF de l'Insee est expérimentale ; chaque réponse est conservée par empreinte et assertions."
  ]
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--collecter",type=Path)
 p.add_argument("--sources",type=Path)
 p.add_argument("--pactols",type=Path)
 p.add_argument("--cog",type=Path)
 p.add_argument("--sortie",type=Path)
 a=p.parse_args()
 if a.collecter:
  print("PDL_UUID_INSEE_SOURCES",json.dumps(collecter(a.collecter),
    ensure_ascii=False,sort_keys=True))
 elif a.sources and a.pactols and a.cog and a.sortie:
  if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
   raise ValueError("Le rapport doit être nouveau, hors docs")
  report=auditer(a.sources,
    json.loads(a.pactols.read_text(encoding="utf-8")),
    json.loads(a.cog.read_text(encoding="utf-8")))
  a.sortie.parent.mkdir(parents=True,exist_ok=True)
  a.sortie.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                      encoding="utf-8")
  print("PDL_UUID_INSEE_AUDIT",json.dumps({
    "bilan":report["bilan"],
    "preuves":[{"code":r["code_COG_2026"],
                "valide":r["validation_documentaire_possible_2026"],
                "codeINSEE":r["rdf_insee"]["codeINSEE"],
                "nom":r["rdf_insee"]["nom_officiel_dans_RDF"]}
              for r in report["dossiers"]]},ensure_ascii=False,sort_keys=True))
 else:p.error("Fournir --collecter DIR, ou --sources DIR --pactols JSON --cog JSON --sortie JSON")
if __name__=="__main__":main()
