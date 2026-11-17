#!/usr/bin/env python3
"""Certification de publication des 48 exactMatch Pactols–COG de Polynésie.

Trois preuves indépendantes :
  1) Export RDF Frantiq Lieux identifié par SHA-256 ;
  2) 6 CSV officiels INSEE COG 2026 identifiés par SHA-256 ;
  3) Registre éditorial versionné VALIDE_ADLFI_2026.
Le rendu public est reproduit exactement à partir de l'index antérieur,
en appliquant le registre via le constructeur historique du projet.

La validation des identifiants 2026 ne qualifie ni contours, ni communes
associées ISPF, ni identité juridique rétroactive.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from auditer_cog_polynesie_2026 import SHAS,read,sha
from auditer_pactols_polynesie_2026 import (RDF_SHA,analyser_rdf,label_compatible,
                                             type_confusion)
from extraire_index_public_outremer_2026 import appliquer_validations

COLS=["code_insee","libelle_COG_2026","ark_pactols","uri_insee",
      "predicat_source","concept_deprecie","statut_validation",
      "portee_COG","prefLabel_fr_pactols"]
CODE=set(f"987{i}" for i in range(11,59))
SOURCE="recette/lieux/POLYNESIE-VALIDATIONS-PACTOLS-COG-2026.csv"
def verifier(registre:Path,rdf:Path,folder:Path,socle:Path,public:Path,
             manifest:Path,chronologie:Path)->dict:
 if sha(rdf)!=RDF_SHA:raise ValueError("RDF Frantiq non épinglé")
 for name,digest in SHAS.items():
  if sha(folder/name)!=digest:raise ValueError("Table COG 2026 non épinglée : "+name)
 current=read(folder/"v_commune_comer_2026.csv")
 poly=[r for r in current if r["COMER"]=="987"]
 if len(poly)!=48 or any(r["NATURE_ZONAGE"]!="COM" for r in poly):
  raise ValueError("Le COG 2026 ne décrit pas exactement 48 communes COM")
 names={r["COM_COMER"]:r["LIBELLE"] for r in poly}
 if set(names)!=CODE:raise ValueError("Codes de communes 987 différents du COG")
 with registre.open(encoding="utf-8-sig",newline="") as file:
  reader=csv.DictReader(file,delimiter=";")
  if reader.fieldnames!=COLS:raise ValueError("Colonnes du registre non conformes")
  decisions=list(reader)
 if len(decisions)!=48 or {r["code_insee"] for r in decisions}!=CODE:
  raise ValueError("Le registre ne comporte pas 48 codes communaux uniques")
 rdf_records=analyser_rdf(rdf,names)
 arks=[]
 for row in decisions:
  code=row["code_insee"];ark=row["ark_pactols"];label=names[code]
  if (row["libelle_COG_2026"]!=label or
      row["uri_insee"]!="http://id.insee.fr/geo/commune/"+code or
      row["predicat_source"]!="exactMatch" or
      row["concept_deprecie"]!="non" or
      row["statut_validation"]!="VALIDE_ADLFI_2026" or
      row["portee_COG"]!="2026-01-01"):
   raise ValueError("Registre de validation divergent : "+code)
  xs=rdf_records["explicites"][code]
  if len(xs)!=1:raise ValueError("L'URI INSEE cite un nombre ambigu de concepts : "+code)
  x=xs[0]
  if (x["ark"]!=ark or
      x["prefLabels_fr"]!=[row["prefLabel_fr_pactols"]] or
      not label_compatible(label,row["prefLabel_fr_pactols"]) or
      x["deprecie"] or x["remplace"] or
      x["risque_ile_atoll_autre_type"] or
      x["codes_communaux_cites"]!=[code] or
      x["insee_exactMatch"]!=[{
         "uri":"http://id.insee.fr/geo/commune/"+code,
         "famille":"commune","code":code}]):
   raise ValueError("Preuve RDF incompatible avec le registre : "+code)
  arks.append(ark)
 if len(set(arks))!=48:raise ValueError("ARK Pactols réutilisé pour plusieurs communes")
 if rdf_records["lexicaux_sans_exactMatch_987"]:
  raise ValueError("Des candidats lexicaux exigent une instruction spécifique")
 originals=json.loads(socle.read_text(encoding="utf-8"))
 published=json.loads(public.read_text(encoding="utf-8"))
 if (originals["schema"]!="adlfi.lieux.recherche.outremer.public.v1"
     or len(originals["pactols_valides"])!=128
     or any(c in originals["pactols_valides"] for c in CODE)):
  raise ValueError("Socle antérieur aux 48 validations non conforme")
 expected=appliquer_validations(originals,[registre])
 expected_bytes=(json.dumps(expected,ensure_ascii=False,
                             separators=(",",":"))+"\n").encode("utf-8")
 actual_bytes=public.read_bytes()
 if actual_bytes!=expected_bytes:
  raise ValueError("L'index public diffère de la régénération canonique du socle")
 if (len(published["pactols_valides"])!=176 or
      {c for c in published["pactols_valides"] if c.startswith("987")}!=CODE):
  raise ValueError("Compteur public Pactols Polynésie non conforme")
 if (published["pactols_valides"]!={**published["pactols_valides"]} or
      published["contours_invalides"]!=["98745","98805"] or
      published["ark_confirmes_non_valides"]!=
       {"97607":"26678/crtZcuFSJVYZU"}):
  raise ValueError("Décisions antérieures ou anomalies de contour modifiées")
 if (len(rdf_records["anciens_ou_territoriaux"]["987"])!=1 or
     rdf_records["anciens_ou_territoriaux"]["987"][0]["ark"]!=
        "26678/pcrt4K8nLVxWOP" or
     rdf_records["anciens_ou_territoriaux"]["98799"]):
  raise ValueError("Territoire 987/Clipperton 98799 mêlés au registre communal")
 man=json.loads(manifest.read_text(encoding="utf-8"))["modules"]["lieux"]
 out=man["recherche_cog_outremer_2026"]
 if (out["relations_pactols_cog_validees_2026"]!=176 or
     out["relations_pactols_cog_validees_polynesie_2026"]!=48 or
     out["source_validations_polynesie"]!=SOURCE or
     out["communes"]!=212 or out["autres_entites"]!=21 or
     out["geometries_publiees"]!=0):
  raise ValueError("Manifeste public incompatible")
 poly=man["historique_communes_polynesie"]
 hist=json.loads(chronologie.read_text(encoding="utf-8"))
 if (poly["correspondances_pactols_2026_validees"]!=48 or
     poly["codes_contours_audites_invalides"]!=["98745"] or
     hist["alignements_pactols_2026_valides"]!=48 or
     hist["source_alignements_pactols_2026"]!=SOURCE or
     hist["alignements_uniquement_millesime_2026"] is not True or
     hist["contour_tahaa_98745_non_homologue"] is not True or
     hist["nouveaux_alignements_pactols"]!=0 or
     hist["contours_historiques_publies"]!=0 or
     hist["communes_associees_creees"]!=0):
  raise ValueError("Périodes historiques ou contours fictivement homologués")
 return {"communes_COG_2026":48,"preuves_RDF_exactMatch_uniques":48,
  "ARK_distincts":48,"alignements_publies_avant":128,"alignements_publies_apres":176,
  "decisions_enregistrees":"VALIDE_ADLFI_2026",
  "code_tahaa":"98745","ARK_tahaa":published["pactols_valides"]["98745"],
  "contour_tahaa_homologue":False,"communes_associees_nouvelles":0,
  "alignements_territoire_987_nouveaux":0,
  "empreinte_index_public":hashlib.sha256(actual_bytes).hexdigest()}

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("registre","rdf","cog-dir","socle","public","manifest","chronologie"):
  p.add_argument("--"+n,type=Path,required=True)
 args=p.parse_args()
 print(json.dumps(verifier(args.registre,args.rdf,getattr(args,"cog_dir"),args.socle,
    args.public,args.manifest,args.chronologie),ensure_ascii=False,sort_keys=True,indent=2))
