#!/usr/bin/env python3
"""Préinstruction P3 BFC : 20 ARK, 16 mouvements initiaux et 6 ultérieurs.

Conserve les lignes officielles COG 2026, sans créer d'alignement ni de
géométrie historique. Deux événements utilisent les mêmes ID qu'en P2.
"""
import argparse,collections,csv,hashlib,json
from pathlib import Path

SHAS={"communes":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
      "historique":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
      "mouvements":"8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1"}
MOV=("MOD","DATE_EFF","TYPECOM_AV","COM_AV","TNCC_AV","NCC_AV","NCCENR_AV","LIBELLE_AV",
     "TYPECOM_AP","COM_AP","TNCC_AP","NCC_AP","NCCENR_AP","LIBELLE_AP")
PER=("TYPECOM","COM","TNCC","NCC","NCCENR","LIBELLE","DATE_DEBUT","DATE_FIN")
EXISTING_P2={("2018-01-01","32","25368"):"BFC-P2-2018-25368",
             ("2016-01-01","32","25529"):"BFC-P2-2016-25529"}
# (date, modalité, COM réceptrice) : (nature, nb lignes COG attendues)
AFTER={
 ("2016-06-01","32","25575"):("commune_nouvelle_Vaire_apres_Vaire_Arcier",2),
 ("2021-03-15","35","25078"):("suppression_statut_COMD",1),
 ("2020-01-01","35","39530"):("suppression_statut_COMD",2),
 ("2020-03-15","35","39021"):("suppression_statut_COMD",3),
 ("2020-03-15","35","39485"):("suppression_statut_COMD",4),
 ("1997-05-01","34","70477"):("transformation_fusion_association_en_fusion_simple",2)}
AFTER_SOURCE={
 "25023":("2016-06-01","32","25575"),"25587":("2021-03-15","35","25078"),
 "39158":("2020-01-01","35","39530"),"39215":("2020-03-15","35","39021"),
 "39488":("2020-03-15","35","39021"),"39544":("2020-03-15","35","39021"),
 "39564":("2020-03-15","35","39485"),"70270":("1997-05-01","34","70477")}
TYPES={"31":"fusion_simple","32":"creation_ou_extension_commune_nouvelle",
       "33":"fusion_association","34":"transformation_fusion_association_en_fusion_simple",
       "35":"suppression_statut_COMD"}

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()

def read(path,fields,sep):
 with Path(path).open("r",encoding="utf-8-sig",newline="") as f:
  rd=csv.DictReader(f,delimiter=sep)
  if not set(fields)<=set(rd.fieldnames or []):raise ValueError("Colonnes absentes: "+str(path))
  return list(rd)

def stable_id(key):
 return EXISTING_P2.get(key) or "BFC-COG-"+key[0]+"-"+key[1]+"-"+key[2]

