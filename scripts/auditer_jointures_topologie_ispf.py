#!/usr/bin/env python3
"""Audit de jointure explicite XLSX–GeoJSON et de validité OGC des contours ISPF.

Contrôle documentaire, non validant pour la publication cartographique.
N'utilise jamais les libellés comme clés de rattachement ni ne répare de polygones.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
from zipfile import ZipFile

from inspecter_nomenclature_geographique_ispf import read_xlsx
from qualifier_communes_associees_ispf import SHA as XLSX_SHA, rows, normaliser
from auditer_geojson_ispf_polynesie import SOURCE_SHA as ZIP_SHA

LAYERS = (
    ("Commune", "Com.GeoJSON", "IDCom", 2, 48, "Commune"),
    ("Commune associée", "Comas.GeoJSON", "IDComas", 3, 116, "Comas"),
    ("Ile", "Ile.GeoJSON", "IDIle", None, 119, "Ile"),
)

def code(val, width=None):
    """Garde les zéros initiaux et refuse toute valeur flottante non entière."""
    if isinstance(val, bool) or val is None:
        raise ValueError("Identifiant absent ou booléen")
    if isinstance(val, int):
        raw = str(val)
    elif isinstance(val, float):
        if not math.isfinite(val) or not val.is_integer():
            raise ValueError("Identifiant numérique non entier")
        raw = str(int(val))
    elif isinstance(val, str):
        raw = val.strip()
        if not raw.isdecimal():
            raise ValueError("Code textuel non numérique : " + raw)
    else:
        raise ValueError("Type de code non reconnu")
    if not raw.isascii() or not raw.isdecimal():
        raise ValueError("Code non ASCII")
    return raw.zfill(width) if width else raw

def indexer(rows_data, key, width):
    data, duplicates = {}, []
    for row in rows_data:
        ident = code(row[key], width)
        if ident in data:
            duplicates.append(ident)
        else:
            data[ident] = row
    return data, sorted(set(duplicates))

def auditer(xlsx: Path, archive: Path):
    from shapely.geometry import shape
    from shapely.validation import explain_validity
    if sha256(xlsx.read_bytes()).hexdigest() != XLSX_SHA:
        raise ValueError("Empreinte XLSX ISPF différente")
    if sha256(archive.read_bytes()).hexdigest() != ZIP_SHA:
        raise ValueError("Empreinte GeoJSON ISPF différente")
    sheets = {x["feuille"]: x for x in read_xlsx(xlsx)}
    if set(sheets) != {"Subdivision", "Commune", "Commune associée", "Ile", "Geo"}:
        raise ValueError("Feuilles XLSX non conformes")
    report = {"schema": "adlfi.lieux.polynesie.jointures.topologie.audit.v1",
              "statut": "RECETTE_NON_VALIDANTE",
              "sources": {"xlsx_sha256": XLSX_SHA, "geojson_zip_sha256": ZIP_SHA},
              "couches": {}, "candidats_publication_automatique": 0,
              "publication": {"contours": 0, "autorites": 0, "ark": 0}}
    with ZipFile(archive) as z:
        if sorted(z.namelist()) != sorted(x[1] for x in LAYERS):
            raise ValueError("Couches GeoJSON différentes du manifeste")
        for sheet, filename, field, width, expected, label in LAYERS:
            xls, duplicates_xlsx = indexer(rows(sheets[sheet]), field, width)
            fc = json.loads(z.read(filename))
            if fc.get("type") != "FeatureCollection" or not isinstance(fc.get("features"), list):
                raise ValueError("GeoJSON non FeatureCollection : " + filename)
            features = fc["features"]
            if len(xls) != expected or len(features) != expected or duplicates_xlsx:
                raise ValueError("Cardinalité ou codes XLSX atypiques : " + sheet)
            geo, duplicates_geo = indexer([f["properties"] for f in features], field, width)
            missing = sorted(set(xls) - set(geo))
            extra = sorted(set(geo) - set(xls))
            label_conflicts, label_details, parent_conflicts, invalid, empty = [], [], [], [], []
            geometry_types = Counter()
            for i, feat in enumerate(features):
                props = feat.get("properties")
                if not isinstance(props, dict) or feat.get("type") != "Feature":
                    raise ValueError("Feature ou propriétés invalides")
                ident = code(props[field], width)
                if ident in xls:
                    source = xls[ident]
                    if normaliser(str(props.get(label, ""))) != normaliser(source[label]):
                        label_conflicts.append(ident)
                        label_details.append({"code": ident, "xlsx": source[label], "geojson": props.get(label)})
                    for parent in (("IDCom", 2), ("IDSub", None)):
                        name, digits = parent
                        if name in source and code(props.get(name), digits) != code(source[name], digits):
                            parent_conflicts.append({"code": ident, "champ": name})
                try:
                    geom = shape(feat["geometry"]) if feat.get("geometry") is not None else None
                    if geom is None or geom.is_empty:
                        empty.append(ident)
                        continue
                    geometry_types[geom.geom_type] += 1
                    if not geom.is_valid:
                        invalid.append({"code": ident, "feature_index": i,
                                        "motif": explain_validity(geom)})
                except Exception as exc:
                    invalid.append({"code": ident, "feature_index": i,
                                    "motif": "Geometry parse failed: " + str(exc)[:160]})
            report["couches"][filename] = {
                "source_xlsx": sheet, "cle": field,
                "nombre_xlsx": len(xls), "nombre_geojson": len(features),
                "codes_communs": len(set(xls) & set(geo)),
                "codes_absents_du_geojson": missing, "codes_supplementaires_geojson": extra,
                "doublons_geojson": duplicates_geo,
                "divergences_libelles_normalises": sorted(set(label_conflicts)),
                "details_divergences_libelles": label_details,
                "divergences_rattachement": parent_conflicts,
                "geometries_valides_ogc": len(features) - len(invalid) - len(empty),
                "geometries_invalides": invalid, "geometries_vides": empty,
                "types_geometriques": dict(sorted(geometry_types.items())),
                "crs_declare": fc.get("crs"),
            }
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xlsx", required=True, type=Path)
    p.add_argument("--archive", required=True, type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    args = p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Rapport uniquement hors docs et sans écrasement")
    report = auditer(args.xlsx, args.archive)
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(report, sort_keys=True, indent=2,
                        ensure_ascii=False) + "\n", encoding="utf-8")
    for name, data in report["couches"].items():
        print("ISPF_JOINTURE_TOPOLOGIE", json.dumps({
            "couche": name, "codes_communs": data["codes_communs"],
            "absents": data["codes_absents_du_geojson"],
            "extras": data["codes_supplementaires_geojson"],
            "doublons": data["doublons_geojson"],
            "libelles": data["details_divergences_libelles"],
            "parents": data["divergences_rattachement"],
            "valides": data["geometries_valides_ogc"],
            "invalides": data["geometries_invalides"],
            "vides": data["geometries_vides"]
        }, sort_keys=True, ensure_ascii=False))

if __name__ == "__main__":
    main()
