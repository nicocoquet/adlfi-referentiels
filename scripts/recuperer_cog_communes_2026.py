#!/usr/bin/env python3
"""Acquérir uniquement le CSV des communes COG 2026 pour les audits d'identités.

Ne dépend pas de la disponibilité des tables des mouvements ou de la chronologie
1943–2026 ; valide toujours l'empreinte SHA-256 officielle épinglée.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.error
import zipfile

from recuperer_cog_2026 import (ROOT, BUNDLE, DATAGOUV, EXPECTED, get, api_mirror_data)

NAME = "v_commune_2026.csv"


def collecter(sortie: Path) -> dict:
    target = Path(sortie)
    name = NAME
    expected = EXPECTED[name]
    errors = []
    source = None
    data = None

    def accept(raw: bytes, url: str) -> bool:
        nonlocal source, data
        if hashlib.sha256(raw).hexdigest() != expected:
            errors.append("Empreinte COG non conforme depuis " + url)
            return False
        source, data = url, raw
        return True

    try:
        accept(get(ROOT + name), ROOT + name)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        errors.append("CSV officiel : " + str(exc)[:190])

    if data is None:
        try:
            archive = get(BUNDLE)
            with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
                members = [info for info in zipped.infolist()
                           if Path(info.filename).name == name and not info.is_dir()]
                if len(members) != 1 or members[0].file_size > 10_000_000:
                    raise ValueError("Fichier COG absent, dupliqué ou trop volumineux dans le ZIP")
                accept(zipped.read(members[0]), BUNDLE)
        except (urllib.error.URLError, OSError, ValueError, zipfile.BadZipFile) as exc:
            errors.append("Archive Insee : " + str(exc)[:190])

    if data is None:
        try:
            mirrors = api_mirror_data(get(DATAGOUV)).get(name, [])
            for url in mirrors:
                try:
                    if accept(get(url), url):
                        break
                except (urllib.error.URLError, OSError, ValueError) as exc:
                    errors.append("Miroir " + url + ": " + str(exc)[:150])
        except (urllib.error.URLError, OSError, ValueError) as exc:
            errors.append("Catalogue data.gouv.fr : " + str(exc)[:190])

    if data is None:
        raise RuntimeError("Aucune source COG 2026 conforme pour " + name + " ; " + str(errors))

    target.mkdir(parents=True, exist_ok=True)
    output = target / name
    if output.exists() and output.read_bytes() != data:
        raise ValueError("Refus d'écraser un fichier COG différent")
    output.write_bytes(data)
    result = {
        "date_source": "2026-01-01", "fichier": name,
        "sha256": expected, "source_telechargement": source, "octets": len(data),
        "erreurs_non_bloquantes": errors,
        "portee": "COG actuel uniquement ; aucune information historique rétroprojetée",
    }
    (target / "provenance-cog-communes-2026.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(collecter(args.sortie), ensure_ascii=False, sort_keys=True))
