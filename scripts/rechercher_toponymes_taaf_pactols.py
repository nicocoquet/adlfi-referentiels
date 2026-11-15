#!/usr/bin/env python3
"""Recherche exploratoire de noms courts TAAF dans Pactols-Lieux th17.

NE PRODUIT AUCUN ALIGNEMENT. La forme « Kerguelen » peut désigner un archipel,
une île ou un district ; un rapprochement de nom n'identifie pas sa portée.
Les termes ci-dessous sont des chaînes de RECHERCHE, non des altLabel Pactols
ni des variantes COG validées.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from auditer_pactols_outremer_integral import RDF, SKOS, OWL, LANG, apercu_concept, digest, norm, SHA_PACTOLS

RECHERCHES = {
    "COMER:TERRITOIRE:984": (
        "Terres australes et antarctiques françaises", "TAAF",
    ),
    "COMER:DIS:98411": (
        "Îles Saint-Paul et Amsterdam", "Saint-Paul et Amsterdam",
        "Saint-Paul et île Amsterdam",
    ),
    "COMER:DIS:98412": (
        "Kerguelen", "Îles Kerguelen", "Archipel Kerguelen",
        "Archipel des Kerguelen",
    ),
    "COMER:DIS:98413": (
        "Crozet", "Îles Crozet", "Archipel Crozet", "Archipel des Crozet",
    ),
    "COMER:DIS:98414": (
        "Terre Adélie", "Terre-Adélie",
    ),
    "COMER:DIS:98415": (
        "Îles Éparses", "Îles Éparses de l'océan Indien",
    ),
}
COLONNES = (
    "cible_cog","terme_de_recherche","label_pactols","type_label",
    "ark_pactols","uri_concept","labels_pref_fr","labels_alt_fr",
    "labels_hidden_fr","relations_broader_litterales","exact_match_litteraux",
    "deprecie","statut","avis_editorial",
)

def rechercher(rdf: Path, min_concepts: int = 30000):
    inverse=collections.defaultdict(list)
    for target, termes in RECHERCHES.items():
        for term in termes:
            inv=norm(term)
            if inv:
                inverse[inv].append((target,term))
    found={}
    n=0;depth=0;root=None
    for event, elem in ET.iterparse(rdf,events=("start","end")):
        if event=="start":
            depth+=1
            if depth==1:
                root=elem
                if elem.tag!=RDF+"RDF":
                    raise ValueError("Document non RDF/XML")
            continue
        if depth==2:
            if elem.tag in (SKOS+"Concept",RDF+"Description"):
                concept=apercu_concept(elem)
                if concept:
                    n+=1
                    broader=sorted(set(
                        ch.get(RDF+"resource","") for ch in elem
                        if ch.tag==SKOS+"broader" and ch.get(RDF+"resource")
                    ))
                    for k in ("pref","alt","hidden"):
                        for label in concept[k]:
                            for target,terme in inverse.get(norm(label),()):
                                key=(target,concept["ark"],k,norm(terme))
                                found[key]={
                                    "cible_cog":target,"terme_de_recherche":terme,
                                    "label_pactols":label,"type_label":k,
                                    "ark_pactols":concept["ark"],"uri_concept":concept["uri"],
                                    "labels_pref_fr":json.dumps(concept["pref"],ensure_ascii=False),
                                    "labels_alt_fr":json.dumps(concept["alt"],ensure_ascii=False),
                                    "labels_hidden_fr":json.dumps(concept["hidden"],ensure_ascii=False),
                                    "relations_broader_litterales":json.dumps(broader,ensure_ascii=False),
                                    "exact_match_litteraux":json.dumps(concept["exact"],ensure_ascii=False),
                                    "deprecie":"oui" if concept["deprecie"] else "non",
                                    "statut":"indice_lexical_non_validant",
                                    "avis_editorial":"A_INSTRUIRE",
                                }
            elem.clear()
            if root is not None: root.clear()
        depth-=1
    if n<min_concepts:
        raise ValueError(f"Export RDF intégral non reconnu : {n} concepts")
    result=sorted(found.values(),key=lambda x:(
        x["cible_cog"],x["ark_pactols"],x["type_label"],x["terme_de_recherche"]
    ))
    return n,result

def produire(rdf:Path,sortie:Path,controle_sha=True):
    rdf,sortie=Path(rdf),Path(sortie)
    sha=digest(rdf)
    if controle_sha and sha!=SHA_PACTOLS:
        raise ValueError("Empreinte RDF Frantiq inattendue")
    if "docs" in sortie.resolve().parts:
        raise ValueError("Sortie de recette interdite dans docs/")
    if sortie.resolve().is_relative_to(rdf.resolve().parent):
        raise ValueError("Sortie dans le répertoire de source RDF interdite")
    nb,items=rechercher(rdf,min_concepts=30000 if controle_sha else 1)
    sortie.mkdir(parents=True,exist_ok=True)
    with (sortie/"recherche_toponymes_taaf_pactols.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=COLONNES,delimiter=";")
        w.writeheader();w.writerows(items)
    counts=collections.Counter(x["cible_cog"] for x in items)
    unique={target:sorted(set(x["ark_pactols"] for x in items if x["cible_cog"]==target))
            for target in RECHERCHES}
    report={
        "schema":"adlfi.lieux.pactols.taaf.noms_de_recherche.v1",
        "statut":"RECETTE_EXPLORATOIRE_NON_VALIDANTE",
        "snapshot_pactols":"2026-07-22",
        "sha256_rdf":sha,
        "nb_concepts_examines":nb,"nb_lignes_indice":len(items),
        "nb_ark_par_cible":{k:len(v) for k,v in unique.items()},
        "ark_candidats_par_cible":unique,
        "methode":"Recherche d'égalité normalisée avec formes de recherche exploratoires, sans inférence COG",
        "nouveaux_alignements_valides":0,
    }
    (sortie/"rapport_recherche_toponymes_taaf_pactols.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(produire(**vars(a)),ensure_ascii=False,indent=2))
