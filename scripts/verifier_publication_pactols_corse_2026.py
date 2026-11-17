#!/usr/bin/env python3
"""Vérifier la publication des 360 couples Pactols–COG corses contre leur registre.

Le fichier de chronologie COG et les géométries ne sont PAS modifiés.
Le registre est la sortie vérifiable du RDF Pactols et du COG 2026 épinglés.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

SOURCE_SHA="3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
FIELDS=("code_insee","libelle_COG_2026","region_COG_2026",
        "departement_COG_2026","ark_pactols","uri_insee",
        "predicat_source","prefLabel_fr_pactols",
        "source_rdf_sha256","statut_validation","portee_COG",
        "type_decision","publication_site")
SCHEMA="adlfi.lieux.pactols.corse.2026.public.v1"

def verifier(index_path:Path,registre_path:Path,chronologie_path:Path,manifest_path:Path):
    published=json.loads(index_path.read_text(encoding="utf-8"))
    cog=json.loads(chronologie_path.read_text(encoding="utf-8"))
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    with registre_path.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f,delimiter=";")
        if tuple(reader.fieldnames or ())!=FIELDS:
            raise ValueError("Colonnes du registre Corse non conformes")
        decisions=list(reader)
    if (len(decisions)!=360 or published.get("schema")!=SCHEMA or
        published.get("region")!="corse" or published.get("millesime_cog")!="2026-01-01" or
        published.get("source_rdf_sha256")!=SOURCE_SHA or
        published.get("nombre_communes")!=360 or
        published.get("nouvelles_geometries")!=0 or
        published.get("liens_historiques_inferes")!=0 or
        published.get("source_registre")!="recette/lieux/CORSE-VALIDATIONS-PACTOLS-COG-2026.csv"):
        raise ValueError("En-tête de la publication Corse incohérent")

    periode={p["code_insee"]:p["libelle"] for p in cog["periodes_com"]
             if p["typecom"]=="COM" and p["debut_inclus"]<="2026-01-01"
             and (not p["fin_exclue"] or p["fin_exclue"]>"2026-01-01")}
    if len(periode)!=360 or cog["alignements_Pactols_COG_valides_2026"]!=[] or cog["geometries_historiques"]!=[]:
        raise ValueError("Le socle chronologique Corse doit rester inchangé")

    seen_codes=set()
    seen_arks=set()
    expected=[]
    for r in decisions:
        c=r["code_insee"]
        ark=r["ark_pactols"]
        if (not c.startswith(("2A","2B")) or len(c)!=5 or
            c not in periode or c in seen_codes or ark in seen_arks or
            periode[c]!=r["libelle_COG_2026"] or
            r["predicat_source"]!="skos:exactMatch" or
            r["uri_insee"]!="http://id.insee.fr/geo/commune/"+c or
            r["source_rdf_sha256"]!=SOURCE_SHA or
            r["statut_validation"]!="VALIDE_ADLFI_2026" or
            r["portee_COG"]!="2026-01-01" or
            r["type_decision"]!="REGLE_EXACTMATCH_UNIVOQUE" or
            r["publication_site"]!="EN_ATTENTE_RECETTE_PUBLICATION"):
            raise ValueError("Décision CSV non prouvée : "+c)
        seen_codes.add(c)
        seen_arks.add(ark)
        expected.append({
           "code_insee":c, "libelle_COG_2026":r["libelle_COG_2026"],
           "ark_pactols":ark,"libelle_pactols":r["prefLabel_fr_pactols"],
           "uri_insee":r["uri_insee"],"predicat_source":"skos:exactMatch",
           "millesime_validation":2026,"date_validation":"2026-11-17",
           "statut":"correspondance_CORSE_validee_2026"
        })
    if seen_codes!=set(periode) or len(seen_arks)!=360:
        raise ValueError("Registre incomplet ou ARK non univoques")
    if published.get("alignements_Pactols_COG_valides_2026")!=expected:
        raise ValueError("Index public ne correspond pas au registre RDF/COG certifié")

    meta=manifest["modules"]["lieux"]["pactols_corse_2026"]
    if (meta["fichier"]!="data/lieux-chronologie/pactols-corse-2026.json" or
        meta["communes"]!=360 or meta["relations_validees"]!=360 or
        meta["portee_COG"]!="2026-01-01" or
        meta["geometries_historiques_validees"]!=0 or
        meta["retroprojections"]!=0):
        raise ValueError("Manifeste Lieux non synchronisé")
    return {"communes":360,"liens_pactols":360,"ark_uniques":360,
            "regions_historiques_modifiees":0,"contours_modifies":0}

def main():
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=root)
    a=p.parse_args()
    d=a.root
    report=verifier(d/"docs/data/lieux-chronologie/pactols-corse-2026.json",
       d/"recette/lieux/CORSE-VALIDATIONS-PACTOLS-COG-2026.csv",
       d/"docs/data/lieux-chronologie/cog-corse.json",
       d/"docs/data/manifest.json")
    print("CORSE_PUBLICATION_360_OK",json.dumps(report,ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
