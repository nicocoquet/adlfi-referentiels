#!/usr/bin/env python3
"""Qualifier la nomenclature officielle ISPF : 98 communes associées + 18 unités non associées.

La source est le fichier officiel Codes_geographiques_ce46ed21ee.xlsx
SHA-256 figé. Ne publie aucune autorité ni alignement Pactols :
le rapport d'audit constitue une recette à vérifier avant sa conversion
en catalogue de données public. Les codes IDComas de l'ISPF sont des
chaînes sur trois positions, distinctes des codes INSEE 987XX.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,unicodedata
from pathlib import Path
from inspecter_nomenclature_geographique_ispf import read_xlsx

SOURCE="https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx"
SHA="d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6"
HEADERS={
 "Subdivision":list("AB"),
 "Commune":list("ABCD"),
 "Commune associée":list("ABCDEF"),
 "Ile":list("ABCD"),
 "Geo":list("ABCDEFGHIJKLM")
}
FIELD_NAMES={
 "Subdivision":["IDSub","Subdivision"],
 "Commune":["IDCom","IDSub","Commune","Subdivision"],
 "Commune associée":["IDComas","IDCom","IDSub","Comas","Commune","Subdivision"],
 "Ile":["IDIle","IDSub","Ile","Subdivision"],
 "Geo":["IDGeo","IDIle","IDComas","IDCom","IDSub","Geo","Ile","Comas","Commune","Subdivision","isCom","isComas","isIleRattachee"]
}

def normaliser(s:str)->str:
 txt=unicodedata.normalize("NFKD",s.casefold())
 return " ".join(re.findall(r"[a-z0-9]+","".join(ch for ch in txt
       if not unicodedata.combining(ch))))

def rows(sheet):
 name=sheet["feuille"];cols=HEADERS.get(name)
 if cols is None:raise ValueError("Feuille ISPF inattendue : "+name)
 vals=sheet["lignes"]
 if not vals or [vals[0]["cells"].get(col) for col in cols]!=FIELD_NAMES[name]:
  raise ValueError("Colonnes du classeur ISPF altérées : "+name)
 return [{field:raw["cells"].get(col,"").strip()
          for col,field in zip(cols,FIELD_NAMES[name])}
         for raw in vals[1:]]

def qualifier(source:Path,index:Path)->dict:
 if hashlib.sha256(source.read_bytes()).hexdigest()!=SHA:
  raise ValueError("La source officielle ISPF a changé : qualification interrompue")
 sheets=read_xlsx(source)
 if {x["feuille"] for x in sheets}!=set(HEADERS):
  raise ValueError("Ensemble des cinq feuilles ISPF inattendu")
 d={x["feuille"]:rows(x) for x in sheets}
 if {k:len(v) for k,v in d.items()}!={"Subdivision":5,"Commune":48,
       "Commune associée":116,"Ile":119,"Geo":179}:
  raise ValueError("Cardinalités ISPF sources différentes de la recette initiale")
 published=json.loads(index.read_text(encoding="utf-8"))
 if (published["schema"]!="adlfi.lieux.recherche.outremer.public.v1" or
     len(published["pactols_valides"])!=176 or
     len(published.get("pactols_collectivites_valides",{}))!=4):
  raise ValueError("Base AdlFI non conforme 176 communes / 4 collectivités")
 cog=dict(v.split("|") for v in published["communes"]["987"].split("\n"))
 if len(cog)!=48:raise ValueError("48 communes COG attendues")
 subs={r["IDSub"]:r["Subdivision"] for r in d["Subdivision"]}
 if len(subs)!=5:raise ValueError("5 subdivisions ISPF attendues")
 communes={}
 for r in d["Commune"]:
  code=r["IDCom"].zfill(2)
  insee="987"+code
  if (not re.fullmatch(r"\d{2}",code) or insee not in cog or code in communes or
       r["IDSub"] not in subs or r["Subdivision"]!=subs[r["IDSub"]]):
   raise ValueError("Commune ISPF sans correspondance COG structurée : "+code)
  communes[code]={"code_ISPF":code,"code_INSEE":insee,"nom_ISPF":r["Commune"],
     "nom_COG_2026":cog[insee],"IDSub":r["IDSub"],"subdivision":r["Subdivision"],
     "variantes_libelles":normaliser(r["Commune"])!=normaliser(cog[insee])}
 if len(communes)!=48:raise ValueError("Rattachement des 48 communes ISPF incomplet")
 assoc,autonomes=[],[]
 parents=collections.Counter()
 for r in d["Commune associée"]:
  com=r["IDCom"].zfill(2);idc=r["IDComas"].zfill(3)
  if (not re.fullmatch(r"\d{3}",idc) or not re.fullmatch(r"\d{2}",com) or
      idc[:2]!=com or com not in communes or
      r["IDSub"]!=communes[com]["IDSub"] or
      r["Commune"]!=communes[com]["nom_ISPF"] or
      r["Subdivision"]!=communes[com]["subdivision"]):
   raise ValueError("Commune associée ISPF sans parent explicitement vérifié : "+idc)
  row={"id_comas_ISPF":idc,"libelle":r["Comas"],"id_commune_ISPF":com,
       "code_commune_COG":communes[com]["code_INSEE"],
       "libelle_commune_ISPF":communes[com]["nom_ISPF"],
       "subdivision_ISPF":r["IDSub"],"nature":None}
  if idc.endswith("0"):
   if r["Comas"]!=r["Commune"]:
    raise ValueError("Code conventionnel 0 sans même libellé communal : "+idc)
   row["nature"]="COMMUNE_SANS_ASSOCIEE_CONVENTION_ISPF"
   autonomes.append(row)
  else:
   row["nature"]="COMMUNE_ASSOCIEE"
   assoc.append(row);parents[com]+=1
 ids=[x["id_comas_ISPF"] for x in assoc+autonomes]
 if len(set(ids))!=116:raise ValueError("Code IDComas ISPF dupliqué")
 if (len(assoc)!=98 or len(autonomes)!=18 or len(parents)!=30 or
     set(parents)&{x["id_commune_ISPF"] for x in autonomes}):
  raise ValueError("Répartition 98 associées / 18 conventionnelles / 30 communes fausse")
 if any(x["id_commune_ISPF"] in parents for x in autonomes):
  raise ValueError("Une commune possède simultanément un code autonome et des associées")
 if len(set(x["code_commune_COG"] for x in assoc))!=30:
  raise ValueError("Rattachements COG des 30 communes non univoques")
 avera=[x for x in assoc if normaliser(x["libelle"]).startswith("avera ")]
 if {(x["id_comas_ISPF"],x["code_commune_COG"],x["libelle"]) for x in avera}!={
     ("501","98750","Avera (Taputapuatea)"),
     ("441","98744","Avera (Rurutu)")}:
  raise ValueError("Les deux Avera homonymes ont un libellé contextualisé inattendu : "+
    json.dumps(avera,ensure_ascii=False))
 # L'île est un niveau parallèle, distinct de la commune associée.
 ile={r["IDIle"]:r["Ile"] for r in d["Ile"]}
 if len(ile)!=119:raise ValueError("Nombre de codes d'îles distinctes inattendu")
 geo=[]
 geo_code_exceptions=[]
 for r in d["Geo"]:
  idc=r["IDComas"].zfill(3)
  if idc not in ids:raise ValueError("Rattachement de l'île à un IDComas inexistant : "+idc)
  if (r["IDCom"].zfill(2)!=idc[:2] or
      r["IDIle"] not in ile or
      r["Ile"]!=ile[r["IDIle"]] or
      r["IDSub"] not in subs or
      r["isCom"] not in ("0","1") or
      r["isComas"] not in ("0","1") or
      r["isIleRattachee"] not in ("0","1")):
   raise ValueError("Code géographique ISPF incompatible : "+r["IDGeo"])
  # Les cinq positions CODGEO ne sont pas des codes de communes INSEE.
  # Le classeur d'origine utilise un suffixe 00 pour plusieurs îles non
  # rattachées : il faut contrôler chaque IDGeo sans le construire.
  if not re.fullmatch(r"\d{5}",r["IDGeo"]):
   raise ValueError("CODGEO ISPF non numérique à cinq positions : "+
      json.dumps(r,ensure_ascii=False))
  if r["IDGeo"][:3]!=idc:
   geo_code_exceptions.append(r)
  geo.append(r)
 if len(set(x["IDGeo"] for x in geo))!=len(geo):
  raise ValueError("CODGEO dupliqué")
 return {
  "schema":"adlfi.lieux.polynesie.ispf.associees.audit.v1",
  "statut":"RECETTE_ISPF_NON_VALIDANTE",
  "source":{"url":SOURCE,"sha256":SHA,
       "edition_precise":None,"date_creation_juridique_des_associees_inferree":False},
  "bilan":{"communes_COG":48,"communes_associees_ISPF":98,
      "communes_ISPF_sans_associees":18,"unites_fines_ISPF":116,
      "communes_parentes_des_associees":30,"subdivisions_ISPF":5,
      "iles_ISPF_dans_classeur":119,"codes_geographiques_ISPF":179,
      "alignements_Pactols_communaux_conserves":176,
      "alignements_Pactols_collectivites_conserves":4,
      "nouveaux_alignements_Pactols":0,"nouveaux_contours":0,
      "dates_historiques_inferrees":0,"autorites_ajoutees_docs":0},
  "communes_ISPF_vers_COG":dict(sorted(communes.items())),
  "communes_associees":sorted(assoc,key=lambda x:x["id_comas_ISPF"]),
  "unites_conventionnelles_non_associees":sorted(autonomes,key=lambda x:x["id_comas_ISPF"]),
  "distribution_associees_par_commune":dict(sorted(parents.items())),
  "homonymes_avera":avera,
  "exceptions_CODE_GEO_prefixe_IDComas":geo_code_exceptions,
  "codes_geographiques":geo
 }
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source',type=Path,required=True)
 p.add_argument('--index-cog',type=Path,required=True)
 p.add_argument('--sortie',type=Path,required=True)
 args=p.parse_args()
 if args.sortie.exists() or 'docs' in args.sortie.resolve().parts:
  raise ValueError("Rapport de recette : création hors docs sans écrasement")
 result=qualifier(args.source,args.index_cog)
 args.sortie.parent.mkdir(parents=True,exist_ok=True)
 args.sortie.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',
                         encoding="utf-8")
 print("ISPF_BILAN",json.dumps(result["bilan"],ensure_ascii=False))
 print("ISPF_RATTACHEMENTS",json.dumps(result["distribution_associees_par_commune"],ensure_ascii=False))
 print("ISPF_HOMONYMES_AVERA",json.dumps(result["homonymes_avera"],ensure_ascii=False))
 print("ISPF_EXCEPTIONS_CODGEO",json.dumps(result["exceptions_CODE_GEO_prefixe_IDComas"],ensure_ascii=False))
 print("ISPF_VARIANTES_ISPF_COG",json.dumps([
   c for c in result["communes_ISPF_vers_COG"].values() if c["variantes_libelles"]],
   ensure_ascii=False))
if __name__=='__main__':main()