def movement_id(row):
 return "cog:"+hashlib.sha256(json.dumps({k:row[k] for k in MOV},
        sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()[:24]

def group_later(key,moves):
 date,mod,dest=key
 nature,count=AFTER[key]
 group=[r for r in moves if (r["DATE_EFF"],r["MOD"],r["COM_AP"])==key]
 if len(group)!=count:raise ValueError("Événement ultérieur incomplet: "+str(key))
 if mod in ("34","35") and not all(r["TYPECOM_AP"]=="COM" and
      r["TYPECOM_AV"] in (("COMA" if mod=="34" else "COMD"),"COM")
      for r in group):
  raise ValueError("Statut COG 34/35 invalide")
 if mod=="32" and not any(r["LIBELLE_AV"]=="Vaire-Arcier" and
     r["LIBELLE_AP"]=="Vaire" and r["COM_AV"]==dest for r in group):
  raise ValueError("Épisode Vaire-Arcier -> Vaire non prouvé")
 return sorted(group,key=movement_id),nature

def csvwrite(path,rows,fields):
 with Path(path).open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter=";",extrasaction="ignore")
  w.writeheader();w.writerows(rows)

def generer(candidatures,communes,historique,mouvements,sortie):
 paths={name:Path(value) for name,value in locals().copy().items() if name in
        ("candidatures","communes","historique","mouvements")}
 for role in SHAS:
  if sha(paths[role])!=SHAS[role]:raise ValueError("COG officiel modifié: "+role)
 p3=read(candidatures,("id_candidature","niveau_priorite","code_source","ark_source",
     "date_evenement_insee","modalite_insee","code_receptrice","libelle_receptrice_insee",
     "ark_cible_candidat","decision_editoriale","etat_instruction"),";")
 if len(p3)!=20 or len({x["id_candidature"] for x in p3})!=20 or \
    len({x["ark_source"] for x in p3})!=20 or any(
     not x["niveau_priorite"].startswith("P3") or x["decision_editoriale"] or
     x["etat_instruction"]!="candidat_non_valide" or not x["ark_cible_candidat"]
     for x in p3):
  raise ValueError("Lot P3 incomplet ou déjà validé")
 if collections.Counter(x["modalite_insee"] for x in p3)!={"31":4,"32":15,"33":1}:
  raise ValueError("Types de mouvements du lot modifiés")
 initial_keys={(x["date_evenement_insee"],x["modalite_insee"],x["code_receptrice"])
               for x in p3}
 if len(initial_keys)!=16 or not set(EXISTING_P2)<=initial_keys or \
    {x["code_source"] for x in p3 if x["code_source"] in AFTER_SOURCE}!=set(AFTER_SOURCE):
  raise ValueError("Périmètre de mouvements et de suivis modifié")
 mv=read(mouvements,MOV,",")
 current=collections.defaultdict(list)
 for r in read(communes,("COM","TYPECOM","LIBELLE","COMPARENT","DEP"),","):
  current[r["COM"]].append(r)
 events=[];by_key={};proofs={}
 for key in sorted(initial_keys|set(AFTER)):
  date,mod,dest=key;phase="initiale" if key in initial_keys else "ulterieure"
  if phase=="initiale":
   main=[r for r in mv if (r["DATE_EFF"],r["MOD"],r["COM_AP"],r["TYPECOM_AV"],
                r["TYPECOM_AP"])==(date,mod,dest,"COM","COM")]
   if len(main)<2 or len({r["COM_AV"] for r in main})!=len(main):
    raise ValueError("Participants initiaux manquants: "+str(key))
   members={r["COM_AV"] for r in main}
   supplements=[r for r in mv if r["DATE_EFF"]==date and r["MOD"]==mod
      and r["TYPECOM_AV"]=="COM" and r["COM_AV"] in members
      and r["TYPECOM_AP"] in ("COMD","COMA") and r["COM_AP"]==r["COM_AV"]]
   group=main+supplements
   nature=TYPES[mod]
  else:
   group,nature=group_later(key,mv)
   main=group;supplements=[]
  eid=stable_id(key)
  if len({movement_id(r) for r in group})!=len(group):
   raise ValueError("Lignes dupliquées dans "+eid)
  names={r["LIBELLE_AP"] for r in group if r["COM_AP"]==dest and r["TYPECOM_AP"]=="COM"}
  valid=[r for r in current[dest] if r["TYPECOM"]=="COM"]
  if len(names)!=1 or len(valid)!=1:
   raise ValueError("Libellé cible COG non univoque: "+eid)
  for r in group:
   mid=movement_id(r)
   if mid in proofs:raise ValueError("Ligne COG appartient à deux événements")
   proofs[mid]={"evenement_id":eid,"preuve_id":mid,**{f:r[f] for f in MOV}}
  related=[r["id_candidature"] for r in p3 if
     ((r["date_evenement_insee"],r["modalite_insee"],r["code_receptrice"])==key
       if phase=="initiale" else AFTER_SOURCE.get(r["code_source"])==key)]
  events.append({"evenement_id":eid,"phase":phase,"date_effet":date,
      "MOD":mod,"nature_insee":nature,"code_receptrice":dest,
      "libelle_recepteur_a_date":next(iter(names)),
      "libelle_COM_2026":valid[0]["LIBELLE"],
      "participants_codes":"|".join(sorted({r["COM_AV"] for r in main})),
      "statuts_apres":"|".join(sorted({r["TYPECOM_AP"] for r in group})),
      "nb_lignes_COM":len(main),"nb_lignes_statut_complementaire":len(supplements),
      "nb_lignes_total":len(group),
      "ids_candidatures_P3":"|".join(sorted(related)),
      "evenement_deja_P2":"oui" if key in EXISTING_P2 else "non",
      "source":"Insee COG 2026 v_mvt_commune_2026.csv",
      "validation":"non_valide"})
  by_key[key]=(eid,main,group)
 events.sort(key=lambda r:(r["date_effet"],r["MOD"],r["code_receptrice"]))
 if (len(events),len(proofs))!=(22,65) or sum(r["nb_lignes_total"] for r in events
      if r["phase"]=="initiale")!=51 or sum(r["nb_lignes_total"] for r in events
      if r["phase"]=="ulterieure")!=14:
  raise ValueError("Cardinalités 22 événements/65 mouvements inattendues")
 checked=[]
 for r in p3:
  key=(r["date_evenement_insee"],r["modalite_insee"],r["code_receptrice"])
  eid,main,group=by_key[key]
  old=[m for m in main if m["COM_AV"]==r["code_source"] and m["TYPECOM_AV"]=="COM"]
  if len(old)!=1 or old[0]["LIBELLE_AP"]!=r["libelle_receptrice_insee"]:
   raise ValueError("Transition source absente: "+r["ark_source"])
  if any(v["TYPECOM"] in ("COM","COMD","COMA") for v in current[r["code_source"]]):
   raise ValueError("Ancienne commune encore présente au COG 2026: "+r["code_source"])
  com=next(x for x in current[r["code_receptrice"]] if x["TYPECOM"]=="COM")
  extra=AFTER_SOURCE.get(r["code_source"])
  alerts=[]
  if com["LIBELLE"]!=r["libelle_receptrice_insee"]:
   alerts.append("libelle_receptrice_evolue_depuis_evenement")
  if any(m["COM_AV"]==m["COM_AP"] and m["LIBELLE_AV"]==m["LIBELLE_AP"]
         for m in main):
   alerts.append("nom_code_recepteur_stables_perimetre_modifie")
  if extra:alerts.append("suivi_evenement_ulterieur")
  if key in EXISTING_P2:alerts.append("evenement_deja_instruite_P2")
  rel={"31":"participation_fusion_simple",
       "32":"participation_creation_ou_extension_commune_nouvelle",
       "33":"fusion_association_rattachement_ancien_COMA"}[r["modalite_insee"]]
  checked.append({**r,"evenement_initial_id":eid,
      "type_relation_affine":rel,"preuve_ligne_COG":movement_id(old[0]),
      "libelle_recepteur_COG2026":com["LIBELLE"],
      "evenement_ulterieur_id":stable_id(extra) if extra else "",
      "alertes":"|".join(alerts),"preinstruction":"documentee_non_validee"})
 checked.sort(key=lambda r:(r["date_evenement_insee"],r["code_source"]))
 codes={r["code_source"] for r in p3}|{r["code_receptrice"] for r in p3}|{"25576"}
 periods=[r for r in read(historique,PER,",") if r["COM"] in codes]
 periods.sort(key=lambda r:(r["COM"],r["DATE_DEBUT"],r["TYPECOM"]))
 report={"statut":"recette_non_validante","dossiers_P3":20,
   "evenements_initiaux_distincts":16,"evenements_initiaux_deja_P2":2,
   "evenements_ulterieurs_distincts":6,"evenements_tous":22,
   "lignes_initiales_COG":51,"lignes_ulterieures_COG":14,
   "lignes_COG_uniques":65,
   "repartition_MOD_dossiers":dict(sorted(collections.Counter(r["modalite_insee"]
       for r in p3).items())),
   "anciens_avec_suppression_COMD_ulterieure":6,
   "ancien_avec_transformation_COMA_ulterieure":1,
   "ancien_dont_recepteur_evolue_en_2016":1,
   "periodes_code_libelle":len(periods),
   "source_sha256":{k:sha(v) for k,v in paths.items()},
   "validations_nouvelles":0,"equivalences_Skos_nouvelles":0,
   "geometries_historiques":0,
   "limites":["Les événements ne prouvent pas une identité intemporelle entre ARK.",
      "MOD32 peut garder le même code et le même nom tout en modifiant le périmètre.",
      "Les épisodes P2 Marchaux et Sancey ne sont pas dupliqués.",
      "MOD34/35 est une transformation de statut et non une nouvelle fusion.",
      "Vaire-Arcier 1974 et Vaire 2016 sont deux épisodes distincts.",
      "Les périodes de noms ne sont pas des géométries historiques."]}
 out=Path(sortie)
 names=("preinstruction-p3-20.csv","evenements-p3-22.csv",
        "preuves-mouvements-p3-65.csv","periodes-noms-p3.csv","rapport-p3.json")
 if any((out/n).resolve() in {v.resolve() for v in paths.values()} for n in names):
  raise ValueError("Source écrasée")
 out.mkdir(parents=True,exist_ok=True)
 csvwrite(out/names[0],checked,list(checked[0]))
 csvwrite(out/names[1],events,list(events[0]))
 csvwrite(out/names[2],[proofs[k] for k in sorted(proofs)],["evenement_id","preuve_id",*MOV])
 csvwrite(out/names[3],periods,PER)
 (out/names[4]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return report

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("candidatures","communes","historique","mouvements","sortie"):
  p.add_argument("--"+n,type=Path,required=True)
 opts=p.parse_args()
 print(json.dumps(generer(**vars(opts)),ensure_ascii=False,indent=2))
