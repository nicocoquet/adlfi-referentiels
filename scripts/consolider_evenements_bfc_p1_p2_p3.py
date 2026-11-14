#!/usr/bin/env python3
"""Graphe transversal P1/P2/P3 BFC, recette NON VALIDANTE.

Consolide 29 candidatures, 28 groupes de mouvements officiels et 86 lignes
COG (2026). Les groupes sont des unités techniques (DATE_EFF, MOD, COM_AP)
et non nécessairement autant d'actes juridiques. Les anciennes communes
et leurs éventuelles réceptrices restent des concepts Pactols distincts.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

INSEE_SHA = {
    "communes": "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
    "historique": "08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
    "mouvements": "8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
}
MOVE = ("MOD","DATE_EFF","TYPECOM_AV","COM_AV","TNCC_AV","NCC_AV","NCCENR_AV",
        "LIBELLE_AV","TYPECOM_AP","COM_AP","TNCC_AP","NCC_AP","NCCENR_AP","LIBELLE_AP")
SIMPLE_MOVE = ("DATE_EFF","MOD","TYPECOM_AV","COM_AV","LIBELLE_AV",
               "TYPECOM_AP","COM_AP","LIBELLE_AP")
P2_LEGACY = {
    ("2018-01-01","32","25368"): "BFC-P2-2018-25368",
    ("2016-01-01","32","25529"): "BFC-P2-2016-25529",
    ("2016-01-01","32","39177"): "BFC-P2-2016-39177",
    ("2020-03-15","35","39177"): "BFC-P2-2020-39177",
    ("1974-06-01","33","25527"): "BFC-P2-1974-25527",
    ("1974-07-01","33","70122"): "BFC-P2-1974-70122",
}
# Ces sept groupes ont été établis lors des préinstructions P2 et P3.
FOLLOW_UP = {
    ("2020-03-15","35","39177"): 3,
    ("2016-06-01","32","25575"): 2,
    ("2021-03-15","35","25078"): 1,
    ("2020-01-01","35","39530"): 2,
    ("2020-03-15","35","39021"): 3,
    ("2020-03-15","35","39485"): 4,
    ("1997-05-01","34","70477"): 2,
}
SOURCE_FOLLOWUP = {
    "39332": ("2020-03-15","35","39177"),
    "25023": ("2016-06-01","32","25575"),
    "25587": ("2021-03-15","35","25078"),
    "39158": ("2020-01-01","35","39530"),
    "39215": ("2020-03-15","35","39021"),
    "39488": ("2020-03-15","35","39021"),
    "39544": ("2020-03-15","35","39021"),
    "39564": ("2020-03-15","35","39485"),
    "70270": ("1997-05-01","34","70477"),
}
KIND = {"31":"fusion_simple","32":"creation_ou_extension_commune_nouvelle",
        "33":"fusion_association","34":"transformation_fusion_association_en_fusion_simple",
        "35":"suppression_statut_commune_deleguee"}
PROPS = {
    "31":"participation_fusion_simple",
    "32":"participation_mouvement_commune_nouvelle",
    "33":"rattachement_par_fusion_association",
}
REL_FIELDS = ("id_candidature","lot","ark_source","libelle_source","code_source",
              "ark_cible_candidat","libelle_cible","code_cible","date_effet",
              "MOD","type_relation_candidate","niveau_preuve_pactols",
              "evenement_initial_id","evenement_ulterieur_id","preuve_mouvement_id",
              "statut_validation","decision_editoriale","justification_editoriale",
              "verificateur","date_validation")

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):
            h.update(block)
    return h.hexdigest()

def read(path,fields,delimiter=";"):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f,delimiter=delimiter)
        if not set(fields)<=set(rd.fieldnames or []):
            raise ValueError("Colonnes absentes: "+str(path)+" "+str(set(fields)-set(rd.fieldnames or [])))
        return list(rd)

def dump_csv(path,rows,fields):
    with Path(path).open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,delimiter=";",fieldnames=fields,extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)

def canonical(key):
    return "BFC-COG-"+key[0]+"-"+key[1]+"-"+key[2]

def mvt_id(row):
    raw=json.dumps({k:row[k] for k in MOVE},ensure_ascii=False,
                   sort_keys=True,separators=(",",":"))
    return "mvt:"+hashlib.sha256(raw.encode()).hexdigest()[:24]

def state(t,code,name):
    obj={"typecom":t,"code":code,"libelle":name}
    ident="etat:"+hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,
                  separators=(",",":")).encode()).hexdigest()[:24]
    return {"id":ident,**obj}

def selected(key,movs,later):
    date,mod,target=key
    if not later:
        main=[r for r in movs if r["DATE_EFF"]==date and r["MOD"]==mod
              and r["COM_AP"]==target and r["TYPECOM_AV"]=="COM"
              and r["TYPECOM_AP"]=="COM"]
        if len(main)<2 or len({r["COM_AV"] for r in main})!=len(main):
            raise ValueError("Groupe initial ambigu: "+str(key))
        codes={r["COM_AV"] for r in main}
        complements=[r for r in movs if r["DATE_EFF"]==date and r["MOD"]==mod
            and r["TYPECOM_AV"]=="COM" and r["COM_AV"] in codes
            and r["TYPECOM_AP"] in ("COMD","COMA") and r["COM_AP"]==r["COM_AV"]]
        if mod=="33" and not any(r["TYPECOM_AP"]=="COMA" for r in complements):
            raise ValueError("Fusion-association sans COMA: "+str(key))
        if mod=="31" and complements:
            raise ValueError("Fusion simple avec statut additionnel: "+str(key))
        rows=main+complements
    else:
        rows=[r for r in movs if (r["DATE_EFF"],r["MOD"],r["COM_AP"])==key]
        if len(rows)!=FOLLOW_UP[key]:
            raise ValueError("Nombre de lignes d'évolution de statut inattendu: "+str(key))
        if mod in ("34","35") and not all(
              r["TYPECOM_AP"]=="COM" and
              r["TYPECOM_AV"] in (("COMA" if mod=="34" else "COMD"),"COM")
              for r in rows):
            raise ValueError("Statut de destination contradictoire: "+str(key))
        if mod=="32" and not any(r["LIBELLE_AV"]=="Vaire-Arcier"
              and r["LIBELLE_AP"]=="Vaire" and r["COM_AV"]==target for r in rows):
            raise ValueError("Épisode Vaire-Arcier/Vaire non retrouvé")
    if len({mvt_id(r) for r in rows})!=len(rows):
        raise ValueError("Lignes COG dupliquées: "+str(key))
    return sorted(rows,key=mvt_id)

def produire(p1,p1_events,p1_transitions,p2,p3,communes,historique,mouvements,sortie):
    inputs={"p1":Path(p1),"p1_events":Path(p1_events),
            "p1_transitions":Path(p1_transitions),"p2":Path(p2),"p3":Path(p3),
            "communes":Path(communes),"historique":Path(historique),
            "mouvements":Path(mouvements)}
    for role,expected in INSEE_SHA.items():
        if sha(inputs[role])!=expected:
            raise ValueError("Source Insee différente de la version contrôlée: "+role)
    c1=read(p1,("id_candidature","ark_source","libelle_source","code_source","evenement_id",
                 "date_effet","code_cible","libelle_cible","ark_cible_propose",
                 "preuve_pactols","etat","decision_editoriale","date_validation"))
    c2=read(p2,("id_candidature","ark_source","libelle_source","code_source","ark_cible",
                "libelle_cible","code_cible","date_evenement","MOD","niveau_preuve",
                "statut_recette","decision_editoriale","date_validation"))
    c3=read(p3,("id_candidature","ark_source","libelle_source","code_source",
                "ark_cible_candidat","libelle_cible_pactols","code_receptrice",
                "date_evenement_insee","modalite_insee","niveau_preuve_pactols",
                "etat_instruction","decision_editoriale","date_validation"))
    p1_refs=read(p1_events,("evenement_id","date_effet","MOD",
                           "code_commune_nouvelle","source_juridique"))
    p1_evidence=read(p1_transitions,("evenement_id",*SIMPLE_MOVE))
    if (len(c1),len(c2),len(c3),len(p1_refs),len(p1_evidence))!=(4,5,20,2,6):
        raise ValueError("Périmètre P1/P2/P3 modifié")
    if len({r["id_candidature"] for r in c1+c2+c3})!=29:
        raise ValueError("Candidatures dupliquées entre les lots")
    cand=[]
    def add(lot,r,date,mod,dest,target,target_name,proof):
        src=r["code_source"]
        if not (len(src)==len(dest)==5 and src.isdecimal() and dest.isdecimal()):
            raise ValueError("Code Insee d'une relation invalide")
        if not r["ark_source"].startswith("26678/") or \
           (target and not target.startswith("26678/")):
            raise ValueError("ARK documentaire invalide")
        if r["decision_editoriale"] or r["date_validation"]:
            raise ValueError("Décision éditoriale préexistante dans le lot")
        if lot=="P1" and r["etat"]!="a_instruire_non_valide":
            raise ValueError("P1 déclaré validé")
        if lot=="P2" and r["statut_recette"]!="candidat_non_valide":
            raise ValueError("P2 déclaré validé")
        if lot=="P3" and r["etat_instruction"]!="candidat_non_valide":
            raise ValueError("P3 déclaré validé")
        cand.append({
            "id_candidature":r["id_candidature"],"lot":lot,
            "ark_source":r["ark_source"],"libelle_source":r["libelle_source"],
            "code_source":src,"ark_cible_candidat":target,
            "libelle_cible":target_name,"code_cible":dest,
            "date_effet":date,"MOD":mod,
            "type_relation_candidate":PROPS[mod],
            "niveau_preuve_pactols":proof,"key":(date,mod,dest),
            "statut_validation":"a_instruire_non_valide",
            "decision_editoriale":"","justification_editoriale":"",
            "verificateur":"","date_validation":""})
    for r in c1:
        if r["evenement_id"] not in {e["evenement_id"] for e in p1_refs}:
            raise ValueError("Référence P1 inconnue")
        add("P1",r,r["date_effet"],"32",r["code_cible"],r["ark_cible_propose"],
            r["libelle_cible"],r["preuve_pactols"])
    for r in c2:
        add("P2",r,r["date_evenement"],r["MOD"],r["code_cible"],r["ark_cible"],
            r["libelle_cible"],r["niveau_preuve"])
    for r in c3:
        add("P3",r,r["date_evenement_insee"],r["modalite_insee"],
            r["code_receptrice"],r["ark_cible_candidat"],
            r["libelle_cible_pactols"],r["niveau_preuve_pactols"])
    if collections.Counter(r["lot"] for r in cand)!={"P1":4,"P2":5,"P3":20}:
        raise ValueError("Bilan des lots incorrect")
    if sum(bool(r["ark_cible_candidat"]) for r in cand)!=28 or \
       any(r["code_source"]!="71131" for r in cand if not r["ark_cible_candidat"]):
        raise ValueError("Un seul dossier doit rester sans ARK: Verdun-Ciel")
    initial={r["key"] for r in cand}
    if len(initial)!=21 or len(initial&set(P2_LEGACY))!=5 or \
       initial&set(FOLLOW_UP):
        raise ValueError("Groupes administratifs initiaux inattendus")
    if set(SOURCE_FOLLOWUP)-{r["code_source"] for r in cand}:
        raise ValueError("Source d'une étape ultérieure non présente dans les 29 dossiers")
    movements_all=read(mouvements,MOVE,",")
    current=collections.defaultdict(list)
    for r in read(communes,("COM","TYPECOM","LIBELLE","COMPARENT"),","):
        current[r["COM"]].append(r)
    events=[];by_key={};proofs={};states={}
    for key in sorted(initial|set(FOLLOW_UP)):
        later=key in FOLLOW_UP
        items=selected(key,movements_all,later)
        aliases=[]
        if not later:
            if key[1]=="33":
                kind="fusion_association"
            else:kind=KIND[key[1]]
        else:kind=KIND[key[1]]
        names={r["LIBELLE_AP"] for r in items if r["TYPECOM_AP"]=="COM"
               and r["COM_AP"]==key[2]}
        if len(names)!=1:
            raise ValueError("Libellé du récepteur non univoque: "+str(key))
        com=[x for x in current[key[2]] if x["TYPECOM"]=="COM"]
        if len(com)!=1:
            raise ValueError("Commune réceptrice absente du COG2026: "+str(key))
        ids=[]
        for r in items:
            mid=mvt_id(r)
            if mid in proofs:
                raise ValueError("Ligne COG attribuée à plusieurs événements")
            before=state(r["TYPECOM_AV"],r["COM_AV"],r["LIBELLE_AV"])
            after=state(r["TYPECOM_AP"],r["COM_AP"],r["LIBELLE_AP"])
            states[before["id"]]=before
            states[after["id"]]=after
            proofs[mid]={"id":mid,"evenement_id":canonical(key),
                         "etat_avant_id":before["id"],"etat_apres_id":after["id"],
                         **{f:r[f] for f in MOVE}}
            ids.append(mid)
        related=sorted(r["id_candidature"] for r in cand if r["key"]==key)
        if later:
            related=sorted(r["id_candidature"] for r in cand
                           if SOURCE_FOLLOWUP.get(r["code_source"])==key)
        events.append({
            "id":canonical(key),"date_effet":key[0],"MOD":key[1],
            "code_recepteur":key[2],"libelle_recepteur_au_mouvement":next(iter(names)),
            "libelle_commune_2026":com[0]["LIBELLE"],"nature":kind,
            "phase":"ulterieure" if later else "initiale",
            "codes_participants_avant":sorted({r["COM_AV"] for r in items
                                              if r["TYPECOM_AV"]=="COM"}),
            "etats_avant_types":sorted({r["TYPECOM_AV"] for r in items}),
            "etats_apres_types":sorted({r["TYPECOM_AP"] for r in items}),
            "ids_mouvements":sorted(ids),"ids_candidatures_liees":related,
            "statut":"observation_COG_non_validation_AdlFI"})
        by_key[key]=items
    events.sort(key=lambda e:(e["date_effet"],e["MOD"],e["code_recepteur"]))
    if (len(events),len(proofs))!=(28,86) or \
       sum(x["phase"]=="initiale" for x in events)!=21 or \
       sum(x["phase"]=="ulterieure" for x in events)!=7:
        raise ValueError("Cardinalités attendues : 21 + 7 groupes, 86 mouvements")
    # Le P1 devait déjà contenir six des mouvements de notre graphe
    p1_lookups={(r["evenement_id"],tuple(r[k] for k in SIMPLE_MOVE)) for r in p1_evidence}
    actual=set()
    for e in p1_refs:
        key=(e["date_effet"],e["MOD"],e["code_commune_nouvelle"])
        if key not in by_key:raise ValueError("Événement P1 absent du graphe")
        items=by_key[key]
        for row in items:
            actual.add((e["evenement_id"],tuple(row[k] for k in SIMPLE_MOVE)))
    if actual!=p1_lookups or len(actual)!=6:
        raise ValueError("Six preuves avant/après P1 différentes du COG officiel")
    aliases=[]
    for e in p1_refs:
        key=(e["date_effet"],e["MOD"],e["code_commune_nouvelle"])
        aliases.append({"lot":"P1","ancien_id":e["evenement_id"],
                        "id_canonique":canonical(key),"source_juridique":e["source_juridique"]})
    for key,name in P2_LEGACY.items():
        if key not in initial|set(FOLLOW_UP):raise ValueError("P2 perdu")
        aliases.append({"lot":"P2","ancien_id":name,"id_canonique":canonical(key),
                        "source_juridique":""})
    p3keys={r["key"] for r in cand if r["lot"]=="P3"}|set(FOLLOW_UP)-{
        ("2020-03-15","35","39177")}
    if len(p3keys)!=22:
        raise ValueError("P3 doit contenir 22 groupes d'événements")
    for key in p3keys:
        aliases.append({"lot":"P3","ancien_id":P2_LEGACY.get(key,canonical(key)),
                        "id_canonique":canonical(key),"source_juridique":""})
    aliases.sort(key=lambda x:(x["lot"],x["ancien_id"]))
    if len(aliases)!=30 or len({r["id_canonique"] for r in aliases})!=28:
        raise ValueError("Les 30 références de lot ne convergent pas vers 28 événements")
    rels=[]
    for r in cand:
        key=r.pop("key")
        old=[x for x in by_key[key] if x["TYPECOM_AV"]=="COM" and
             x["COM_AV"]==r["code_source"] and x["TYPECOM_AP"]=="COM"
             and x["COM_AP"]==r["code_cible"]]
        if len(old)!=1:
            raise ValueError("Pas de preuve de participation unique pour "+r["id_candidature"])
        later=SOURCE_FOLLOWUP.get(r["code_source"])
        if r["MOD"]=="33":
            associated=[v for v in by_key[key] if v["TYPECOM_AP"]=="COMA"
                        and v["COM_AV"]==r["code_source"]
                        and v["COM_AP"]==r["code_source"]]
            if len(associated)!=1:
                raise ValueError("Participation COMA non documentée: "+r["id_candidature"])
            if r["lot"]=="P2":
                coma=[x for x in current[r["code_source"]] if x["TYPECOM"]=="COMA"]
                if len(coma)!=1 or coma[0]["COMPARENT"]!=r["code_cible"]:
                    raise ValueError("COMPARENT 2026 non conforme: "+r["id_candidature"])
        rels.append({**r,"evenement_initial_id":canonical(key),
                     "evenement_ulterieur_id":canonical(later) if later else "",
                     "preuve_mouvement_id":mvt_id(old[0])})
    rels.sort(key=lambda r:(r["lot"],r["date_effet"],r["code_source"]))
    all_codes={x["code_source"] for x in rels}
    if len(all_codes)!=29:raise ValueError("Une source ARK/COG dupliquée")
    report={
        "schema_version":"1.0.0","etat":"recette_non_validante",
        "lots":{"P1":4,"P2":5,"P3":20},"candidatures":29,
        "ark_cibles_candidats":28,"candidatures_sans_ark_cible":1,
        "evenements_initiaux":21,"evenements_ulterieurs":7,
        "groupes_evenements_uniques":28,"transitions_insee_distinctes":86,
        "etats_administratifs_distincts":len(states),
        "references_evenements_anterieures":30,
        "references_anterieures_dedoublonnees":2,
        "evenements_communs_P2_P3":2,
        "relations_avec_suivi_ulterieur":sum(bool(x["evenement_ulterieur_id"]) for x in rels),
        "empreintes_sources":{k:sha(v) for k,v in inputs.items()},
        "validations_editoriales_nouvelles":0,"nouveaux_exactMatch_skos":0,
        "geometries_historiques_attribuees":0,
        "limites":[
            "Les groupes (DATE_EFF,MOD,COM_AP) sont des unités techniques, pas nécessairement des actes juridiques distincts.",
            "Un code conservé ou un libellé concordant ne crée pas d'identité conceptuelle entre ARK.",
            "Une participation à une fusion ne vaut pas skos:exactMatch.",
            "Les liens COMPARENT sont millésimés 2026 ; aucune rétroprojection géométrique.",
            "Toutes les décisions éditoriales des 29 candidats restent vides.",
        ],
    }
    graph={"schema":"adlfi.lieux.bfc.historique.transversal.recette.v1",
           "provenance":report["empreintes_sources"],
           "evenements":events,
           "mouvements":sorted(proofs.values(),key=lambda x:x["id"]),
           "etats":sorted(states.values(),key=lambda x:x["id"]),
           "relations_candidates":rels,"alias_identifiants_evenements":aliases,
           "nouvelles_validations":[],"geometries_historiques":[]}
    out=Path(sortie)
    names=("graphe-transversal-bfc.json","rapport-transversal-bfc.json",
           "evenements-canoniques-bfc-28.csv",
           "transitions-bfc-86.csv","relations-bfc-29.csv","alias-evenements-bfc-30.csv")
    if any((out/n).resolve() in {p.resolve() for p in inputs.values()} for n in names):
        raise ValueError("Sortie écraserait une source")
    out.mkdir(parents=True,exist_ok=True)
    (out/names[0]).write_text(json.dumps(graph,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (out/names[1]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    erows=[{**e,"codes_participants_avant":"|".join(e["codes_participants_avant"]),
            "etats_avant_types":"|".join(e["etats_avant_types"]),
            "etats_apres_types":"|".join(e["etats_apres_types"]),
            "ids_mouvements":"|".join(e["ids_mouvements"]),
            "ids_candidatures_liees":"|".join(e["ids_candidatures_liees"])} for e in events]
    dump_csv(out/names[2],erows,list(erows[0]))
    dump_csv(out/names[3],sorted(proofs.values(),key=lambda x:x["id"]),
             ["id","evenement_id","etat_avant_id","etat_apres_id",*MOVE])
    dump_csv(out/names[4],rels,REL_FIELDS)
    dump_csv(out/names[5],aliases,list(aliases[0]))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for role in ("p1","p1_events","p1_transitions","p2","p3",
                 "communes","historique","mouvements","sortie"):
        p.add_argument("--"+role.replace("_","-"),required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(produire(**vars(args)),ensure_ascii=False,indent=2))
