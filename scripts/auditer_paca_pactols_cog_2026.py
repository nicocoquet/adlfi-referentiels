#!/usr/bin/env python3
"""Audit comparatif PACA 2026 : pilote éditorial 103 / RDF Pactols / COG 946.

Recette NON validante : les 103 décisions du pilote éditorial ne sont pas
révoquées par un écart de RDF, et les nouveaux exactMatch restent candidats.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
from pathlib import Path

from auditer_pactols_polynesie_2026 import analyser_rdf, RDF_SHA, RDF_COMMIT
from auditer_pactols_cog_regions_prioritaires_2026 import qualifier, sha
from preparer_index_cog_national_temporel import SOURCES as COG_SHA

SCHEMA="adlfi.lieux.paca.cog-pactols.2026.audit.v1"


def lire_communes(path: Path) -> dict:
    if sha(path)!=COG_SHA["courant"]:
        raise ValueError("Fichier COG Insee 2026 non conforme")
    communes={}
    with path.open(encoding="utf-8-sig",newline="") as fd:
        reader=csv.DictReader(fd)
        if not {"COM","TYPECOM","REG","DEP","LIBELLE"}.issubset(reader.fieldnames or ()):
            raise ValueError("COG 2026 incomplet")
        for row in reader:
            if row["TYPECOM"]!="COM" or row["REG"]!="93":
                continue
            code=row["COM"]
            if code in communes or not row["LIBELLE"] or row["DEP"] not in {
                "04","05","06","13","83","84"
            }:
                raise ValueError("Commune PACA invalide ou dupliquée : "+code)
            communes[code]={"code":code,"libelle":row["LIBELLE"],
                            "departement":row["DEP"]}
    if len(communes)!=946:
        raise ValueError("PACA : 946 communes COG attendues")
    return communes


def lire_pilote(path:Path,cog:dict) -> dict:
    data=json.loads(path.read_text(encoding="utf-8"))
    if (data.get("totaux",{}).get("autorites_pactols")!=103 or
        data.get("totaux",{}).get("communes_cog")!=103 or
        data.get("totaux",{}).get("geometries")!=103):
        raise ValueError("Pilote historique PACA de 103 autorités modifié")
    pilote={}
    for a in data["autorites"]:
        matches=a["correspondances"]
        if len(matches)!=1 or matches[0]["relation_editoriale"]!="correspondance_communale_validee":
            raise ValueError("Validation du pilote PACA ambiguë")
        code=matches[0]["code_insee"]
        if (code in pilote or code not in cog or
            matches[0]["millesime_cog"]!=2026 or
            matches[0]["libelle_cog"]!=cog[code]["libelle"]):
            raise ValueError("Code ou libellé du pilote PACA divergent")
        pilote[code]={"ark":a["ark_pactols"],"libelle":a["libelle_pactols"],
                      "date_validation":matches[0]["validation"]["date"],
                      "source_validation":matches[0]["validation"]["source"]}
    if len(pilote)!=103 or len({p["ark"] for p in pilote.values()})!=103:
        raise ValueError("103 ARK pilotes uniques attendus")
    return pilote


def croiser(communes:dict,pilote:dict,scan:dict) ->dict:
    rows=[]
    for code,c in sorted(communes.items()):
        hits=scan["explicites"][code]
        status=qualifier(code,c["libelle"],hits)
        precedent=pilote.get(code)
        concordants=[p for p in hits if precedent and p["ark"]==precedent["ark"]]
        rows.append({
            **c,"statut_rdf":status,
            "pilote_103_valide":bool(precedent),
            "ark_pilote":precedent["ark"] if precedent else None,
            "ark_pilote_retrouve_sur_le_code":bool(concordants),
            "arks_exactMatch_dans_rdf":sorted(p["ark"] for p in hits),
            "preuves_RDF_exactMatch":hits,
            "candidats_lexicaux_non_validants":
                scan["lexicaux_sans_exactMatch_987"].get(code,[]),
            "nouvelle_decision_editoriale": "NON_PRISE",
            "publication_cette_recette": "NON_PUBLIEE",
        })
    counts=collections.Counter(p["statut_rdf"] for p in rows)
    pilot=[p for p in rows if p["pilote_103_valide"]]
    return {
        "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
        "sources":{"pactols":{"commit":RDF_COMMIT,"sha256":RDF_SHA},
                   "cog":{"date":"2026-01-01","sha256":COG_SHA["courant"]}},
        "bilan":{
            "communes_COG_PACA_2026":len(rows),
            "pilote_valide_preexistant":len(pilote),
            "pilote_retrouve_par_exactMatch_RDF":sum(x["ark_pilote_retrouve_sur_le_code"] for x in pilot),
            "pilote_non_retrouve_dans_RDF":sum(not x["ark_pilote_retrouve_sur_le_code"] for x in pilot),
            "statuts_RDF":dict(sorted(counts.items())),
            "eligibles_hors_pilote":sum(x["statut_rdf"]=="ELIGIBLE_SELON_REGLE" and not x["pilote_103_valide"] for x in rows),
            "cas_a_instruire_hors_pilote":sum(x["statut_rdf"]!="ELIGIBLE_SELON_REGLE" and not x["pilote_103_valide"] for x in rows),
            "nouveaux_ARK_publies":0,"geometries_ajoutees":0,
            "relations_historiques_inferees":0,
            "concepts_RDF_examines":scan["concepts_RDF_examines"],
        },
        "communes":rows,
        "limites":[
            "Les 103 décisions éditoriales historiques du pilote sont une catégorie de preuve distincte du RDF courant.",
            "Une correspondance d'ARK au RDF ne valide aucune forme géométrique historique.",
            "Les liens RDF hors des 103 autorités restent candidats, sous préflight de toute URI INSEE supplémentaire.",
            "L'appartenance régionale est déterminée par REG=93 du COG 2026, non par le préfixe géographique.",
            "Les limites de 2026 ne sont pas transposées aux périodes antérieures.",
        ]
    }


def audit(rdf:Path,cog:Path,pilote:Path)->dict:
    if sha(rdf)!=RDF_SHA:
        raise ValueError("RDF Pactols non conforme au commit/empreinte épinglés")
    comm=lire_communes(cog)
    pil=lire_pilote(pilote,comm)
    scan=analyser_rdf(rdf,{code:c["libelle"] for code,c in comm.items()})
    return croiser(comm,pil,scan)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf",required=True,type=Path)
    p.add_argument("--cog",required=True,type=Path)
    p.add_argument("--pilote",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Audit de recette nouveau et hors du dossier public docs")
    result=audit(a.rdf,a.cog,a.pilote)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                         encoding="utf-8")
    print("PACA_COG_PACTOLS_BILAN",json.dumps(result["bilan"],ensure_ascii=False,sort_keys=True))


if __name__=="__main__":main()
