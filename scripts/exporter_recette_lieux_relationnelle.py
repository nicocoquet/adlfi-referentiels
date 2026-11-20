#!/usr/bin/env python3
"""Produire un instantané relationnel de RECETTE Lieux, jamais un export public.

Entrée : 13 tables CSV du registre éditorial, séparées par ';'.
Sorties : lieux-recette.json et lieux-recette.sqlite dans un dossier HORS docs/.
Aucune identification ARK / COG, succession ou géométrie n'est inférée.
Python 3.12, bibliothèque standard uniquement.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "lieux-recette.sql"

# Les tables sont dans l'ordre des dépendances (pour les clés étrangères).
TABLES = (
    "dossiers", "concepts_pactols", "evenements_cog", "groupes_pdl",
    "validations", "couples_neutres", "liens_dossiers", "mouvements_cog",
    "periodes_cog", "uri_pdl", "conventions", "journal_arbitrages", "sources",
)
SCHEMA_VERSION = "adlfi-lieux-recette-relationnelle-1.0"


def proteger_chemins(tables: Path, sortie: Path) -> None:
    """Interdire toute sortie dans docs/ et tout écrasement des sources."""
    entrees, destination = tables.resolve(), sortie.resolve()
    if "docs" in destination.parts:
        raise ValueError("Sortie interdite dans docs/ (GitHub Pages)")
    if entrees == destination or destination.is_relative_to(entrees) or entrees.is_relative_to(destination):
        raise ValueError("Les sorties et les sources doivent être dans des dossiers distincts")
    if any((destination / name).exists() for name in ("lieux-recette.json", "lieux-recette.sqlite")):
        raise ValueError("La sortie existe déjà ; aucun écrasement implicite")


def lire_tables(dossier: Path, db: sqlite3.Connection) -> tuple[dict, dict]:
    tables, empreintes = {}, {}
    for name in TABLES:
        fichier = dossier / (name + ".csv")
        contenu = fichier.read_bytes()
        empreintes[name + ".csv"] = hashlib.sha256(contenu).hexdigest()
        with fichier.open("r", encoding="utf-8-sig", newline="") as handle:
            lecteur = csv.DictReader(handle, delimiter=";")
            champs = [row[1] for row in db.execute("PRAGMA table_info(" + name + ")")]
            if (not lecteur.fieldnames or len(set(lecteur.fieldnames)) != len(lecteur.fieldnames)
                    or set(lecteur.fieldnames) != set(champs)):
                raise ValueError("Colonnes CSV incompatibles avec le schéma : " + name)
            donnees = list(lecteur)
        if any(None in r or any(v is None for v in r.values()) for r in donnees):
            raise ValueError("CSV mal formé : " + name)
        pk = [row[1] for row in sorted(
            (r for r in db.execute("PRAGMA table_info(" + name + ")") if r[5]),
            key=lambda r: r[5],
        )]
        if pk:
            cles = [tuple(r[k] for k in pk) for r in donnees]
            if len(set(cles)) != len(cles) or any(not v for cle in cles for v in cle):
                raise ValueError("Clé primaire absente ou dupliquée : " + name)
            donnees.sort(key=lambda r: tuple(r[k] for k in pk))
        else:
            donnees.sort(key=lambda r: tuple(r[k] or "" for k in champs))
        tables[name] = donnees
    return tables, empreintes


def verifier_liens(tables: dict) -> None:
    # Une référence polymorphe n'est pas représentable par une FK SQLite simple.
    evenements = {r["id_evenement"] for r in tables["evenements_cog"]}
    groupes = {r["id_groupe"] for r in tables["groupes_pdl"]}
    for row in tables["liens_dossiers"]:
        ref = row["id_objet"]
        nature = row["type_objet"]
        if (nature == "evenement" and ref not in evenements) or (
                nature == "groupe_PDL" and ref not in groupes) or nature not in ("evenement", "groupe_PDL"):
            raise ValueError("Référence administrative introuvable (liens_dossiers)")
    # Une approbation collective ne vaut jamais validation individuelle.
    for row in tables["validations"]:
        if row["decision_editoriale"] == "Valider" and row["assertion_editoriale"] != "regle_collective":
            requis = ("justification", "responsable_validation", "date_validation",
                      "assertion_editoriale", "preuve_editoriale")
            if any(not row[k].strip() for k in requis):
                raise ValueError("Décision individuelle positive incomplète")


def charger_sqlite(db: sqlite3.Connection, tables: dict) -> None:
    for name in TABLES:
        colonnes = [r[1] for r in db.execute("PRAGMA table_info(" + name + ")")]
        numeros = {r[1] for r in db.execute("PRAGMA table_info(" + name + ")") if r[2].upper() == "INTEGER"}
        valeurs = []
        for row in tables[name]:
            record = []
            for k in colonnes:
                valeur = row[k]
                if valeur == "":
                    record.append(None)
                elif k in numeros:
                    entier = int(valeur)
                    if entier < 0:
                        raise ValueError("Nombre négatif : " + name + "." + k)
                    record.append(entier)
                else:
                    record.append(valeur)
            valeurs.append(tuple(record))
        if valeurs:
            placeholders = ",".join("?" for _ in colonnes)
            db.executemany("INSERT INTO " + name + " VALUES (" + placeholders + ")", valeurs)
    if db.execute("PRAGMA foreign_key_check").fetchall():
        raise ValueError("Violation de clé étrangère SQLite")
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("Intégrité SQLite invalide")


def generer(tables_csv: Path, sortie: Path, schema: Path = SCHEMA) -> dict:
    tables_csv, sortie = Path(tables_csv), Path(sortie)
    proteger_chemins(tables_csv, sortie)
    schema_sql = Path(schema).read_text(encoding="utf-8")
    db = sqlite3.connect(":memory:")
    try:
        db.executescript(schema_sql)
        tables, empreintes = lire_tables(tables_csv, db)
        verifier_liens(tables)
        with db:
            charger_sqlite(db, tables)
        # Ces listes sont délibérément vides : cet outil ne publie rien.
        resultat = {
            "metadata": {
                "schema_version": SCHEMA_VERSION,
                "statut": "RECETTE_NON_PUBLIABLE",
                "empreintes_sha256_csv": empreintes,
                "unites": {name: len(rows) for name, rows in tables.items()},
                "avertissement": (
                    "Un code COG partagé n'identifie pas une autorité Pactols. "
                    "Les événements, groupes techniques, décisions et géométries sont distincts."
                ),
            },
            "publication_gate": {
                "publication_autorisee": False,
                "nouvelles_relations_pactols_validees": [],
                "nouvelles_geometries_historiques_validees": [],
                "motif": "Instantané technique ; aucun export public depuis cet outil.",
            },
            "tables": tables,
        }
        sortie.mkdir(parents=True, exist_ok=True)
        json_path = sortie / "lieux-recette.json"
        sqlite_path = sortie / "lieux-recette.sqlite"
        json_path.write_text(
            json.dumps(resultat, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        destination = sqlite3.connect(sqlite_path)
        try:
            db.backup(destination)
        finally:
            destination.close()
        return {"tables": resultat["metadata"]["unites"],
                "publication_autorisee": False,
                "json": str(json_path), "sqlite": str(sqlite_path)}
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables-csv", required=True, type=Path, help="Dossier des 13 CSV de recette")
    parser.add_argument("--sortie", required=True, type=Path, help="Dossier hors docs/ et hors sources")
    args = parser.parse_args()
    print(json.dumps(generer(args.tables_csv, args.sortie), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
