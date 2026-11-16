#!/usr/bin/env python3
"""Découvrir la classe BD TOPO Condominium diffusée par WFS IGN.

Audit non validant : 98101 est un code COG CDM, pas un code de commune.
Aucune attribution automatique entre une feature BD TOPO et le code COG.
Le rapport n'exporte ni géométrie ni coordonnées précises des sommets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

BASE_WFS = "https://data.geopf.fr/wfs/ows"
DOC = "https://geoservices.ign.fr/bdtopo"
CAPABILITIES = {"service": "WFS", "version": "2.0.0", "request": "GetCapabilities"}


def charger(params: dict[str, str]) -> tuple[bytes, str]:
    url = BASE_WFS + "?" + urlencode(params)
    request = Request(url, headers={"User-Agent": "AdlFI-COG-98101-audit/1.0"})
    with urlopen(request, timeout=90) as result:
        raw = result.read(26_000_001)
    if not raw or len(raw) > 26_000_000:
        raise ValueError("Réponse WFS vide ou trop volumineuse")
    return raw, url


def lister_couches(xml: bytes) -> list[dict]:
    root = ET.fromstring(xml)
    # On se limite aux FeatureType explicitement décrits dans les capabilities.
    listed = []
    for node in root.findall(".//{*}FeatureType"):
        name = node.findtext("{*}Name") or ""
        title = node.findtext("{*}Title") or ""
        if not name:
            continue
        listed.append({"name": name, "title": title})
    return sorted(listed, key=lambda x: x["name"])


def candidat_condominium(couches: list[dict]) -> list[dict]:
    return [r for r in couches
            if "condominium" in (r["name"] + " " + r["title"]).casefold()]


def analyser_geojson(data: dict) -> dict:
    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError("Le WFS n'a pas renvoyé de FeatureCollection JSON")
    from shapely.geometry import shape
    from pyproj import Transformer
    from shapely.ops import transform

    transformeur = Transformer.from_crs("EPSG:4326", "EPSG:6933", always_xy=True)
    inspectes = []
    for feat in data["features"]:
        geom = shape(feat.get("geometry"))
        bounds = geom.bounds
        # Zone de la Bidassoa, garde-fou pour ne pas associer une autre entité.
        region = (len(bounds) == 4 and -2.5 < bounds[0] < -1.0
                  and -2.5 < bounds[2] < -1.0 and 42.5 < bounds[1] < 44
                  and 42.5 < bounds[3] < 44)
        km2 = (transform(transformeur.transform, geom).area / 1e6
               if geom.is_valid and not geom.is_empty else None)
        inspectes.append({
            "proprietes": feat.get("properties", {}),
            "type_geometrie": geom.geom_type,
            "valide_topologiquement": geom.is_valid,
            "emprise_region_bidassoa": region,
            "surface_km2": round(km2, 6) if km2 is not None else None,
            "bounds_wgs84": [round(x, 7) for x in bounds],
        })
    return {
        "nombre_features": len(inspectes),
        "features": inspectes,
        "identite_COG_98101_etablie": False,
        "geometries_publiees": 0,
    }


def construire() -> dict:
    raw, url = charger(CAPABILITIES)
    couches = lister_couches(raw)
    candidats = candidat_condominium(couches)
    report = {
        "schema": "adlfi.lieux.condominium.ign.wfs.v1",
        "statut": "RECETTE_NON_VALIDANTE_NON_PUBLIEE",
        "service": BASE_WFS, "documentation": DOC,
        "url_capabilities": url,
        "capabilities_sha256": hashlib.sha256(raw).hexdigest(),
        "nombre_couches_wfs": len(couches),
        "couches_condominium": candidats,
        "cog_cible": {"famille": "COMER", "nature": "CDM", "code": "98101"},
        "nouvel_alignement_pactols": 0, "geometries_publiees": 0,
    }
    if len(candidats) != 1:
        report["diagnostic"] = "COUCHE_NON_TROUVEE_OU_AMBIGUE"
        return report
    layer = candidats[0]["name"]
    params = {
        "service": "WFS", "version": "2.0.0",
        "request": "GetFeature", "typeNames": layer,
        "count": "10", "outputFormat": "application/json",
        "srsName": "EPSG:4326",
    }
    try:
        features_raw, feature_url = charger(params)
        feat = json.loads(features_raw)
        contents = analyser_geojson(feat)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        report["diagnostic"] = "GEOMETRIE_JSON_NON_EXPLOITABLE"
        report["erreur"] = str(exc)[:300]
        return report
    report["getfeature_url"] = feature_url
    report["getfeature_sha256"] = hashlib.sha256(features_raw).hexdigest()
    report["resultat"] = contents
    report["diagnostic"] = "COUCHE_CONDOMINIUM_INTERROGEE"
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sortie", type=Path, required=True)
    args = p.parse_args()
    if "docs" in args.sortie.resolve().parts:
        raise ValueError("Aucune recette sous docs/")
    report = construire()
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
