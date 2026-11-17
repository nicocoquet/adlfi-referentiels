#!/usr/bin/env python3
"""Audit non validant Pactols ↔ 97501/97502 au millésime COG 2026.

Un label homonyme, en particulier « Saint-Pierre », n'est pas un alignement.
Une URI INSEE explicite par skos:exactMatch est une preuve éditoriale, à
contrôler avec unicité, statut du concept et cohérence du prefLabel.
La source RDF Frantiq (commit et SHA) est strictement épinglée.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,re,unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

RDF="{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
SKOS="{http://www.w3.org/2004/02/skos/core#}"
OWL="{http://www.w3.org/2002/07/owl#}"
DCT="{http://purl.org/dc/terms/}"
XML="{http://www.w3.org/XML/1998/namespace}"
ARK=re.compile(r"^https?://ark\.frantiq\.fr/ark:/(26678/[A-Za-z0-9]+)$")
INSEE=re.compile(r"^https?://id\.insee\.fr/geo/commune/(\d{5})/?$")
CODES={"97501":"Miquelon-Langlade","97502":"Saint-Pierre"}
RDF_SHA="3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
COG_SHA="9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8"

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as stream:
  for block in iter(lambda:stream.read(1<<20),b""):
   h.update(block)
 return h.hexdigest()

def normaliser(t:str)->str:
 t=unicodedata.normalize("NFKD",t.casefold())
 t="".join(c for c in t if not unicodedata.combining(c))
 return " ".join(re.findall(r"[a-z0-9]+",t))

def label_compatible(code:str,label:str)->bool:
 name=normaliser(CODES[code])
 actual=normaliser(label)
 if actual==name:return True
 return code=="97502" and actual in (
   "saint pierre saint pierre et miquelon","saint pierre saint pierre et miquelon france",
 )

def candidats_rdf(path:Path)->dict:
 exact=collections.defaultdict(list)
 lexical=[]
 plain_saint_pierre=0
 total=0
 parser=ET.iterparse(path,events=("start","end"))
 _,root=next(parser)
 if root.tag!=RDF+"RDF":raise ValueError("RDF/XML Pactols attendu")
 for event,el in parser:
  if event!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):
   continue
  m=ARK.fullmatch(el.get(RDF+"about",""))
  if not m:
   el.clear();root.clear();continue
  if el.tag==RDF+"Description" and not any(
    x.get(RDF+"resource")=="http://www.w3.org/2004/02/skos/core#Concept"
    for x in el.findall(RDF+"type")
  ):
   el.clear();root.clear();continue
  total+=1
  labels=sorted({x.text.strip() for x in el.findall(SKOS+"prefLabel")
     if x.text and x.get(XML+"lang","").lower().startswith("fr")})
  alt=sorted({x.text.strip() for x in el.findall(SKOS+"altLabel")
     if x.text and x.get(XML+"lang","").lower().startswith("fr")})
  uris=sorted({x.get(RDF+"resource","") for x in el.findall(SKOS+"exactMatch")
               if x.get(RDF+"resource","")})
  codes=sorted({mm.group(1) for u in uris if (mm:=INSEE.fullmatch(u))})
  deprecated=any((x.text or "").strip().lower() in ("true","1")
                 for x in el.findall(OWL+"deprecated"))
  replaced=bool(el.findall(DCT+"isReplacedBy"))
  info={"ark":m.group(1),"prefLabels_fr":labels,"altLabels_fr":alt,
        "insee_exactmatch_codes":codes,"insee_exactmatch_uris":[
          u for u in uris if u.startswith(("http://id.insee.fr/","https://id.insee.fr/"))],
        "deprecie":deprecated,"remplace":replaced}
  for code in CODES:
   if code in codes:exact[code].append(info)
  plain_saint_pierre+=int(any(normaliser(x)=="saint pierre" for x in labels)
                          and not any(x in codes for x in CODES))
  if any(label_compatible(code,label) and (
       code=="97501" or normaliser(label)!="saint pierre")
       for code in CODES for label in labels) and not any(code in codes for code in CODES):
   lexical.append(info)
  el.clear();root.clear()
 return {"explicites":{c:sorted(exact[c],key=lambda x:x["ark"]) for c in CODES},
         "lexicaux_qualifies":sorted(lexical,key=lambda x:x["ark"]),
         "homonymes_prefLabel_saint_pierre_non_retenus":plain_saint_pierre,
         "concepts_rdf_inspectes":total}

def verifier_cog(path:Path)->None:
 if sha(path)!=COG_SHA:raise ValueError("COG 2026 différent du snapshot épinglé")
 with path.open(encoding="utf-8-sig",newline="") as f:
  header=f.readline();f.seek(0)
  rows=list(csv.DictReader(f,delimiter=";" if header.count(";")>header.count(",") else ","))
 now={r["COM_COMER"]:r["LIBELLE"] for r in rows
      if r["COMER"]=="975" and r["NATURE_ZONAGE"]=="COM"}
 if now!=CODES:raise ValueError("Codes ou libellés SPM COG 2026 modifiés")

def rapport(rdf:Path,cog:Path)->dict:
 if sha(rdf)!=RDF_SHA:raise ValueError("Pactols RDF différent du commit épinglé")
 verifier_cog(cog)
 scan=candidats_rdf(rdf)
 lines=[]
 for code,name in CODES.items():
  items=scan["explicites"][code]
  qualifies=[x for x in items if len(items)==1 and
   x["insee_exactmatch_codes"]==[code] and len(x["prefLabels_fr"])==1 and
   label_compatible(code,x["prefLabels_fr"][0]) and
   not x["deprecie"] and not x["remplace"]]
  lines.append({"code_insee":code,"nom_COG_2026":name,
    "preuve_exactMatch_dans_RDF":items,
    "statut":"ELIGIBLE_A_VALIDATION_EDITORIALE" if len(qualifies)==1 else (
       "A_INSTRUIRE" if items else "AUCUN_EXACTMATCH_ATTESTE"),
    "nombre_exactMatch":len(items),"geometry_historique":None,
    "decision_publication":"NON_PUBLIE"})
 return {
  "schema":"adlfi.lieux.spm.audit.pactols-cog2026.v1",
  "statut":"RECETTE_NON_VALIDANTE",
  "source_rdf":{"repository":"frantiq/PACTOLS",
   "commit":"69bf9697e24cefd645a69465bbd271702786285a",
   "fichier":"pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf",
   "sha256":RDF_SHA},
  "source_cog":{"fichier":"v_commune_comer_2026.csv","sha256":COG_SHA,
    "url":"https://www.insee.fr/fr/information/8740222"},
  "communes_COG_2026":2,
  "lignes":lines,
  "concepts_RDF_inspectes":scan["concepts_rdf_inspectes"],
  "homonymes_saint_pierre_non_retenus":scan["homonymes_prefLabel_saint_pierre_non_retenus"],
  "candidats_lexicaux_qualifies_non_valides":scan["lexicaux_qualifies"],
  "bilan":{"candidats_explicites":sum(x["nombre_exactMatch"] for x in lines),
    "codes_eligibles":sum(x["statut"]=="ELIGIBLE_A_VALIDATION_EDITORIALE" for x in lines),
    "codes_a_instruire":sum(x["statut"]=="A_INSTRUIRE" for x in lines),
    "codes_sans_exactMatch":sum(x["statut"]=="AUCUN_EXACTMATCH_ATTESTE" for x in lines),
    "validations_publiees":0,"geometries_historiques_publiees":0}
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--pactols-rdf",type=Path,required=True)
 p.add_argument("--cog",type=Path,required=True)
 p.add_argument("--sortie",type=Path,required=True)
 a=p.parse_args()
 if "docs" in a.sortie.resolve().parts or a.sortie.exists():
  raise ValueError("Rapport d'audit hors docs/ seulement, sans écrasement")
 obj=rapport(a.pactols_rdf,a.cog)
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"bilan":obj["bilan"],"lignes":obj["lignes"],
                   "candidats_lexicaux":obj["candidats_lexicaux_qualifies_non_valides"],
                   "homonymes":obj["homonymes_saint_pierre_non_retenus"]},
                   ensure_ascii=False,indent=2))
if __name__=="__main__":main()
