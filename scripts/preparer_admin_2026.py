#!/usr/bin/env python3
"""Qualifier les contours administratifs 2026 et leurs codes COG Insee.

Sources : régions/départements 100 m de data.gouv.fr (édition 2026-05-04)
et CSV officiels Insee au 2026-01-01. Aucun ARK Pactols n'est créé.
L'édition cartographique ne prétend pas dater chaque frontière au 1er janvier.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

INSEE="https://www.insee.fr/fr/information/8740222"
CONTOURS="https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/"
HASHES={
 "regions":"d903566d9c0d263389d279baea6761917b7460749a07bec8ba37dd8f2ff7d98a",
 "departements":"513900ca23edc682ef9b912d7bfc317129eac3a7d71ff19bc22b40ea4838e6eb",
}
EDITION="2026-05-04"
# Les fichiers de contour présentent aussi huit COM/TAAF/Clipperton ;
# ces entités ne sont ni des régions ni des départements du COG.
HORS_ECHELON={"975","977","978","984","986","987","988","989"}
GEO_HASHES={
 "regions":"52ec7200994624753908c9cc1f7dd88d090abddb348c7e757d1eb60190f3bc74",
 "departements":"c330276ba97a2c273c7b0508db9e47f3025d90b1734faf454fd089b87d9e96ea",
}
SCHEMA="adlfi.lieux.contours.administratifs_2026.v1"

def sha(b):return hashlib.sha256(b).hexdigest()

def nom_search(s):
 s=unicodedata.normalize("NFKD",s.casefold())
 s="".join(c for c in s if not unicodedata.combining(c))
 return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9]+"," ",s)).strip()

def lire_cog(path,kind):
 data=Path(path).read_bytes()
 if sha(data)!=HASHES[kind]:raise ValueError("COG 2026 : empreinte non conforme pour "+kind)
 rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
 key="REG" if kind=="regions" else "DEP"
 required=({"REG","NCCENR","LIBELLE"} if kind=="regions" else {"DEP","REG","NCCENR","LIBELLE"})
 if not rows or not required.issubset(rows[0]):raise ValueError("En-têtes COG 2026 manquants")
 lookup={r[key]:r for r in rows}
 if len(rows)!=len(lookup) or len(rows)!=(18 if kind=="regions" else 101):
  raise ValueError("Codes COG 2026 dupliqués ou incomplets : "+kind)
 return lookup,sha(data)

def lire_carte(path,kind):
 raw=Path(path).read_bytes()
 if not raw:raise ValueError("Source géométrique vide")
 if sha(raw)!=GEO_HASHES[kind]:raise ValueError("Source GeoJSON 2026 différente de l’édition vérifiée : "+kind)
 data=json.loads(gzip.decompress(raw) if raw[:2]==b"\x1f\x8b" else raw)
 if data.get("type")!="FeatureCollection" or not isinstance(data.get("features"),list):
  raise ValueError("Source géographique non GeoJSON FeatureCollection")
 return data,sha(raw)

def geo_par_codes(fc,attendus,kind):
 geoms={};inattendus=[]
 for f in fc["features"]:
  props=f.get("properties") or {}
  raw_code=props.get("code")
  if raw_code is None:raise ValueError("Contour sans code : "+kind)
  code=str(raw_code)
  if code in geoms:raise ValueError("Code géographique dupliqué "+kind+"/"+code)
  if code not in attendus:
   if code not in HORS_ECHELON:raise ValueError("Contour hors COG non qualifié "+kind+"/"+code)
   if code in inattendus:raise ValueError("Code de territoire dupliqué "+kind+"/"+code)
   inattendus.append(code)
   continue
  if f.get("geometry",{}).get("type") not in ("Polygon","MultiPolygon") or not f["geometry"].get("coordinates"):
   raise ValueError("Géométrie absente "+kind+"/"+code)
  geoms[code]=f
 missing=sorted(set(attendus)-set(geoms))
 if missing:raise ValueError("Codes COG 2026 sans géométrie "+kind+" : "+",".join(missing))
 return geoms,sorted(inattendus)

def construire(reg,dep,georeg,geodep,hash_sources):
 if len(reg)!=18 or len(dep)!=101:raise ValueError("Cardinalités COG 2026 incompatibles")
 if set(georeg)!=set(reg) or set(geodep)!=set(dep):raise ValueError("Codes des contours ≠ codes COG")
 groupe=defaultdict(list)
 for code,r in dep.items():
  parent=r["REG"]
  if parent not in reg:raise ValueError("Région parente inconnue : "+code+" → "+parent)
  groupe[parent].append(code)
 if set(groupe)!=set(reg):raise ValueError("Région COG sans département")
 collections={};idx=[]
 for kind,orig,cog in (("region",georeg,reg),("departement",geodep,dep)):
  features=[]
  for code in sorted(cog):
   r=cog[code];f=orig[code]
   nom=r["LIBELLE"].strip()
   if not nom:raise ValueError("Nom officiel vide pour "+code)
   props={"code":code,"nom":nom,"niveau":kind,"annee":2026,
          "date_reference_COG":"2026-01-01","date_edition_contours":EDITION,
          "source_geometrie":"data.gouv.fr / contours administratifs (IGN Admin Express)",
          "pactols_valide":False}
   if kind=="region":
    props["departements"]=sorted(groupe[code])
   else:
    props["code_region_parent"]=r["REG"]
    props["nom_region_parent"]=reg[r["REG"]]["LIBELLE"].strip()
   features.append({"type":"Feature","properties":props,"geometry":f["geometry"]})
   idx.append({"kind":"admin","year":2026,"level":kind,"code":code,"label":nom,
               "champs":sorted(set((nom_search(nom),code.casefold())))})
  key=kind+"s-2026.geojson"
  collections[key]={
   "type":"FeatureCollection",
   "provenance":{"schema":SCHEMA,"cog_au_premier_janvier":"2026",
       "edition_contours":EDITION,"source_geometrie":"data.gouv.fr/contours-administratifs",
       "source_geometrie_url":CONTOURS+kind+"s-100m.geojson.gz",
       "source_cog_url":INSEE,"pactols_valide":False,"generalisation_m":100,
       "source_archives_sha256":hash_sources},
   "features":features}
 index={"schema":"adlfi.lieux.admin.index_2026.v1","date_reference":"2026-01-01",
        "edition_contours":EDITION,"source_cog":INSEE,
        "nouvelles_correspondances_pactols":0,"entries":idx}
 rapport={"schema":"adlfi.lieux.admin.controle_2026.v1",
          "regions":len(reg),"departements":len(dep),"zones_ultramarines":{
           "regions":sorted(k for k in reg if k in ("01","02","03","04","06")),
           "departements":sorted(k for k in dep if k in ("971","972","973","974","976"))},
          "mayotte":{"region":dep["976"]["REG"],"departement":"976",
                     "collectivite_statut_particulier":"976R — autorité distincte, non créée par cette chaîne"},
          "validite":{"date_COG":"2026-01-01","edition_cartographique":EDITION},
          "source_SHA256":hash_sources,"alignements_Pactols_crees":0,
          "contours_source_conserves":True}
 if rapport["zones_ultramarines"]!={"regions":["01","02","03","04","06"],"departements":["971","972","973","974","976"]}:
  raise ValueError("Couverture région/département DROM 2026 inattendue")
 if rapport["mayotte"]["region"]!="06":raise ValueError("Rattachement Mayotte non attesté dans COG")
 return collections,index,rapport

def produire(regions_geo,departements_geo,regions_cog,departements_cog,sortie):
 sortie=Path(sortie)
 if "docs" in sortie.parts:raise ValueError("Pas de sortie directement sous docs/")
 if sortie.exists() and any(sortie.iterdir()):raise ValueError("Refus de remplacer une sortie existante")
 reg,hr=lire_cog(regions_cog,"regions")
 dep,hd=lire_cog(departements_cog,"departements")
 rgeo,hgr=lire_carte(regions_geo,"regions");dgeo,hgd=lire_carte(departements_geo,"departements")
 gr,exr=geo_par_codes(rgeo,reg,"region");gd,exd=geo_par_codes(dgeo,dep,"departement")
 source={"cog_region_2026.csv":hr,"cog_departement_2026.csv":hd,
         "regions-100m.geojson.gz":hgr,"departements-100m.geojson.gz":hgd}
 col,index,rapport=construire(reg,dep,gr,gd,source)
 rapport["contours_autres_territoires_ignores"]={"regions":exr,"departements":exd}
 if exr!=sorted(HORS_ECHELON):raise ValueError("Couverture des territoires complémentaires 2026 inattendue : "+str(exr))
 sortie.mkdir(parents=True,exist_ok=True)
 for path,obj in {**col,"index-2026.json":index,"rapport-2026.json":rapport}.items():
  (sortie/path).write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
 return rapport

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for a in ("regions-geo","departements-geo","regions-cog","departements-cog","sortie"):
  p.add_argument("--"+a,required=True,type=Path)
 args=vars(p.parse_args())
 print(json.dumps(produire(**{k.replace("-","_"):v for k,v in args.items()}),ensure_ascii=False,indent=2))
