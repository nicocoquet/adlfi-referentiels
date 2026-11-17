#!/usr/bin/env python3
"""Audit des voisinages et recouvrements intra-couche des GeoJSON ISPF.

Les coordonnées natives sont en degrés (CRS déclaré EPSG:4687). On teste
l'intersection des INTÉRIEURS sans calculer de surfaces métriques, sans réparer
de géométrie et sans publier de données spatiales.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

SOURCE_SHA = "6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62"
LAYERS = {"Com.GeoJSON": ("IDCom", 48),
          "Comas.GeoJSON": ("IDComas", 116),
          "Ile.GeoJSON": ("IDIle", 119)}
CRS = "urn:ogc:def:crs:EPSG::4687"

def normaliser_code(val):
    if isinstance(val, bool) or val is None:
        raise ValueError("Identifiant absent")
    if isinstance(val, (int, float)):
        if not float(val).is_integer():
            raise ValueError("Code d'autorité fractionnaire")
        return str(int(val))
    if isinstance(val, str) and val.strip().isascii() and val.strip().isdecimal():
        return str(int(val.strip()))
    raise ValueError("Identifiant d'autorité non numérique")

def analyser_couche(fc, layer):
    # Import dans l'audit spécialisé pour garder les tests généraux sans Shapely.
    from shapely.geometry import shape
    from shapely.strtree import STRtree

    key, expected = LAYERS[layer]
    if fc.get("type") != "FeatureCollection":
        raise ValueError("La couche n'est pas une FeatureCollection")
    if fc.get("crs", {}).get("properties", {}).get("name") != CRS:
        raise ValueError("CRS ISPF non confirmé")
    features = fc["features"]
    if len(features) != expected:
        raise ValueError("Effectif de couche inattendu")
    geometries, codes = [], []
    for row in features:
        props = row.get("properties")
        if row.get("type") != "Feature" or not isinstance(props, dict):
            raise ValueError("Objet GeoJSON invalide")
        ident = normaliser_code(props.get(key))
        geom = shape(row["geometry"]) if row.get("geometry") else None
        if geom is None or geom.is_empty or not geom.is_valid or geom.geom_type != "MultiPolygon":
            raise ValueError("Géométrie absente, invalide ou non MultiPolygon : " + ident)
        geometries.append(geom)
        codes.append(ident)
    if len(set(codes)) != expected:
        raise ValueError("Code SIG dupliqué")

    tree = STRtree(geometries)
    contacts = Counter()
    intersections = []
    inspectes = 0
    for i, geom in enumerate(geometries):
        # Le R-tree limite les paires candidates aux boîtes englobantes qui
        # se croisent ; seules les paires i < j sont examinées.
        for hit in tree.query(geom):
            j = int(hit)
            if j <= i:
                continue
            inspectes += 1
            other = geometries[j]
            if not geom.intersects(other):
                continue
            if geom.touches(other):
                contacts["frontieres_seulement"] += 1
                continue
            # Une intersection d'intérieur en dimension 2 reste suspecte même
            # si elle est microscopique ; ne PAS fixer un seuil arbitraire
            # en degrés carrés, ni prétendre mesurer une superficie légale.
            inter = geom.intersection(other)
            if inter.area > 0:
                contacts["interieurs_en_recouvrement"] += 1
                intersections.append({
                    "code_a": codes[i], "code_b": codes[j],
                    "intersection_geometrique": inter.geom_type,
                    "geometries_identiques": geom.equals(other),
                    "superposition_totale_de_a": geom.within(other),
                    "superposition_totale_de_b": other.within(geom),
                })
            else:
                contacts["intersection_sans_surface_plane"] += 1
    return {
        "features": len(features),
        "crs_declare": CRS,
        "paires_candidates_selon_emprise": inspectes,
        "paires_contact_limites": contacts["frontieres_seulement"],
        "paires_recouvrement_interieur": contacts["interieurs_en_recouvrement"],
        "paires_intersection_sans_surface": contacts["intersection_sans_surface_plane"],
        "paires_recouvrements_a_instruire": intersections,
        "validation_topologique_individuelle": "CONTROLE_PR80",
        "statut": "AUDIT_NON_VALIDANT",
    }

def auditer(archive: Path):
    if sha256(archive.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Empreinte archive ISPF différente de la PR78")
    with ZipFile(archive) as z:
        if sorted(z.namelist()) != sorted(LAYERS):
            raise ValueError("Manifeste de trois couches SIG non conforme")
        couches = {name: analyser_couche(json.loads(z.read(name)), name)
                   for name in LAYERS}
    return {
        "schema": "adlfi.lieux.polynesie.recouvrements.intracouche.audit.v1",
        "statut": "RECETTE_NON_VALIDANTE",
        "source_sha256": SOURCE_SHA,
        "couches": couches,
        "limites": [
            "Seules les paires d'une même couche sont comparées.",
            "Les emprises en EPSG:4687 ne sont pas des superficies métriques.",
            "Aucun seuil de tolérance surfacique, aucune correction automatique.",
            "Le test de recouvrement OGC n'établit aucune limite historique.",
        ],
        "publication": {"polygones": 0, "autorites": 0, "nouveaux_ark": 0},
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--sortie", type=Path, required=True)
    a = p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Rapport de recette hors docs et sans écrasement")
    report = auditer(a.archive)
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    a.sortie.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True,
                                  indent=2) + "\n", encoding="utf-8")
    for layer, info in report["couches"].items():
        print("ISPF_RECOUVREMENT", json.dumps({
            "couche": layer,
            "objets": info["features"],
            "paires_candidates": info["paires_candidates_selon_emprise"],
            "contacts": info["paires_contact_limites"],
            "recouvrements": info["paires_recouvrement_interieur"],
            "autres": info["paires_intersection_sans_surface"],
            "paires": info["paires_recouvrements_a_instruire"],
        }, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
