#!/usr/bin/env python3
"""Recette non validante des codes PDL 2026 ayant plusieurs ARK Pactols."""
from __future__ import annotations
import argparse, collections, csv, json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import audit

SCHEMA="adlfi.lieux.pdl.multiple-ark.2026.audit.v1"

def construire(audit_regional:dict, chronologie:dict)->dict:
    lignes=[r for r in audit_regional["communes"] if r["region"]=="52"
            and r["etat"]=="A_INSTRUIRE_PLUSIEURS_ARK"]
    evenements=chronologie["lignes_mouvements_cog"]
    sortie=[]
    for row in lignes:
        code=row["code"]
        candidats=row["preuves_RDF_exactMatch"]
        if len({p["ark"] for p in candidats})<2:
            raise ValueError("Multiplicité ARK absente : "+code)
        mouvements=[{k:e.get(k) for k in ("id","date_effet","mod","code_avant",
                     "code_apres","libelle_avant","libelle_apres",
                     "typecom_avant","typecom_apres")}
                   for e in evenements
                   if e.get("code_apres")==code or e.get("code_avant")==code]
        mouvements.sort(key=lambda e:(e["date_effet"] or "",e["id"] or ""))
        # Les modifications COG constituent des indices de tri, jamais des liens ARK.
        communes_nouvelles=[e for e in mouvements
                           if e["mod"]=="32" and e["code_apres"]==code]
        sortie.append({"code_COG_2026":code,"libelle_COG_2026":row["nom"],
                       "departement":row["departement"],
                       "nombre_ARK":len(candidats),
                       "candidats_RDF":candidats,
                       "mouvements_COG_documentes":mouvements,
                       "evenement_creation_commune_nouvelle":bool(communes_nouvelles),
                       "priorite_instruction":("COMMUNE_NOUVELLE" if communes_nouvelles
                                               else "AUTRE_MULTIPLICITE"),
                       "ark_retenu":None,
                       "decision_editoriale":"NON_PRISE",
                       "publication":"NON_PUBLIE"})
    sortie.sort(key=lambda x:(x["priorite_instruction"]!="COMMUNE_NOUVELLE",
                              x["code_COG_2026"]))
    compte=collections.Counter(r["priorite_instruction"] for r in sortie)
    return {"schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
            "sources":{"pactols":audit_regional["pactols"],
                       "cog":audit_regional["cog"],
                       "chronologie":"docs/data/lieux-chronologie/cog-pdl.json"},
            "bilan":{"codes_ARK_multiples":len(sortie),
                     "repartition":dict(sorted(compte.items())),
                     "nouveaux_alignements":0,"liens_historiques_inferes":0,
                     "nouvelles_geometries":0},
            "communes":sortie,
            "limites":["La présence de plusieurs exactMatch vers un même code ne rend pas les concepts équivalents.",
                       "Les mouvements COG sont des indices de classement, non des assertions de correspondance avec les ARK.",
                       "Une sélection d'ARK exige une décision éditoriale spécifique et une preuve datée."]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf",required=True,type=Path)
    p.add_argument("--cog",required=True,type=Path)
    p.add_argument("--chronologie",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Écriture limitée à une nouvelle sortie de recette hors docs")
    regional=audit(a.rdf,a.cog)
    chronologie=json.loads(a.chronologie.read_text(encoding="utf-8"))
    resultat=construire(regional,chronologie)
    if resultat["bilan"]["codes_ARK_multiples"]!=60:
        raise ValueError("Nombre de codes multiples inattendu : "+
                         str(resultat["bilan"]["codes_ARK_multiples"]))
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(resultat,ensure_ascii=False,indent=2,
                                   sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"bilan":resultat["bilan"],
                      "communes_nouvelles":[{"code":r["code_COG_2026"],
                                            "nom":r["libelle_COG_2026"],
                                            "arks":[c["ark"] for c in r["candidats_RDF"]]}
                                           for r in resultat["communes"] if
                                           r["priorite_instruction"]=="COMMUNE_NOUVELLE"]},
                     ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
