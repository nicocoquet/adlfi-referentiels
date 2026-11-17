#!/usr/bin/env python3
"""Audit Pactols-Lieux ↔ 48 communes COG de Polynésie française, sans publication.

Source INSEE COG 2026 six CSV SHA-256 (auditer_cog_polynesie_2026.py) ;
source RDF Frantiq Lieux th17 du 22/07/2026 épinglée SHA-256.
Les 98 communes associées ISPF, les îles/atolls et le code historique
Clipperton 98799 ne sont pas alignés automatiquement aux 48 communes.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,unicodedata
from pathlib import Path
import xml.etree.ElementTree as ET
from auditer_cog_polynesie_2026 import SHAS as COG_SHAS,analyser as analyser_cog,sha

RDF="{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
SKOS="{http://www.w3.org/2004/02/skos/core#}"
OWL="{http://www.w3.org/2002/07/owl#}"
DCT="{http://purl.org/dc/terms/}"
XML="{http://www.w3.org/XML/1998/namespace}"
ARK=re.compile(r"^https?://ark\.frantiq\.fr/ark:/(26678/[A-Za-z0-9]+)$")
INSEE=re.compile(r"^https?://id\.insee\.fr/geo/([^?#]+?)/(\d{3,6})/?$")
RDF_SHA="3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
RDF_COMMIT="69bf9697e24cefd645a69465bbd271702786285a"

def norm(label:str)->str:
 s=unicodedata.normalize("NFKD",label.casefold())
 s="".join(c for c in s if not unicodedata.combining(c))
 return " ".join(re.findall(r"[a-z0-9]+",s))

def label_compatible(cog:str,label:str)->bool:
 target=norm(cog);value=norm(label)
 if not target or not value:return False
 if value==target:return True
 # Une précision géographique au sens "nom (Polynésie/Tahiti/Tuamotu)"
 # reste candidate ; aucune similitude lexicale ne crée une validation.
 if label.strip().startswith(cog+" (") and label.rstrip().endswith(")"):
  return True
 return False

def type_confusion(pref:list[str])->bool:
 return any(norm(label).startswith(("ile ","ilot ","atoll ","archipel ",
                                     "royaume ","district ")) for label in pref)

def analyser_rdf(path:Path,communes:dict[str,str])->dict:
 explicit=collections.defaultdict(list)
 autre=collections.defaultdict(list)
 lexicals=collections.defaultdict(list)
 examined=0
 normalized=collections.defaultdict(list)
 for code,name in communes.items():normalized[norm(name)].append(code)
 parser=ET.iterparse(path,events=("start","end"))
 _,root=next(parser)
 if root.tag!=RDF+"RDF":raise ValueError("Source non RDF/XML")
 for event,el in parser:
  if event!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):continue
  ark=ARK.fullmatch(el.get(RDF+"about",""))
  if not ark:el.clear();root.clear();continue
  if el.tag==RDF+"Description" and not any(
      x.get(RDF+"resource")=="http://www.w3.org/2004/02/skos/core#Concept"
      for x in el.findall(RDF+"type")):
   el.clear();root.clear();continue
  examined+=1
  pref=sorted({x.text.strip() for x in el.findall(SKOS+"prefLabel")
      if x.text and x.get(XML+"lang","").lower().startswith("fr")})
  alt=sorted({x.text.strip() for x in el.findall(SKOS+"altLabel")
      if x.text and x.get(XML+"lang","").lower().startswith("fr")})
  exact=sorted({x.get(RDF+"resource","") for x in el.findall(SKOS+"exactMatch")
                if x.get(RDF+"resource","")})
  insee=sorted([{"uri":x,"famille":m.group(1),"code":m.group(2)}
                for x in exact if (m:=INSEE.fullmatch(x))],
               key=lambda y:(y["code"],y["famille"],y["uri"]))
  current=sorted({x["code"] for x in insee
      if x["famille"]=="commune" and x["code"] in communes})
  historical=sorted({x["code"] for x in insee
      if x["code"] in ("987","98799")})
  deprec=any((x.text or "").strip().lower() in ("true","1")
             for x in el.findall(OWL+"deprecated"))
  replacement=bool(el.findall(DCT+"isReplacedBy"))
  lex=sorted({code for x in pref for code in normalized.get(norm(x),[])})
  if current or historical or lex:
   row={"ark":ark.group(1),"prefLabels_fr":pref,"altLabels_fr":alt,
       "insee_exactMatch":insee,
       "codes_communaux_cites":current,
       "deprecie":deprec,"remplace":replacement,
       "risque_ile_atoll_autre_type":type_confusion(pref)}
   for code in current:explicit[code].append(row)
   for code in historical:autre[code].append(row)
   if not current and not historical:
    for code in lex:lexicals[code].append({
       "ark":row["ark"],"prefLabels_fr":pref,"exactMatch_INSEE":insee,
       "statut":"HOMONYMIE_POSSIBLE_NON_VALIDANTE"})
  el.clear();root.clear()
 return {"explicites":{c:sorted(explicit[c],key=lambda x:x["ark"]) for c in communes},
   "anciens_ou_territoriaux":{c:sorted(autre[c],key=lambda x:x["ark"])
      for c in ("987","98799")},
   "lexicaux_sans_exactMatch_987":{c:sorted(lexicals[c],key=lambda x:x["ark"])
      for c in communes if lexicals[c]},
   "concepts_RDF_examines":examined}

def rapport(rdf:Path,cog_dir:Path,index_public:Path)->dict:
 if sha(rdf)!=RDF_SHA:raise ValueError("RDF Pactols non identique à la version épinglée")
 cog=analyser_cog(cog_dir,index_public)
 names={x["code"]:x["libelle"] for x in cog["communes_2026"]}
 result=analyser_rdf(rdf,names)
 rows=[]
 for code,name in sorted(names.items()):
  hits=result["explicites"][code]
  if not hits:
   status="AUCUN_EXACTMATCH_RDF"
  elif len(hits)!=1:
   status="A_INSTRUIRE_CANDIDATS_MULTIPLES"
  else:
   p=hits[0]
   uri=[x for x in p["insee_exactMatch"] if x["famille"]=="commune"
         and x["code"]==code]
   others=[x for x in p["insee_exactMatch"] if
          not (x["famille"]=="commune" and x["code"]==code)]
   compatible=any(label_compatible(name,label) for label in p["prefLabels_fr"])
   if p["deprecie"] or p["remplace"] or p["risque_ile_atoll_autre_type"] or (
       not compatible or len(uri)!=1 or others or len(p["codes_communaux_cites"])!=1):
    status="A_INSTRUIRE_ONTOLOGIE_LIBELLE_OU_MULTIPLICITE"
   else:
    status="ELIGIBLE_A_ARBITRAGE_COMMUNE_2026"
  rows.append({"code_COG":code,"libelle_COG":name,"categorie_COG":"COMMUNE_COMER",
   "preuves_RDF_exactMatch":hits,"nombre_concepts_exactMatch":len(hits),
   "candidats_lexicaux_non_validants":result["lexicaux_sans_exactMatch_987"].get(code,[]),
   "statut":status,"alignement_publie":False})
 recap=collections.Counter(x["statut"] for x in rows)
 return {
  "schema":"adlfi.lieux.polynesie.audit.pactols-cog2026.v1",
  "statut":"RECETTE_PACTOLS_NON_VALIDANTE",
  "source_rdf":{"repo":"frantiq/PACTOLS","commit":RDF_COMMIT,
     "fichier":"pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf",
     "sha256":RDF_SHA},
  "source_COG":{"edition":"2026-01-01","sha256":COG_SHAS},
  "codes_communes_2026":rows,
  "concepts_vers_territoire_987":result["anciens_ou_territoriaux"]["987"],
  "concepts_vers_Clipperton_historique_98799":result["anciens_ou_territoriaux"]["98799"],
  "concepts_RDF_examines":result["concepts_RDF_examines"],
  "bilan":{"communes_COG":48,
    "codes_avec_exactMatch":sum(x["nombre_concepts_exactMatch"]>0 for x in rows),
    "concepts_exactMatch_total":sum(x["nombre_concepts_exactMatch"] for x in rows),
    "statuts":dict(sorted(recap.items())),
    "codes_avec_candidats_lexicaux":sum(bool(x["candidats_lexicaux_non_validants"])
      for x in rows),
    "comptage_communes_associees_ISPF_non_inferre":98,
    "validations_automatiques":0,"nouveaux_alignements_publies":0,
    "contours_historiques_publies":0,
    "correspondances_anciennes_ou_associees_inferrees":0}
 }
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--rdf",type=Path,required=True)
 p.add_argument("--cog-dir",type=Path,required=True)
 p.add_argument("--index-public",type=Path,required=True)
 p.add_argument("--sortie",type=Path,required=True)
 a=p.parse_args()
 if "docs" in a.sortie.resolve().parts or a.sortie.exists():
  raise ValueError("Écriture de recette hors docs et sans écrasement uniquement")
 r=rapport(a.rdf,a.cog_dir,a.index_public)
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(r,sort_keys=True,indent=2,ensure_ascii=False)+"\n",
   encoding="utf-8")
 print(json.dumps({"bilan":r["bilan"],
   "exactMatch_codes":[{"code":x["code_COG"],"libelle":x["libelle_COG"],
      "statut":x["statut"],
      "ark":[v["ark"] for v in x["preuves_RDF_exactMatch"]]}
     for x in r["codes_communes_2026"] if x["nombre_concepts_exactMatch"]],
   "territoire_987":r["concepts_vers_territoire_987"],
   "Clipperton_98799":r["concepts_vers_Clipperton_historique_98799"]
 },ensure_ascii=False))
if __name__=="__main__":main()
