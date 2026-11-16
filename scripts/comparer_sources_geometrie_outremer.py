#!/usr/bin/env python3
"""Comparer deux géométries ultramarines à leurs sources territoriales, en recette.

Mode acquisition : interroger deux FeatureServer publics, enregistrer la réponse
dans un fichier temporaire horodaté par son SHA-256 (hors dépôt).
Mode comparaison : lire ces réponses gelées et le GeoJSON national IGN/Etalab
au 4 mai 2026. JAMAIS de substitution ou de publication de géométrie.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from pyproj import Transformer
    from shapely import make_valid
    from shapely.geometry import shape
    from shapely.ops import transform
    from shapely.validation import explain_validity
    GEOMETRIES_DISPONIBLES = True
except ImportError:
    Transformer = None
    make_valid = None
    shape = None
    transform = None
    explain_validity = None
    GEOMETRIES_DISPONIBLES = False

TARGETS = {
    "98745": {
        "name": "Tahaa",
        "url": "https://services.arcgis.com/L4H4rU26VyhEF588/ArcGIS/rest/services/Communes_de_la_Polyn%C3%A9sie_fran%C3%A7aise_%28Tefenua%29/FeatureServer/0",
        "name_field": "com_nom", "id_field": "ObjectId", "local_code_field": "com_id",
        "attribution": "Administration de la Polynésie française, Te Fenua",
    },
    "98805": {
        "name": "Dumbéa",
        "url": "https://services1.arcgis.com/TZcrgU6CIbqWt9Qv/arcgis/rest/services/limites_terrestres/FeatureServer/0",
        "name_field": "nom", "id_field": "objectid", "local_code_field": "code_com",
        "attribution": "Gouvernement de la Nouvelle-Calédonie, DITTT",
    },
}


def normalized(value: object) -> str:
    if value is None:
        return ""
    return re.sub(
        "[^a-z0-9]+", "",
        "".join(c for c in unicodedata.normalize("NFKD", str(value).casefold())
                if not unicodedata.combining(c)),
    )


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def api_query(url: str, params: dict) -> tuple[dict, str, str]:
    endpoint = url + "/query?" + urlencode(params)
    request = Request(endpoint, headers={"User-Agent": "AdlFI-source-audit/1.0",
                                         "Accept": "application/json"})
    with urlopen(request, timeout=80) as response:
        data = response.read(16_000_001)
    if len(data) > 16_000_000:
        raise ValueError("Réponse géographique trop volumineuse")
    payload = json.loads(data)
    if not isinstance(payload, dict) or payload.get("error"):
        raise ValueError("Service ArcGIS indisponible : " + str(payload.get("error")))
    return payload, sha(data), endpoint


def acquerir(destination: Path) -> dict:
    if "docs" in destination.resolve().parts:
        raise ValueError("Ne jamais verser la recette dans docs")
    audit = {"schema": "adlfi.lieux.sources.territoriales.v1", "sources": {}}
    for code, target in TARGETS.items():
        # Récupérer les attributs des 48 / 33 communes sans leurs géométries.
        listing, lsha, listing_url = api_query(target["url"], {
            "where": "1=1", "outFields": "*",
            "returnGeometry": "false", "f": "json",
        })
        entries = listing.get("features")
        if not isinstance(entries, list):
            raise ValueError("Inventaire ArcGIS sans features : " + code)
        matches = [f["attributes"] for f in entries
                   if normalized(f.get("attributes", {}).get(target["name_field"]))
                   == normalized(target["name"])]
        if len(matches) != 1:
            raise ValueError("Nom territorial non désambiguïsé : " + code +
                             " candidats=" + str(len(matches)))
        props = matches[0]
        oid = props.get(target["id_field"])
        if not isinstance(oid, int):
            raise ValueError("Identifiant interne source invalide pour " + code)
        fc, gsha, query_url = api_query(target["url"], {
            "where": target["id_field"] + "=" + str(oid),
            "outFields": "*", "returnGeometry": "true",
            "outSR": "4326", "f": "geojson",
        })
        features = fc.get("features")
        if fc.get("type") != "FeatureCollection" or not isinstance(features, list) \
           or len(features) != 1 or not features[0].get("geometry"):
            raise ValueError("Géométrie alternative non unique pour " + code)
        audit["sources"][code] = {
            "libelle_cog": target["name"], "attribution": target["attribution"],
            "endpoint": target["url"], "liste_url": listing_url, "requete_url": query_url,
            "liste_sha256": lsha, "geometrie_sha256": gsha,
            "proprietes": props, "geojson": features[0],
            "champ_code_source": target["local_code_field"],
            "code_source": props.get(target["local_code_field"]),
            "statut_identifiant": "CONTROLE_COG_REQUIS",
        }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(audit, ensure_ascii=False,
                                      sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    return audit


def lire_national(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" \
         else path.open("r", encoding="utf-8") as stream:
        fc = json.load(stream)
    if fc.get("type") != "FeatureCollection":
        raise ValueError("GeoJSON national incomplet")
    return fc


def _polygones(geom):
    """Parcourir aussi les GeometryCollections issues de différences exactes."""
    if geom.is_empty:
        return
    if geom.geom_type == "Polygon":
        yield geom
    elif geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        for part in geom.geoms:
            yield from _polygones(part)


def localiser_ecarts(a, b) -> dict:
    """Décomposer les écarts en composantes surfaciques, sans exporter les polygones.

    a et b sont des copies géométriques valides en EPSG:6933.
    Les coordonnées des points témoins proviennent de l'inverse EPSG:6933.
    """
    inverse = Transformer.from_crs("EPSG:6933", "EPSG:4326", always_xy=True)
    zones = []
    for sens, geom in (("source_seule", a.difference(b)),
                       ("national_seul", b.difference(a))):
        for piece in _polygones(geom):
            if piece.area <= 1:  # <1 m² : ne pas multiplier les microsurfaces
                continue
            point = piece.representative_point()
            lon, lat = inverse.transform(point.x, point.y)
            zones.append({
                "sens": sens, "surface_km2": round(piece.area / 1e6, 9),
                "point_temoin_lon": round(lon, 6),
                "point_temoin_lat": round(lat, 6),
            })
    zones.sort(key=lambda x: (-x["surface_km2"], x["sens"],
                              x["point_temoin_lon"], x["point_temoin_lat"]))
    source_seule = a.difference(b).area / 1e6
    national_seul = b.difference(a).area / 1e6
    union = a.union(b).area / 1e6
    return {
        "source_hors_national_km2": round(source_seule, 6),
        "national_hors_source_km2": round(national_seul, 6),
        "nombre_zones_superieures_1m2": len(zones),
        "dix_principales_zones": zones[:10],
        "part_dix_principales_zones_pct": (
            round(sum(z["surface_km2"] for z in zones[:10]) /
                  (source_seule + national_seul) * 100, 6)
            if source_seule + national_seul > 0 else 0.0
        ),
        "indice_jaccard_pct": (
            round(a.intersection(b).area / (union * 1e6) * 100, 6)
            if union > 0 else None
        ),
        "methode": "Différences surfaciques EPSG:6933, polygones sur copies "
                   "valides seulement ; points témoins, ni frontières ni géométrie publiées.",
    }


def stats_comparaison(source_geometry: dict, national_geometry: dict) -> dict:
    if not GEOMETRIES_DISPONIBLES:
        raise RuntimeError("Les dépendances Shapely et pyproj sont nécessaires à la comparaison")
    source, national = shape(source_geometry), shape(national_geometry)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:6933", always_xy=True)
    source_ok, national_ok = source.is_valid, national.is_valid
    source_copy = source if source_ok else make_valid(source)
    national_copy = national if national_ok else make_valid(national)
    if not source_copy.is_valid or not national_copy.is_valid:
        raise ValueError("Diagnostic make_valid invalide, comparaison impossible")
    if source_copy.geom_type not in ("Polygon", "MultiPolygon") or \
       national_copy.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError("Réparation produisant une géométrie non polygonale")
    a = transform(transformer.transform, source_copy)
    b = transform(transformer.transform, national_copy)
    return {
        "validite_source": source_ok, "validite_nationale": national_ok,
        "motif_source": "Valid Geometry" if source_ok else explain_validity(source),
        "motif_national": "Valid Geometry" if national_ok else explain_validity(national),
        "source_type": source.geom_type, "national_type": national.geom_type,
        "source_bounds_wgs84": list(source.bounds),
        "national_bounds_wgs84": list(national.bounds),
        "diagnostic_sur_copie_uniquement": True,
        "reparation_diagnostic_source": not source_ok,
        "reparation_diagnostic_nationale": not national_ok,
        "source_surface_km2": round(a.area / 1e6, 6),
        "national_surface_km2": round(b.area / 1e6, 6),
        "ecart_surface_km2": round(abs(a.area - b.area) / 1e6, 6),
        "difference_symetrique_km2": round(a.symmetric_difference(b).area / 1e6, 6),
        "localisation_ecarts": localiser_ecarts(a, b),
        "recouvrement_pct_surface_source": round(
            a.intersection(b).area / a.area * 100, 6
        ) if a.area else None,
        "methodologie": "Shapely make_valid si nécessaire sur copies temporaires; "
                        "surfaces EPSG:6933 équivalentes et non une validation COG",
    }


def comparer(national: dict, sources: dict) -> dict:
    if sources.get("schema") != "adlfi.lieux.sources.territoriales.v1":
        raise ValueError("Inventaire alternatif invalide")
    features = {}
    for f in national.get("features", []):
        code = str(f.get("properties", {}).get("code", ""))
        if code in TARGETS:
            features.setdefault(code, []).append(f)
    resultat = {"schema": "adlfi.lieux.sources.comparaison2026.v1",
                "statut": "RECETTE_NON_VALIDANTE_NON_PUBLIEE",
                "alignements_pactols_crees": 0, "geometries_publiees": 0,
                "comparaisons": {}}
    for code in TARGETS:
        entries = features.get(code, [])
        alt = sources.get("sources", {}).get(code)
        if len(entries) != 1 or not alt:
            raise ValueError("Source ou géométrie nationale manquante : " + code)
        props = entries[0].get("properties", {})
        if props.get("code") != code:
            raise ValueError("Code COG inattendu " + code)
        info = stats_comparaison(alt["geojson"]["geometry"], entries[0]["geometry"])
        resultat["comparaisons"][code] = {
            "libelle_cog": TARGETS[code]["name"],
            "identite_source": alt["proprietes"],
            "identifiant_source": alt["code_source"],
            "verification_identite_source": "A_INSTRUIRE",
            "endpoint_source": alt["endpoint"],
            "empreinte_geojson_source": alt["geometrie_sha256"],
            "donnees_geometriques": info,
        }
    return resultat


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--acquerir", action="store_true")
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--national", type=Path)
    p.add_argument("--sortie", type=Path)
    args = p.parse_args()
    if args.acquerir:
        print(json.dumps({"sources": sorted(acquerir(args.sources)["sources"])},
                         ensure_ascii=False))
    else:
        if args.national is None or args.sortie is None:
            p.error("--national et --sortie nécessaires pour comparer")
        if "docs" in args.sortie.resolve().parts:
            raise ValueError("Ne jamais publier la recette sous docs")
        src = json.loads(args.sources.read_text(encoding="utf-8"))
        result = comparer(lire_national(args.national), src)
        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        args.sortie.write_text(json.dumps(result, ensure_ascii=False,
                                         sort_keys=True, indent=2) + "\n",
                              encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
