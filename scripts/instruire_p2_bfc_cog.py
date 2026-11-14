#!/usr/bin/env python3
"""Préinstruction P2 des cinq candidatures BFC, sur le COG 2026 authentifié.

Les 5 relations documentaires correspondent à 5 événements initiaux, auxquels
s'ajoute la suppression du statut COMD de Mirebel/Crançot/Granges en 2020.
Aucun SKOS exactMatch ni rapport ARK -> ARK n'est approuvé ou publié.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

SHA = {
    "communes": "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
    "mouvements": "8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
}
MOV_FIELDS = ("MOD", "DATE_EFF", "TYPECOM_AV", "COM_AV", "TNCC_AV",
              "NCC_AV", "NCCENR_AV", "LIBELLE_AV", "TYPECOM_AP", "COM_AP",
              "TNCC_AP", "NCC_AP", "NCCENR_AP", "LIBELLE_AP")
# Les groupes sont définis par les preuves exactes et non par une
# déduction de toutes les lignes partageant une date.
EVENTS = [
    {"id": "BFC-P2-2018-25368", "date": "2018-01-01", "mod": "32",
     "type": "creation_commune_nouvelle",
     "reception": "25368", "participants": ("25137", "25368"), "n": 2},
    {"id": "BFC-P2-2016-25529", "date": "2016-01-01", "mod": "32",
     "type": "creation_commune_nouvelle",
     "reception": "25529", "participants": ("25529", "25530"), "n": 2},
    {"id": "BFC-P2-2016-39177", "date": "2016-01-01", "mod": "32",
     "type": "creation_commune_nouvelle_avec_COMD",
     "reception": "39177", "participants": ("39177", "39260", "39332"), "n": 6},
    {"id": "BFC-P2-2020-39177", "date": "2020-03-15", "mod": "35",
     "type": "suppression_statut_communes_deleguees",
     "reception": "39177", "participants": ("39177", "39260", "39332"), "n": 3},
    {"id": "BFC-P2-1974-25527", "date": "1974-06-01", "mod": "33",
     "type": "fusion_association",
     "reception": "25527", "participants": ("25527", "39012"), "n": 3},
    {"id": "BFC-P2-1974-70122", "date": "1974-07-01", "mod": "33",
     "type": "fusion_association",
     "reception": "70122", "participants": ("70122", "52210"), "n": 3},
]
SOURCE_TARGETS = {
    "25368": ("25368", "2018-01-01", "32", "BFC-P2-2018-25368"),
    "25529": ("25529", "2016-01-01", "32", "BFC-P2-2016-25529"),
    "39332": ("39177", "2016-01-01", "32", "BFC-P2-2016-39177"),
    "39012": ("25527", "1974-06-01", "33", "BFC-P2-1974-25527"),
    "52210": ("70122", "1974-07-01", "33", "BFC-P2-1974-70122"),
}
EXPECTED_IDS = {
    "candidate:b4b663cd4579a0313a34",
    "candidate:1d32a3f521a249ec3719",
    "candidate:07401e4a2764a618e4a5",
    "candidate:ce7f1f62d15377591f33",
    "candidate:ce02dcf8b84e34b1d4a6",
}

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def lire(path, champs):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        beginning = f.readline()
        f.seek(0)
        rd = csv.DictReader(f, delimiter=";" if beginning.count(";") > beginning.count(",") else ",")
        if not set(champs) <= set(rd.fieldnames or []):
            raise ValueError("Colonnes absentes: " + str(path))
        return list(rd)

def ecrire(path, rows, fields):
    with Path(path).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def selection_mouvements(e, rows):
    result = [r for r in rows
              if r["DATE_EFF"] == e["date"] and r["MOD"] == e["mod"]
              and r["COM_AV"] in e["participants"]
              and r["COM_AP"] in set(e["participants"]) | {e["reception"]}]
    if len(result) != e["n"]:
        raise ValueError(f"Cardinalité mouvements COG anormale {e['id']}: {len(result)}")
    before = {r["COM_AV"] for r in result}
    if before != set(e["participants"]):
        raise ValueError("Participants COG incomplets: " + e["id"])
    if e["type"] == "suppression_statut_communes_deleguees":
        if not all(r["TYPECOM_AV"] == "COMD" and r["TYPECOM_AP"] == "COM"
                   and r["COM_AP"] == e["reception"] for r in result):
            raise ValueError("MOD35 non conforme: " + e["id"])
    elif e["type"] == "fusion_association":
        associated = [r for r in result if r["TYPECOM_AP"] == "COMA"]
        source = set(e["participants"]) - {e["reception"]}
        if len(associated) != 1 or associated[0]["COM_AP"] not in source or \
           associated[0]["COM_AV"] != associated[0]["COM_AP"]:
            raise ValueError("Association COMA non conforme: " + e["id"])
    elif e["type"] == "creation_commune_nouvelle_avec_COMD":
        if sum(r["TYPECOM_AP"] == "COMD" for r in result) != 3 or \
           sum(r["TYPECOM_AP"] == "COM" and r["COM_AP"] == e["reception"] for r in result) != 3:
            raise ValueError("Création COM/COMD incomplète: " + e["id"])
    else:
        if not all(r["TYPECOM_AV"] == r["TYPECOM_AP"] == "COM"
                   and r["COM_AP"] == e["reception"] for r in result):
            raise ValueError("MOD32 non conforme: " + e["id"])
    return sorted(result, key=lambda r:(r["COM_AV"],r["TYPECOM_AP"],r["COM_AP"]))

def verifier_homonymes(termes):
    if len(termes) != 3:
        raise ValueError("Trois concepts Pactols attendus pour le code 39177")
    idx = {r["qualification_dans_cette_recette"]:r for r in termes}
    if set(idx) != {"commune_nouvelle", "homonyme_autre_departement",
                    "ancienne_commune_code_reutilise"}:
        raise ValueError("Les trois concepts distincts ne sont pas conservés")
    if not (idx["commune_nouvelle"]["ark_pactols"] == "26678/pcrtdDWDTOLZXu"
            and idx["commune_nouvelle"]["code_insee_exactMatch"] == "39177"
            and idx["commune_nouvelle"]["ark_broader"] == "26678/pcrtX910KjTURm"
            and idx["homonyme_autre_departement"]["code_insee_exactMatch"] == "21314"
            and idx["homonyme_autre_departement"]["ark_broader"] == "26678/pcrtGQwa5EVqVh"
            and idx["ancienne_commune_code_reutilise"]["code_insee_exactMatch"] == "39177"
            and idx["ancienne_commune_code_reutilise"]["ark_broader"] ==
            idx["commune_nouvelle"]["ark_pactols"]):
        raise ValueError("Hauteroche Jura / Côte-d'Or / Crançot ambigu")

def produire(candidatures, contexte_39177, communes, mouvements, sortie):
    paths = {"candidatures":Path(candidatures), "contexte_39177":Path(contexte_39177),
             "communes":Path(communes), "mouvements":Path(mouvements)}
    for k in ("communes","mouvements"):
        if sha(paths[k]) != SHA[k]:
            raise ValueError("COG source non conforme : " + k)
    docs = lire(candidatures, ["id_candidature","ark_source","libelle_source","code_source",
                              "ark_cible","libelle_cible","code_cible","date_evenement","MOD",
                              "type_relation_candidate","decision_editoriale","statut_recette"])
    if len(docs) != 5 or {r["id_candidature"] for r in docs} != EXPECTED_IDS or \
       {r["code_source"] for r in docs} != set(SOURCE_TARGETS):
        raise ValueError("Lot de cinq P2 incorrect")
    if any(r["decision_editoriale"] or r["statut_recette"] != "candidat_non_valide"
           for r in docs):
        raise ValueError("Décision éditoriale préexistante interdite")
    hom = lire(contexte_39177, ["ark_pactols","code_insee_exactMatch",
                               "ark_broader","qualification_dans_cette_recette"])
    verifier_homonymes(hom)
    insee = lire(communes, ["TYPECOM","COM","LIBELLE","COMPARENT","DEP","REG"])
    bycode=collections.defaultdict(list)
    for r in insee:bycode[r["COM"]].append(r)
    movements_all = lire(mouvements, MOV_FIELDS)
    records = []
    events = []
    for ev in EVENTS:
        selected = selection_mouvements(ev, movements_all)
        for rec in selected:
            records.append({"evenement_id":ev["id"], **{k:rec[k] for k in MOV_FIELDS}})
        old = sorted({r["COM_AV"]+":"+r["LIBELLE_AV"] for r in selected
                      if r["TYPECOM_AV"] == "COM"})
        receiving = [r for r in bycode[ev["reception"]] if r["TYPECOM"]=="COM"]
        if len(receiving)!=1:
            raise ValueError("Récepteur actuel non univoque : "+ev["reception"])
        events.append({"evenement_id":ev["id"],"date_effet":ev["date"],"MOD":ev["mod"],
                       "nature_administrative":ev["type"],
                       "code_recepteur":ev["reception"],
                       "libelle_commune_actuelle_2026":receiving[0]["LIBELLE"],
                       "participants":"|".join(old or sorted(ev["participants"])),
                       "nb_lignes_cog":len(selected),
                       "source":"Insee COG 2026 v_mvt_commune_2026.csv",
                       "validation_editoriale":"non_valide"})
    if len(records)!=19 or len(events)!=6:
        raise ValueError("Épisodes complets P2 incorrects")

    result=[]
    for doc in docs:
        code=doc["code_source"]
        destination,date,mod,ev_id=SOURCE_TARGETS[code]
        if (doc["code_cible"],doc["date_evenement"],doc["MOD"]) != (destination,date,mod):
            raise ValueError("Candidature incompatible avec le COG pour "+code)
        ev = next(x for x in EVENTS if x["id"]==ev_id)
        assertions = [r for r in movements_all if r["COM_AV"]==code and
                      r["TYPECOM_AV"]=="COM" and r["COM_AP"]==destination and
                      r["TYPECOM_AP"]=="COM" and r["MOD"]==mod and r["DATE_EFF"]==date]
        if len(assertions)!=1 or assertions[0]["LIBELLE_AP"] not in (
            doc["libelle_cible"], "Hauteroche"):
            raise ValueError("Transition source → récepteur non justifiée : "+code)
        current = [r for r in bycode[destination] if r["TYPECOM"]=="COM"]
        if not current or current[0]["LIBELLE"]!=assertions[0]["LIBELLE_AP"]:
            raise ValueError("Libellé de la commune actuelle incohérent")
        if mod=="33":
            associated=[r for r in bycode[code] if r["TYPECOM"]=="COMA"]
            if len(associated)!=1 or associated[0]["COMPARENT"]!=destination:
                raise ValueError("COMPARENT 2026 ne documente pas le rattachement: "+code)
            etat_2026="COMA "+code+" → COMPARENT "+destination
            suite=""
            meaning="fusion_association_et_rattachement_COMA"
        else:
            etat_2026="COM "+destination
            if code==destination:
                if assertions[0]["LIBELLE_AV"]==assertions[0]["LIBELLE_AP"]:
                    raise ValueError("Une commune nouvelle ne peut être inférée d'une identité inchangée")
                meaning="participation_crea_commune_nouvelle_code_reutilise"
                suite=""
            else:
                meaning="participation_crea_commune_nouvelle"
                complement=[r for r in movements_all if r["COM_AV"]==code and
                            r["TYPECOM_AV"]=="COM" and r["TYPECOM_AP"]=="COMD" and
                            r["COM_AP"]==code and r["DATE_EFF"]==date]
                if len(complement)!=1:
                    raise ValueError("COMD de Mirebel à la création de Hauteroche introuvable")
                suppression=[r for r in movements_all if r["COM_AV"]==code and
                             r["TYPECOM_AV"]=="COMD" and r["MOD"]=="35" and
                             r["TYPECOM_AP"]=="COM" and r["COM_AP"]==destination]
                if len(suppression)!=1 or suppression[0]["DATE_EFF"]!="2020-03-15":
                    raise ValueError("Suppression COMD de Mirebel 2020 introuvable")
                suite="BFC-P2-2020-39177"
                etat_2026="COMD Mirebel supprimé le 2020-03-15 ; COM Hauteroche 39177"
        result.append({**doc,
            "evenement_principal_id":ev_id,"evenement_statut_ulterieur_id":suite,
            "nature_documentee":meaning,
            "observation_COG_2026":etat_2026,
            "validation": "non_valide"})
    result.sort(key=lambda x:x["date_evenement"])
    sortie=Path(sortie)
    names=("preinstruction-p2-bfc-5.csv","evenements-p2-bfc-6.csv",
           "preuves-mouvements-p2-bfc-19.csv","contexte-hauteroche-p2-bfc-3.csv",
           "rapport-p2-bfc.json")
    if any((sortie/n).resolve() in {v.resolve() for v in paths.values()} for n in names):
        raise ValueError("Écrasement de source interdit")
    sortie.mkdir(parents=True,exist_ok=True)
    ecrire(sortie/names[0],result,list(result[0]))
    ecrire(sortie/names[1],events,list(events[0]))
    ecrire(sortie/names[2],records,list(records[0]))
    ecrire(sortie/names[3],hom,list(hom[0]))
    summary={
        "etat":"recette_non_validante","candidatures_P2":len(docs),
        "evenements_administratifs_distincts":len(events),
        "mouvements_officiels_avant_apres":len(records),
        "creation_communes_nouvelles":3,
        "fusions_associations":2,
        "evenement_ulterieur_suppression_COMD":1,
        "concepts_homonymes_ou_codes_historiques_39177":3,
        "communes_associees_2026":2,
        "codes_reutilises_communes_nouvelles":2,
        "sha256_sources":{k:sha(v) for k,v in paths.items()},
        "validations_editoriales":0,"nouvelles_equivalences_skos":0,
        "geometries_historiques":0,
        "reserves":[
           "Les cinq relations portent sur des participations ou rattachements, pas sur cinq équivalences entre concepts.",
           "MOD35 en 2020 supprime un statut COMD, pas le toponyme Mirebel.",
           "COMPARENT 2026 n'est pas un identifiant d'identité historique intemporelle.",
           "Le code 39177 et le nom Hauteroche exigent la double qualification Jura/Côte-d'Or.",
        ]}
    (sortie/names[4]).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("candidatures","contexte_39177","communes","mouvements","sortie"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(produire(**vars(a)),ensure_ascii=False,indent=2))
