#!/usr/bin/env python3
"""Générer, hors docs/, les 14 contours régionaux/départementaux COG 2018–2025.

Chaque millésime exige son ZIP Insee et sa couche géographique source dont les
SHA256 sont figés dans les deux scripts d'audit. Zéro inférence Pactols.
La copie vers docs/ est une opération de publication distincte, après tests.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from shapely import make_valid
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union
from shapely.validation import explain_validity
from pyproj import Transformer

import auditer_contours_region_departement_2018_2025 as auditer
import qualifier_cog_annuels_regions_departements as cog_annuel

ANNEES = auditer.ANNEES
NIVEAUX = auditer.NIVEAUX
TRANSFORM_TO_M = Transformer.from_crs("EPSG:4326", "EPSG:6933", always_xy=True).transform
REPARATIONS_ATTENDUES = {
    (2019, "regions", "53"),
    (2019, "departements", "22"),
    (2019, "departements", "39"),
    (2019, "departements", "71"),
    (2025, "regions", "53"),
    (2025, "departements", "22"),
}
MAX_ECART_AIRE_PCT = 0.00001


def verifier_dossier_sortie(dossier: Path) -> None:
    if "docs" in dossier.resolve().parts:
        raise ValueError("Refus d'écrire des fichiers non qualifiés directement dans docs/")
    if dossier.exists():
        raise ValueError("Refus d'écraser le dossier de recette existant : " + str(dossier))


def polygons_only(geom):
    if geom.geom_type == "Polygon":
        return [geom]
    if geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        return [p for part in geom.geoms for p in polygons_only(part)]
    return []


def corriger_geometrie(geo: dict, *, annee: int, niveau: str, code: str):
    poly = shape(geo)
    if poly.is_empty or poly.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError(f"Géométrie vide ou non surfacique : {annee}/{niveau}/{code}")
    cle = (annee, niveau, code)
    if poly.is_valid:
        if cle in REPARATIONS_ATTENDUES:
            raise ValueError(f"Anomalie source précédemment attestée devenue absente : {cle}")
        return geo, None
    if cle not in REPARATIONS_ATTENDUES:
        raise ValueError(f"Nouvelle anomalie géométrique non arbitrée : {cle} : {explain_validity(poly)}")
    fixe = make_valid(poly)
    parties = polygons_only(fixe)
    if not parties:
        raise ValueError("Réparation sans composante surfacique : " + str(cle))
    surface = unary_union(parties)
    if surface.is_empty or not surface.is_valid or surface.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError("Réparation topologiquement incorrecte : " + str(cle))
    ancienne_aire = transform(TRANSFORM_TO_M, poly).area
    nouvelle_aire = transform(TRANSFORM_TO_M, surface).area
    if ancienne_aire <= 0:
        raise ValueError("Aire initiale nulle : " + str(cle))
    delta = nouvelle_aire - ancienne_aire
    delta_pct = abs(delta) / ancienne_aire * 100
    if delta_pct > MAX_ECART_AIRE_PCT:
        raise ValueError(f"Réparation trop importante pour {cle} : {delta_pct}%")
    return mapping(surface), {
        "annee": annee, "niveau": niveau[:-1] if niveau == "regions" else "departement",
        "code": code, "anomalie": explain_validity(poly),
        "methode": "shapely.make_valid; composantes surfaciques seulement; unary_union",
        "type_obtenu_make_valid": fixe.geom_type,
        "difference_aire_m2": round(delta, 5),
        "difference_relative_aire_pct": round(delta_pct, 11),
    }


def construire(archives_sig: Path, archives_cog: Path, sortie: Path) -> dict:
    verifier_dossier_sortie(sortie)
    dossier_geo = sortie / "lieux-historique"
    rapport = {
        "schema": "adlfi.lieux.production_couches_annuelles.v1",
        "annees": list(ANNEES),
        "couches": {}, "reparations_geometriques": [],
        "nouvelles_correspondances_pactols": 0,
        "source_geometrique": "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/",
        "restitution_historique_depuis_2026": False,
    }
    index = {
        "schema": "adlfi.lieux.admin.index_annuels.v1",
        "annees": list(ANNEES),
        "nouvelles_correspondances_pactols": 0,
        "entries": [],
    }
    fichiers = {}
    reparations_vues = set()
    for annee in ANNEES:
        zip_cog = (archives_cog / f"cog_ensemble_{annee}_csv.zip" if annee > 2018 else None)
        cog_reg, ref_reg = cog_annuel.lire_cog(
            archives_cog / "regions-2018-txt.zip" if annee == 2018 else zip_cog,
            annee, "regions")
        cog_dep, ref_dep = cog_annuel.lire_cog(
            archives_cog / "departements-2018-txt.zip" if annee == 2018 else zip_cog,
            annee, "departements")
        if len(cog_reg) != 18 or len(cog_dep) != 101:
            raise ValueError("Cardinalité COG annuelle insuffisante")
        region_departements = defaultdict(list)
        for code, dep in cog_dep.items():
            if dep["region"] not in cog_reg:
                raise ValueError(f"Rattachement COG sans région : {annee}/{code}")
            region_departements[dep["region"]].append(code)
        for niveau in NIVEAUX:
            source_path = archives_sig / f"{niveau}-{annee}.geojson.gz"
            geo, source_sha = auditer.lire_geojson(source_path, originaire=True)
            geos, exclus = auditer.indexer(geo, source_path.name)
            cog_map = cog_reg if niveau == "regions" else cog_dep
            codes_qualifies = set(geos) - auditer.HORS_COG
            if codes_qualifies != set(cog_map):
                raise ValueError(f"Codes SIG différents du COG : {annee}/{niveau}")
            features = []
            for code in sorted(cog_map):
                original = geos[code]
                source_props = original["properties"]
                nom = cog_map[code]["nom"]
                if cog_annuel.normaliser(nom) != cog_annuel.normaliser(source_props.get("nom", "")):
                    raise ValueError(f"Dénomination SIG/COG discordante : {annee}/{niveau}/{code}")
                p = {"annee": annee, "code": code, "nom": nom,
                     "niveau": "region" if niveau == "regions" else "departement",
                     "date_reference_COG": f"{annee}-01-01",
                     "annee_geometrie": annee,
                     "pactols_valide": False,
                     "source_geometrie": "Etalab / IGN — contours administratifs 100 m"}
                if niveau == "departements":
                    parent = cog_map[code]["region"]
                    if source_props["region"] != parent:
                        raise ValueError(f"Rattachement SIG/COG divergent : {annee}/{code}")
                    p["code_region_parent"] = parent
                    p["nom_region_parent"] = cog_reg[parent]["nom"]
                else:
                    p["departements"] = sorted(region_departements[code])
                shape_corrigee, reparation = corriger_geometrie(
                    original["geometry"], annee=annee, niveau=niveau, code=code)
                if reparation:
                    reparations_vues.add((annee, niveau, code))
                    rapport["reparations_geometriques"].append(reparation)
                features.append({"type": "Feature", "properties": p,
                                 "geometry": shape_corrigee})
                index["entries"].append({
                    "kind": "admin", "year": annee,
                    "level": p["niveau"], "code": code, "label": nom,
                    "champs": sorted({cog_annuel.normaliser(nom), code.lower()}),
                })
            source_cog = ref_reg if niveau == "regions" else ref_dep
            meta = {
                "schema": "adlfi.lieux.contours.annuels.v1",
                "cog_au_premier_janvier": str(annee),
                "annee_geometrie": annee,
                "generalisation_m": 100,
                "pactols_valide": False,
                "source_geometrie": "Etalab / IGN — contours administratifs",
                "source_geometrie_url": f"https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/{annee}/geojson/{niveau}-100m.geojson.gz",
                "source_cog_url": cog_annuel.SOURCE_PAGES[annee],
                "source_archives_sha256": {source_path.name: source_sha,
                                          source_cog["archive"]: source_cog["sha256"]},
                "nombre_reparations": sum(r["annee"] == annee and r["niveau"] == ("region" if niveau == "regions" else "departement")
                                          for r in rapport["reparations_geometriques"]),
            }
            key = f"{niveau}-{annee}.geojson"
            fichiers[key] = {"type": "FeatureCollection", "provenance": meta,
                            "features": features}
            rapport["couches"][key] = {"nombre_codes": len(features),
                                       "sha256_origine": source_sha,
                                       "sha256_COG": source_cog["sha256"],
                                       "exclus_hors_echelon": exclus}
    if reparations_vues != REPARATIONS_ATTENDUES:
        raise ValueError(f"Liste réelle des réparations différente du protocole : {sorted(reparations_vues)}")
    if len(index["entries"]) != len(ANNEES) * (18 + 101):
        raise ValueError("Index administratif incomplet")
    if len(rapport["reparations_geometriques"]) != 6:
        raise ValueError("Six réparations attendues")
    # On ne publie aucun fichier avant que TOUS les contrôles ne soient passés.
    dossier_geo.mkdir(parents=True, exist_ok=False)
    for path, fc in sorted(fichiers.items()):
        (dossier_geo / path).write_text(json.dumps(fc, ensure_ascii=False,
                 separators=(",", ":"), sort_keys=True)+"\n", encoding="utf-8")
    (dossier_geo / "index-annuels.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":"), sort_keys=True)+"\n",
        encoding="utf-8")
    (dossier_geo / "rapport-annuels.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
        encoding="utf-8")
    return rapport


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives-sig", type=Path, required=True)
    parser.add_argument("--archives-cog", type=Path, required=True)
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    bilan = construire(args.archives_sig, args.archives_cog, args.sortie)
    print(json.dumps({"annees": bilan["annees"],
                      "couches": len(bilan["couches"]),
                      "reparations": bilan["reparations_geometriques"]},
                     ensure_ascii=False))
