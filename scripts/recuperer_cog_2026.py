#!/usr/bin/env python3
"""Acquérir le COG Insee 2026 sans dépendance à un artefact GitHub expirant.

Sources : téléchargement Insee 2026 (ZIP et CSV individuels), puis miroir
du jeu de données public de l'Insee sur data.gouv.fr. La signature SHA-256
de chaque CSV fait foi : un téléchargement d'un autre millésime est rejeté.
Aucune donnée privée ni aucune modification des sources existantes.
"""
from __future__ import annotations
import argparse, hashlib, io, json, re, time, urllib.error, urllib.parse
import urllib.request, zipfile
from pathlib import Path

ROOT="https://www.insee.fr/fr/statistiques/fichier/8740222/"
BUNDLE=ROOT+"cog_ensemble_2026_csv.zip"
DATAGOUV="https://www.data.gouv.fr/api/1/datasets/code-officiel-geographique-1/"
EXPECTED={
 "v_commune_2026.csv":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
 "v_commune_depuis_1943.csv":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
 "v_mvt_commune_2026.csv":"8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
}
UA="AdlFI-Cog-2026-public-source-audit/1"
def sha(buf):
 return hashlib.sha256(buf).hexdigest()
def valid(name,buf):
 return name in EXPECTED and sha(buf)==EXPECTED[name]
def get(url,timeout=25):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/zip,application/json,text/csv,*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as resp:
  if resp.status!=200:raise ValueError("Statut HTTP inattendu")
  return resp.read(15_000_000)
def from_zip(data):
 out={}
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  for info in z.infolist():
   name=Path(info.filename).name
   if name not in EXPECTED:continue
   if info.file_size>10_000_000 or (info.file_size and info.compress_size==0):
    raise ValueError("Entrée ZIP anormale")
   raw=z.read(info)
   if not valid(name,raw):raise ValueError("Source COG du ZIP différente du snapshot contrôlé: "+name)
   if name in out:raise ValueError("CSV dupliqué dans le ZIP")
   out[name]=raw
 return out
def api_mirror_data(data):
 obj=json.loads(data)
 resources=obj.get("resources") or []
 result={}
 # Les URLs proviennent des métadonnées publiques du producteur du COG ;
 # les noms sont seulement des indices. Le SHA-256 doit toujours correspondre.
 for item in resources:
  label=(item.get("title") or "").casefold()
  url=item.get("url") or ""
  if "2026" not in label or not url.startswith("https://"):continue
  if "communes depuis 1943" in label:
   name="v_commune_depuis_1943.csv"
  elif ("évènements" in label or "événements" in label) and "communes" in label:
   name="v_mvt_commune_2026.csv"
  elif "communes" in label and "1943" not in label and "outre-mer" not in label and "territoires" not in label:
   name="v_commune_2026.csv"
  else:continue
  if name not in result:result[name]=[]
  result[name].append(url)
 return result

def obtenir(sortie,allow_mirror=True,fichiers=None):
 required=set(EXPECTED) if fichiers is None else set(fichiers)
 if not required or not required.issubset(EXPECTED):
  raise ValueError('Sélection de sources COG inconnue ou vide')
 target=Path(sortie)
 target.mkdir(parents=True,exist_ok=True)
 found={};sources={};errors=[]
 def collect(rows,origin):
  for name,raw in rows.items():
   if name not in required:continue
   if not valid(name,raw):
    raise ValueError("Contrôle SHA-256 échoué pour "+name+" depuis "+origin)
   if name not in found:found[name]=raw;sources[name]=origin
 # Pour un seul fichier, privilégier d'abord le CSV direct plutôt que l'archive complète.
 if len(required)==1:
  name=next(iter(required))
  try:collect({name:get(ROOT+name)},ROOT+name)
  except (urllib.error.URLError,OSError,ValueError) as e:
   errors.append(name+': '+str(e)[:190])
 if not found:
  try:
   collect(from_zip(get(BUNDLE)),BUNDLE)
  except (urllib.error.URLError,OSError,ValueError,zipfile.BadZipFile) as e:
   errors.append("archive_Insee: "+str(e)[:190])
 for name in sorted(required):
  if name in found:continue
  try:
   data=get(ROOT+name)
   collect({name:data},ROOT+name)
  except (urllib.error.URLError,OSError,ValueError) as e:
   errors.append(name+": "+str(e)[:190])
 if allow_mirror and required.difference(found):
  try:
   res=api_mirror_data(get(DATAGOUV))
   for name in sorted(required):
    if name in found:continue
    for url in res.get(name,[]):
     try:
      data=get(url)
      if valid(name,data):
       collect({name:data},url)
       break
     except (urllib.error.URLError,OSError,ValueError) as e:
      errors.append("miroir "+name+": "+str(e)[:150])
  except (urllib.error.URLError,OSError,ValueError) as e:
   errors.append("métadonnées data.gouv.fr: "+str(e)[:190])
 missing=sorted(required-set(found))
 if missing:
  raise RuntimeError("Sources COG 2026 indisponibles ou non conformes SHA-256 : "+",".join(missing)+" ; "+str(errors))
 # Aucune écriture avant contrôle complet : refuse les vieux contenus.
 for name,data in sorted(found.items()):
  dst=target/name
  if dst.exists() and dst.read_bytes()!=data:
   raise ValueError("Refus d'écraser une source COG préexistante différente")
 for name,data in sorted(found.items()):
  (target/name).write_bytes(data)
 result={"date_source":"2026-01-01","source_officielle":"Insee / Code officiel géographique 2026",
         "mode_acquisition":"sources publiques contrôlées sans artefact GitHub",
         "fichiers":{name:{"sha256":EXPECTED[name],"source_telechargement":sources[name],
                          "octets":len(found[name])} for name in sorted(found)},
         "erreurs_non_bloquantes":errors}
 (target/"provenance-cog-2026.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return result

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--sortie",required=True,type=Path)
 p.add_argument("--communes-seulement",action="store_true",
                help="Acquérir seulement v_commune_2026.csv après contrôle SHA-256")
 a=p.parse_args()
 print(json.dumps(obtenir(a.sortie,fichiers={'v_commune_2026.csv'} if a.communes_seulement else None),ensure_ascii=False,indent=2))
