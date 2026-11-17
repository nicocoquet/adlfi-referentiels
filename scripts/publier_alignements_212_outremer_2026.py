#!/usr/bin/env python3
"""Reconstituer l'index des 212 alignements communaux ultramarins COG 2026.

Socle 176 de recette épinglé et 36 décisions éditoriales RDF vérifiées.
Aucune inférence historique, géométrique ou inter-échelon.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

CODES_VALIDES={"97501","97502","97607"}
EXCEPTIONS={"97502","98809"}
SOURCE_RDF="Pactols_Lieux_th17_20260722.rdf"
COG_DATE="2026-01-01"
COLONNES=("code_insee","libelle_COG_2026","ark_pactols","uri_insee",
          "predicat_source","source","statut_validation","portee_COG",
          "qualification","note_editoriale")

def produire(socle:dict,registre:Path)->dict:
    if (socle.get("schema")!="adlfi.lieux.recherche.outremer.public.v1"
        or socle.get("cog_ref")!=COG_DATE
        or len(socle["pactols_valides"])!=176
        or socle["ark_confirmes_non_valides"]!={"97607":"26678/crtZcuFSJVYZU"}
        or len(socle["pactols_collectivites_valides"])!=4
        or len(socle["autres"])!=21
        or socle["contours_invalides"]!=["98745","98805"]):
        raise ValueError("Socle documentaire antérieur 176+4 non conforme")

    communes={}
    for group,records in socle["communes"].items():
        for entry in records.splitlines():
            code,label=entry.split("|",1)
            if code in communes or not code.startswith(group):
                raise ValueError("Référence COG 2026 dupliquée ou ambiguë")
            communes[code]=label
    if len(communes)!=212:
        raise ValueError("212 communes COG attendues")

    attendu=CODES_VALIDES|{c for c in communes if c.startswith("988")}
    if len(attendu)!=36:
        raise ValueError("33 communes NC + 2 SPM + 1 Mayotte attendues")
    with registre.open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream,delimiter=";")
        if tuple(reader.fieldnames or ())!=COLONNES:
            raise ValueError("Schéma des décisions 2026 différent")
        lignes=list(reader)
    if len(lignes)!=36 or any(None in r or any(v is None for v in r.values()) for r in lignes):
        raise ValueError("36 décisions complètes exigées")

    new={}
    existants=set(socle["pactols_valides"].values())|set(
        socle["pactols_collectivites_valides"].values())
    for r in lignes:
        code=r["code_insee"];ark=r["ark_pactols"]
        if (code not in attendu or code in new or code in socle["pactols_valides"]
            or communes.get(code)!=r["libelle_COG_2026"]
            or r["uri_insee"]!="http://id.insee.fr/geo/commune/"+code
            or r["predicat_source"]!="skos:exactMatch"
            or r["source"]!=SOURCE_RDF
            or r["statut_validation"]!="VALIDE_ADLFI_2026"
            or r["portee_COG"]!=COG_DATE
            or r["qualification"]!=("EXCEPTION_EDITORIALE_LIBELLE_ILE"
               if code in EXCEPTIONS else "CONFORME_REGLE")
            or not ark.startswith("26678/") or ark in existants
            or ark in new.values()):
            raise ValueError("Preuve, décision ou unicité insuffisante : "+code)
        new[code]=ark
    if set(new)!=attendu or new["97607"]!=socle["ark_confirmes_non_valides"]["97607"]:
        raise ValueError("Dembeni ou couverture 33+2+1 incomplets")

    result=json.loads(json.dumps(socle,ensure_ascii=False))
    result["pactols_valides"]=dict(sorted({**socle["pactols_valides"],**new}.items()))
    result["ark_confirmes_non_valides"]={}
    if (len(result["pactols_valides"])!=212
        or len(set(result["pactols_valides"].values()))!=212
        or set(result["pactols_valides"])!=set(communes)):
        raise ValueError("Publication communale complète non garantie")
    if result["pactols_collectivites_valides"]!=socle["pactols_collectivites_valides"]:
        raise ValueError("Collectivités ne doivent pas changer")
    return result

def canonical(data:dict)->bytes:
    return (json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--socle",type=Path,required=True)
    p.add_argument("--registre",type=Path,required=True)
    p.add_argument("--verifier",type=Path,required=True)
    a=p.parse_args()
    old=json.loads(a.socle.read_text(encoding="utf-8"))
    updated=produire(old,a.registre)
    actual=a.verifier.read_bytes()
    expected=canonical(updated)
    if actual!=expected:
        raise ValueError("Index publié différent de la reconstitution des 36 décisions")
    print("PUBLICATION_PACTOLS_COG_212_OK",
          json.dumps({"communes":len(updated["pactols_valides"]),
           "collectivites":len(updated["pactols_collectivites_valides"]),
           "sans_ARK_confirme_non_valide":len(updated["ark_confirmes_non_valides"])==0,
           "aucun_contour_ajoute":updated["contours_invalides"]==old["contours_invalides"]},
           ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
