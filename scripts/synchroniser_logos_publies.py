#!/usr/bin/env python3
"""Synchroniser uniquement les logos JPEG des autorités dans le JSON publié.

Contrat unique : docs/assets/organismes/ID.jpg (ID = ORG-XXXX ou SER-XXXX).
Les fichiers absents ne créent aucune référence : pictogramme côté interface.
Le script n'altère ni le classeur, ni les champs institutionnels, ni les ARK.

Usage :
  python3 scripts/synchroniser_logos_publies.py --check
  python3 scripts/synchroniser_logos_publies.py --write
"""
from __future__ import annotations

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

    logos = set()
    for fichier in sorted(FOLDER.iterdir()):
        if fichier.name == "README.md":
            continue
        if not fichier.is_file() or not PATTERN.fullmatch(fichier.name):
            raise ValueError("Nom de média interdit ; seul ID.jpg est admis : " + fichier.name)
        identifiant = fichier.stem
        if identifiant not in par_identifiant:
            raise ValueError("JPEG sans autorité : " + fichier.name)
        logos.add(identifiant)

    changements = []
    for identifiant, fiche in sorted(par_identifiant.items()):
        media = fiche["presentation"]["media"]
        attendu = "assets/organismes/" + identifiant + ".jpg" if identifiant in logos else None
        if media.get("logo") != attendu or media.get("image") is not None:
            media["logo"] = attendu
            media["image"] = None
            changements.append(identifiant)
    produit = json.dumps(jeu, ensure_ascii=False, indent=2)
    if original.endswith("\n"):
        produit += "\n"
    return original, produit, changements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    original, produit, changements = synchroniser()
    if args.check and changements:
        parser.exit(1, "Médias non synchronisés : " + ", ".join(changements) + "\n")
    if args.write and original != produit:
        JSON.write_text(produit, encoding="utf-8")
    print("Autorités à synchroniser : " + str(len(changements)))
    print("Identifiants : " + (", ".join(changements) if changements else "aucun"))


if __name__ == "__main__":
    main()
