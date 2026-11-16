#!/usr/bin/env python3
"""Guyane : états COG annuels, événements sourcés, autorités disparues.

Reçoit le rapport du lot Guyane 01 (sources INSEE 2026 épinglées) et les
registres éditoriaux AdlFI. N'exporte ni frontière ni succession non attestée.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path

SCHEMA="adlfi.lieux.guyane.chronologie.1943-2026.recette.v1"
YEARS=range(1943,2027)
CODES_HISTORIQUES={"97351","97354","97355","97359"}
MOD={
 "10":"Changement de nom",
 "20":"Création",
 "21":"Rétablissement",
 "30":"Suppression",
 "31":"Fusion simple",
 "32":"Création de commune nouvelle",
 "33":"Fusion association",
 "34":"Transformation de fusion association en fusion simple",
}
IMPORTANTES=("1946-03-21","1953-01-01","1969-03-27",
             "1976-11-12","1989-01-01","1993-01-01")


def serializer(obj: object) -> bytes:
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,
                       separators=(",",":"))+"\n").encode("utf8")


def lire_csv(path: Path, colonnes: set[str]) -> list[dict]:
    with path.open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream,delimiter=";")
        if set(reader.fieldnames or ()) != colonnes:
            raise ValueError("Structure de registre inattendue : "+path.name)
        rows=list(reader)
    if not rows or any(None in row or not all(row.values()) for row in rows):
        raise ValueError("Registre de décisions incomplet")
    return rows


def actif(p: dict, instant: str) -> bool:
    return p["debut_inclus"]<=instant and (
        p["fin_exclue"] is None or instant<p["fin_exclue"])


def etat(episodes: list[dict], instant: str) -> list[dict]:
    active=[{"code":r["code"],"libelle":r["libelle"],
             "debut_documente":r["debut_inclus"],
             "fin_exclue":r["fin_exclue"],
             "statut_relation_Pactols_historique":"NON_INFERABLE_DE_2026",
             "geometrie":None}
            for r in episodes if actif(r,instant)]
    active.sort(key=lambda x:x["code"])
    if len({x["code"] for x in active})!=len(active):
        raise ValueError("Deux identités simultanées pour un même code COG")
    return active


def preparer(audit: dict, validees: list[dict],
             anciennes: list[dict]) -> dict:
    if (audit.get("schema")!="adlfi.lieux.guyane.audit.cog-pactols-geom.v1" or
        audit.get("bilan",{}).get("communes_COG_2026")!=22 or
        audit["bilan"]["codes_distincts_historiques_973"]!=26 or
        audit["bilan"]["periodes_historiques_973"]!=41 or
        audit["bilan"]["mouvements_impliquant_code_973"]!=52):
        raise ValueError("Rapport d'audit Guyane incompatible")
    episodes=audit["historique_codes_973"]
    events=audit["mouvements_source_avec_code_973"]
    if len(episodes)!=41 or len(events)!=52 or len(validees)!=22 or len(anciennes)!=4:
        raise ValueError("Cardinalités sources Guyane non conformes")
    codes_by_period=collections.defaultdict(list)
    for p in episodes:
        if (p["fichier_source"]!="v_commune_depuis_1943.csv" or
            p["geometrie_historique"] is not None or
            p["identite_juridique_retroactive"]!="NON_ETABLIE"):
            raise ValueError("Observation COG non conforme")
        date.fromisoformat(p["debut_inclus"])
        if p["fin_exclue"]:date.fromisoformat(p["fin_exclue"])
        codes_by_period[p["code"]].append(p)
    if len(codes_by_period)!=26 or (
        set(codes_by_period)-{r["code_COG_2026"] for r in audit["communes"]})!=CODES_HISTORIQUES:
        raise ValueError("Codes historiques non conformes")
    for code,ps in codes_by_period.items():
        periods=sorted(ps,key=lambda p:p["debut_inclus"])
        for prev,nxt in zip(periods,periods[1:]):
            if prev["fin_exclue"] is None or prev["fin_exclue"]>nxt["debut_inclus"]:
                raise ValueError("Périodes chevauchantes pour "+code)
    current={r["code_COG_2026"]:r for r in audit["communes"]}
    validations={}
    for row in validees:
        code,ark=row["code_insee"],row["ark_pactols"]
        if (code in validations or code not in current or
            row["libelle_COG_2026"]!=current[code]["libelle_COG_2026"] or
            row["statut_validation"]!="VALIDE_ADLFI_2026" or
            row["portee_COG"]!="2026-01-01" or
            row["predicat_source"]!="exactMatch" or
            row["concept_deprecie"]!="non"):
            raise ValueError("Validation actuelle Guyane incompatible")
        validations[code]=ark
    if len(set(validations.values()))!=22:raise ValueError("ARK réutilisé")
    attendus={
        x["code_insee_cite"]:x
        for x in audit["bilan"]["source_Pactols_stats"]["liens_insee_non_courants"]
    }
    if set(attendus)!=CODES_HISTORIQUES:
        raise ValueError("Les 4 liens historiques Pactols de l'audit ont changé")
    old_index={}
    for row in anciennes:
        code=row["code_insee_historique"]
        src=attendus.get(code)
        if (not src or code in old_index or
            row["ark_pactols"]!=src["ark"] or
            row["uri_insee"]!=src["uri_insee"] or
            row["predicat_source"]!=src["predicat"] or
            row["predicat_source"]!="exactMatch" or
            row["statut_historique"]!="CONCEPT_PACTOLS_HISTORIQUE_A_INSTRUIRE" or
            src["concept_deprecie"] or src["concept_remplace"] or
            src["codes_communes_INSEE_exactMatch"]!=[code]):
            raise ValueError("Autorité historique Pactols non justifiée : "+code)
        ps=sorted(codes_by_period[code],key=lambda x:x["debut_inclus"])
        old_index[code]={
            "code_insee_historique":code,
            "libelles_COG_attestes":[x["libelle"] for x in ps],
            "periodes_COG":ps,
            "ark_Pactols_candidat":src["ark"],
            "URI_INSEE_citee":src["uri_insee"],
            "source_relation":"skos:exactMatch / Pactols RDF juillet 2026",
            "statut":"AUTORITE_HISTORIQUE_DISTINCTE_NON_VALIDEE",
            "successeur_COG":"A_INSTRUIRE_A_PARTIR_DES_MOUVEMENTS",
            "correspondance_avec_commune_2026":None,
            "geometrie_historique":None,
        }
    if len(old_index)!=4:raise ValueError("Quatre identités anciennes attendues")

    vues=[]
    for year in YEARS:
        instant=f"{year}-01-01"
        rows=etat(episodes,instant)
        vues.append({"date_reference":instant,"annee":year,
                     "source":"Insee COG 2026 / communes depuis 1943",
                     "couverture":"NON_DOCUMENTEE_DANS_LE_FICHIER" if not rows
                           else "ETAT_COG_DOCUMENTE",
                     "communes":rows,"total":len(rows),
                     "geometries_historiques_publiees":0,
                     "interpretation_identite_Pactols":"NON_RETROPROJETEE"})
    if {x["code"] for x in vues[-1]["communes"]}!=set(current):
        raise ValueError("Etat 2026 différent des 22 communes validées")
    for row in vues[-1]["communes"]:
        if row["libelle"]!=current[row["code"]]["libelle_COG_2026"]:
            raise ValueError("Toponymie historique et COG actuel contradictoires")

    evenements=[]
    par_date=collections.defaultdict(list)
    for e in events:
        day=e["DATE_EFF"]
        date.fromisoformat(day)
        if not (e["COM_AV"].startswith("973") or e["COM_AP"].startswith("973")):
            raise ValueError("Mouvement hors Guyane")
        mod=e["MOD"]
        row={
            "date_effet_COG":day,
            "code_modalite":mod,
            "modalite":MOD.get(mod,"Modalité COG à instruire"),
            "avant":{"code":e["COM_AV"] or None,"type":e["TYPECOM_AV"] or None,
                     "libelle":e["LIBELLE_AV"] or None},
            "apres":{"code":e["COM_AP"] or None,"type":e["TYPECOM_AP"] or None,
                     "libelle":e["LIBELLE_AP"] or None},
            "preuve":"v_mvt_commune_2026.csv",
            "relation_historique_reciproque_validee":False,
            "transformation_geographique_demontree":False,
        }
        evenements.append(row)
        par_date[day].append(row)
    evenements.sort(key=lambda x:(x["date_effet_COG"],x["code_modalite"],
                         x["avant"]["code"] or "",x["apres"]["code"] or "",
                         x["avant"]["libelle"] or "",x["apres"]["libelle"] or ""))
    dates=[]
    for day,rows in sorted(par_date.items()):
        d=date.fromisoformat(day)
        before=etat(episodes,(d-timedelta(days=1)).isoformat())
        after=etat(episodes,day)
        dates.append({
            "date_effet_COG":day,"lignes_mouvements":len(rows),
            "codes_avant":sorted({x["avant"]["code"] for x in rows
                                  if x["avant"]["code"]}),
            "codes_apres":sorted({x["apres"]["code"] for x in rows
                                  if x["apres"]["code"]}),
            "modalites_COG":dict(sorted(collections.Counter(
                x["code_modalite"] for x in rows).items())),
            "etat_COG_avant":len(before),
            "etat_COG_apres":len(after),
            "codes_actifs_avant":sorted(x["code"] for x in before),
            "codes_actifs_apres":sorted(x["code"] for x in after),
            "delta_nombre_communes":len(after)-len(before),
            "remarque":"Ce sont des événements INSEE à cette date, non des contours géographiques.",
        })
    stats={
        "communes_COG_2026":22,
        "codes_distincts_historique":len(codes_by_period),
        "periodes_COG":len(episodes),
        "lignes_mouvements_COG":len(evenements),
        "dates_mouvements_distinctes":len(dates),
        "codes_historiques_disparus":len(old_index),
        "liens_Pactols_actuels_valides_2026":len(validations),
        "liens_Pactols_historiques_valides":0,
        "geometries_historiques_validees":0,
        "nouvelles_succession_inferrees":0,
        "etats_annuels":len(vues),
        "premiere_observation_COG":min(x["debut_inclus"] for x in episodes),
    }
    return {
        "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIEE",
        "portee":"Code officiel géographique 1943–2026 : identité administrative et mouvements, sans contours historiques",
        "validations_Pactols_2026":validations,
        "autorites_historiques_candidats":list(old_index.values()),
        "etats_1er_janvier":vues,
        "mouvements_COG_sans_succession_inferree":evenements,
        "bilans_par_date_effet":dates,
        "statistiques":stats,
        "geometries_historiques":[],
        "incertitudes":[
            "Les données COG ne garantissent pas une couverture effective au 1er janvier 1943.",
            "La date d'effet du COG peut différer d'un jour de la date présentée sur le portail historique Insee.",
            "L'état du premier janvier précédant une transformation dans la même année n'est pas l'état de fin d'année.",
            "Les codes anciens restent distincts des codes actuels ; les mouvements ne prouvent pas la continuité géométrique.",
            "Les 22 ARK validés pour COG 2026 ne sont pas automatiquement valides pour les années antérieures.",
            "Aucun contour de 2026, 2015, 1997 ou autre millésime n'est projeté rétroactivement.",
        ],
    }


def produire(audit: Path, validations: Path, historiques: Path, sortie: Path) -> dict:
    files=[Path(audit),Path(validations),Path(historiques)]
    out=Path(sortie).resolve()
    if "docs" in out.parts or out.exists() and any(out.iterdir()) or any(
         out==p.resolve() or out.is_relative_to(p.resolve().parent) for p in files):
        raise ValueError("Sortie interdite ou déjà occupée")
    raw=json.loads(files[0].read_text(encoding="utf8"))
    rows=lire_csv(files[1],{"code_insee","libelle_COG_2026","ark_pactols",
          "uri_insee","predicat_source","concept_deprecie","statut_validation",
          "portee_COG","prefLabel_fr_pactols"})
    old=lire_csv(files[2],{"code_insee_historique","ark_pactols","uri_insee",
             "predicat_source","statut_historique"})
    report=preparer(raw,rows,old)
    out.mkdir(parents=True,exist_ok=False)
    fichiers={
        "guyane-etats-1943-2026.json":{
            "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIEE",
            "etats":report["etats_1er_janvier"]},
        "guyane-evenements-1943-2026.json":{
            "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIEE",
            "evenements":report["mouvements_COG_sans_succession_inferree"],
            "groupes_date":report["bilans_par_date_effet"]},
        "guyane-autorites-historiques.json":{
            "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIEE",
            "candidats":report["autorites_historiques_candidats"]},
    }
    for name,payload in fichiers.items():
        (out/name).write_bytes(serializer(payload))
    manifest={
        "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIEE",
        "sources_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in files},
        "sorties_sha256":{name:hashlib.sha256(serializer(v)).hexdigest()
                         for name,v in fichiers.items()},
        "statistiques":report["statistiques"],
        "restrictions":report["incertitudes"],
        "nouvelles_relations_Pactols":0,
        "nouvelles_geometries":0,
    }
    (out/"manifest-guyane-chronologie.json").write_bytes(serializer(manifest))
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("audit","validations","historiques","sortie"):
        p.add_argument("--"+key,required=True,type=Path)
    args=p.parse_args()
    result=produire(**vars(args))
    summary={
        "statistiques":result["statistiques"],
        "dates":result["bilans_par_date_effet"],
        "etats_selection":{v["date_reference"]:v["total"] for v
                          in result["etats_1er_janvier"]
                          if v["annee"] in (1943,1946,1947,1953,1954,1969,
                                           1970,1976,1977,1988,1989,1992,1993,2026)},
        "historique_candidats":[{"code":x["code_insee_historique"],
                    "ark":x["ark_Pactols_candidat"],
                    "periodes":len(x["periodes_COG"])}
                   for x in result["autorites_historiques_candidats"]],
    }
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2))
