#!/usr/bin/env python3
"""Inventaire reproductible d'une archive Shapefile administrative de Polynésie.

Ne produit aucun nouveau contour et n'infère aucune relation entre les IDCom
de la source et les identifiants COG. Les occurrences de Tahaa sont une piste
documentaire uniquement.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

try:
    import shapefile
except ImportError:
    shapefile = None  # L'index documentaire reste importable hors CI géométrique.


def normaliser(value):
    return "".join(ch for ch in unicodedata.normalize("NFKD", str(value).casefold())
                   if not unicodedata.combining(ch) and ch.isalnum())


def analyser(path: Path) -> dict:
    if shapefile is None:
        raise RuntimeError("pyshp est requis pour contrôler les shapefiles")
    if not zipfile.is_zipfile(path):
        raise ValueError("Archive ZIP attendue")
    if path.stat().st_size > 40_000_000:
        raise ValueError("Archive trop volumineuse")
    raw = path.read_bytes()
    report = {
        "statut": "RECETTE_NON_VALIDANTE",
        "source": "Section Cadastre-Topographie, Polynésie française, diffusion 2022",
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "fichiers": [],
        "couches": [],
        "geom_disponible": False,
        "alignements_cog_crees": 0,
        "geometries_publiees": 0,
    }
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members = {entry.filename: entry for entry in z.infolist()
                   if not entry.is_dir() and not entry.filename.startswith("__MACOSX/")}
        if any(info.file_size > 110_000_000 for info in members.values()):
            raise ValueError("Contenu source anormalement volumineux")
        paths = sorted(members)
        report["fichiers"] = [
            {"nom": filename, "octets": members[filename].file_size}
            for filename in paths
        ]
        lower = {f.lower(): f for f in paths}
        for shp_lower in sorted(f for f in lower if f.endswith(".shp")):
            stem = shp_lower[:-4]
            if stem + ".dbf" not in lower or stem + ".shx" not in lower:
                raise ValueError("Jeu Shapefile incomplet : " + stem)
            parts = {}
            for ext in (".shp", ".dbf", ".shx", ".prj", ".cpg"):
                name = lower.get(stem + ext)
                if name is not None:
                    parts[ext] = z.read(name)
            shp = shapefile.Reader(
                shp=io.BytesIO(parts[".shp"]),
                shx=io.BytesIO(parts[".shx"]),
                dbf=io.BytesIO(parts[".dbf"]),
                encoding="cp1252",
                encodingErrors="replace",
            )
            fields = [f[0] for f in shp.fields[1:]]
            matches = []
            for i, record in enumerate(shp.iterRecords()):
                attrs = dict(zip(fields, record))
                concordants = [key for key, value in attrs.items()
                               if isinstance(value, str) and normaliser(value) == "tahaa"]
                if concordants:
                    matches.append({
                        "index_enregistrement": i,
                        "champs_concordants": concordants,
                        "identifiants_et_libelles": {
                            str(k): str(v)[:150] for k, v in attrs.items()
                            if isinstance(v, (str, int, float)) and
                            ("id" in k.lower() or "com" in k.lower() or
                             "nom" in k.lower() or "sub" in k.lower())
                        },
                    })
            report["couches"].append({
                "shp": lower[shp_lower], "champs": fields,
                "nombre_enregistrements": len(shp),
                "occurrences_tahaa": matches,
                "projection_prj": parts.get(".prj", b"").decode(
                    "utf-8", errors="replace")[:1200],
                "fichier_cpg": parts.get(".cpg", b"").decode(
                    "ascii", errors="replace").strip(),
            })
        report["geom_disponible"] = bool(report["couches"])
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--sortie", type=Path, required=True)
    args = p.parse_args()
    if "docs" in args.sortie.resolve().parts:
        raise ValueError("Ne jamais verser la recette dans docs/")
    r = analyser(args.archive)
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(
        json.dumps(r, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "sha256": r["archive_sha256"],
        "fichiers": len(r["fichiers"]),
        "couches": [{"shp": x["shp"], "nombre": x["nombre_enregistrements"],
                     "champs": x["champs"],
                     "tahaa": x["occurrences_tahaa"],
                     "prj": x["projection_prj"][:160]}
                    for x in r["couches"]]
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
