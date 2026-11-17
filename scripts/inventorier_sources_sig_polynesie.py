#!/usr/bin/env python3
"""Inventorier une archive SIG officielle sans homologuer aucun contour.

Audit strictement documentaire : SHA-256, liste des membres, tailles, types
et présence éventuelle de couches insulaires/administratives. Pas d'extraction,
pas de transformation CRS, pas de publication GeoJSON.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, BadZipFile

SUSPICIOUS = ("../", "/")
MAX_MEMBERS = 10000
MAX_UNCOMPRESSED = 4 * 1024**3
EXTENSIONS = {".geojson", ".json", ".shp", ".dbf", ".shx", ".prj", ".cpg",
              ".gpkg", ".csv", ".txt", ".xml", ".qmd", ".md", ".pdf"}

def analyser_archive(path: Path, url: str) -> dict:
    if not path.is_file():
        raise ValueError("Archive source introuvable")
    try:
        with ZipFile(path) as z:
            entries = z.infolist()
            if not entries or len(entries) > MAX_MEMBERS or z.testzip() is not None:
                raise ValueError("Archive absente, trop complexe ou corrompue")
            members, total = [], 0
            for entry in entries:
                name = entry.filename.replace("\\", "/")
                parts = PurePosixPath(name).parts
                if (name.startswith("/") or ".." in parts or
                    "\x00" in name or "\\" in entry.filename):
                    raise ValueError("Chemin ZIP dangereux")
                total += entry.file_size
                if total > MAX_UNCOMPRESSED:
                    raise ValueError("Volume décompressé excessif")
                ext = PurePosixPath(name).suffix.casefold()
                members.append({
                    "nom": name, "extension": ext, "octets": entry.file_size,
                    "octets_compresses": entry.compress_size,
                    "repertoire": entry.is_dir(),
                    "type_reconnu": ext in EXTENSIONS,
                })
    except BadZipFile as exc:
        raise ValueError("Source non ZIP") from exc
    return {
        "schema": "adlfi.lieux.polynesie.sources_sig.inventaire.v1",
        "statut": "AUDIT_SOURCE_NON_VALIDANT",
        "source": {"url": url, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                   "octets": path.stat().st_size},
        "nombre_membres": len(members),
        "taille_totale_decompressee": total,
        "inventaire": members,
        "decision": "AUCUNE_GEOMETRIE_HOMOLOGUEE",
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--sortie", type=Path, required=True)
    args = p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Rapport de recette à conserver hors docs, sans écrasement")
    result = analyser_archive(args.archive, args.url)
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print("SOURCES_SIG_BILAN", json.dumps({
        "fichiers": result["nombre_membres"],
        "octets": result["source"]["octets"],
        "sha256": result["source"]["sha256"],
        "candidats": [r["nom"] for r in result["inventaire"]
                      if any(t in r["nom"].casefold()
                             for t in ("ile", "île", "commune", "codgeo", "geo"))],
    }, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
