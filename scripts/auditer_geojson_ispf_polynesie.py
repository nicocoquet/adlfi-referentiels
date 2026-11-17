#!/usr/bin/env python3
"""Préflight structurel des trois GeoJSON ISPF : aucune homologation spatiale.

Source : archive GeoJSON ISPF contrôlée par SHA-256. Audit des schémas,
géométries présentes et attributs; ne déduit aucun appariement d'un nom.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

SOURCE_SHA = "6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62"
LAYERS = ("Com.GeoJSON", "Comas.GeoJSON", "Ile.GeoJSON")
GEOMETRIES = {"Polygon", "MultiPolygon", "Point", "MultiPoint",
              "LineString", "MultiLineString", "GeometryCollection"}

def coordonnees(obj):
    if isinstance(obj, list):
        if obj and all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in obj):
            if len(obj) < 2 or not all(math.isfinite(n) for n in obj[:2]):
                raise ValueError("Coordonnée invalide")
            yield (obj[0], obj[1])
        else:
            for member in obj:
                yield from coordonnees(member)

def analyser_couche(data, filename):
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
        raise ValueError(filename + ": FeatureCollection attendu")
    features = data.get("features")
    if not isinstance(features, list):
        raise ValueError(filename + ": tableau de features absent")
    keys, types, geometry_types = Counter(), {}, Counter()
    missing, empty, malformed = 0, 0, 0
    coords_seen, lon_min, lat_min, lon_max, lat_max = 0, math.inf, math.inf, -math.inf, -math.inf
    sample = []
    for position, feat in enumerate(features):
        if not isinstance(feat, dict) or feat.get("type") != "Feature":
            raise ValueError(filename + ": objet non Feature")
        props = feat.get("properties")
        if not isinstance(props, dict):
            raise ValueError(filename + ": propriétés non-objet")
        for key, value in props.items():
            keys[key] += 1
            types.setdefault(key, Counter())[type(value).__name__] += 1
        if position < 3:
            sample.append({"index": position, "properties": props,
                           "feature_id": feat.get("id")})
        geom = feat.get("geometry")
        if geom is None:
            missing += 1
            continue
        if not isinstance(geom, dict) or geom.get("type") not in GEOMETRIES:
            malformed += 1
            continue
        geometry_types[geom["type"]] += 1
        if geom["type"] == "GeometryCollection":
            # GeometryCollection analysé explicitement comme cas à contrôler.
            malformed += 1
            continue
        coordinates = geom.get("coordinates")
        if not isinstance(coordinates, list) or not coordinates:
            empty += 1
            continue
        n = 0
        for lon, lat in coordonnees(coordinates):
            lon_min, lat_min = min(lon_min, lon), min(lat_min, lat)
            lon_max, lat_max = max(lon_max, lon), max(lat_max, lat)
            n += 1
        if n == 0:
            empty += 1
        coords_seen += n
    return {
        "fichier": filename,
        "features": len(features),
        "crs_declare": data.get("crs"),
        "types_geometriques": dict(sorted(geometry_types.items())),
        "geometries_nulles": missing,
        "geometries_vides": empty,
        "geometries_non_conformes": malformed,
        "nombre_positions": coords_seen,
        "emprise_coordonnees_brutes": ([lon_min, lat_min, lon_max, lat_max]
                                       if coords_seen else None),
        "proprietes": [
            {"nom": k, "presence": c, "types": dict(sorted(types[k].items()))}
            for k, c in sorted(keys.items())],
        "echantillon_attributaire_3_features": sample,
    }

def auditer(path: Path) -> dict:
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != SOURCE_SHA:
        raise ValueError("Source SIG ISPF modifiée : empreinte inattendue")
    with ZipFile(path) as archive:
        names = archive.namelist()
        if sorted(names) != sorted(LAYERS):
            raise ValueError("Archive non conforme aux trois fichiers inventoriés")
        layers = []
        for name in LAYERS:
            data = json.loads(archive.read(name).decode("utf-8-sig"))
            layers.append(analyser_couche(data, name))
    return {
        "schema": "adlfi.lieux.polynesie.geojson.preflight.v1",
        "statut": "AUDIT_STRUCTUREL_NON_VALIDANT",
        "source_sha256": sha,
        "couches": layers,
        "publication": {"nouvelles_geometries": 0, "nouveaux_ark": 0,
                         "rattachements_valide_geo": 0},
        "limites": [
            "Une emprise brute ne prouve pas le système de référence.",
            "Contrôle topologique non réalisé à cette étape.",
            "Aucun identifiant n'est aligné sur l'ISPF sans vérification explicite.",
        ],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--sortie", required=True, type=Path)
    a = parser.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette hors docs, sans écrasement")
    report = auditer(a.archive)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True,
                                  indent=2) + "\n", encoding="utf-8")
    for layer in report["couches"]:
        print("ISPF_GEOJSON_LAYER", json.dumps({
            "nom": layer["fichier"], "features": layer["features"],
            "crs": layer["crs_declare"],
            "geometry_types": layer["types_geometriques"],
            "null": layer["geometries_nulles"], "empty": layer["geometries_vides"],
            "malformed": layer["geometries_non_conformes"],
            "bbox_raw": layer["emprise_coordonnees_brutes"],
            "fields": [x["nom"] for x in layer["proprietes"]],
            "sample": layer["echantillon_attributaire_3_features"][:1],
        }, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
