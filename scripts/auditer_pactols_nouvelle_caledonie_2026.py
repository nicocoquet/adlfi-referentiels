#!/usr/bin/env python3
"""Nouvelle-Calédonie : qualifier les 33 communes COG 2026 face au RDF Pactols.

Réutilise l'analyse RDF du lot polynésien, avec le socle historique NC officiel.
N'assimile ni îles ni tribus, provinces ou aires coutumières à une commune ;
aucune décision de validation ou géométrie n'est créée.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from auditer_cog_nouvelle_caledonie_2026 import analyser as analyser_cog
from auditer_pactols_polynesie_2026 import (
    analyser_rdf, label_compatible, type_confusion,
    RDF_SHA, RDF_COMMIT, sha,
)

CODES_EXCLUS=("collectiviteDOutreMer/988",)
def qualifier(code,nom,hits):
    if not hits:
        return "SANS_ASSERTION_EXPLICITE"
    if len(hits)!=1:
        return "A_INSTRUIRE_MULTIPLICITE"
    h=hits[0]
    matching=[u for u in h["insee_exactMatch"] if u["famille"]=="commune" and u["code"]==code]
    other=[u for u in h["insee_exactMatch"] if u not in matching]
    if (len(matching)!=1 or other or h["deprecie"] or h["remplace"] or
        len(h["codes_communaux_cites"])!=1 or len(h["prefLabels_fr"])!=1 or
        type_confusion(h["prefLabels_fr"]) or
        not label_compatible(nom,h["prefLabels_fr"][0])):
        return "A_INSTRUIRE_ONTOLOGIE_OU_DIVERGENCE"
    return "ELIGIBLE_SELON_REGLE"

def rapport(rdf:Path,cog_dir:Path,index:Path)->dict:
    if sha(rdf)!=RDF_SHA:
        raise ValueError("RDF Pactols différent du snapshot du 22 juillet 2026")
    cog=analyser_cog(cog_dir,index)
    communes={item["code"]:item["libelle"] for item in cog["communes_COG_2026"]}
    if len(communes)!=33 or set(c[:3] for c in communes)!={"988"}:
        raise ValueError("33 communes COG de Nouvelle-Calédonie requises")
    matches=analyser_rdf(rdf,communes)
    rows=[]
    for code,nom in sorted(communes.items()):
        hits=matches["explicites"][code]
        decision=qualifier(code,nom,hits)
        rows.append({
            "code_COG_2026":code,
            "libelle_COG_2026":nom,
            "nature_zonage_COG":"COM",
            "statut":decision,
            "preuves_RDF_exactMatch":hits,
            "candidats_lexicaux_non_validants":matches["lexicaux_sans_exactMatch_987"].get(code,[]),
            "nombre_concepts_exactMatch":len(hits),
            "alignement_publie":False,
            "decision_editoriale":"NON_PRISE",
        })
    labels={r["code_COG_2026"] for r in rows}
    assert len(labels)==33
    compteur=Counter(r["statut"] for r in rows)
    return {
        "schema":"adlfi.lieux.nouvelle-caledonie.pactols-cog2026.audit.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "sources":{
            "pactols":{"commit":RDF_COMMIT,"sha256":RDF_SHA},
            "cog_2026":cog["sources"]["sha256_COG"],
        },
        "territoire":"988",
        "communes_COG_2026":rows,
        "concepts_RDF_examines":matches["concepts_RDF_examines"],
        "bilan":{
           "communes_COG":33,
           "codes_avec_exactMatch":sum(x["nombre_concepts_exactMatch"]>0 for x in rows),
           "concepts_exactMatch_total":sum(x["nombre_concepts_exactMatch"] for x in rows),
           "statuts":dict(sorted(compteur.items())),
           "codes_avec_candidats_lexicaux":sum(bool(x["candidats_lexicaux_non_validants"]) for x in rows),
           "alignements_automatiques":0,
           "nouveaux_ark":0,
           "contours_publies":0,
           "communes_rattachees_a_province_unique":0,
        },
        "particularites_hors_alignement":{
            "Kouaoua":"98833 : épisode COG ouvert en 1995 (division de Canala)",
            "Poya":"98827 : commune répartie entre provinces Nord et Sud",
            "provinces":3,
            "aires_coutumieres":8,
            "ARK_territoire_988_inferre":False,
        },
        "publication":{"nouvelles_relations":0,"nouveaux_contours":0,"nouveaux_ARK":0}
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("rdf","cog_dir","index_public","sortie"):
        parser.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=parser.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette hors docs, sans écrasement")
    d=rapport(a.rdf,a.cog_dir,a.index_public)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("NC_PACTOLS_BILAN",json.dumps(d["bilan"],ensure_ascii=False,sort_keys=True))
    for r in d["communes_COG_2026"]:
        print("NC_PACTOLS_CODE",json.dumps({
            "code":r["code_COG_2026"],"nom":r["libelle_COG_2026"],
            "statut":r["statut"],
            "arks":[h["ark"] for h in r["preuves_RDF_exactMatch"]],
        },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
