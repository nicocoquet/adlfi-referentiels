#!/usr/bin/env python3
"""Inventorier le SHP GEO PF sans supposer l'indépendance des limites ISPF.

Recette purement documentaire : archive institutionnelle 2022, inventaire
de couches, champs, géométrie, projection et échantillons. Aucune jointure
par nom, aucune géométrie publiée, aucun téléchargement par défaut.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile

SOURCE = "https://www.data.gouv.fr/api/1/datasets/r/89d202c3-4f04-4168-842d-4c50036125c7"
EXPECTED_RESOURCE = "loc-commune-associee.zip"
VERSION_CATALOGUE = "2022-02-28"

def audit(archive: Path) -> dict:
    import shapefile
    data = archive.read_bytes()
    result = {
        "schema": "adlfi.lieux.polynesie.geopf.provenance.audit.v1",
        "statut": "RECETTE_NON_VALIDANTE",
        "resource_url": SOURCE,
        "resource_catalogue_date": VERSION_CATALOGUE,
        "ressource_nomme": EXPECTED_RESOURCE,
        "archive_sha256": hashlib.sha256(data).hexdigest(),
        "archive_bytes": len(data),
        "couches": [],
        "fichiers": [],
        "comparaison_geometrique_ispf": "NON_REALISEE",
        "independance_source_geometrique": "NON_ETABLIE",
        "publication": {"polygones": 0, "autorites": 0, "ark": 0}
    }
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        files = sorted(i for i in z.infolist() if not i.is_dir())
        for info in files:
            p = PurePosixPath(info.filename)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError("Chemin ZIP dangereux")
            result["fichiers"].append({"nom": info.filename, "taille": info.file_size,
                                       "sha256": hashlib.sha256(z.read(info)).hexdigest()})
        groups = {}
        for info in files:
            p = PurePosixPath(info.filename)
            ext = p.suffix.lower()
            if ext in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
                stem = str(p.with_suffix(""))
                groups.setdefault(stem, {})[ext] = info.filename
        candidates = [(stem, group) for stem, group in groups.items()
                      if all(ext in group for ext in (".shp", ".shx", ".dbf"))]
        if not candidates:
            raise ValueError("Aucune couche SHP/SHX/DBF complète")
        for stem, group in sorted(candidates):
            reader = shapefile.Reader(shp=io.BytesIO(z.read(group[".shp"])),
                                      shx=io.BytesIO(z.read(group[".shx"])),
                                      dbf=io.BytesIO(z.read(group[".dbf"])),
                                      encoding="utf-8", encodingErrors="replace")
            fields = [{"nom": f[0], "type": f[1], "taille": f[2]}
                      for f in reader.fields[1:]]
            # Les noms de champs sont lus directement, sans présumer de ca_id.
            sample = []
            geometry_types = Counter()
            ids = Counter()
            for i, sr in enumerate(reader.iterShapeRecords()):
                geometry_types[str(sr.shape.shapeType)] += 1
                record = sr.record.as_dict()
                if i < 3:
                    sample.append({str(k): str(v)[:120] for k, v in record.items()})
                for field in fields:
                    name = field["nom"]
                    if "id" in name.casefold() or "code" in name.casefold():
                        if record.get(name) is not None:
                            ids[name] += 1
            result["couches"].append({
                "nom": stem, "entites": len(reader), "champs": fields,
                "types_geometrie_shp": dict(sorted(geometry_types.items())),
                "champs_identifiants_renseignes": dict(sorted(ids.items())),
                "echantillons_attributaires": sample,
                "projection_prj": z.read(group[".prj"]).decode("utf-8", "replace")[:3000]
                    if ".prj" in group else None,
                "composants": group,
            })
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--sortie", type=Path, required=True)
    a = p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Rapport hors docs, aucun écrasement")
    report = audit(a.archive)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("GEO_PF_AUDIT", json.dumps({
        "sha256": report["archive_sha256"],
        "taille": report["archive_bytes"],
        "couches": [{
            "nom": x["nom"], "entites": x["entites"],
            "champs": [f["nom"] for f in x["champs"]],
            "types": x["types_geometrie_shp"],
            "prj": x["projection_prj"][:450] if x["projection_prj"] else None,
            "echantillons": x["echantillons_attributaires"][:1]
        } for x in report["couches"]],
    }, sort_keys=True, ensure_ascii=False))

if __name__ == "__main__":
    main()
