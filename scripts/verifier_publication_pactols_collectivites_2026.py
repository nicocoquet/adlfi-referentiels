#!/usr/bin/env python3
"""Certifier les 4 liens Pactols–COG 2026 des collectivités 977,978,986,987.

Les quatre autorités sont de nature TERRITOIRE et restent séparées des
176 correspondances communales et des codes cinq positions 97701/97801.
Vérifie les 2 fichiers COG Insee officiels, le RDF Frantiq Lieux épinglé,
le registre de décisions et la reconstruction OCTET PAR OCTET de l'index.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
from auditer_pactols_collectivites_antilles_2007 import analyser_rdf as scan_antilles
from auditer_pactols_wallis_futuna_2026 import scan_rdf as scan_wallis
from auditer_pactols_polynesie_2026 import analyser_rdf as scan_polynesie
from auditer_cog_polynesie_2026 import read,sha

SOURCE_RDF_SHA="3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
COG_SHAS={
 "v_comer_2026.csv":"d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed",
 "v_commune_comer_2026.csv":"9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8",
}
CODES={"977":"Saint-Barthélemy","978":"Saint-Martin",
       "986":"Wallis-et-Futuna","987":"Polynésie française"}
ARKS={"977":"26678/pcrtrGdtY56gmH","978":"26678/pcrty5LooX8FgU",
      "986":"26678/pcrtwFq5jKHO3k","987":"26678/pcrt4K8nLVxWOP"}
PREFS={"977":"Saint-Barthélemy (Antilles Françaises)",
       "978":"Saint-Martin (Antilles Françaises)",
       "986":"Wallis et Futuna","987":"Polynésie française"}
SOURCE_CSV="recette/lieux/COLLECTIVITES-COMER-VALIDATIONS-PACTOLS-COG-2026.csv"
COLS=("code_cog_2026","libelle_COG_2026","nature_autorite",
      "ark_pactols","prefLabel_fr_pactols","uri_insee_exactMatch_collectivite",
      "uri_secondaire_exactMatch_non_publiee","predicat_source",
      "concept_deprecie","concept_remplace","statut_validation","portee_COG",
      "source_rdf_sha256","transfert_autres_echelons")
INTERDITS={"97123","97127","97701","97801","98607","98609",
           "98611","98612","98613","98799"}

def decisions(path:Path)->dict[str,dict]:
 with path.open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f,delimiter=";")
  if tuple(reader.fieldnames or ())!=COLS:
   raise ValueError("Colonnes du registre des collectivités divergentes")
  lines=list(reader)
 if len(lines)!=4 or {x["code_cog_2026"] for x in lines}!=set(CODES):
  raise ValueError("Quatre collectivités uniques exigées")
 if any(None in x or any(v is None for v in x.values()) for x in lines):
  raise ValueError("Ligne du registre mal formée")
 for r in lines:
  c=r["code_cog_2026"]
  if (r["libelle_COG_2026"]!=CODES[c] or
      r["nature_autorite"] not in ("COLLECTIVITE_OUTREMER","TERRITOIRE_COMER") or
      (r["nature_autorite"]=="TERRITOIRE_COMER")!=(c=="986") or
      r["ark_pactols"]!=ARKS[c] or
      r["prefLabel_fr_pactols"]!=PREFS[c] or
      r["uri_insee_exactMatch_collectivite"]!=
        "http://id.insee.fr/geo/collectiviteDOutreMer/"+c or
      r["uri_secondaire_exactMatch_non_publiee"]!=
        ("http://id.insee.fr/geo/commune/"+c+"01" if c in ("977","978") else "") or
      r["predicat_source"]!="skos:exactMatch" or
      r["concept_deprecie"]!="non" or r["concept_remplace"]!="non" or
      r["statut_validation"]!="VALIDE_ADLFI_2026" or
      r["portee_COG"]!="2026-01-01" or
      r["source_rdf_sha256"]!=SOURCE_RDF_SHA or
      r["transfert_autres_echelons"]!="interdit"):
   raise ValueError("Décision ou portée éditoriale insuffisamment documentée : "+c)
 return {r["code_cog_2026"]:r for r in lines}

def verifier_cog(folder:Path):
 for name,digest in COG_SHAS.items():
  if sha(folder/name)!=digest:raise ValueError("COG non épinglé : "+name)
 terr={x["COMER"]:x["LIBELLE"] for x in read(folder/"v_comer_2026.csv")
       if x["COMER"] in CODES}
 if terr!=CODES:raise ValueError("Quatre territoires COG 2026 incompatibles")
 r=[x for x in read(folder/"v_commune_comer_2026.csv")
    if x["COMER"] in CODES]
 ant={x["COM_COMER"]:(x["COMER"],x["LIBELLE"],x["NATURE_ZONAGE"])
       for x in r if x["COMER"] in ("977","978")}
 if ant!={"97701":("977","Saint-Barthélemy","COM"),
          "97801":("978","Saint-Martin","COM")}:
  raise ValueError("Codes cinq positions COG 977/978 altérés")
 circ={x["COM_COMER"]:(x["COMER"],x["LIBELLE"],x["NATURE_ZONAGE"])
       for x in r if x["COMER"]=="986"}
 if circ!={"98611":("986","Alo","CIR"),
           "98612":("986","Sigave","CIR"),
           "98613":("986","Uvea","CIR")}:
  raise ValueError("Circonscriptions 986 confondues avec des communes")
 poly=[x for x in r if x["COMER"]=="987"]
 if len(poly)!=48 or any(x["NATURE_ZONAGE"]!="COM" for x in poly):
  raise ValueError("48 communes polynésiennes attendues")
 return {x["COM_COMER"]:x["LIBELLE"] for x in poly}

def verifier_preuves(rdf:Path,communes:dict[str,str]):
 if sha(rdf)!=SOURCE_RDF_SHA:raise ValueError("RDF Frantiq altéré")
 ant=scan_antilles(rdf)["codes"]
 wall=scan_wallis(rdf)["explicites"]
 poly=scan_polynesie(rdf,communes)["anciens_ou_territoriaux"]
 candidates={c:(ant[c] if c in ant else wall[c] if c in wall else poly[c])
             for c in CODES}
 for c,hits in candidates.items():
  if len(hits)!=1:raise ValueError("ARK RDF absent ou multiple pour la collectivité "+c)
  h=hits[0]
  if (h["ark"]!=ARKS[c] or h["prefLabels_fr"]!=[PREFS[c]] or
      h["deprecie"] or h["remplace"]):
   raise ValueError("RDF concept déprécié/remplacé ou libellé incompatible : "+c)
  insee=(h.get("exactMatch_INSEE_cibles") if c!="987"
         else h["insee_exactMatch"])
  urls={x["uri"] for x in insee}
  expected={"http://id.insee.fr/geo/collectiviteDOutreMer/"+c}
  if c in ("977","978"):
   expected.add("http://id.insee.fr/geo/commune/"+c+"01")
  if urls!=expected or len(insee)!=len(expected):
   raise ValueError("Relations RDF incohérentes, secondaire non isolée : "+c)
  if c=="986" and "Territoire des îles Wallis et Futuna" not in h["altLabels_fr"]:
   raise ValueError("Libellé territorial de Wallis non retrouvé")
  if c=="987" and h["codes_communaux_cites"]:
   raise ValueError("RDF collectivité 987 affecté à une commune")
 if ant["97123"] or ant["97127"]:
  raise ValueError("Un concept Pactols historique antillais réclame instruction")
 if wall["98609"] or wall["98607"] or any(wall[c] for c in ("98611","98612","98613")):
  raise ValueError("Un code historique ou CIR contient un exactMatch non instruit")

def verifier(registre:Path,rdf:Path,cog:Path,socle:Path,public:Path,
             manifest:Path)->dict:
 rows=decisions(registre)
 names=verifier_cog(cog)
 verifier_preuves(rdf,names)
 old=json.loads(socle.read_text(encoding="utf-8"))
 newer=json.loads(public.read_text(encoding="utf-8"))
 if (old.get("pactols_collectivites_valides") is not None or
     len(old["pactols_valides"])!=176 or len(old["autres"])!=21):
  raise ValueError("État antérieur 176 communes non retrouvé")
 expected={**old,"pactols_collectivites_valides":
           {code:rows[code]["ark_pactols"] for code in sorted(rows)}}
 actual=public.read_bytes()
 canonical=(json.dumps(expected,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8")
 if actual!=canonical:
  raise ValueError("Index publié différent de la reconstruction à partir du socle 176")
 if (newer["pactols_valides"]!=old["pactols_valides"] or
     newer["ark_confirmes_non_valides"]!=old["ark_confirmes_non_valides"] or
     newer["contours_invalides"]!=old["contours_invalides"] or
     newer["autres"]!=old["autres"] or
     newer["communes"]!=old["communes"]):
  raise ValueError("Une autorité commune ou géométrie historique a été altérée")
 coll=newer["pactols_collectivites_valides"]
 if (coll!=ARKS or len(set(coll.values()))!=4 or
     set(coll).intersection(INTERDITS) or
     set(coll.values()).intersection(newer["pactols_valides"].values()) or
     set(coll.values()).intersection(newer["ark_confirmes_non_valides"].values())):
  raise ValueError("Identifiants des collectivités confondus avec des communes")
 m=json.loads(manifest.read_text(encoding="utf-8"))["modules"]["lieux"]
 outre=m["recherche_cog_outremer_2026"]
 if (outre["relations_pactols_cog_validees_2026"]!=176 or
     outre["relations_pactols_collectivites_2026"]!=4 or
     outre["codes_collectivites_pactols_2026"]!=sorted(CODES) or
     outre["source_validations_collectivites"]!=SOURCE_CSV or
     outre["relations_pactols_collectivites_2026_distinctes_des_communes"] is not True or
     outre["alignements_codes_5_positions_97701_97801_inferes"]!=0 or
     outre["alignements_circonscriptions_98611_98612_98613_inferes"]!=0 or
     outre["alignements_communes_historiques_97123_97127_inferes"]!=0 or
     outre["retroprojection_identifiants_2026"] is not False or
     outre["geometries_publiees"]!=0):
  raise ValueError("Manifeste des quatre collectivités non conforme")
 if (m["historique_collectivites_antilles_2007"]["correspondances_pactols_collectivites_2026"]!=2 or
     m["historique_circonscriptions_wallis_futuna"]["correspondance_pactols_territoire_986_2026_validee"] is not True or
     m["historique_communes_polynesie"]["correspondance_pactols_territoire_987_2026_validee"] is not True):
  raise ValueError("Manifestes régionaux non synchronisés")
 return {"code_collectivites":sorted(coll),"ARK_collectivites":coll,
         "relations_communales_conservees":176,
         "relations_collectivites_validees_2026":4,
         "codes_cinq_positions_97701_97801_non_alignes":2,
         "circonscriptions_986_non_alignees":3,
         "communes_anciennes_97123_97127_non_alignees":2,
         "nouveaux_contours":0,"validite_retroactive":False,
         "sha256_index_public":hashlib.sha256(actual).hexdigest()}
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for name in ("registre","rdf","cog","socle","public","manifest"):
  p.add_argument("--"+name,required=True,type=Path)
 a=p.parse_args()
 d=verifier(a.registre,a.rdf,a.cog,a.socle,a.public,a.manifest)
 print(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True))
