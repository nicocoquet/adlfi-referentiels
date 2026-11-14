#!/usr/bin/env python3
"""Index de recherche des 9 928 ARK attestés dans les XML AdlFI (recette).

Ne crée aucun lien Pactols-COG : seuls les 103 alignements éditoriaux PACA
déjà validés sont conservés. Les années d'opération ne datent ni les
noms administratifs ni les géométries.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,re,unicodedata
from pathlib import Path

SHA_SOURCES={
 "autorites":"878aa70f32d43313ea5bd36bbb30bbd6b57b4872ba2f68a5117ac6c35b6380b6",
 "occurrences":"b2e7332515c051e0c63e1fb29c840fa338aa85040fb2358a7df64d735b2942cd",
}
ARK=re.compile(r"^26678/(?:pcrt|crt)[A-Za-z0-9_-]+$")
SCHEMA="adlfi.lieux.pactols.xml.index.recette.v1"
AUT_REQUIRED=("ark_pactols","libelle_fr_xml","nombre_notices_distinctes","nombre_occurrences",
              "annees_operation_relevees","alignement_pilote","code_insee_2026_valide",
              "nom_cog_2026_valide")
OCC_REQUIRED=("ark_terminal","libelle_terminal_fr","libelle_original_index","notice_id")
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for data in iter(lambda:f.read(1048576),b""):h.update(data)
 return h.hexdigest()
def read(path,required):
 with Path(path).open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f,delimiter=";")
  if not set(required)<=set(reader.fieldnames or []):
   raise ValueError("Colonnes sources manquantes: "+str(path))
  return list(reader)
def normaliser(s):
 t=unicodedata.normalize("NFKD",(s or "").replace("œ","oe").replace("Œ","Oe"))
 return " ".join(re.sub("[^a-z0-9]+"," ", "".join(
  c for c in t if unicodedata.category(c)!="Mn").casefold()).split())
def serialiser(x):
 return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def produire(autorites,occurrences,sortie,controler_empreintes=True):
 paths={"autorites":Path(autorites),"occurrences":Path(occurrences)}
 if controler_empreintes:
  for name,path in paths.items():
   if sha(path)!=SHA_SOURCES[name]:
    raise ValueError("Extraction XML nationale non conforme à la version du 13 novembre : "+name)
 a=read(autorites,AUT_REQUIRED);o=read(occurrences,OCC_REQUIRED)
 if controler_empreintes and (len(a),len(o))!=(9928,30772):
  raise ValueError("Population d'extraction nationale modifiée")
 byark={r["ark_pactols"]:r for r in a}
 if len(byark)!=len(a) or any(not ARK.fullmatch(k) for k in byark):
  raise ValueError("ARK XML vides, dupliqués ou mal formés")
 variants=collections.defaultdict(set)
 for r in o:
  ark=r["ark_terminal"]
  if ark not in byark:raise ValueError("Occurrence sans autorité terminale: "+ark)
  for key in ("libelle_terminal_fr","libelle_original_index"):
   label=r[key].strip()
   if label:variants[ark].add(label)
 if set(variants)!=set(byark):
  raise ValueError("Autorité sans occurrence ou occurrence orpheline")
 validated=set();codes=set()
 rows=[]
 for ark,r in sorted(byark.items()):
  label=r["libelle_fr_xml"].strip()
  if not label:raise ValueError("ARK sans libellé français: "+ark)
  names=sorted(variants[ark]|{label},key=lambda v:(normaliser(v),v))
  statut=r["alignement_pilote"]
  if statut=="valide_pilote_paca_2026":
   code=r["code_insee_2026_valide"]
   if len(code)!=5 or not re.fullmatch("[0-9A-Z]{5}",code) or not r["nom_cog_2026_valide"]:
    raise ValueError("Alignement préexistant incomplet: "+ark)
   if code in codes:raise ValueError("Collision COG des validations existantes: "+code)
   codes.add(code);validated.add(ark)
   link={"type":"correspondance_communale_editoriale_existante",
         "code_insee":code,"libelle_cog":r["nom_cog_2026_valide"],
         "millesime":2026,"provenance":"pilote_PACA_validation_2026-10-18"}
  elif statut=="hors_pilote_non_instruit":
   if r["code_insee_2026_valide"] or r["nom_cog_2026_valide"]:
    raise ValueError("Code COG sur ARK sans validation: "+ark)
   link=None
  else:raise ValueError("Statut de rapprochement inconnu: "+ark)
  yrs=json.loads(r["annees_operation_relevees"] or "[]")
  if not isinstance(yrs,list) or any(type(y)!=int for y in yrs):
   raise ValueError("Années d'opérations incorrectes: "+ark)
  rows.append({"ark_pactols":ark,"libelle_documentaire":label,
     "formes_attestees_xml":names,
     "notice_distinctes":int(r["nombre_notices_distinctes"]),
     "occurrences_xml":int(r["nombre_occurrences"]),
     "annees_operation_xml":sorted(set(yrs)),
     "correspondance_cog_validee_2026":link,
     "statut":"validation_existante_paca" if link else "aucune_validation_cog",
     "geometrie_historique":None})
 if controler_empreintes and (len(rows),len(validated))!=(9928,103):
  raise ValueError("Les 103 validations PACA doivent être conservées sans ajout")
 if sum(r["occurrences_xml"] for r in rows)!=len(o):
  raise ValueError("Occurrences XML non concordantes")
 out=Path(sortie)
 if any((out/n).resolve() in {p.resolve() for p in paths.values()} for n in (
     "index-autorites-pactols-xml.json","rapport-index-pactols-xml.json")):
  raise ValueError("La sortie écraserait une source")
 out.mkdir(parents=True,exist_ok=True)
 data={"schema":SCHEMA,"etat":"recette_non_publiee",
       "perimetre":"concepts terminaux Pactols attestes dans XML AdlFI, non exhaustivite Pactols",
       "index_type":"recherche_lexicale_XML",
       "autorites":rows,
       "regles":["Recherche d'ARK et de noms XML indépendante de la date administrative.",
                 "Les années d'opération ne datent pas les noms ni les limites.",
                 "Aucun code Insee attribué par simple correspondance lexicale.",
                 "Seuls les 103 alignements du pilote PACA sont déjà validés.",
                 "Aucune nouvelle géométrie historique ou équivalence SKOS."],
       "source_sha256":{k:sha(v) for k,v in paths.items()}}
 raw=serialiser(data)
 (out/"index-autorites-pactols-xml.json").write_bytes(raw)
 rapport={"statut":"recette_non_publiee",
          "autorites_xml":len(rows),"occurrences_xml":len(o),
          "correspondances_cog_2026_deja_validees":len(validated),
          "autorites_sans_correspondance_validee":len(rows)-len(validated),
          "formes_documentaires_distinctes_par_ark":sum(len(r["formes_attestees_xml"]) for r in rows),
          "source_sha256":data["source_sha256"],
          "index_sha256":hashlib.sha256(raw).hexdigest(),
          "nouvelles_validations":0,"geometries_historiques":0}
 (out/"rapport-index-pactols-xml.json").write_bytes(serialiser(rapport))
 return rapport

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for key in ("autorites","occurrences","sortie"):
  p.add_argument("--"+key,type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(produire(**vars(a)),ensure_ascii=False,indent=2))
