#!/usr/bin/env python3
"""Diagnostiquer l'URI UUID INSEE de Céreste sans fabriquer d'alignement.

Une réponse officielle positive exige un triplet au sujet de l'URI UUID avec
le prédicat <http://rdf.insee.fr/def/geo#codeINSEE> et la valeur "04045".
Les libellés et les identifiants agrégés par Wikidata sont seulement corroborants.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError, URLError
from xml.etree import ElementTree as ET

UUID="3cb419d3-63ba-4e7c-be42-2640cf521de8"
CODE="04045"
URI=f"http://id.insee.fr/geo/commune/{UUID}"
CODE_PRED="http://rdf.insee.fr/def/geo#codeINSEE"
SOURCES={
 "uri_canonique":URI,
 "endpoint":"https://rdf.insee.fr/sparql/",
 "insee_cog":"https://www.insee.fr/fr/metadonnees/geographie/commune/04045-cereste-en-luberon",
 "rdf_complet":"https://static.insee.fr/metadonnees/geo/cog.zip",
 "pactols":"26678/pcrtHxveTzUMik",
 "rdf_pactols_sha256":"3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7",
}
SCHEMA="adlfi.lieux.paca.cereste.uuid-insee.audit.v1"

def digest(data:bytes)->str:
 return hashlib.sha256(data).hexdigest()

def get(url:str,accept:str,max_bytes:int=1500000)->dict:
 req=Request(url,headers={"Accept":accept,"User-Agent":"AdlFI-Insee-URI-Audit/1.0 (research)","Cache-Control":"no-cache"})
 try:
  with urlopen(req,timeout=24) as response:
   data=response.read(max_bytes+1)
   return {"url":response.url,"status":response.status,
           "content_type":response.headers.get("Content-Type"),
           "octets_lus":len(data),"tronque":len(data)>max_bytes,
           "sha256_du_corps_lu":digest(data[:max_bytes]),"body":data[:max_bytes]}
 except HTTPError as e:
  return {"url":e.url,"status":e.code,"erreur":str(e)[:240],"body":b""}
 except (URLError,TimeoutError,OSError) as e:
  return {"url":url,"status":None,"erreur":str(e)[:400],"body":b""}

def preuve_directe(bindings:list[dict],subject:str=URI)->dict:
 if not isinstance(bindings,list):raise ValueError("Résultat SPARQL mal formé")
 relevant=[]
 for b in bindings:
  if not {"s","p","o"}.issubset(b):continue
  s=b["s"].get("value","");p=b["p"].get("value","");o=b["o"].get("value","")
  relevant.append({"s":s,"p":p,"o":o,"type":b["o"].get("type"),"lang":b["o"].get("xml:lang")})
 good=[x for x in relevant if x["s"]==subject and x["p"]==CODE_PRED
       and x["o"]==CODE and x["type"]=="literal"]
 other=[x for x in relevant if x["s"]==subject and x["p"]==CODE_PRED
        and (x["o"]!=CODE or x["type"]!="literal")]
 return {"preuve_directe_code_04045":bool(good) and not other,
         "valeurs_codeINSEE":[x["o"] for x in relevant if x["p"]==CODE_PRED],
         "nombre_triples":len(relevant),
         "triples":relevant[:180]}

def analyser_sparql()->list[dict]:
 sparql=("SELECT ?s ?p ?o WHERE { VALUES ?s { <"+URI+"> <"+URI.replace("http://","https://")+"> } "
         "?s ?p ?o } LIMIT 200")
 base=SOURCES["endpoint"]
 params=urlencode({"query":sparql,"format":"application/sparql-results+json"})
 results=[]
 for endpoint in (base,base.rstrip("/")):
  res=get(endpoint+"?"+params,"application/sparql-results+json")
  raw=res.pop("body")
  if res["status"]==200 and raw:
   try:
    doc=json.loads(raw.decode("utf-8"))
    res["preuve"]=preuve_directe(doc.get("results",{}).get("bindings",[]))
   except (ValueError,UnicodeError,KeyError) as e:
    res["analyse_erreur"]=str(e)[:240]
    res["corps_extrait"]=raw[:600].decode("utf-8","replace")
  else:
   res["corps_extrait"]=raw[:300].decode("utf-8","replace")
  results.append(res)
  if res.get("preuve",{}).get("preuve_directe_code_04045"):
   break
 return results

def analyser_rdf_direct()->list[dict]:
 data=[]
 for uri in (URI,URI.replace("http://","https://")):
  for accept in ("application/rdf+xml","text/turtle"):
   result=get(uri,accept)
   content=result.pop("body")
   if result["status"]==200 and content:
    result["corps_extrait"]=content[:2200].decode("utf-8","replace")
    if "rdf+xml" in (result.get("content_type") or "").lower():
     try:
      root=ET.fromstring(content)
      about="{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
      predicate="{http://rdf.insee.fr/def/geo#}codeINSEE"
      values=[(x.text or "").strip() for e in root.iter() if e.attrib.get(about)==URI
              for x in e.findall(predicate)]
      result["codeINSEE_du_sujet_UUID"]=values
      result["preuve_directe_code_04045"]=values==[CODE]
     except ET.ParseError as e:
      result["parse_error"]=str(e)[:160]
   data.append(result)
   if result.get("preuve_directe_code_04045"):
    return data
 return data

def main()->None:
 ap=argparse.ArgumentParser()
 ap.add_argument("--sortie",type=Path,required=True)
 args=ap.parse_args()
 if args.sortie.exists() or "docs" in args.sortie.resolve().parts:raise ValueError("Sortie de recette neuve hors docs")
 direct=analyser_rdf_direct()
 sparql=analyser_sparql()
 preuve_directe_officielle=any(x.get("preuve_directe_code_04045") for x in direct) or any(
  x.get("preuve",{}).get("preuve_directe_code_04045") for x in sparql)
 decision=("URI_UUID_CONFIRME_COG_04045_PAR_TRIPLET_INSEE"
           if preuve_directe_officielle else "CORRESPONDANCE_UUID_CODE_NON_DEMONTREE")
 report={"schema":SCHEMA,"statut":"AUDIT_NON_PUBLIANT","sources":SOURCES,
   "code_COG_2026_officiel":"04045",
   "libelle_COG_2026_officiel":"Céreste-en-Luberon",
   "preuve_par_triplet_insee":preuve_directe_officielle,
   "decision_documentaire":decision,
   "appels_dereferencement":direct,"appels_sparql":sparql,
   "limites":"Une erreur réseau ou l'absence de triples ne prouvent pas l'inexistence du lien. Ne pas déduire l'identité UUID à partir du nom ou du site Wikidata.",
   "nouvel_ARK_publie":False,"nouvel_etat_historique":False}
 args.sortie.parent.mkdir(parents=True,exist_ok=True)
 args.sortie.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print("INSEE_UUID_04045_AUDIT",json.dumps({
  "direct": [(x["status"],x.get("preuve_directe_code_04045",False)) for x in direct],
  "sparql":[(x["status"],x.get("preuve",{}).get("preuve_directe_code_04045",False)) for x in sparql],
  "preuve":preuve_directe_officielle,"decision":decision,"sha256":digest(args.sortie.read_bytes())
 },sort_keys=True))
if __name__=="__main__":main()
