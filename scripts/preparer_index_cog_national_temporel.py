#!/usr/bin/env python3
"""Exporter le COG 2026 national, historisé depuis 1943, par préfixe de code.

Les préfixes regroupent des identifiants : ils ne constituent PAS une
géométrie ni une localisation historique. Les couples code-libellé COM/ARM,
les COMA/COMD au 1er janvier 2026 et les mouvements COG sont distincts.
Aucun rapprochement Pactols n'est déduit ou publié.
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, json
from pathlib import Path

SOURCES={
 "historique":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
 "courant":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
 "mouvements":"8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
}
MV=("MOD","DATE_EFF","TYPECOM_AV","COM_AV","TNCC_AV","NCC_AV","NCCENR_AV","LIBELLE_AV",
    "TYPECOM_AP","COM_AP","TNCC_AP","NCC_AP","NCCENR_AP","LIBELLE_AP")
SCHEMA="adlfi.lieux.cog.national.temporel.recette.v1"
def sha(data):
 return hashlib.sha256(data).hexdigest()
def lire(path,required):
 with Path(path).open("r",encoding="utf-8-sig",newline="") as fh:
  rdr=csv.DictReader(fh,delimiter=",")
  if not set(required)<=set(rdr.fieldnames or ()):
   raise ValueError("Colonnes manquantes dans le COG : "+str(path))
  return list(rdr)
def segment(code):
 if len(code)!=5:raise ValueError("Code COG non sur 5 caractères: "+code)
 return code[:2]
def serialiser(obj):
 return (json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf8")
def actif(p,reference):
 return p["debut_inclus"]<=reference and (
  not p["fin_exclue"] or reference<p["fin_exclue"])
def vues_premier_janvier(shard,year):
 if type(year)!=int or not 1943<=year<=2026:raise ValueError("Année incorrecte")
 at=f"{year}-01-01"
 return {
  "date_reference":at,
  "COM":[r for r in shard["periodes_COM"] if actif(r,at)],
  "ARM":[r for r in shard["periodes_ARM"] if actif(r,at)],
  "COMA_COMD_observes":shard["observations_COMA_COMD_2026"] if year==2026 else [],
  "mouvements_survenus":[r for r in shard["mouvements"] if r["date_effet"]<=at],
  "contours_historiques":[],
 }
def construire(historique,courant,mouvements,sortie):
 paths={n:Path(v) for n,v in (("historique",historique),("courant",courant),("mouvements",mouvements))}
 for n,path in paths.items():
  if sha(path.read_bytes())!=SOURCES[n]:raise ValueError("COG 2026 non conforme SHA-256 : "+n)
 hist=lire(historique,("TYPECOM","COM","LIBELLE","DATE_DEBUT","DATE_FIN"))
 curr=lire(courant,("TYPECOM","COM","LIBELLE","COMPARENT","DEP","REG"))
 moves=lire(mouvements,MV)
 counts=collections.Counter(r["TYPECOM"] for r in curr)
 if (len(hist),len(moves))!=(42333,13734) or counts!={"COM":34875,"COMD":2105,"COMA":471,"ARM":45}:
  raise ValueError("Cardinalités COG 2026 inattendues")
 shards=collections.defaultdict(lambda:{"periodes_COM":[],"periodes_ARM":[],
               "observations_COMA_COMD_2026":[],"observations_COM_ARM_2026":[],
               "mouvements":[]})
 percode=collections.defaultdict(list);lex=collections.defaultdict(set)
 zero_duration=[]
 for r in hist:
  if r["TYPECOM"] not in ("COM","ARM"):raise ValueError("Historique TYPECOM non prévu")
  code=r["COM"];date0=r["DATE_DEBUT"];date1=r["DATE_FIN"] or None
  if not (len(date0)==10 and (date1 is None or (len(date1)==10 and date0<=date1))):
   raise ValueError("Dates COG incohérentes : "+code)
  if date1==date0:
   zero_duration.append({"code_insee":code,"libelle":r["LIBELLE"],"date":date0})
  period={"code_insee":code,"typecom":r["TYPECOM"],"libelle":r["LIBELLE"],
          "debut_inclus":date0,"fin_exclue":date1}
  shards[segment(code)]["periodes_"+r["TYPECOM"]].append(period)
  lex[code].add(r["LIBELLE"])
  if r["TYPECOM"]=="COM":percode[code].append(period)
 if len(percode)!=39117 or sum(len(v) for v in percode.values())!=42288:
  raise ValueError("Index national COM incomplet")
 for code,terms in percode.items():
  prev=None
  for p in sorted(terms,key=lambda x:x["debut_inclus"]):
   if prev is not None and (prev["fin_exclue"] is None or prev["fin_exclue"]>p["debut_inclus"]):
    raise ValueError("Chevauchement de périodes COM : "+code)
   prev=p
 for r in curr:
  code=r["COM"];t=r["TYPECOM"]
  if t in ("COM","ARM"):
   shards[segment(code)]["observations_COM_ARM_2026"].append(
    {"code_insee":code,"typecom":t,"libelle":r["LIBELLE"],
     "departement_COG_2026":r["DEP"],"region_COG_2026":r["REG"],
     "date_observation":"2026-01-01"})
   if t=="COM":
    matches=[p for p in percode[code] if p["fin_exclue"] is None and
             p["libelle"]==r["LIBELLE"]]
    if len(matches)!=1:raise ValueError("COM actuelle différente de la période ouverte : "+code)
  else:
   if t not in ("COMA","COMD") or not r["COMPARENT"]:
    raise ValueError("Statut courant inattendu : "+code)
   shards[segment(code)]["observations_COMA_COMD_2026"].append(
    {"code_insee":code,"typecom":t,"libelle":r["LIBELLE"],
     "comparent_COG_2026":r["COMPARENT"],"departement_COG_2026":r["DEP"],
     "date_observation":"2026-01-01"})
   lex[code].add(r["LIBELLE"])
 moves_global=set()
 sans_avant=0;sans_apres=0
 for r in moves:
  if not r["COM_AV"]:sans_avant+=1
  if not r["COM_AP"]:sans_apres+=1
  # SHA sur toutes les colonnes officielles pour dédoublonnage inter-segments.
  full={k:r[k] for k in MV}
  ident="mvt:"+sha(serialiser(full))[:24]
  if ident in moves_global:raise ValueError("Mouvement dupliqué dans la source Insee")
  moves_global.add(ident)
  entry={"id":ident,"date_effet":r["DATE_EFF"],"MOD":r["MOD"],
         "typecom_avant":r["TYPECOM_AV"],"code_avant":r["COM_AV"],
         "libelle_avant":r["LIBELLE_AV"],"typecom_apres":r["TYPECOM_AP"],
         "code_apres":r["COM_AP"],"libelle_apres":r["LIBELLE_AP"]}
  # MOD 20/30 : l'Insee peut déclarer une création sans code AV
  # ou une disparition administrative sans code AP. Ne rien inventer.
  codes=[r[k] for k in ("COM_AV","COM_AP") if r[k]]
  if not codes:raise ValueError("Mouvement sans code avant ET après")
  for group in {segment(code) for code in codes}:
   shards[group]["mouvements"].append(entry)
 if len(shards)!=98 or len(moves_global)!=13734 or (sans_avant,sans_apres)!=(127,2):
  raise ValueError("Segmentation nationale COG incohérente")
 out=Path(sortie)
 if any((out/name).resolve() in {p.resolve() for p in paths.values()}
        for name in ("manifest-cog-national.json","index-toponymes-cog.json")):
  raise ValueError("Sortie identique à une source COG")
 segdir=out/"segments";segdir.mkdir(parents=True,exist_ok=True)
 metas=[];written={}
 for group,data in sorted(shards.items()):
  for values in data.values():
   values.sort(key=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True))
  blob={"schema":SCHEMA,"etat":"recette_non_publiee",
        "prefixe_code":group,"reference":"instant_au_1er_janvier",
        "annee_min":1943,"annee_max":2026,
        "avertissement":"Préfixe de CODE, non département géographique historique.",
        **data,"geometries_historiques":[],"validations_editoriales":[]}
  file=f"cog-{group}.json"
  raw=serialiser(blob);(segdir/file).write_bytes(raw)
  written[file]=raw
  metas.append({"prefixe_code":group,"fichier":"segments/"+file,
    "sha256":sha(raw),"octets":len(raw),
    "periodes_COM":len(data["periodes_COM"]),
    "periodes_ARM":len(data["periodes_ARM"]),
    "observations_COMA_COMD_2026":len(data["observations_COMA_COMD_2026"]),
    "lignes_mouvements_concernees":len(data["mouvements"])})
 # Index lexical COG historique : ce n'est PAS une table de relations Pactols.
 names=[{"code_insee":code,"libelles_attestes":sorted(values)}
        for code,values in sorted(lex.items())]
 lexicon={"schema":SCHEMA,"etat":"recette_non_publiee",
  "nature":"index_COG_par_code_et_noms_attestes_sans_relations_Pactols",
  "entrees":names}
 idx=serialiser(lexicon)
 (out/"index-toponymes-cog.json").write_bytes(idx)
 manifest={"schema":SCHEMA,"statut":"recette_non_publiee",
   "millesime_COG":2026,"annee_min":1943,"annee_max":2026,
   "annee_initiale":2026,"date_reference":"AAAA-01-01",
   "index_toponymes":{"fichier":"index-toponymes-cog.json",
                       "sha256":sha(idx),"entrees":len(names)},
   "segments":metas,
   "periodes_sans_duree":sorted(zero_duration,key=lambda x:x["code_insee"]),
   "mouvements_sans_commune_avant":sans_avant,
   "mouvements_sans_commune_apres":sans_apres,
   "statistiques":{"codes_historiques_COM":39117,
     "periodes_COM":42288,"periodes_ARM":45,
     "communes_COM_2026":34875,"communes_deleguees_2026":2105,
     "communes_associees_2026":471,"arrondissements_municipaux_2026":45,
     "mouvements_COG_uniques":13734,"segments":len(shards)},
   "provenance_sha256":{n:sha(path.read_bytes()) for n,path in paths.items()},
   "garanties":["Périodes COM et ARM seulement pour l'historique depuis 1943.",
     "Statuts COMD/COMA uniquement observés au millésime 2026.",
     "Les deux lignes COG de durée nulle sont conservées mais jamais actives au curseur.",
     "MOD 20/30 peut produire des mouvements sans commune avant ou après ; conserver le côté vide officiel.",
     "Événements et changements de périmètre distincts des changements de libellé.",
     "Le préfixe de code ne constitue pas un département de localisation historique.",
     "Aucun ARK attribué à partir du code ni des libellés.",
     "Aucune géométrie historique ou relation éditoriale publiée."]}
 (out/"manifest-cog-national.json").write_bytes(serialiser(manifest))
 return manifest

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for role in ("historique","courant","mouvements","sortie"):
  p.add_argument("--"+role,required=True,type=Path)
 a=p.parse_args()
 m=construire(**vars(a))
 print(json.dumps({"statistiques":m["statistiques"],
                   "index_toponymes":m["index_toponymes"],
                   "nombre_segments":len(m["segments"])},ensure_ascii=False,indent=2))
