#!/usr/bin/env python3
"""Audit non validant Pactols Lieux ↔ COG Wallis-et-Futuna (986, 98611–13).

Le territoire 986 et les CIR 98611/12/13 n'ont aucune commune.
Une URI INSEE typée 'commune', un concept d'île/royaume, ou un ancien code
98607 (Nouvelle-Calédonie) ne deviennent jamais un alignement administratif
par homonymie ou succession supposée. Source RDF épinglée par SHA.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,unicodedata,collections
import xml.etree.ElementTree as ET
from pathlib import Path
RDF="{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
SKOS="{http://www.w3.org/2004/02/skos/core#}"
OWL="{http://www.w3.org/2002/07/owl#}"
DCT="{http://purl.org/dc/terms/}"
XML="{http://www.w3.org/XML/1998/namespace}"
ARK=re.compile(r"^https?://ark\.frantiq\.fr/ark:/(26678/[A-Za-z0-9]+)$")
INSEE=re.compile(r"^https?://id\.insee\.fr/geo/([^?#]+?)/(\d{3,5})/?$")
TARGET={"986":("Wallis-et-Futuna","TERRITOIRE"),
 "98611":("Alo","CIRCONSCRIPTION"),"98612":("Sigave","CIRCONSCRIPTION"),
 "98613":("Uvea","CIRCONSCRIPTION")}
HISTORIC={"98609":"CODE_HISTORIQUE_WALLIS", "98607":"ANCIEN_CODE_NOUVELLE_CALEDONIE_NON_ADOPTE"}
RDF_SHA="3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
COG_SHA={
 "v_comer_2026.csv":"d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed",
 "v_commune_comer_2026.csv":"9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8"
}
def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for buf in iter(lambda:f.read(1048576),b""):h.update(buf)
 return h.hexdigest()
def lire(path):
 with path.open(encoding="utf-8-sig",newline="") as f:
  first=f.readline();f.seek(0)
  return list(csv.DictReader(f,delimiter=";" if first.count(";")>first.count(",") else ","))
def verifier_cog(folder:Path):
 for name,expected in COG_SHA.items():
  if digest(folder/name)!=expected:raise ValueError("COG 2026 non épinglé : "+name)
 terr={r["COMER"]:r["LIBELLE"] for r in lire(folder/"v_comer_2026.csv") if r["COMER"]=="986"}
 if terr!={"986":"Wallis-et-Futuna"}:raise ValueError("Territoire 986 non conforme")
 cir={r["COM_COMER"]:(r["LIBELLE"],r["NATURE_ZONAGE"])
   for r in lire(folder/"v_commune_comer_2026.csv") if r["COMER"]=="986"}
 if cir!={"98611":("Alo","CIR"),"98612":("Sigave","CIR"),"98613":("Uvea","CIR")}:
  raise ValueError("Trois CIR non communales attendues")
def norm(label):
 x=unicodedata.normalize("NFKD",label.casefold())
 return " ".join(re.findall(r"[a-z0-9]+","".join(c for c in x if not unicodedata.combining(c))))
def candidat_lexical_qualifie(label):
 x=norm(label)
 return x in {"wallis et futuna","wallis et futuna france",
              "alo wallis et futuna","sigave wallis et futuna","uvea wallis et futuna",
              "alo futuna","sigave futuna","uvea wallis"}
def scan_rdf(path:Path)->dict:
 got=collections.defaultdict(list);lex=[]
 unqualified=0;total=0
 parser=ET.iterparse(path,events=("start","end"))
 _,root=next(parser)
 if root.tag!=RDF+"RDF":raise ValueError("Source non RDF/XML")
 for ev,el in parser:
  if ev!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):continue
  m=ARK.fullmatch(el.get(RDF+"about",""))
  if not m:el.clear();root.clear();continue
  if el.tag==RDF+"Description" and not any(
    x.get(RDF+"resource")=="http://www.w3.org/2004/02/skos/core#Concept"
    for x in el.findall(RDF+"type")):
   el.clear();root.clear();continue
  total+=1
  pref=sorted({v.text.strip() for v in el.findall(SKOS+"prefLabel")
     if v.text and v.get(XML+"lang","").lower().startswith("fr")})
  alt=sorted({v.text.strip() for v in el.findall(SKOS+"altLabel")
     if v.text and v.get(XML+"lang","").lower().startswith("fr")})
  match=sorted({v.get(RDF+"resource","") for v in el.findall(SKOS+"exactMatch")
                if v.get(RDF+"resource","")})
  iuris=[{"uri":uri,"famille":m2.group(1),"code":m2.group(2)}
    for uri in match if (m2:=INSEE.fullmatch(uri))]
  codes=sorted(set(v["code"] for v in iuris if v["code"] in TARGET or v["code"] in HISTORIC))
  has_name=any(candidat_lexical_qualifie(v) for v in pref)
  dep=any((x.text or "").strip().lower() in ("true","1") for x in el.findall(OWL+"deprecated"))
  repl=bool(el.findall(DCT+"isReplacedBy"))
  if codes or has_name:
   item={"ark":m.group(1),"prefLabels_fr":pref,"altLabels_fr":alt,
         "exactMatch_INSEE_cibles":[x for x in iuris if x["code"] in TARGET or x["code"] in HISTORIC],
         "codes_cibles":codes,"deprecie":dep,"remplace":repl,
         "reserve_categorie_ile_royaume":any(
            norm(v).startswith(("ile ","royaume ")) for v in pref)}
   for code in codes:got[code].append(item)
   if has_name and not codes:lex.append(item)
  elif any(norm(v) in ("alo","sigave","uvea","wallis","futuna") for v in pref):
   unqualified+=1
  el.clear();root.clear()
 return {"explicites":{c:sorted(got[c],key=lambda x:x["ark"]) for c in [*TARGET,*HISTORIC]},
         "lexicaux_non_validants":sorted(lex,key=lambda x:x["ark"]),
         "homonymes_sans_contexte_qualifie":unqualified,"concepts_examines":total}
def rapport(rdf:Path,cog:Path)->dict:
 if digest(rdf)!=RDF_SHA:raise ValueError("Source RDF Pactols non épinglée")
 verifier_cog(cog)
 d=scan_rdf(rdf)
 lines=[]
 for code,(name,kind) in TARGET.items():
  explicit=d["explicites"][code]
  lines.append({"code_COG":code,"libelle_COG":name,"categorie_COG":kind,
   "nombre_concepts_exactMatch":len(explicit),"preuves_RDF_exactMatch":explicit,
   "statut":"A_INSTRUIRE_ONTOLOGIQUEMENT" if explicit else "AUCUN_EXACTMATCH_EXPLICITE",
   "alignement_publie":False,"geometrie_historique":None})
 historic=[{"code_COG":code,"categorie":label,"preuves_RDF_exactMatch":d["explicites"][code],
            "susceptible_d_equivalence_986_ou_CIR":False} for code,label in HISTORIC.items()]
 return {"schema":"adlfi.lieux.wallis-futuna.audit.pactols-cog2026.v1",
   "statut":"AUDIT_RDF_NON_VALIDANT",
   "source_Pactols":{"repository":"frantiq/PACTOLS",
       "commit":"69bf9697e24cefd645a69465bbd271702786285a",
       "fichier":"pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf",
       "sha256":RDF_SHA},
   "source_COG":{"edition":"2026-01-01","sha256":COG_SHA},
   "lignes":lines,"anciens_codes_exclus_de_validation":historic,
   "candidats_lexicaux_non_valides":d["lexicaux_non_validants"],
   "homonymes_sans_contexte_qualifie":d["homonymes_sans_contexte_qualifie"],
   "concepts_RDF_examines":d["concepts_examines"],
   "bilan":{"territoires":1,"circonscriptions":3,"communes":0,
       "codes_avec_exactMatch":sum(x["nombre_concepts_exactMatch"]>0 for x in lines),
       "concepts_exactMatch":sum(x["nombre_concepts_exactMatch"] for x in lines),
       "nouveaux_alignements_pactols":0,"nouvelles_geometries":0,
       "validations_autorisees_automatiquement":0}}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--rdf",required=True,type=Path)
 p.add_argument("--cog-dir",required=True,type=Path)
 p.add_argument("--sortie",required=True,type=Path)
 a=p.parse_args()
 if "docs" in a.sortie.resolve().parts or a.sortie.exists():
  raise ValueError("Refus de publier l'audit RDF ou d'écraser une sortie")
 d=rapport(a.rdf,a.cog_dir)
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"bilan":d["bilan"],"lignes":d["lignes"],
   "historiques":d["anciens_codes_exclus_de_validation"],
   "lexicaux":d["candidats_lexicaux_non_valides"][:12]},ensure_ascii=False))
if __name__=="__main__":main()
