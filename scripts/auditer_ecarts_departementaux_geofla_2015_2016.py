#!/usr/bin/env python3
"""Auditer les écarts départementaux GEOFLA 2015/2016 sans les confondre avec des événements.

Les 96 codes sont stables, mais les limites ne le sont pas nécessairement.
Identifier en particulier la surface perdue par le 44 et gagnée par le 49,
à rapprocher du décret n° 2015-1751 (effet 31 décembre 2015).
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from auditer_cog_regions_millesimes import sha256
from comparer_geofla_2015_2016_bfc import SHA_2015
from construire_regions_metropole_geofla_2015_2016 import (
    SHA_2016, charger_departements, mesurer
)

DECRET_TRANSFERT = "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000031690124/"


def calculer_transfert(geom_source_2015, geom_source_2016,
                      geom_cible_2015, geom_cible_2016) -> float:
    """Surface commune à la perte d'un département et au gain de l'autre (m²)."""
    depart = geom_source_2015.difference(geom_source_2016)
    arrivee = geom_cible_2016.difference(geom_cible_2015)
    return depart.intersection(arrivee).area


def comparer(ancien: dict, nouveau: dict) -> tuple[list, dict]:
    if len(ancien) != 96 or set(ancien) != set(nouveau):
        raise ValueError("Comparaison nationale exige les mêmes 96 codes départementaux")
    rows = []
    for dep in sorted(ancien):
        reg15, geom15 = ancien[dep]
        reg16, geom16 = nouveau[dep]
        m = mesurer(geom15, geom16)
        rows.append({
            "code_departement": dep,
            "code_region_2015": reg15,
            "code_region_2016": reg16,
            "aire_perdue_2015_2016_km2": round(geom15.difference(geom16).area / 1e6, 4),
            "aire_gagnee_2015_2016_km2": round(geom16.difference(geom15).area / 1e6, 4),
            **m,
        })
    geo15_44, geo16_44 = ancien["44"][1], nouveau["44"][1]
    geo15_49, geo16_49 = ancien["49"][1], nouveau["49"][1]
    transfert_km2 = calculer_transfert(geo15_44, geo16_44, geo15_49, geo16_49) / 1e6
    if not (6.0 <= transfert_km2 <= 6.4):
        raise ValueError(f"Transfert géométrique Le Fresne-sur-Loire 44→49 hors référence : {transfert_km2}")
    if ancien["44"][0] != nouveau["44"][0] or ancien["49"][0] != nouveau["49"][0]:
        raise ValueError("Le transfert interdépartemental ne doit pas être compté comme changement régional")
    rapport = {
        "schema": "adlfi.lieux.audit_departements_geofla_2015_2016.v1",
        "statut": "RECETTE_HORS_PAGES_NON_VALIDANTE",
        "departements_controles": len(rows),
        "sources_SHA256": {"GEOFLA_archive_2015": SHA_2015, "GEOFLA_archive_2016": SHA_2016},
        "ecarts_principaux_km2": [
            {"code_departement": item["code_departement"],
             "difference_symetrique_km2": item["difference_symetrique_km2"]}
            for item in sorted(rows, key=lambda v: -v["difference_symetrique_km2"])[:6]
        ],
        "transfert_interdepartemental_documente": {
            "departement_source": "44", "departement_cible": "49",
            "commune": "Le Fresne-sur-Loire",
            "surface_geometrique_perdue_et_gagnee_km2": round(transfert_km2, 4),
            "date_effet_juridique": "2015-12-31",
            "texte_juridique": "décret n° 2015-1751 du 23 décembre 2015, art. 1 et 4",
            "source_juridique": DECRET_TRANSFERT,
            "statut": "TRANSFERT_ADMINISTRATIF_CONFIRME_ACTE_JURIDIQUE",
        },
        "qualifications_a_ne_pas_inferer": [
            "Les écarts entre les géométries des départements littoraux ne prouvent pas un transfert terrestre.",
            "Les fortes différences 33/17 (estuaire de la Gironde) et 56 (golfe du Morbihan) nécessitent de distinguer conventions de représentation et évolution juridique.",
            "La stabilité du code départemental et du rattachement régional n'implique pas la stabilité des limites départementales.",
            "Les éditions IGN 2015-03-04 et 2016-06-28 ne sont pas des photographies des limites au 1er janvier.",
        ],
        "nouveaux_alignements_Pactols": 0,
        "publication_docs": False,
    }
    return rows, rapport


def analyser(shp2015: Path, shp2016: Path, archive2015: Path, archive2016: Path):
    if sha256(archive2015) != SHA_2015 or sha256(archive2016) != SHA_2016:
        raise ValueError("Empreinte archive GEOFLA inattendue")
    ancien = charger_departements(shp2015, 2015)
    nouveau = charger_departements(shp2016, 2016)
    return comparer(ancien, nouveau)


def exporter(rows: list, rapport: dict, sortie: Path) -> None:
    dest = Path(sortie)
    if "docs" in dest.resolve().parts:
        raise ValueError("Interdiction de publication dans docs/")
    if len(rows) != 96 or len({r["code_departement"] for r in rows}) != 96:
        raise ValueError("96 départements attendus")
    dest.mkdir(parents=True, exist_ok=True)
    with (dest / "comparaison-96-departements-GEOFLA-2015-2016.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    (dest / "rapport-ecarts-departements-GEOFLA-2015-2016.json").write_text(
        json.dumps(rapport, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("shp2015", "shp2016", "archive2015", "archive2016", "sortie"):
        ap.add_argument("--" + name, type=Path, required=True)
    args = vars(ap.parse_args())
    dest = args.pop("sortie")
    rows, report = analyser(**args)
    exporter(rows, report, dest)
    print(json.dumps({
        "departements": len(rows),
        "transfert_44_49_km2": report["transfert_interdepartemental_documente"]["surface_geometrique_perdue_et_gagnee_km2"],
        "principaux_ecarts": report["ecarts_principaux_km2"]
    }, ensure_ascii=False, sort_keys=True))
