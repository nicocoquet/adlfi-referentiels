#!/usr/bin/env python3
"""Dissoudre les départements GEOFLA 2015/2016 en 22 + 13 régions métropolitaines.

Sources : deux archives originales IGN et quatre tableaux COG Insee (reg/dep).
Les contours sont des reconstructions SIG au millésime de leur édition,
non des polygones de régions natifs IGN, ni des géométries garanties au 1er janvier.
Recette seulement : aucune donnée publiée dans docs/ ni alignement Pactols.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from auditer_cog_regions_millesimes import FUSIONS_2016, HASHES, csv_lire, sha256
from comparer_geofla_2015_2016_bfc import SHA_2015

SHA_2016 = "8e1538791c12b7679ef0ffb638a0fc53f8e9dede359c170af6e15576826ea91a"
IGN_EDITION = {2015: "2015-03-04", 2016: "2016-06-28"}
IGN_ARCHIVE = {
    2015: "GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04",
    2016: "GEOFLA_2-2_DEPARTEMENT_SHP_LAMB93_FXX_2016-06-28",
}


def charger_departements(shapefile: Path, annee: int) -> dict:
    import geopandas as gpd

    couche = gpd.read_file(shapefile)
    colonnes = {"CODE_DEPT", "CODE_REG", "geometry"}
    if not colonnes.issubset(couche.columns):
        raise ValueError(f"GEOFLA {annee} : colonnes manquantes")
    if len(couche) != 96 or couche.crs is None or couche.crs.to_epsg() != 2154:
        raise ValueError(f"GEOFLA {annee} : 96 départements Lambert-93 attendus")
    if couche["CODE_DEPT"].isna().any() or couche["CODE_REG"].isna().any():
        raise ValueError("GEOFLA : code géographique absent")
    codes = [str(v) for v in couche["CODE_DEPT"]]
    if len(set(codes)) != 96:
        raise ValueError("GEOFLA : codes départementaux non uniques")
    if couche.geometry.isna().any() or couche.geometry.is_empty.any() or not couche.geometry.is_valid.all():
        raise ValueError(f"GEOFLA {annee} : géométrie absente, vide ou invalide")
    return {
        str(r["CODE_DEPT"]): (str(r["CODE_REG"]), r.geometry)
        for _, r in couche.iterrows()
    }


def dissoudre(departements: dict, noms: dict, annee: int) -> tuple[dict, dict]:
    """Regrouper sans appliquer de simplification ni utiliser de contours contemporains."""
    from shapely.ops import unary_union

    groupes = defaultdict(list)
    codes_groupes = defaultdict(list)
    for dep, (region, geometrie) in sorted(departements.items()):
        if region not in noms:
            raise ValueError(f"Région {region} absente du COG {annee}")
        if geometrie is None or geometrie.is_empty or not geometrie.is_valid:
            raise ValueError(f"Géométrie départementale invalide : {dep}")
        groupes[region].append(geometrie)
        codes_groupes[region].append(dep)
    geoms = {}
    for reg in sorted(groupes):
        geo = unary_union(groupes[reg])
        if geo.is_empty or not geo.is_valid or geo.area <= 0:
            raise ValueError(f"Union régionale invalide : {annee}/{reg}")
        geoms[reg] = geo
    return geoms, {reg: sorted(codes_groupes[reg]) for reg in sorted(codes_groupes)}


def mesurer(a, b) -> dict:
    intersection = a.intersection(b).area
    reunion = a.union(b).area
    if reunion <= 0:
        raise ValueError("Comparaison de contours sans aire")
    return {
        "intersection_sur_union_pct": round(100 * intersection / reunion, 6),
        "difference_symetrique_km2": round(a.symmetric_difference(b).area / 1e6, 4),
        "hausdorff_m": round(a.hausdorff_distance(b), 2),
        "aire_2015_km2": round(a.area / 1e6, 4),
        "aire_2016_km2": round(b.area / 1e6, 4),
    }


def construire(deps15: dict, deps16: dict, regs15: dict, regs16: dict) -> tuple[dict, list]:
    """Vérifier la succession départementale avant toute dissolution régionale."""
    from shapely.ops import unary_union, transform
    from shapely.geometry import mapping
    from pyproj import Transformer

    if set(deps15) != set(deps16) or len(deps15) != 96:
        raise ValueError("Les deux éditions ne contiennent pas les mêmes 96 départements")
    groups15, codes15 = dissoudre(deps15, regs15, 2015)
    groups16, codes16 = dissoudre(deps16, regs16, 2016)
    if len(groups15) != 22 or len(groups16) != 13:
        raise ValueError("22 régions 2015 et 13 régions 2016 attendues")
    ancien_vers_nouveau = {old: new for new, olds in FUSIONS_2016.items() for old in olds}
    if len(ancien_vers_nouveau) != 16 or len(FUSIONS_2016) != 7:
        raise ValueError("Table de fusion régionale incomplète")
    changements = 0
    for code in sorted(deps15):
        old, new = deps15[code][0], deps16[code][0]
        if ancien_vers_nouveau.get(old, old) != new:
            raise ValueError(f"Rattachement impossible {code}: {old} → {new}")
        changements += old != new
    if changements != 65:
        raise ValueError(f"65 changements régionaux attendus, {changements} observés")

    comparaisons = []
    for new in sorted(groups16):
        predecessors = list(FUSIONS_2016.get(new, (new,)))
        if any(old not in groups15 for old in predecessors):
            raise ValueError(f"Prédécesseur régional manquant : {new}")
        attendu = sorted(dep for old in predecessors for dep in codes15[old])
        if attendu != codes16[new]:
            raise ValueError(f"Composition des départements différente : région {new}")
        avant = unary_union([groups15[old] for old in sorted(predecessors)])
        mesure = mesurer(avant, groups16[new])
        # Un garde-fou contre les erreurs de source ou d'assemblage, sans
        # exiger une égalité géométrique entre deux éditions IGN distinctes.
        if mesure["intersection_sur_union_pct"] < 99.0:
            raise ValueError(f"Discordance spatiale majeure {new}: {mesure}")
        comparaisons.append({
            "code_region_2016": new,
            "nature": "fusion" if new in FUSIONS_2016 else "continuite",
            "codes_regions_2015": ",".join(sorted(predecessors)),
            "nombre_departements": len(codes16[new]),
            **mesure,
        })
    if sum(r["nature"] == "fusion" for r in comparaisons) != 7:
        raise ValueError("Sept fusions attendues")
    if sum(r["nature"] == "continuite" for r in comparaisons) != 6:
        raise ValueError("Six régions métropolitaines maintenues attendues")

    vers_wgs84 = Transformer.from_crs(2154, 4326, always_xy=True).transform
    collections = {}
    for year, geoms, codes, noms in (
        (2015, groups15, codes15, regs15), (2016, groups16, codes16, regs16)
    ):
        features = [{
            "type": "Feature",
            "properties": {
                "code_region": reg,
                "nom_COG": noms[reg],
                "niveau": "region",
                "code_departement_sources": codes[reg],
                "millesime_COG": year,
                "date_reference_COG": f"{year}-01-01",
                "date_edition_IGN": IGN_EDITION[year],
                "nature_geometrie": "union_departements_GEOFLA_meme_edition",
                "source_couche": "IGN GEOFLA DEPARTEMENT",
                "contour_regional_natif": False,
                "alignement_Pactols_valide": False,
                "precision_historique": "millésime_SIG_non_validite_temporelle",
            },
            "geometry": mapping(transform(vers_wgs84, geoms[reg])),
        } for reg in sorted(geoms)]
        collections[str(year)] = {
            "type": "FeatureCollection",
            "provenance": {
                "producteur": "IGN",
                "edition": IGN_ARCHIVE[year],
                "source": "GEOFLA DEPARTEMENT, EPSG:2154",
                "transformation": "unions par codes régionaux du COG contemporain à l'édition",
                "geometries_2026_utilisees": False,
            },
            "features": features,
        }
    return collections, comparaisons


def analyser(sources: dict) -> tuple[dict, list, dict]:
    if sha256(sources["archive2015"]) != SHA_2015 or sha256(sources["archive2016"]) != SHA_2016:
        raise ValueError("Empreintes des archives IGN originales incorrectes")
    for year in (2015, 2016):
        for kind in ("dep", "reg"):
            role = f"{kind}{year}"
            if sha256(sources[role]) != HASHES[role]:
                raise ValueError(f"Empreinte COG officielle incorrecte : {role}")
    reg_rows = {y: csv_lire(sources[f"reg{y}"], "reg", y) for y in (2015, 2016)}
    dep_rows = {y: csv_lire(sources[f"dep{y}"], "dep", y) for y in (2015, 2016)}
    if any(len(reg_rows[y]) != n for y, n in ((2015, 27), (2016, 18))):
        raise ValueError("Listes COG de régions incomplètes")
    if any(len(dep_rows[y]) != 101 for y in (2015, 2016)):
        raise ValueError("Listes COG de départements incomplètes")
    noms = {y: {r["REGION"]: r["NCCENR"] for r in reg_rows[y]} for y in (2015, 2016)}
    geofla = {y: charger_departements(sources[f"shp{y}"], y) for y in (2015, 2016)}
    for year in (2015, 2016):
        dep_cog = {r["DEP"]: r["REGION"] for r in dep_rows[year]}
        if len(dep_cog) != 101:
            raise ValueError("Codes départementaux COG non uniques")
        if not set(geofla[year]).issubset(dep_cog):
            raise ValueError("Code IGN absent du COG")
        for dep, (reg, _) in geofla[year].items():
            if dep_cog[dep] != reg:
                raise ValueError(f"GEOFLA / COG {year}, département {dep}: {reg} ≠ {dep_cog[dep]}")
    collections, comparaisons = construire(geofla[2015], geofla[2016], noms[2015], noms[2016])
    rapport = {
        "schema": "adlfi.lieux.regions_metropole_geofla_2015_2016.v1",
        "statut": "RECETTE_HORS_PAGES_NON_VALIDANTE",
        "regions_par_millesime": {"2015": 22, "2016": 13},
        "nombre_geometries_regionales_derivees": 35,
        "nombre_departements_source_par_millesime": 96,
        "fusions_regionales_controlees": 7,
        "regions_maintenues_controlees": 6,
        "departements_changeant_de_code_region": 65,
        "sources_SHA256": {
            "IGN_archive_2015": sha256(sources["archive2015"]),
            "IGN_archive_2016": sha256(sources["archive2016"]),
            **{role: sha256(sources[role]) for role in ("dep2015", "dep2016", "reg2015", "reg2016")},
        },
        "comparaisons_contours": comparaisons,
        "absence_retroprojection_depuis_2026": True,
        "alignements_Pactols_crees": 0,
        "publication_docs": False,
        "limites": [
            "Les régions sont des unions de départements IGN, pas des géométries régionales natives.",
            "Les millésimes GEOFLA du 4 mars 2015 et du 28 juin 2016 ne sont pas les états SIG garantis au 1er janvier.",
            "La différence géométrique entre deux éditions n'est pas une évolution administrative démontrée.",
            "La couche métropolitaine GEOFLA FXX exclut les cinq départements ultramarins.",
        ],
    }
    return collections, comparaisons, rapport


def exporter(collections: dict, comparaisons: list, rapport: dict, sortie: Path) -> None:
    dest = Path(sortie)
    if "docs" in dest.resolve().parts:
        raise ValueError("Interdiction de publier des géométries de recette dans docs/")
    if set(collections) != {"2015", "2016"}:
        raise ValueError("Les deux éditions doivent être présentes")
    if (len(collections["2015"]["features"]), len(collections["2016"]["features"])) != (22, 13):
        raise ValueError("35 contours régionaux attendus")
    if len(comparaisons) != 13:
        raise ValueError("13 régions successeures à contrôler")
    dest.mkdir(parents=True, exist_ok=True)
    for year in ("2015", "2016"):
        path = dest / f"regions-metropole-{year}-IGN-geofla.geojson"
        path.write_text(json.dumps(collections[year], ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (dest / "comparaisons-regions-metropole-IGN-2015-2016.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(comparaisons[0]), delimiter=";")
        writer.writeheader()
        writer.writerows(comparaisons)
    (dest / "rapport-regions-metropole-IGN-2015-2016.json").write_text(
        json.dumps(rapport, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    for key in ("shp2015", "shp2016", "archive2015", "archive2016",
                "dep2015", "dep2016", "reg2015", "reg2016", "sortie"):
        ap.add_argument("--" + key, type=Path, required=True)
    args = vars(ap.parse_args())
    sortie = args.pop("sortie")
    collections, comparaisons, rapport = analyser(args)
    exporter(collections, comparaisons, rapport, sortie)
    print(json.dumps({
        "regions_2015": len(collections["2015"]["features"]),
        "regions_2016": len(collections["2016"]["features"]),
        "fusions_controlees": rapport["fusions_regionales_controlees"],
        "min_recouvrement_pct": min(v["intersection_sur_union_pct"] for v in comparaisons)
    }, ensure_ascii=False, sort_keys=True))
