#!/usr/bin/env python3
"""Audit non validant des 4 tables COG 2026 spécifiques aux COMER et assimilés.

Ne pas assimiler COM, DIS, CIR, CPT, CDM. Les codes historiques n'ont pas
nécessairement le même niveau de granularité, ni le même territoire qu'en 2026.
La table historique des subdivisions comprend aussi des entités anciennes
(Algérie, Maroc, Tunisie) : ne pas en faire des COMER contemporaines.
Aucun ARK Pactols, géométrie ou lien de succession n'est inféré.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

SOURCES = {
    "collectivites_2026": "v_comer_2026.csv",
    "collectivites_historiques": "v_tom_depuis_1943.csv",
    "zonages_2026": "v_commune_comer_2026.csv",
    "zonages_historiques": "v_commune_outremer_depuis_1943.csv",
}
COLONNES = {
    "collectivites_2026": {"COMER", "LIBELLE"},
    "collectivites_historiques": {"COMER", "LIBELLE", "DATE_DEBUT", "DATE_FIN"},
    "zonages_2026": {"COMER", "COM_COMER", "NATURE_ZONAGE", "LIBELLE"},
    "zonages_historiques": {
        "COM_COMER", "NATURE_ZONAGE", "LIBELLE", "DATE_DEBUT", "DATE_FIN"},
}
NATURES = {
    "COM": "Commune", "DIS": "District", "CIR": "Circonscription territoriale",
    "CPT": "Clipperton (code géographique)", "CDM": "Île des Faisans (condominium)",
}
# Ce contrôle n'impose pas d'affiliation historique par préfixe de code.
TAAF_COMER_2026 = "984"

def empreinte(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

def lire(path: Path, role: str) -> tuple[list[dict], dict]:
    raw = path.read_bytes()
    if not raw or len(raw) > 5_000_000:
        raise ValueError("Fichier vide ou anormalement volumineux : " + path.name)
    try:
        contenu = raw.decode("utf-8-sig")
    except UnicodeError as e:
        raise ValueError("Encodage non conforme : " + path.name) from e
    first = contenu.splitlines()[0]
    sep = ";" if first.count(";") > first.count(",") else ","
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=sep)
        columns = reader.fieldnames or []
        if len(columns) != len(set(columns)) or not COLONNES[role] <= set(columns):
            raise ValueError("Schéma COG inconnu : " + path.name + " " + repr(columns))
        rows = list(reader)
    if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("CSV vide ou mal formé : " + path.name)
    for i, row in enumerate(rows, 2):
        needed = {"COMER"} if role.startswith("collectivites_") else {"COM_COMER", "NATURE_ZONAGE"}
        if not all(row.get(k, "").strip() for k in needed):
            raise ValueError(f"Identifiant absent {path.name}:{i}")
        if role == "zonages_2026" or role == "zonages_historiques":
            if row["NATURE_ZONAGE"] not in NATURES:
                raise ValueError("Nature de zonage inconnue : " + row["NATURE_ZONAGE"])
        if role.endswith("historiques"):
            start, end = row["DATE_DEBUT"], row["DATE_FIN"]
            if (len(start) != 10 or start[4] != "-" or start[7] != "-"
                or end and (len(end) != 10 or end[4] != "-" or end[7] != "-" or end < start)):
                raise ValueError(f"Période incohérente {path.name}:{i}")
    return rows, {
        "nom_fichier": path.name, "sha256": empreinte(raw), "octets": len(raw),
        "nombre_lignes": len(rows), "colonnes": columns, "separateur": sep}

def csv_ecrire(path: Path, lignes: list[dict], champs: list[str]):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=champs, delimiter=";")
        writer.writeheader()
        writer.writerows({k: row.get(k, "") for k in champs} for row in lignes)

def sauver_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8")

def construire(sources: Path, sortie: Path) -> dict:
    sources, sortie = Path(sources).resolve(), Path(sortie).resolve()
    if sortie == sources or sortie.is_relative_to(sources) or sources.is_relative_to(sortie):
        raise ValueError("Dossiers sources et résultats non indépendants")
    if "docs" in sortie.parts:
        raise ValueError("Aucun fichier de recette dans docs/ (GitHub Pages)")
    data, meta = {}, {}
    for role, name in SOURCES.items():
        data[role], meta[role] = lire(sources / name, role)

    cur = data["collectivites_2026"]
    curzones = data["zonages_2026"]
    hist = data["collectivites_historiques"]
    hiszones = data["zonages_historiques"]
    if len({r["COMER"] for r in cur}) != len(cur):
        raise ValueError("Identifiants COMER actuels dupliqués")
    if len({(r["NATURE_ZONAGE"], r["COM_COMER"]) for r in curzones}) != len(curzones):
        raise ValueError("Types et codes de zonages actuels dupliqués")

    parents = {r["COMER"]: r["LIBELLE"] for r in cur}
    manquants = [r for r in curzones if r["COMER"] not in parents]
    if manquants:
        raise ValueError("Zonage sans COMER 2026 : " + repr(manquants[:3]))
    taaf = [r for r in curzones if r["COMER"] == TAAF_COMER_2026]
    if not taaf:
        raise ValueError("Aucun district/zonage TAAF dans le COG")

    # Contrôle de doublon EXACT sur les périodes ; les codes historiques réutilisés
    # ou partagés sont documentés, jamais dédupliqués selon le seul code.
    doublons = {}
    for role in ("collectivites_historiques", "zonages_historiques"):
        rows = data[role]
        groups = collections.Counter(tuple(sorted(r.items())) for r in rows)
        doublons[role] = sum(v-1 for v in groups.values() if v>1)
        if doublons[role]:
            raise ValueError("Doublons exacts de lignes historiques : " + role)
    sortie.mkdir(parents=True, exist_ok=True)
    stats = []
    for c in sorted(cur, key=lambda x:x["COMER"]):
        rows = [r for r in curzones if r["COMER"] == c["COMER"]]
        counts = collections.Counter(r["NATURE_ZONAGE"] for r in rows)
        stats.append({
            "code_comer": c["COMER"], "collectivite_2026": c["LIBELLE"],
            "zonages_2026": len(rows),
            **{"nature_"+k: counts.get(k,0) for k in NATURES},
        })

    historiques_par_nature = collections.Counter(r["NATURE_ZONAGE"] for r in hiszones)
    historiques_codes = collections.Counter(r["COM_COMER"] for r in hiszones)
    changed_names = {
        code: sorted({r["LIBELLE"] for r in hiszones if r["COM_COMER"] == code})
        for code, n in historiques_codes.items() if n>1
    }
    # Cette liste est une piste documentaire, pas une chaîne de succession.
    changements = [{"code": code, "noms_attestes": noms, "nombre_noms": len(noms)}
                    for code,noms in sorted(changed_names.items()) if len(noms)>1]

    csv_ecrire(sortie / "collectivites_2026.csv", cur, meta["collectivites_2026"]["colonnes"])
    csv_ecrire(sortie / "collectivites_historiques.csv", hist,
               meta["collectivites_historiques"]["colonnes"])
    csv_ecrire(sortie / "zonages_2026.csv", curzones, meta["zonages_2026"]["colonnes"])
    csv_ecrire(sortie / "zonages_historiques.csv", hiszones,
               meta["zonages_historiques"]["colonnes"])
    csv_ecrire(sortie / "taaf_zonages_2026.csv", taaf, meta["zonages_2026"]["colonnes"])
    csv_ecrire(sortie / "bilan_collectivites_2026.csv", stats,
               ["code_comer", "collectivite_2026", "zonages_2026"] +
               ["nature_"+x for x in NATURES])
    csv_ecrire(sortie / "homonymies_et_changements_de_noms_historiques.csv",
               [{"code":r["code"],"nombre_noms":r["nombre_noms"],
                 "noms_attestes":" | ".join(r["noms_attestes"])} for r in changements],
               ["code","nombre_noms","noms_attestes"])
    report = {
        "schema": "adlfi.lieux.comer.cog2026.audit.v1",
        "statut": "RECETTE_NON_VALIDANTE_NON_PUBLIEE",
        "source": "Insee COG 2026 https://www.insee.fr/fr/information/8740222",
        "sources": meta,
        "volumes": {role: len(rows) for role, rows in data.items()},
        "natures_zonages_actuels": dict(sorted(collections.Counter(
            r["NATURE_ZONAGE"] for r in curzones).items())),
        "natures_zonages_historiques": dict(sorted(historiques_par_nature.items())),
        "taaf_2026": [{"code":r["COM_COMER"],"nature":r["NATURE_ZONAGE"],
                       "libelle":r["LIBELLE"]} for r in taaf],
        "taaf_tous_districts": all(r["NATURE_ZONAGE"]=="DIS" for r in taaf),
        "codes_historiques_plusieurs_noms": len(changements),
        "collectivites_2026": stats,
        "limites": [
            "Les codes des anciennes collectivités ne prouvent pas un rattachement actuel.",
            "Un code historique identique à un code actuel ne démontre aucune identité géographique intemporelle.",
            "Ne pas inférer les dates de validité COMA/COMD, de géométries ou de relations Pactols.",
            "Les subdivisions historiques comprennent d'anciennes possessions françaises : ne pas les publier comme actuelles.",
            "NATURE_ZONAGE est obligatoire ; DIS, CIR, CPT, CDM ne sont pas des communes.",
            "Saint-Martin et Saint-Barthélemy 2007 : transition COG COM vers COMER à instruire séparément.",
        ],
        "nombre_ark_pactols_attribues": 0,
        "nombre_geometries_historiques_attribuees": 0,
    }
    sauver_json(sortie / "rapport_comer_2026.json", report)
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources",required=True,type=Path)
    parser.add_argument("--sortie",required=True,type=Path)
    args=parser.parse_args()
    r=construire(args.sources,args.sortie)
    print(json.dumps({"volumes":r["volumes"],
                      "natures":r["natures_zonages_actuels"],
                      "taaf_2026":r["taaf_2026"]},
                     ensure_ascii=False,indent=2))
