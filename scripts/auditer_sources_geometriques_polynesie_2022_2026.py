#!/usr/bin/env python3
"""Inventaire NON PUBLIANT des fonds ISPF / GEO PF (2022) et des 48 communes COG 2026.

Les noms, surfaces et géométries anciennes ne constituent pas une identité géographique
2026 ; la comparaison détaillée attend une seconde instruction par couche et par code.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import itertools
import json
import zipfile
from pathlib import Path

ETALAB_SHA = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
ISPF_URL = "https://static.data.gouv.fr/resources/limites-geographiques-administratives/20220610-202135/shapefiles.zip"
GEOPF_URL = "https://static.data.gouv.fr/resources/geographie-administrative-de-la-polynesie-francaise/20220228-205331/loc-commune-associee.zip"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def inventaire_zip(path: Path, url: str, source: str) -> dict:
    import shapefile
    layers = []
    with zipfile.ZipFile(path) as arc:
        if arc.testzip():
            raise ValueError("Archive corrompue : " + source)
        members = {name.casefold(): name for name in arc.namelist()}
        for shp in sorted((x for x in arc.namelist() if x.lower().endswith(".shp")),
                          key=str.casefold):
            stem = shp[:-4]
            dbf = members.get((stem + ".dbf").casefold())
            shx = members.get((stem + ".shx").casefold())
            prj = members.get((stem + ".prj").casefold())
            if not dbf:
                layers.append({"fichier": shp, "erreur": "DBF_ABSENT"})
                continue
            args = {"shp": io.BytesIO(arc.read(shp)), "dbf": io.BytesIO(arc.read(dbf))}
            if shx:
                args["shx"] = io.BytesIO(arc.read(shx))
            reader = shapefile.Reader(**args)
            fields = [f[0] for f in reader.fields[1:]]
            samples = []
            for record in itertools.islice(reader.iterRecords(), 3):
                samples.append({k: str(v)[:100] for k, v in zip(fields, record)})
            wkt = arc.read(prj).decode("utf-8", errors="replace") if prj else None
            layers.append({
                "fichier": shp, "effectif": len(reader), "bbox_native": reader.bbox,
                "champs": fields, "exemples_attributs": samples,
                "prj_present": bool(wkt), "prj_debut": wkt[:360] if wkt else None,
                "champs_identifiants_possibles": [
                    x for x in fields if any(k in x.casefold()
                    for k in ("idcom", "code", "commune", "codgeo", "idile", "idsub"))
                ],
            })
    if not layers:
        raise ValueError("Aucun SHP dans l'archive : " + source)
    return {
        "source": source, "url": url, "date_annoncee": "2022",
        "sha256": sha256(path), "octets": path.stat().st_size,
        "nombre_couches_shp": len(layers), "couches": layers,
    }

def preflight_etalab(path: Path, index: dict) -> dict:
    from shapely.geometry import shape
    if sha256(path) != ETALAB_SHA:
        raise ValueError("SHA-256 Etalab 2026 non conforme")
    if index.get("schema") != "adlfi.lieux.recherche.outremer.public.v1" or index.get("cog_ref") != "2026-01-01":
        raise ValueError("Index ultramarin COG 2026 inattendu")
    expected = {}
    for line in index["communes"]["987"].splitlines():
        code, sep, label = line.partition("|")
        if not sep or len(code) != 5 or not code.startswith("987") or code in expected:
            raise ValueError("Code COG 987 ambigu")
        expected[code] = label
    if len(expected) != 48:
        raise ValueError("48 communes COG attendues")
    raw = path.read_bytes()
    collection = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    geoms = {}
    for f in collection["features"]:
        code = str((f.get("properties") or {}).get("code") or "")
        if code in expected:
            if code in geoms:
                raise ValueError("Géométrie dupliquée : " + code)
            geoms[code] = f["geometry"]
    if set(geoms) != set(expected):
        raise ValueError("Couverture Etalab des communes PF incomplète")
    invalid = {}
    for code in sorted(expected):
        g = shape(geoms[code])
        if g.is_empty or not g.is_valid or g.area <= 0:
            from shapely.validation import explain_validity
            invalid[code] = explain_validity(g)
    if set(invalid) != {"98745"}:
        raise ValueError("Anomalies géométriques différentes du contrôle 2026 : " + str(invalid))
    return {
        "date_cog": "2026-01-01", "edition_geometrie": "2026-05-04",
        "sha256": ETALAB_SHA, "codes_cog": sorted(expected),
        "communes_COG": 48, "geometries_presentes": len(geoms),
        "geometries_valides_GEOS": 48 - len(invalid), "anomalies": invalid,
        "lien_Pactols_infere": 0, "contour_historique_infere": 0,
    }

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ispf-zip", type=Path, required=True)
    p.add_argument("--geopf-zip", type=Path, required=True)
    p.add_argument("--etalab", type=Path, required=True)
    p.add_argument("--index-cog", type=Path, required=True)
    p.add_argument("--sortie", type=Path, required=True)
    args = p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Sortie neuve strictement hors docs/")
    index = json.loads(args.index_cog.read_text(encoding="utf-8"))
    rapport = {
        "schema": "adlfi.lieux.pf.inventaire_ispf_geopf.2022_2026.v1",
        "statut": "AUDIT_NON_PUBLIANT_SANS_ALIGNEMENT_GEOMETRIQUE",
        "sources_territoriales": [
            inventaire_zip(args.ispf_zip, ISPF_URL, "ISPF-2022"),
            inventaire_zip(args.geopf_zip, GEOPF_URL, "GEO-PF-2022"),
        ],
        "etalab_2026": preflight_etalab(args.etalab, index),
        "conclusion": "Sources territoriales de 2022 non extrapolees a 2026 ; examen comparatif par code et couche requis avant publication.",
        "nouveaux_ARK": 0, "nouvelles_geometries_publiees": 0,
    }
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(rapport, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print("PF_AUDIT_NON_PUBLIANT", json.dumps({
        "shapefiles": [x["nombre_couches_shp"] for x in rapport["sources_territoriales"]],
        "sha256_archives": [x["sha256"] for x in rapport["sources_territoriales"]],
        "communes_etudiees": 48, "invalides": ["98745"],
        "sha256_rapport": sha256(args.sortie),
    }, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
