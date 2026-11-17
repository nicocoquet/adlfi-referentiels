#!/usr/bin/env python3
"""Extraire et contrôler 98 communes associées ISPF sans inventer de codes INSEE.

Lecture en ZIP/XML des seules valeurs de la nomenclature XLSX officielle :
- Commune (48), Commune associée (116 = 98 + 18), Subdivision (5),
  Geo (179 = 98 + 18 + 63 îles rattachées).
- Seuls les 98 enregistrements IDComas ne finissant pas par « 0 »
  représentent des communes associées ; les 18 « xx0 » sont des *unités
  statistiques* des communes principales non subdivisées.
- Le code COG 987xx n'est utilisé que comme identifiant de la commune
  PARENTE 2026 (48 communes de l'index déjà homologué).
- Les trois chiffres IDComas ne sont JAMAIS transformés en code INSEE.
- L'ISPF ne donne pas dans ce fichier de dates de création juridique.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,posixpath,re,unicodedata,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

URL="https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx"
SHA="d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6"
M="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
P="{http://schemas.openxmlformats.org/package/2006/relationships}"
SCHEMA="adlfi.lieux.polynesie.associees_ispf_nomenclature.v1"
DATE_CONSULTATION="2026-11-17"
SOURCE_LEGALE="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000046768003/2026-04-17"

def normaliser(txt):
 s=unicodedata.normalize("NFKD",str(txt).casefold())
 return "".join(x for x in s if not unicodedata.combining(x) and x.isalnum())

def sha(path:Path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def classeur(source:Path):
 if sha(source)!=SHA:
  raise ValueError("Source XLSX ISPF différente de l'empreinte contrôlée")
 tables={}
 with zipfile.ZipFile(source) as z:
  workbook=ET.fromstring(z.read("xl/workbook.xml"))
  relations=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
  links={x.get("Id"):x.get("Target") for x in relations.findall(P+"Relationship")}
  strings=[]
  if "xl/sharedStrings.xml" in z.namelist():
   root=ET.fromstring(z.read("xl/sharedStrings.xml"))
   strings=["".join(n.text or "" for n in item.iter(M+"t"))
            for item in root.findall(M+"si")]
  for sh in workbook.findall(M+"sheets/"+M+"sheet"):
   name=sh.get("name");loc=links.get(sh.get(R+"id"))
   if not loc:raise ValueError("Feuille sans lien XLSX : "+name)
   path=loc.lstrip("/") if loc.startswith("/") else posixpath.normpath("xl/"+loc)
   root=ET.fromstring(z.read(path))
   rows=[]
   for row in root.findall(".//"+M+"sheetData/"+M+"row"):
    values={}
    for cell in row.findall(M+"c"):
     loc=cell.get("r","")
     col=re.match(r"^[A-Z]+",loc)
     if not col:raise ValueError("Cellule sans coordonnées : "+loc)
     val=cell.find(M+"v")
     if cell.get("t")=="s" and val is not None:
      value=strings[int(val.text)]
     elif cell.get("t")=="inlineStr":
      value="".join(n.text or "" for n in cell.iter(M+"t"))
     else:
      value=val.text if val is not None else ""
     values[col.group()]=str(value or "").strip()
    if values:rows.append(values)
   if not rows:raise ValueError("Feuille ISPF vide : "+name)
   header=rows[0]
   if not all(re.fullmatch("[A-Z]+",c) for c in header):
    raise ValueError("Colonnes illisibles : "+name)
   names=[header[c] for c in header]
   if len(set(names))!=len(names):raise ValueError("En-têtes dupliqués : "+name)
   contents=[{header[c]:r.get(c,"") for c in header}
             for r in rows[1:]]
   tables[name]=contents
 return tables

def analyser(ispf:Path,index_public:Path):
 t=classeur(ispf)
 needed={
  "Commune":["IDCom","IDSub","Commune","Subdivision"],
  "Commune associée":["IDComas","IDCom","IDSub","Comas","Commune","Subdivision"],
  "Subdivision":["IDSub","Subdivision"],
  "Geo":["IDGeo","IDIle","IDComas","IDCom","IDSub",
         "Geo","Ile","Comas","Commune","Subdivision",
         "isCom","isComas","isIleRattachee"],
 }
 if not set(needed).issubset(t):raise ValueError("Feuilles ISPF manquantes")
 for name,columns in needed.items():
  if not t[name] or list(t[name][0])!=columns:
   raise ValueError("En-têtes inattendus dans "+name)
 if len(t["Commune"])!=48 or len(t["Commune associée"])!=116 or (
     len(t["Subdivision"])!=5 or len(t["Geo"])!=179):
  raise ValueError("Périmètre des tables ISPF incompatible (48/116/5/179)")
 subdivisions={r["IDSub"]:r["Subdivision"] for r in t["Subdivision"]}
 if set(subdivisions)!={"1","2","3","4","5"}:
  raise ValueError("Cinq subdivisions administratives attendues")
 communes={r["IDCom"]:r for r in t["Commune"]}
 if len(communes)!=48 or set(communes)!={str(i) for i in range(11,59)}:
  raise ValueError("48 communes ISPF avec codes 11–58 attendues")
 published=json.loads(index_public.read_text(encoding="utf-8"))
 if (published.get("schema")!="adlfi.lieux.recherche.outremer.public.v1" or
     len(published["pactols_valides"])!=176 or
     len(published["pactols_collectivites_valides"])!=4 or
     len(published["autres"])!=21 or
     published["contours_invalides"]!=["98745","98805"]):
  raise ValueError("Socle AdlFI 2026 déjà publié non conforme")
 ref=dict(line.split("|",1) for line in published["communes"]["987"].splitlines())
 if len(ref)!=48 or set(ref)!={"987"+str(i) for i in range(11,59)}:
  raise ValueError("48 communes COG polynésiennes attendues")
 ecarts=[]
 for code,r in communes.items():
  if r["IDSub"] not in subdivisions or (
      r["Subdivision"]!=subdivisions[r["IDSub"]]):
   raise ValueError("Subdivision de commune ISPF invalide : "+code)
  if normaliser(ref["987"+code])!=normaliser(r["Commune"]):
   ecarts.append({"code_parent_COG":"987"+code,
     "libelle_COG":ref["987"+code],"libelle_ISPF":r["Commune"]})
 # Les différences de libellé ISPF/COG demandent un arbitrage, pas un alignement implicite.
 # Ici la jointure repose sur le code numérique officiel (IDCom), puis la
 # compatibilité du libellé sert d'alerte documentaire.
 related=[];nonassoc=[];seen=set();counts=collections.Counter()
 for row in t["Commune associée"]:
  code,parent,sub=row["IDComas"],row["IDCom"],row["IDSub"]
  if not re.fullmatch(r"[0-9]{3}",code) or code in seen or code[:2]!=parent:
   raise ValueError("Code ISPF de commune associée invalide ou dupliqué : "+code)
  if parent not in communes or sub!=communes[parent]["IDSub"] or (
       row["Commune"]!=communes[parent]["Commune"] or
       row["Subdivision"]!=subdivisions[sub] or not row["Comas"]):
   raise ValueError("Rattachement ISPF hors des 48 communes COG : "+code)
  seen.add(code)
  item={
   "code_ispf":code,
   "libelle":row["Comas"],
   "commune_parent_cog":"987"+parent,
   "commune_parent_libelle_cog":ref["987"+parent],
   "subdivision_ispf":sub,
   "subdivision_libelle":subdivisions[sub],
  }
  if code.endswith("0"):
   # Il s'agit de la commune entière, avec code ISPF de partition statistique
   # et non d'une 99e commune associée.
   if normaliser(item["libelle"])!=normaliser(row["Commune"]):
    raise ValueError("Code ISPF xx0 d'une commune non associée mal libellé : "+code)
   nonassoc.append(item)
  else:
   related.append(item);counts[parent]+=1
 if len(related)!=98 or len(nonassoc)!=18 or len(counts)!=30 or (
       len(set(x["code_ispf"] for x in related))!=98):
  raise ValueError("98 associées dans 30 parents + 18 non subdivisées attendues")
 if set(counts).intersection(x["code_ispf"][:2] for x in nonassoc):
  raise ValueError("Commune subdivisée classée non subdivisée")
 if len(set(x["commune_parent_cog"] for x in related))!=30:
  raise ValueError("Rattachements des 98 associées non univoques")
 if set(r["code_ispf"] for r in related)|set(r["code_ispf"] for r in nonassoc)!=seen:
  raise ValueError("Partition 116 des unités ISPF incomplète")
 # Deux Avera homonymes : seules leurs identités ISPF+parents les distinguent.
 avera={x["code_ispf"]:x["commune_parent_cog"] for x in related
        if normaliser(x["libelle"])=="avera"}
 if avera!={"441":"98744","501":"98750"}:
  raise ValueError("Homonymie Avera (441 Rurutu / 501 Taputapuatea) mal résolue")
 # Vérifier indépendamment la partition fine dans la feuille géographique.
 flags=collections.Counter()
 compact=set()
 for row in t["Geo"]:
  codes=[row["isCom"],row["isComas"],row["isIleRattachee"]]
  if codes.count("1")!=1 or any(x not in ("0","1") for x in codes):
   raise ValueError("Typologie géographique ISPF non exclusive")
  typ=("COM" if codes[0]=="1" else "COMAS" if codes[1]=="1" else "ILE_RATTACHEE")
  flags[typ]+=1
  code=row["IDComas"]
  if code not in seen or row["IDCom"]!=code[:2]:
   raise ValueError("Geo : code de rattachement absent de la partition 116")
  if typ!="ILE_RATTACHEE":
   if row["IDGeo"]!=code+"00" or code in compact:
    raise ValueError("Geo : plusieurs unités de base pour le même code ISPF")
   compact.add(code)
 if (flags!={"COM":18,"COMAS":98,"ILE_RATTACHEE":63} or compact!=seen):
  raise ValueError("Geo : partition 116 unités + 63 îles rattachées non certifiée")
 if len(t.get("Ile",[]))!=119:
  raise ValueError("Feuille Ile ISPF modifiée ; inspecter le millésime")
 result={
  "schema":SCHEMA,
  "statut":"NOMENCLATURE_ISPF_CONSULTEE_2026-11-17_SANS_VALIDITE_HISTORIQUE_RETROPROJETEE",
  "source_ispf":{"url":URL,"sha256":SHA,"consultee_le":DATE_CONSULTATION,
                 "nom_feuille":"Commune associée","nom_feuille_controle":"Geo"},
  "source_juridique_statistique_2022":SOURCE_LEGALE,
  "referentiel_parent_COG":"2026-01-01",
  "subdivisions":[{"code_ispf":r["IDSub"],"libelle":r["Subdivision"]}
                  for r in t["Subdivision"]],
  "communes_associees":sorted(related,key=lambda x:x["code_ispf"]),
  "unites_communes_non_subdivisees":sorted(nonassoc,key=lambda x:x["code_ispf"]),
  "ecarts_libelles_48_parents_ISPF_COG":ecarts,
  "statistiques":{
    "communes_COG_parentes":48,
    "communes_avec_associees":30,
    "communes_associees":98,
    "communes_non_subdivisees":18,
    "unites_nomenclature_fine":116,
    "subdivisions_ISPF":5,
    "iles_rattachees_lignes_Geo":63,
    "lignes_geo_source":179,
    "fiches_communales_COG_remplacees":0,
    "alignements_Pactols_communes_conserves":176,
    "alignements_Pactols_collectivites_conserves":4,
    "nouveaux_ARK_Pactols_crees":0,
    "geometries_nouvelles_publiees":0,
    "validite_historique_inferree":0,
  },
  "interdits":{
    "code_ISPF_interprete_comme_code_INSEE":False,
    "codes_ISPF_termines_par_zero_crees_comme_associees":False,
    "ile_rattachee_creee_comme_commune_associee":False,
    "retrospection_2022_sur_1943":False
  }
 }
 return result

def payload(d):
 return (json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode("utf-8")

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--ispf",type=Path,required=True)
 p.add_argument("--index-public",type=Path,required=True)
 p.add_argument("--sortie",type=Path,default=None)
 p.add_argument("--verifier",type=Path,default=None)
 p.add_argument("--imprimer-donnees",action="store_true")
 a=p.parse_args()
 if a.sortie is not None and a.verifier is not None:
  p.error("Choisir une seule sortie ou vérification")
 d=analyser(a.ispf,a.index_public)
 if a.sortie:
  a.sortie.parent.mkdir(parents=True,exist_ok=True)
  a.sortie.write_bytes(payload(d))
 if a.verifier and payload(d)!=a.verifier.read_bytes():
  raise ValueError("Référentiel public des 98 associées différent du XLSX ISPF")
 print("ISPF_BILAN",json.dumps(d["statistiques"],ensure_ascii=False,sort_keys=True))
 print("ISPF_ECARTS_LIBELLES",json.dumps(d["ecarts_libelles_48_parents_ISPF_COG"],ensure_ascii=False))
 print("ISPF_AVERA",json.dumps([
     r for r in d["communes_associees"] if r["code_ispf"] in ("441","501")],
     ensure_ascii=False))
 if a.imprimer_donnees:print("ISPF_DONNEES_JSON",payload(d).decode("utf-8").replace("\n","\\n"))
if __name__=="__main__":
 main()
