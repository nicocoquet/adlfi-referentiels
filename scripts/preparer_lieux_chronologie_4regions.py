#!/usr/bin/env python3
"""Préparer quatre régions COG 1943–2026 pour une recette cartographique.

Les périodes COM/ARM sont celles du COG 2026 depuis 1943. Les COMA/COMD ne
sont observées qu'en 2026 ; les contours sont UNIQUEMENT ceux de 2026.
Les alignements Pactols proviennent EXCLUSIVEMENT du pilote PACA déjà publié.
Les régions historiques ne sont PAS reconstituées par un préfixe de code.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

COG_SHA256 = {
    "communes": "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
    "historique": "08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
    "mouvements": "8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
}
REGIONS = {
    "bfc": {"titre": "Bourgogne-Franche-Comté", "reg": "27",
            "departements": ("21", "25", "39", "58", "70", "71", "89", "90")},
    "pdl": {"titre": "Pays de la Loire", "reg": "52",
            "departements": ("44", "49", "53", "72", "85")},
    "corse": {"titre": "Corse", "reg": "94",
              "departements": ("20", "2A", "2B")},
    "paca": {"titre": "Provence-Alpes-Côte d'Azur", "reg": "93",
             "departements": ("04", "05", "06", "13", "83", "84")},
}
GEO_URL = ("https://etalab-datasets.geo.data.gouv.fr/"
           "contours-administratifs/2026/geojson/communes-100m.geojson.gz")
SCHEMA = "adlfi.lieux.chronologie.4regions.public-recette.v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lire_csv(path: Path, required: set[str]) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rdr = csv.DictReader(stream)
        if not set(required).issubset(rdr.fieldnames or []):
            raise ValueError("Colonnes COG manquantes : " + str(path))
        return list(rdr)


def periode_active(row: dict, date: str) -> bool:
    """[DATE_DEBUT, DATE_FIN[ ; les périodes de durée nulle sont inactives."""
    return row["debut_inclus"] <= date and (
        not row["fin_exclue"] or date < row["fin_exclue"])


def construire(communes: Path, historique: Path, mouvements: Path,
               contours: Path, paca: Path, sortie: Path,
               verifier_sha: bool = True) -> dict:
    paths = {"communes": Path(communes), "historique": Path(historique),
             "mouvements": Path(mouvements)}
    for role, path in paths.items():
        if verifier_sha and sha(path) != COG_SHA256[role]:
            raise ValueError("SHA-256 COG 2026 incompatible : " + role)
    courant = lire_csv(paths["communes"], {"TYPECOM", "COM", "LIBELLE", "REG", "DEP", "COMPARENT"})
    hist = lire_csv(paths["historique"], {"TYPECOM", "COM", "LIBELLE", "DATE_DEBUT", "DATE_FIN"})
    mvt = lire_csv(paths["mouvements"], {
        "MOD", "DATE_EFF", "TYPECOM_AV", "COM_AV", "LIBELLE_AV",
        "TYPECOM_AP", "COM_AP", "LIBELLE_AP"})
    if verifier_sha and (len(courant), len(hist), len(mvt)) != (37496, 42333, 13734):
        raise ValueError("Cardinalité COG inattendue")

    # Les contours 2026 sont distincts des codes historiques.
    raw_geo = Path(contours).read_bytes()
    geo = json.loads(gzip.decompress(raw_geo) if raw_geo[:2] == b"\x1f\x8b" else raw_geo)
    if geo.get("type") != "FeatureCollection" or not isinstance(geo.get("features"), list):
        raise ValueError("Source de contours non GeoJSON")
    features = {}
    for feature in geo["features"]:
        props = feature.get("properties") or {}
        code = props.get("code")
        if code:
            if code in features:
                raise ValueError("Code géométrique 2026 dupliqué : " + code)
            features[code] = feature

    pilote = json.loads(Path(paca).read_text(encoding="utf-8"))
    autorites = pilote.get("autorites", [])
    if verifier_sha and len(autorites) != 103:
        raise ValueError("Le pilote PACA doit conserver 103 correspondances")
    valid_paca = {}
    for row in autorites:
        relations = row.get("correspondances", [])
        if len(relations) != 1 or relations[0].get("relation_editoriale") != "correspondance_communale_validee":
            raise ValueError("Relation PACA non validée dans le pilote")
        relation = relations[0]
        code = relation["code_insee"]
        if code in valid_paca:
            raise ValueError("Code PACA validé en double")
        valid_paca[code] = {
            "ark_pactols": row["ark_pactols"],
            "libelle_pactols": row["libelle_pactols"],
            "code_insee": code,
            "millesime_validation": relation["millesime_cog"],
            "date_validation": relation["validation"]["date"],
            "statut": "correspondance_PACA_preexistante_validee",
        }

    output = Path(sortie)
    if "recette" in output.parts and "docs" not in output.parts:
        pass
    # Un contrat distinct décide la publication, jamais ce constructeur.
    output.mkdir(parents=True, exist_ok=True)
    resultat = {}
    for slug, reg in REGIONS.items():
        prefix = reg["departements"]
        # Le préfixe est un critère documentaire d'indexation et NON
        # une preuve de rattachement territorial historique à la région.
        codes_periodes = {row["COM"] for row in hist
                          if row["TYPECOM"] == "COM" and row["COM"].startswith(prefix)}
        code_2026 = {r["COM"] for r in courant if r["REG"] == reg["reg"]
                     and r["TYPECOM"] == "COM"}
        codes = codes_periodes | code_2026
        periodes = sorted((
            {"code_insee": r["COM"], "typecom": r["TYPECOM"],
             "libelle": r["LIBELLE"], "debut_inclus": r["DATE_DEBUT"],
             "fin_exclue": r["DATE_FIN"] or None}
            for r in hist if r["TYPECOM"] == "COM" and r["COM"] in codes
        ), key=lambda r: (r["code_insee"], r["debut_inclus"], r["libelle"]))
        observations = sorted((
            {"code_insee": r["COM"], "typecom": r["TYPECOM"],
             "libelle": r["LIBELLE"], "comparent_2026": r["COMPARENT"] or None,
             "date_observation": "2026-01-01"}
            for r in courant if r["COMPARENT"] in code_2026
            and r["TYPECOM"] in ("COMA", "COMD")
        ), key=lambda r: (r["code_insee"], r["typecom"]))
        evenements = []
        lignes_seen = set()
        for r in mvt:
            if not ({r["COM_AV"], r["COM_AP"]} - {""}) & codes:
                continue
            colonnes = (r["MOD"], r["DATE_EFF"], r["TYPECOM_AV"], r["COM_AV"],
                        r["LIBELLE_AV"], r["TYPECOM_AP"], r["COM_AP"], r["LIBELLE_AP"])
            key = hashlib.sha256(json.dumps(colonnes, ensure_ascii=False).encode("utf-8")).hexdigest()[:24]
            if key in lignes_seen:
                raise ValueError("Ligne COG dupliquée")
            lignes_seen.add(key)
            evenements.append({
                "id": "cog:" + key, "date_effet": r["DATE_EFF"], "mod": r["MOD"],
                "typecom_avant": r["TYPECOM_AV"], "code_avant": r["COM_AV"],
                "libelle_avant": r["LIBELLE_AV"], "typecom_apres": r["TYPECOM_AP"],
                "code_apres": r["COM_AP"], "libelle_apres": r["LIBELLE_AP"],
            })
        evenements.sort(key=lambda r: (r["date_effet"], r["id"]))
        alignements = sorted(
            (v for k, v in valid_paca.items() if k in code_2026),
            key=lambda r: r["code_insee"]
        ) if slug == "paca" else []
        if verifier_sha and slug == "paca" and len(alignements) != 103:
            raise ValueError("Les 103 validations PACA ont été perdues")
        geometries = [
            {"type": "Feature",
             "properties": {
                "code": code, "nom": (features[code].get("properties") or {}).get("nom", ""),
                "millesime": 2026, "statut": "contour_COG_2026_sans_validation_ARK_inferree",
                "ark_pactols_valide_2026": valid_paca[code]["ark_pactols"]
                  if slug == "paca" and code in valid_paca else None},
             "geometry": features[code]["geometry"]}
            for code in sorted(code_2026) if code in features
        ]
        manquants = sorted(code_2026 - set(features))
        if verifier_sha and len(manquants) > 4:
            raise ValueError("Contours communaux 2026 manquants en grand nombre: " + slug)
        data = {
            "schema": SCHEMA, "region": slug, "nom_region": reg["titre"],
            "millesime_cog": 2026, "annee_min": 1943, "annee_max": 2026,
            "annee_initiale": 2026,
            "critere_regional": "prefixes_de_codes_historiques_et_REGION_2026",
            "limite": "Le préfixe du code n'établit pas la localisation historique. "
                "Aucune géométrie ancienne ni équivalence Pactols historique n'est inférée.",
            "periodes_com": periodes, "observations_COMA_COMD_2026": observations,
            "lignes_mouvements_cog": evenements,
            "alignements_Pactols_COG_valides_2026": alignements,
            "geometries_historiques": [],
        }
        geo_out = {"type": "FeatureCollection", "features": geometries,
                   "provenance": {"source": GEO_URL,
                                  "sha256_fichier_geo_source": sha(Path(contours)),
                                  "millesime": 2026, "generalisation": "100m",
                                  "licence": "ODbL"}}
        (output / ("cog-" + slug + ".json")).write_text(
            json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8")
        (output / ("contours-2026-" + slug + ".geojson")).write_text(
            json.dumps(geo_out, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8")
        resultat[slug] = {
            "periodes": len(periodes), "mouvements": len(evenements),
            "contours_2026": len(geometries), "contours_manquants": manquants,
            "validations_pactols_existantes": len(alignements)}
    manifest = {
        "schema": SCHEMA, "statut": "publication_pilote_quatre_regions",
        "regions": resultat,
        "sources": {**{k: sha(v) for k, v in paths.items()},
                    "contours_2026": sha(Path(contours)),
                    "pilote_paca": sha(Path(paca))},
        "garanties": ["Aucun code historique n'est une localisation historique inférée.",
                      "Aucune relation Pactols nouvelle validée.",
                      "Seules les 103 validations PACA préexistantes sont reprises.",
                      "Tous les contours sont de 2026.",
                      "Le statut COMA/COMD n'est connu ici qu'en 2026.",
                      "Les lignes COG ne sont pas des actes administratifs dédoublonnés."]
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("communes", "historique", "mouvements", "contours", "paca", "sortie"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(construire(**vars(args)), ensure_ascii=False, indent=2))
