#!/usr/bin/env python3
"""Parité stricte entre l'exporteur officiel et le JSON candidat 1.58.

Exécution locale avec le maître privé (jamais déposé dans le dépôt) :
    python3 scripts/recette_parite_organismes_157.py "/chemin/vers/maitre-1-56.xlsx"

Lecture seule : n'écrit ni dans le classeur ni dans docs/data/organismes.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.export_organismes import build
EXPECTED_NAME = "AdlFI_referentiel_1-58_A05F_ARCHEO_ATLANTICA_CANDIDAT.xlsx"
EXPECTED_SHA = "6aa15da3019bc0a08987cd48631e95d09172d36b9fb80009b10a9636f1bf67d8"
EPOCH = "1795305600"  # 22 novembre 2026, 00:00:00 UTC

def first_differences(actual, expected, path="$", limit=24):
    found = []
    def compare(a, b, key):
        if len(found) >= limit:
            return
        if type(a) != type(b):
            found.append(f"{key}: types différents {type(a).__name__} / {type(b).__name__}")
        elif isinstance(a, dict):
            for k in sorted(set(a) | set(b)):
                if k not in a or k not in b:
                    found.append(f"{key}.{k}: propriété absente d'un côté")
                else:
                    compare(a[k], b[k], f"{key}.{k}")
                if len(found) >= limit:
                    return
        elif isinstance(a, list):
            if len(a) != len(b):
                found.append(f"{key}: tailles {len(a)} / {len(b)}")
            for i, (x, y) in enumerate(zip(a, b)):
                compare(x, y, f"{key}[{i}]")
                if len(found) >= limit:
                    return
        elif a != b:
            found.append(f"{key}: {a!r} != {b!r}")
    compare(actual, expected, path)
    return found

def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage : python3 scripts/recette_parite_organismes_157.py '/chemin/maitre_1-56.xlsx'", file=sys.stderr)
        return 2

    source = Path(args[0]).expanduser().resolve()
    if not source.is_file():
        print("Maître introuvable :", source, file=sys.stderr)
        return 2
    if source.name != EXPECTED_NAME:
        print(f"ATTENTION : nom du fichier {source.name!r}, attendu {EXPECTED_NAME!r}",
              file=sys.stderr)
        # Le nom fait partie de la provenance. Un suffixe de téléchargement
        # tel que (2) ne permet pas une parité exacte sans renommer une copie.
        return 2
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA:
        print(f"ÉCHEC : SHA-256 du maître {sha} (attendu {EXPECTED_SHA})",
              file=sys.stderr)
        return 1

    previous = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = EPOCH
    try:
        computed = build(source)
    finally:
        if previous is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = previous
    publication = json.loads((ROOT / "docs/data/organismes.json").read_text(encoding="utf-8"))

    diffs = first_differences(computed, publication)
    if diffs:
        print("ÉCHEC — différences exporteur officiel / JSON publié :", file=sys.stderr)
        for diff in diffs:
            print(" -", diff, file=sys.stderr)
        return 1
    print("PARITÉ OFFICIELLE 1.58 : OK")
    print(f"Maître SHA-256 : {sha}")
    print(f"Autorités : {len(computed['authorities'])} ; relations : {len(computed['relations'])}")
    print("JSON publié et exporteur officiel strictement identiques, médias inclus.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
