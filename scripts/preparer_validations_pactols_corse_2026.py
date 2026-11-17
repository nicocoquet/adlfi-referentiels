#!/usr/bin/env python3
"""Corse : produire un registre des exactMatch Pactols–COG 2026 éligibles.

Source RDF Pactols et COG 2026 à SHA-256 épinglés. Un registre de décisions
est éditorialement admissible dans la politique du 16 novembre 2026 ;
ce générateur ne publie AUCUN ARK dans l'interface ni aucune géométrie.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import audit

FIELDS=("code_insee","libelle_COG_2026","region_COG_2026",
        "departement_COG_2026","ark_pactols","uri_insee",
        "predicat_source","prefLabel_fr_pactols",
        "source_rdf_sha256","statut_validation","portee_COG",
        "type_decision","publication_site")

def produire(rdf:Path,cog:Path):
    a=audit(rdf,cog)
    rows=[x for x in a["communes"] if x["region"]=="94"]
    if len(rows)!=360 or any(x["etat"]!="ELIGIBLE_SELON_REGLE" for x in rows):
        raise ValueError("Les 360 communes corses doivent être individuellement éligibles")
    records=[]
    arks=set()
    for r in rows:
        hits=r["preuves_RDF_exactMatch"]
        if len(hits)!=1:
            raise ValueError("Plusieurs preuves RDF : "+r["code"])
        p=hits[0];ark=p["ark"];code=r["code"]
        uri=[x["uri"] for x in p["insee_exactMatch"] if
             x["famille"]=="commune" and x["code"]==code]
        if len(uri)!=1 or len(p["insee_exactMatch"])!=1 or ark in arks:
            raise ValueError("Preuve INSEE ou ARK non univoque : "+code)
        arks.add(ark)
        records.append(dict(zip(FIELDS,(
            code,r["nom"],r["region"],r["departement"],ark,uri[0],
            "skos:exactMatch",p["prefLabels_fr"][0],
            a["pactols"]["sha256"],"VALIDE_ADLFI_2026",
            "2026-01-01","REGLE_EXACTMATCH_UNIVOQUE",
            "EN_ATTENTE_RECETTE_PUBLICATION"
        ))))
    records.sort(key=lambda r:r["code_insee"])
    if len(set(r["code_insee"] for r in records))!=360:
        raise ValueError("Code COG corse dupliqué")
    return a,records

def ecrire_csv(rows,out:Path):
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS,delimiter=";",lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf",type=Path,required=True)
    p.add_argument("--cog",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    args=p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Sortie nouvelle, hors répertoire docs")
    a,rows=produire(args.rdf,args.cog)
    ecrire_csv(rows,args.sortie)
    print("CORSE_360_REGISTRE",json.dumps({
        "lignes":len(rows),
        "cog":"2026-01-01",
        "source_rdf_sha256":a["pactols"]["sha256"],
        "sha256_csv":hashlib.sha256(args.sortie.read_bytes()).hexdigest(),
        "departements":{d:sum(r["departement_COG_2026"]==d for r in rows)
                        for d in sorted(set(r["departement_COG_2026"] for r in rows))},
        "nouvelles_relations_publiees":0,
    },sort_keys=True,ensure_ascii=False))
if __name__=="__main__": main()
