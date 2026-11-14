#!/usr/bin/env python3
"""Contrôle d'intégrité du graphe BFC P1/P2/P3, jamais de publication.

Cette validation est technique : elle ne valide aucune identité historique
ni aucune correspondance éditoriale Pactols-COG.
"""
from __future__ import annotations
import argparse
import collections
import json
import re
from pathlib import Path

EVENT_RE=re.compile(r"BFC-COG-(\d{4}-\d\d-\d\d)-(31|32|33|34|35)-([0-9]{5})$")

def controler(graphe):
    g=json.loads(Path(graphe).read_text(encoding="utf-8"))
    if g.get("schema")!="adlfi.lieux.bfc.historique.transversal.recette.v1":
        raise ValueError("Schéma transversal non reconnu")
    ev=g["evenements"];mv=g["mouvements"];st=g["etats"]
    rel=g["relations_candidates"];aliases=g["alias_identifiants_evenements"]
    if (len(ev),len(mv),len(st),len(rel),len(aliases))!=(28,86,83,29,30):
        raise ValueError("Population du graphe inattendue")
    if g["nouvelles_validations"] or g["geometries_historiques"]:
        raise ValueError("Le graphe de recette contient des validations ou des géométries")
    def keyed(rows,key):
        ids=[x[key] for x in rows]
        if len(ids)!=len(set(ids)):raise ValueError("Identifiants dupliqués: "+key)
        return {x[key]:x for x in rows}
    evs=keyed(ev,"id");mvs=keyed(mv,"id");states=keyed(st,"id");rels=keyed(rel,"id_candidature")
    if collections.Counter(x["lot"] for x in rel)!={"P1":4,"P2":5,"P3":20}:
        raise ValueError("Périmètre des trois lots incorrect")
    if sum(bool(x["ark_cible_candidat"]) for x in rel)!=28:
        raise ValueError("Il doit rester un dossier sans ARK (Verdun-Ciel)")
    for e in ev:
        mat=EVENT_RE.fullmatch(e["id"])
        if not mat or (mat.group(1),mat.group(2),mat.group(3)) != (
            e["date_effet"],e["MOD"],e["code_recepteur"]):
            raise ValueError("Identifiant d'événement non canonique: "+e["id"])
        if e["phase"] not in ("initiale","ulterieure") or not e["ids_mouvements"]:
            raise ValueError("Phase ou preuves de l'événement absentes")
        if e["statut"]!="observation_COG_non_validation_AdlFI":
            raise ValueError("Statut d'événement non conforme")
        for p in e["ids_mouvements"]:
            if p not in mvs or mvs[p]["evenement_id"]!=e["id"]:
                raise ValueError("Mouvement non attaché à son événement")
        for rid in e["ids_candidatures_liees"]:
            if rid not in rels:
                raise ValueError("Référence de candidature manquante dans événement")
    for row in mv:
        if row["evenement_id"] not in evs or \
           row["id"] not in evs[row["evenement_id"]]["ids_mouvements"]:
            raise ValueError("Transition orpheline")
        for suffix,tfield,cfield,lfield in (
             ("avant","TYPECOM_AV","COM_AV","LIBELLE_AV"),
             ("apres","TYPECOM_AP","COM_AP","LIBELLE_AP")):
            state_id=row["etat_"+suffix+"_id"]
            if state_id not in states:
                raise ValueError("État administratif manquant")
            s=states[state_id]
            if (s["typecom"],s["code"],s["libelle"]) != (
                row[tfield],row[cfield],row[lfield]):
                raise ValueError("Etat incompatible avec la ligne de mouvement")
    for row in rel:
        init=evs.get(row["evenement_initial_id"])
        if init is None or init["phase"]!="initiale" or \
           row["id_candidature"] not in init["ids_candidatures_liees"]:
            raise ValueError("Candidature non liée à l'événement initial")
        proof=mvs.get(row["preuve_mouvement_id"])
        if not proof or proof["evenement_id"]!=init["id"] or \
           proof["COM_AV"]!=row["code_source"] or \
           proof["COM_AP"]!=row["code_cible"] or \
           proof["TYPECOM_AV"]!="COM" or proof["TYPECOM_AP"]!="COM":
            raise ValueError("Preuve administrative de participation manquante")
        if row["statut_validation"]!="a_instruire_non_valide" or any(
            row[k] for k in ("decision_editoriale","justification_editoriale",
                             "verificateur","date_validation")):
            raise ValueError("Décision éditoriale attribuée à tort")
        if row["evenement_ulterieur_id"]:
            later=evs.get(row["evenement_ulterieur_id"])
            if not later or later["phase"]!="ulterieure" or \
               row["id_candidature"] not in later["ids_candidatures_liees"]:
                raise ValueError("Relation de suivi ultérieur incorrecte")
    if sum(bool(r["evenement_ulterieur_id"]) for r in rel)!=9:
        raise ValueError("Nombre de relations avec suite historique inattendu")
    if sum(e["phase"]=="initiale" for e in ev)!=21:
        raise ValueError("Le graphe doit distinguer 21 groupes initiaux et 7 ultérieurs")
    if len({(x["lot"],x["ancien_id"]) for x in aliases})!=30:
        raise ValueError("Deux références anciennes identiques au sein d'un même lot")
    for a in aliases:
        if a["id_canonique"] not in evs:
            raise ValueError("Alias vers un événement inexistant")
    shared=collections.Counter(x["id_canonique"] for x in aliases)
    if collections.Counter(shared.values())!={1:26,2:2}:
        raise ValueError("Les deux chevauchements P2/P3 ne sont pas isolés")
    if len([a for a in aliases if a["source_juridique"]])!=2:
        raise ValueError("Provenance juridique des deux événements P1 perdue")
    return {
        "schema_valide":True,"evenements":len(ev),"mouvements":len(mv),
        "etats":len(st),"relations":len(rel),"alias":len(aliases),
        "chevauchements_deux_lots":2,"dossiers_sans_cible":1,
        "relations_a_suivre":9,"validations_editoriales":0,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--graphe",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(controler(args.graphe),ensure_ascii=False,indent=2))
