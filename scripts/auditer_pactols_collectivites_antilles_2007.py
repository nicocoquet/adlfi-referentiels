#!/usr/bin/env python3
"""Audit non validant des six codes historiques / COM antillais dans Pactols RDF.

97123/97127 = anciennes communes, 977/978 = collectivités,
97701/97801 = codification applicative cinq positions (pas communes).
Un skos:exactMatch RDF est extrait, mais JAMAIS converti en alignement
automatique sans contrôle de catégorie ontologique et de millésime.
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
CODE={"97123":("Saint-Barthélemy","ANCIENNE_COMMUNE"),
 "97127":("Saint-Martin","ANCIENNE_COMMUNE"),
 "977":("Saint-Barthélemy","COLLECTIVITE"),
 "978":("Saint-Martin","COLLECTIVITE"),
 "97701":("Saint-Barthélemy","CODE_APPLICATION_NON_COMMUNAL"),
 "97801":("Saint-Martin","CODE_APPLICATION_NON_COMMUNAL")}
RDF_SHA="3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
COG_SHA="9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8"
ARK=re.compile(r"^https?://ark\.frantiq\.fr/ark:/(26678/[A-Za-z0-9]+)$")
URI=re.compile(r"^https?://id\.insee\.fr/geo/([^?#]+?)/(\d{3,5})/?$")
def empreinte(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for buf in iter(lambda:f.read(1<<20),b""):h.update(buf)
 return h.hexdigest()
def normaliser(s):
 s=unicodedata.normalize("NFKD",s.casefold())
 s="".join(c for c in s if not unicodedata.combining(c))
 return " ".join(re.findall(r"[a-z0-9]+",s))
def cible_lexicale(label):
 x=normaliser(label)
 # Les seules ressemblances non ambiguës sont des CANDIDATS, jamais des preuves.
 return "saint barthelemy" in x or (
  "saint martin" in x and any(z in x for z in (
   "guadeloupe","antilles","outre mer","collectivite","saint martin et")))
def verifier_cog(path):
 if empreinte(path)!=COG_SHA:raise ValueError("Table COMER 2026 COG non épinglée")
 with path.open(encoding="utf-8-sig",newline="") as f:
  first=f.readline();f.seek(0)
  rows=list(csv.DictReader(f,delimiter=";" if first.count(";")>first.count(",") else ","))
 apps={x["COM_COMER"]:(x["COMER"],x["LIBELLE"],x["NATURE_ZONAGE"]) for x in rows
  if x["COM_COMER"] in ("97701","97801")}
 if apps!={"97701":("977","Saint-Barthélemy","COM"),
           "97801":("978","Saint-Martin","COM")}:
  raise ValueError("Codes d'application 5 positions COG incompatibles")

def analyser_rdf(path):
 explicit=collections.defaultdict(list)
 lexical=[]
 checked=0
 parser=ET.iterparse(path,events=("start","end"))
 _,root=next(parser)
 if root.tag!=RDF+"RDF":raise ValueError("Fichier Pactols non RDF/XML")
 for ev,el in parser:
  if ev!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):continue
  m=ARK.fullmatch(el.get(RDF+"about",""))
  if not m:el.clear();root.clear();continue
  if el.tag==RDF+"Description" and not any(
     x.get(RDF+"resource")=="http://www.w3.org/2004/02/skos/core#Concept"
     for x in el.findall(RDF+"type")):
    el.clear();root.clear();continue
  checked+=1
  pref=sorted({x.text.strip() for x in el.findall(SKOS+"prefLabel")
               if x.text and x.get(XML+"lang","").lower().startswith("fr")})
  alt=sorted({x.text.strip() for x in el.findall(SKOS+"altLabel")
               if x.text and x.get(XML+"lang","").lower().startswith("fr")})
  exact=sorted({x.get(RDF+"resource","") for x in el.findall(SKOS+"exactMatch")
                if x.get(RDF+"resource","")})
  insee=[(u,match.group(1),match.group(2))
   for u in exact if (match:=URI.fullmatch(u)) is not None]
  matched=sorted({c for _,_,c in insee if c in CODE})
  dep=any((x.text or "").strip().lower() in ("true","1")
          for x in el.findall(OWL+"deprecated"))
  repl=bool(el.findall(DCT+"isReplacedBy"))
  if matched or any(cible_lexicale(v) for v in pref):
   item={"ark":m.group(1),"prefLabels_fr":pref,"altLabels_fr":alt,
     "exactMatch_INSEE_cibles":[{"uri":u,"famille":kind,"code":c}
                                 for u,kind,c in insee if c in CODE],
     "codes_INSEE_cibles":matched,"deprecie":dep,"remplace":repl}
   for c in matched:explicit[c].append(item)
   if not matched and any(cible_lexicale(v) for v in pref):
    lexical.append(item)
  el.clear();root.clear()
 return {"codes":{c:sorted(explicit[c],key=lambda x:x["ark"]) for c in CODE},
         "lexicaux_non_validants":sorted(lexical,key=lambda x:x["ark"]),
         "concepts_examines":checked}

def rapport(rdf,cog):
 if empreinte(rdf)!=RDF_SHA:raise ValueError("RDF Pactols non identique au commit épinglé")
 verifier_cog(cog)
 d=analyser_rdf(rdf)
 rows=[]
 for code,(name,typ) in CODE.items():
  exact=d["codes"][code]
  rows.append({"code_COG":code,"libelle_COG":name,"categorie_COG":typ,
   "preuves_RDF_exactMatch":exact,"nombre_concepts_exactMatch":len(exact),
   "statut":"A_INSTRUIRE_ONTOLOGIQUEMENT" if exact else "AUCUN_LIEN_EXPLICITE_RDF",
   "lien_pactols_publie_par_audit":False})
 return {"schema":"adlfi.lieux.antilles2007.audit.pactols-cog2026.v1",
  "statut":"AUDIT_NON_VALIDANT_PAR_CATEGORIE_ADMINISTRATIVE",
  "source_rdf":{"repository":"frantiq/PACTOLS","commit":"69bf9697e24cefd645a69465bbd271702786285a",
   "fichier":"pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf",
   "sha256":RDF_SHA},
  "source_cog":{"fichier":"v_commune_comer_2026.csv","sha256":COG_SHA},
  "codes_instruits":rows,
  "candidats_lexicaux_non_valides":d["lexicaux_non_validants"],
  "concepts_RDF_examines":d["concepts_examines"],
  "bilan":{"codes_verifies":len(CODE),
   "liens_RDF_explicites":sum(x["nombre_concepts_exactMatch"] for x in rows),
   "codes_avec_exactMatch":sum(bool(x["nombre_concepts_exactMatch"]) for x in rows),
   "candidats_lexicaux":len(d["lexicaux_non_validants"]),
   "nouveaux_alignements_pactols":0,"nouveaux_contours_historiques":0,
   "validations_autorisees_automatiquement":0}
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--rdf",type=Path,required=True)
 p.add_argument("--cog",type=Path,required=True)
 p.add_argument("--sortie",type=Path,required=True)
 args=p.parse_args()
 if "docs" in args.sortie.resolve().parts or args.sortie.exists():
  raise ValueError("Ecriture interdite sous docs/ ou sur une sortie existante")
 out=rapport(args.rdf,args.cog)
 args.sortie.parent.mkdir(parents=True,exist_ok=True)
 args.sortie.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"bilan":out["bilan"],"codes":out["codes_instruits"],
   "lexicaux":out["candidats_lexicaux_non_valides"][:20]},ensure_ascii=False))
if __name__=="__main__":main()
