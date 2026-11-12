#!/usr/bin/env python3
"""Synchronise uniquement les références aux JPEG canoniques nouvellement ajoutés.

Une publication statique ne suffit pas : les fiches Organismes lisent les
références de médias depuis docs/data/organismes.json. Ce script actualise
exclusivement les champs presentation.media des autorités déjà présentes.

Usage :
    python3 scripts/synchroniser_logos_publies.py --check
    python3 scripts/synchroniser_logos_publies.py --write

Aucun XLSX, rattachement, libellé ou statut institutionnel n'est modifié.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "docs/data/organismes.json"
FOLDER = ROOT / "docs/assets/organismes"
PATTERN = re.compile(r"(?:ORG|SER)-[0-9]{4}\.jpg")


def synchroniser():
    original = JSON.read_text(encoding="utf-8")
    jeu = json.loads(original)
    if not jeu.get("provenance", {}).get("source_filename", "").startswith(
        "AdlFI_referentiel_1-49_"
    ):
        raise ValueError("Source du référentiel différente du maître 1.49")
    autorites = jeu["authorities"]
    par_identifiant = {a["id"]: a for a in autorites}
    if len(par_identifiant) != len(autorites):
        raise ValueError("Identifiant d'autorité dupliqué")
    changements = []
    for image in sorted(FOLDER.iterdir()):
        if not image.is_file() or not PATTERN.fullmatch(image.name):
            continue
        identifiant = image.stem
        fiche = par_identifiant.get(identifiant)
        if fiche is None:
            raise ValueError("JPEG canonique sans autorité : " + image.name)
        media = fiche["presentation"]["media"]
        attendu = "assets/organismes/" + image.name
        if media["logo"] == attendu:
            continue
        if media["logo"] is not None or media["image"] is not None:
            raise ValueError(
                "Référence média déjà renseignée, arbitrage requis : "
                + identifiant + " : " + str(media)
            )
        media["logo"] = attendu
        changements.append(identifiant)
    # Le schéma de sérialisation reste identique à celui du fichier historique.
    produit = json.dumps(jeu, ensure_ascii=False, indent=2)
    if original.endswith("\n"):
        produit += "\n"
    return original, produit, changements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    groupe = parser.add_mutually_exclusive_group(required=True)
    groupe.add_argument("--check", action="store_true")
    groupe.add_argument("--write", action="store_true")
    args = parser.parse_args()
    original, nouveau, changements = synchroniser()
    if args.check and changements:
        parser.exit(1, "Références JPEG non synchronisées : "
                    + ", ".join(changements) + "\n")
    if args.write and original != nouveau:
        JSON.write_text(nouveau, encoding="utf-8")
    print("JPEG canoniques à actualiser : " + str(len(changements)))
    print("IDs : " + (", ".join(changements) if changements else "aucun"))


if __name__ == "__main__":
    main()
