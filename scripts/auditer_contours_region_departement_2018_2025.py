#!/usr/bin/env python3
"""Audit reproductible des archives cartographiques 2018/2019/2021–2025.

Ne publie aucune géométrie, aucune identité COG historique ni aucun ARK.
Les contours des millésimes intermédiaires ne sont pas extrapolés depuis 2026.
Le GeoJSON 2026 n'est utilisé ici que pour le contrôle des ensembles de codes.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

ANNEES = (2018, 2019, 2021, 2022, 2023, 2024, 2025)
NIVEAUX = ("regions", "departements")
HORS_COG = frozenset(("975", "977", "978", "984", "986", "987", "988", "989"))
METRO_REGIONS = frozenset(("11", "24", "27", "28", "32", "44", "52", "53",
                           "75", "76", "84", "93", "94"))
DROM_REGIONS = frozenset(("01", "02", "03", "04", "06"))
# Les empreintes des originaux sont introduites uniquement après une première
# recette vérifiée ; aucune prétention d'authentification lors de l'inventaire.
HASHES_VALIDES = {}

def sha256(donnees: bytes) -> str:
    return hashlib.sha256(donnees).hexdigest()

def lire_geojson(path: Path, *, originaire: bool) -> tuple[dict, str]:
    brut = path.read_bytes()
    empreinte = sha256(brut)
    if originaire and (path.name in HASHES_VALIDES
                       and HASHES_VALIDES[path.name] != empreinte):
        raise ValueError("Archive source différente de la version validée : "+path.name)
    payload = gzip.decompress(brut) if brut.startswith(b"\x1f\x8b") else brut
    if len(payload) > 8_000_000:
        raise ValueError("Source cartographique trop volumineuse pour la recette : "+path.name)
    doc = json.loads(payload)
    if doc.get("type") != "FeatureCollection" or not isinstance(doc.get("features"), list):
        raise ValueError("Source GeoJSON invalide : "+path.name)
    return doc, empreinte

def indexer(doc: dict, source: str) -> tuple[dict, list]:
    codes, doublons = {}, []
    for element in doc["features"]:
        p = element.get("properties") or {}
        code = p.get("code")
        if code is None:
            raise ValueError("Contour sans code : "+source)
        code = str(code)
        if code in codes:
            doublons.append(code)
        else:
            codes[code] = element
    if doublons:
        raise ValueError("Codes géographiques dupliqués : "+source+" : "+",".join(doublons))
    return codes, sorted(c for c in codes if c in HORS_COG)

def mesurer(ancien, nouveau):
    """Comparaison d'affichage en Lambert-93, avec réparation de lecture locale."""
    from shapely import make_valid
    from shapely.geometry import shape
    from shapely.ops import transform
    from pyproj import Transformer
    projection = Transformer.from_crs(4326, 2154, always_xy=True).transform
    a = transform(projection, make_valid(shape(ancien["geometry"])))
    b = transform(projection, make_valid(shape(nouveau["geometry"])))
    if a.is_empty or b.is_empty:
        raise ValueError("Géométrie vide pendant la comparaison")
    i, u = a.intersection(b).area, a.union(b).area
    if not u:
        raise ValueError("Union géographique vide")
    return {"intersection_union_pct": round(100 * i / u, 5),
            "difference_symetrique_km2": round((u - i) / 1e6, 3)}

def auditer(racine: Path, actuel: Path, sortie: Path) -> dict:
    ref = {}
    for niveau in NIVEAUX:
        carte, hash_actuel = lire_geojson(actuel / (niveau+"-2026.geojson"), originaire=False)
        refs, exclus = indexer(carte, niveau+"/2026")
        if exclus:
            raise ValueError("Index COG 2026 : territoires hors échelon non exclus")
        attendu = 18 if niveau == "regions" else 101
        if len(refs) != attendu:
            raise ValueError("COG 2026 : nombre inattendu de "+niveau)
        ref[niveau] = refs

    rapport = {
        "schema": "adlfi.lieux.audit_archives_intermediaires.v1",
        "annees_presentes": list(ANNEES),
        "annees_sans_archive_dans_ce_depot": [2017, 2020],
        "origine": "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/",
        "generalisation_m": 100,
        "date_reconstruction_hebergement": "2026-05-04",
        "cog_2026_est_reference_codes_et_non_cog_annuel": True,
        "nouvelles_correspondances_pactols": 0,
        "etats_administratifs_historiques_publies": 0,
        "lots": {},
    }
    for annee in ANNEES:
        rapport["lots"][str(annee)] = {}
        for niveau in NIVEAUX:
            nom = f"{niveau}-{annee}.geojson.gz"
            chemin = racine / nom
            carte, empreinte = lire_geojson(chemin, originaire=True)
            geos, exclus = indexer(carte, nom)
            ref_codes = set(ref[niveau])
            present = set(geos) & ref_codes
            manquants = sorted(ref_codes - set(geos))
            nouveaux = sorted(set(geos) - ref_codes - HORS_COG)
            if nouveaux or manquants:
                raise ValueError(f"Codes {niveau}/{annee} ≠ 2026 : manquants={manquants}, nouveaux={nouveaux}")
            if set(exclus) != set(geos) - ref_codes:
                raise ValueError("Codes COM non qualifiés")
            if niveau == "regions" and not METRO_REGIONS.issubset(present):
                raise ValueError("Absence de région métropolitaine : "+nom)
            invalides, vides = [], []
            from shapely.geometry import shape
            for code in sorted(present):
                geo = geos[code].get("geometry") or {}
                if geo.get("type") not in ("Polygon", "MultiPolygon"):
                    raise ValueError("Géométrie non surfacique "+nom+"/"+code)
                polygon = shape(geo)
                if polygon.is_empty:
                    vides.append(code)
                if not polygon.is_valid:
                    invalides.append(code)
            if vides:
                raise ValueError("Géométries vides : "+nom+" "+str(vides))
            metriques = {}
            if niveau == "regions":
                for code in sorted(METRO_REGIONS):
                    metriques[code] = mesurer(geos[code], ref[niveau][code])
            rapport["lots"][str(annee)][niveau] = {
                "archive": nom,
                "source_sha256": empreinte,
                "nombre_COG": len(present),
                "territoires_hors_COG": sorted(exclus),
                "geometries_invalides": invalides,
                "comparaison_avec_2026": metriques,
            }
    if sortie.exists():
        raise ValueError("Refus d'écraser un rapport existant")
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(rapport, ensure_ascii=False, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    return rapport

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sources", required=True, type=Path)
    p.add_argument("--reference-2026", required=True, type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    args = p.parse_args()
    result = auditer(args.sources, args.reference_2026, args.sortie)
    print(json.dumps({
        "annees": result["annees_presentes"],
        "comptages": {y: {k: x["nombre_COG"] for k,x in v.items()}
                      for y,v in result["lots"].items()},
        "invalides": {y: {k: x["geometries_invalides"] for k,x in v.items()}
                      for y,v in result["lots"].items()},
        "aucune_publication": True,
    }, ensure_ascii=False))
