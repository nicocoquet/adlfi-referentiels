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
# Empreintes SHA256 figées après contrôle de tous les fichiers originaux
# dans le rapport du run GitHub Actions 43869252036. Toute variation bloque.
HASHES_VALIDES = {
    "regions-2018.geojson.gz": "24aab871b958675ed5aff9162229ea5abfcd55c1d15f13ee43a916b7558d37ca",
    "departements-2018.geojson.gz": "cfbc29aa611707116bd364f070cc990591f929a8d25e8633ccef92f46f001667",
    "regions-2019.geojson.gz": "9dee9ede27ed019551922883ee941c7bca9646d96b4df13894edd784608a23c6",
    "departements-2019.geojson.gz": "429c4a8b645c02564f641f9106ee5738c77c4b3f665522eb03f5d30d0a4e1fd4",
    "regions-2021.geojson.gz": "ddc570806e8fbf817227ce8478f1e7176ce1df53512bba225abe8081109c10c3",
    "departements-2021.geojson.gz": "debf967fb7c5fd3fe5dbb369bfb7d3e24d1198a0092aeaf800cc16ca83e36b22",
    "regions-2022.geojson.gz": "387bfc839ebeaa514c60fa4a9297c7fcf9bbaa71f27bca2e954aa9ff2e373a56",
    "departements-2022.geojson.gz": "0e06b418f4e41e739b345fde31146b67ad3ca00594f993697faa8c9b1600fdfa",
    "regions-2023.geojson.gz": "ee20c63792b1b6d8e3f6a5f5784c229857151aa0b88ba4c7a65bda18cd7e2371",
    "departements-2023.geojson.gz": "3264f8e1894782d58e604889c6ae8acd36c0c354fb929049de352ef17a3da635",
    "regions-2024.geojson.gz": "b745ef61874aacfd2ffeb2681250b0de9146d24edcae77e2dd0fc79202ced556",
    "departements-2024.geojson.gz": "a9c6e5acac23fa557fb3cf33c30bc0229001215079e0c79f706bc0ffdb90bd1f",
    "regions-2025.geojson.gz": "396b35422d1f10332b85bb07f7747baf7e86e79b7175070fc03431e34114924c",
    "departements-2025.geojson.gz": "7ea4ce7830de4e1284ea6fc41ba053b32536ff0b6f5f40c465c9a81dd6894340",
}

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
        "date_reconstruction_hebergement": "non_etablie",
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
            divergences_rattachement = []
            if niveau == "regions":
                for code in sorted(METRO_REGIONS):
                    metriques[code] = mesurer(geos[code], ref[niveau][code])
            else:
                for code in sorted(present):
                    p = geos[code].get("properties") or {}
                    region_archive = p.get("region")
                    if not isinstance(region_archive, str) or not region_archive:
                        raise ValueError("Département sans code de région source : "+nom+"/"+code)
                    region_2026 = ref[niveau][code]["properties"]["code_region_parent"]
                    if region_archive != region_2026:
                        divergences_rattachement.append({
                            "departement": code, "region_archive": region_archive,
                            "region_COG_2026": region_2026})
            rapport["lots"][str(annee)][niveau] = {
                "archive": nom,
                "source_sha256": empreinte,
                "nombre_COG": len(present),
                "territoires_hors_COG": sorted(exclus),
                "geometries_invalides": invalides,
                "departements_region_autre_que_COG_2026": divergences_rattachement,
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
