#!/usr/bin/env python3
"""Audit non validant des exactMatch Pactols / COG 2026 pour trois régions.

Ne confond pas les identifiants COG communaux 2026 avec les codes historiques
et ne crée ni validation éditoriale ni contour. Analyse le RDF épinglé en flux
et conserve les assertions explicites, ainsi que les homonymies à titre indicatif.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import sys

from auditer_pactols_polynesie_2026 import (
    analyser_rdf, label_compatible, type_confusion, RDF_SHA, RDF_COMMIT,
)
from preparer_index_cog_national_temporel import SOURCES as COG_SHA

REGIONS={"94":"Corse","52":"Pays de la Loire","27":"Bourgogne-Franche-Comté"}
SOURCE="Pactols_Lieux_th17_20260722.rdf"
SCHEMA="adlfi.lieux.pactols-cog.regions-prioritaires.2026.audit.v1"

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()

def communes_actuelles(path:Path)->dict:
    if sha(path)!=COG_SHA["courant"]:
        raise ValueError("Empreinte COG officiel 2026 non conforme")
    records={}
    with path.open(encoding="utf-8-sig",newline="") as f:
        rdr=csv.DictReader(f)
        fields={"TYPECOM","COM","LIBELLE","REG","DEP"}
        if not fields.issubset(rdr.fieldnames or ()):
            raise ValueError("Colonnes COG attendues absentes")
        for row in rdr:
            if row["TYPECOM"]!="COM" or row["REG"] not in REGIONS:
                continue
            code=row["COM"]
            if (len(code)!=5 or code in records or not row["DEP"]
                or not row["LIBELLE"]):
                raise ValueError("Code courant incohérent : "+code)
            records[code]={"code":code,"nom":row["LIBELLE"],
                           "region":row["REG"],"departement":row["DEP"]}
    if not records or set(x["region"] for x in records.values())!=set(REGIONS):
        raise ValueError("Les trois régions doivent être présentes dans le COG")
    return records

def qualifier(code:str,nom:str,hits:list)->str:
    if not hits:
        return "SANS_EXACTMATCH"
    if len(hits)!=1:
        return "A_INSTRUIRE_PLUSIEURS_ARK"
    p=hits[0]
    target=[i for i in p["insee_exactMatch"] if i["famille"]=="commune" and i["code"]==code]
    other=[i for i in p["insee_exactMatch"] if i not in target]
    if (len(target)!=1 or other or p["deprecie"] or p["remplace"] or
        len(p["codes_communaux_cites"])!=1 or len(p["prefLabels_fr"])!=1 or
        type_confusion(p["prefLabels_fr"]) or
        not label_compatible(nom,p["prefLabels_fr"][0])):
        return "A_INSTRUIRE_LIBELLE_STATUT_OU_URI"
    return "ELIGIBLE_SELON_REGLE"

def audit(rdf:Path,cog:Path)->dict:
    if sha(rdf)!=RDF_SHA:
        raise ValueError("RDF Pactols différent du snapshot épinglé")
    names=communes_actuelles(cog)
    scan=analyser_rdf(rdf,{c:p["nom"] for c,p in names.items()})
    rows=[]
    for code,p in sorted(names.items()):
        hits=scan["explicites"][code]
        rows.append({**p,"etat":qualifier(code,p["nom"],hits),
                     "preuves_RDF_exactMatch":hits,
                     "candidats_lexicaux_non_validants":
                        scan["lexicaux_sans_exactMatch_987"].get(code,[]),
                     "decision_editoriale":"NON_PRISE",
                     "publication":"NON_PUBLIE"})
    counts=collections.Counter(r["etat"] for r in rows)
    parts={}
    for reg,name in REGIONS.items():
        subset=[r for r in rows if r["region"]==reg]
        stats=collections.Counter(r["etat"] for r in subset)
        parts[reg]={"nom":name,"communes_COG_2026":len(subset),
                    "codes_avec_exactMatch":sum(bool(r["preuves_RDF_exactMatch"]) for r in subset),
                    "statuts":dict(sorted(stats.items()))}
    return {"schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
            "perimetre":"Communes TYPECOM=COM et REG 94, 52, 27 au COG 2026",
            "pactols":{"commit":RDF_COMMIT,"sha256":RDF_SHA,"fichier":SOURCE},
            "cog":{"date":"2026-01-01","fichier":"v_commune_2026.csv",
                   "sha256":COG_SHA["courant"]},
            "regions":parts,
            "bilan":{"communes_COG":len(rows),"codes_avec_exactMatch":
                       sum(bool(r["preuves_RDF_exactMatch"]) for r in rows),
                     "concepts_RDF_examines":scan["concepts_RDF_examines"],
                     "statuts":dict(sorted(counts.items())),
                     "candidats_lexicaux_non_validants":
                        sum(len(r["candidats_lexicaux_non_validants"]) for r in rows),
                     "nouvelles_validations":0,"nouvelles_geometries":0,
                     "liens_historiques_inferes":0},
            "communes":rows,
            "limitations":[
               "La région est celle du COG 2026, jamais déduite du préfixe communal.",
               "Un exactMatch est une preuve candidate, pas une validation historique.",
               "Les communes associées, déléguées, ARM, DPM et lieux non communaux sont exclus.",
               "Les périodes COG anciennes, fusions et autres identités à instruire sont hors de ce premier lot.",
               "La conformité du libellé est un préflight éditorial et non une preuve d'identité historique.",
               "Le référentiel des 9928 autorités documentaire AdlFI n'est pas une entrée de cet audit : le croisement reste à réaliser.",
            ]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf",required=True,type=Path)
    p.add_argument("--cog",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Répertoire de recette seulement, sortie non existante")
    report=audit(a.rdf,a.cog)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                        encoding="utf-8")
    print("REGIONS_PACTOLS_COG",json.dumps({"regions":report["regions"],
                "bilan":report["bilan"]},ensure_ascii=False,sort_keys=True))
    for row in report["communes"]:
        if row["etat"].startswith("A_INSTRUIRE_"):
            print("REGIONS_ARBITRAGE",json.dumps({"code":row["code"],"nom":row["nom"],
                "region":row["region"],"statut":row["etat"],
                "arks":[x["ark"] for x in row["preuves_RDF_exactMatch"]]},
                ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
