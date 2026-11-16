#!/usr/bin/env python3
"""Audit NON validant des contours 2026 pour les 233 cibles ultramarines COG.

Distingue 129 communes DROM, 95 subdivisions COMER typées et 9 territoires
COMER. La source cartographique est un fichier de communes, PAS un fichier
attestant les limites propres des collectivités, districts ou circonscriptions.
Aucune géométrie n'est publiée, aucun ARK n'est attribué.
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path

try:
    from shapely.geometry import shape
except ImportError:  # Le test de structure reste importable sans Shapely.
    shape = None

DROM = frozenset(("971", "972", "973", "974", "976"))
NATURES = ("COM", "DIS", "CIR", "CPT", "CDM")
GEO_SOURCE = (
    "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/"
    "2026/geojson/communes-100m.geojson.gz"
)
COG_SOURCE = "https://www.insee.fr/fr/information/8740222"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_lignes(path: Path, colonnes: set[str]) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        first = stream.readline()
        stream.seek(0)
        reader = csv.DictReader(
            stream, delimiter=";" if first.count(";") > first.count(",") else ","
        )
        if not colonnes.issubset(reader.fieldnames or []):
            raise ValueError(f"Colonnes COG inattendues : {path.name}")
        lignes = list(reader)
    if not lignes or any(None in ligne or None in ligne.values() for ligne in lignes):
        raise ValueError(f"CSV COG incomplet : {path.name}")
    return lignes


def cibles(drom: list[dict], comer: list[dict],
           territoires: list[dict], strict: bool) -> list[dict]:
    resultats = []
    for r in drom:
        if r["TYPECOM"] == "COM" and r["DEP"] in DROM:
            resultats.append({
                "cle": "DROM:COM:" + r["COM"], "code": r["COM"],
                "nature": "COM", "famille": "DROM",
                "parent": r["DEP"], "libelle_cog": r["LIBELLE"],
            })
    for r in comer:
        if r["NATURE_ZONAGE"] not in NATURES:
            raise ValueError("NATURE_ZONAGE inconnue : " + r["NATURE_ZONAGE"])
        resultats.append({
            "cle": "COMER:" + r["NATURE_ZONAGE"] + ":" + r["COM_COMER"],
            "code": r["COM_COMER"], "nature": r["NATURE_ZONAGE"],
            "famille": "COMER", "parent": r["COMER"],
            "libelle_cog": r["LIBELLE"],
        })
    for r in territoires:
        resultats.append({
            "cle": "COMER:TERRITOIRE:" + r["COMER"], "code": r["COMER"],
            "nature": "TERRITOIRE", "famille": "COMER",
            "parent": "", "libelle_cog": r["LIBELLE"],
        })
    cles = [r["cle"] for r in resultats]
    if len(cles) != len(set(cles)):
        raise ValueError("Clé COG typée dupliquée")
    parents = {r["code"] for r in resultats if r["nature"] == "TERRITOIRE"}
    if any(r["parent"] not in parents for r in resultats
           if r["famille"] == "COMER" and r["nature"] != "TERRITOIRE"):
        raise ValueError("Subdivisions COMER sans collectivité de référence")
    if strict:
        comptes = collections.Counter((r["famille"], r["nature"]) for r in resultats)
        attendu = {
            ("DROM", "COM"): 129, ("COMER", "COM"): 85,
            ("COMER", "DIS"): 5, ("COMER", "CIR"): 3,
            ("COMER", "CPT"): 1, ("COMER", "CDM"): 1,
            ("COMER", "TERRITOIRE"): 9,
        }
        if comptes != attendu:
            raise ValueError(f"Cardinalités du COG 2026 modifiées : {comptes}")
    return sorted(resultats, key=lambda r: r["cle"])


def lire_geojson(path: Path) -> dict[str, list[dict]]:
    with gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" \
         else path.open("r", encoding="utf-8") as stream:
        geo = json.load(stream)
    if geo.get("type") != "FeatureCollection" or not isinstance(
        geo.get("features"), list
    ):
        raise ValueError("Fichier GeoJSON incompatible")
    index = collections.defaultdict(list)
    for f in geo["features"]:
        if f.get("type") != "Feature" or not isinstance(f.get("properties"), dict):
            raise ValueError("Feature GeoJSON incompatible")
        code = str(f["properties"].get("code", ""))
        if code:
            index[code].append(f)
    if not index:
        raise ValueError("Codes géographiques absents du GeoJSON")
    return index


def qualifier(cible: dict, index: dict[str, list[dict]]) -> dict:
    sortie = dict(cible)
    sortie.update(statut="ABSENTE_DU_FICHIER_COMMUNES",
                  type_geometrie="", valide_topologie="",
                  alerte_antimeridien="", nombre_features=0)
    if cible["nature"] == "TERRITOIRE":
        sortie["statut"] = "NON_EVALUE_TERRITOIRE_SANS_COUCHE_DEDIEE"
        return sortie
    geoms = index.get(cible["code"], [])
    sortie["nombre_features"] = len(geoms)
    if len(geoms) > 1:
        sortie["statut"] = "DOUBLON_CODE_DANS_SOURCE"
        return sortie
    if not geoms:
        return sortie
    if shape is None:
        raise RuntimeError("Shapely requis pour qualifier les géométries")
    try:
        g = shape(geoms[0]["geometry"])
        sortie["type_geometrie"] = g.geom_type
        ok = bool(g.is_valid and not g.is_empty and g.area > 0
                  and g.geom_type in ("Polygon", "MultiPolygon"))
        sortie["valide_topologie"] = "oui" if ok else "non"
        minx, miny, maxx, maxy = g.bounds
        sortie["alerte_antimeridien"] = (
            "A_CONTROLER" if maxx - minx > 180 else ""
        )
        if minx < -180 or maxx > 180 or miny < -90 or maxy > 90:
            ok = False
            sortie["valide_topologie"] = "non"
        sortie["statut"] = "PRESENTE_VALIDE_A_QUALIFIER" if ok else "PRESENTE_INVALIDE"
    except (ValueError, TypeError, KeyError, AttributeError, IndexError):
        sortie["statut"] = "PRESENTE_INVALIDE"
        sortie["valide_topologie"] = "non"
    return sortie


def construire(source_dir: Path, geo_path: Path, sortie_dir: Path,
               strict: bool = True) -> dict:
    source_dir, geo_path, sortie_dir = (
        Path(source_dir).resolve(), Path(geo_path).resolve(),
        Path(sortie_dir).resolve()
    )
    if "docs" in sortie_dir.parts or sortie_dir == source_dir \
       or sortie_dir.is_relative_to(source_dir):
        raise ValueError("Audit de recette interdit sous docs/ ou sous les sources")
    noms = {
        "drom": "v_commune_2026.csv",
        "comer": "v_commune_comer_2026.csv",
        "territoires": "v_comer_2026.csv",
    }
    lignes = {
        "drom": csv_lignes(source_dir / noms["drom"],
                          {"COM", "TYPECOM", "DEP", "LIBELLE"}),
        "comer": csv_lignes(source_dir / noms["comer"],
                           {"COM_COMER", "NATURE_ZONAGE", "COMER", "LIBELLE"}),
        "territoires": csv_lignes(source_dir / noms["territoires"],
                                 {"COMER", "LIBELLE"}),
    }
    index = lire_geojson(geo_path)
    audit = [qualifier(c, index) for c in cibles(
        lignes["drom"], lignes["comer"], lignes["territoires"], strict
    )]
    stats = {}
    for famille, nature in sorted({(r["famille"], r["nature"]) for r in audit}):
        subset = [r for r in audit if (r["famille"], r["nature"]) == (famille, nature)]
        stats[famille + ":" + nature] = {
            "total": len(subset),
            "statuts": dict(sorted(collections.Counter(
                r["statut"] for r in subset).items())),
            "alertes_antimeridien": sum(bool(r["alerte_antimeridien"]) for r in subset),
        }
    rapport = {
        "schema": "adlfi.lieux.outremer.geometries2026.audit.v1",
        "statut": "RECETTE_NON_VALIDANTE_NON_PUBLIEE",
        "annee_etat_cog": 2026,
        "date_contours": "2026-05-04",
        "source_cog": COG_SOURCE,
        "source_geo": GEO_SOURCE,
        "licence_contours": "ODbL",
        "sources_sha256": {
            **{noms[k]: sha256(source_dir / noms[k]) for k in sorted(noms)},
            geo_path.name: sha256(geo_path),
        },
        "nombre_cibles": len(audit),
        "repartition": stats,
        "limites": [
            "Le GeoJSON des communes ne constitue pas une couche des neuf collectivités COMER.",
            "Un contour nommé ou portant le bon code ne valide pas l'identité juridique du zonage.",
            "COM dans le fichier COMER n'implique pas commune de droit commun.",
            "Les DIS, CIR, CPT, CDM ne deviennent pas des communes dans l'interface.",
            "Validité topologique de la source contrôlée sans réparation; provenance locale à instruire.",
            "Un intervalle de longitude supérieur à 180 degrés demande un contrôle de l'antiméridien.",
            "COG au 1er janvier 2026 et édition des contours du 4 mai 2026 distincts.",
            "Aucune géométrie 2026 n'est une géométrie historique par défaut.",
        ],
        "nouveaux_alignements_pactols": 0,
        "geometries_publiees": 0,
    }
    sortie_dir.mkdir(parents=True, exist_ok=True)
    with (sortie_dir / "controle_233_cibles.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        colonnes = list(audit[0].keys())
        w = csv.DictWriter(f, fieldnames=colonnes, delimiter=";")
        w.writeheader()
        w.writerows(audit)
    (sortie_dir / "rapport_couverture_2026.json").write_text(
        json.dumps(rapport, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8"
    )
    return rapport


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--geojson", required=True, type=Path)
    parser.add_argument("--sortie", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(construire(args.sources, args.geojson, args.sortie),
                     ensure_ascii=False, sort_keys=True, indent=2))
