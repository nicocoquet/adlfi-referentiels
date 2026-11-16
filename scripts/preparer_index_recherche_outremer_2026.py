#!/usr/bin/env python3
"""Indexer en RECETTE les 212 communes ultramarines COG 2026 et 21 autres entités.

Complément au pilote national temporel des communes, pas remplacement. Les
autorités administratives, les décisions éditoriales Pactols, les observations
historiques COG et les diagnostics de géométries sont quatre dimensions
distinctes. Aucune nouvelle équivalence, géométrie ou relation historique.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

from auditer_contours_outremer_2026 import cibles, csv_lignes

SCHEMA = "adlfi.lieux.recherche.outremer.cog2026.recette.v1"
DATE = "2026-01-01"
GEOMETRIE_DATE = "2026-05-04"
PARENTS_COMER = {"975": 2, "987": 48, "988": 33}
DROM = {"971": 32, "972": 34, "973": 22, "974": 24, "976": 17}
SHA = {
    "v_commune_2026.csv": "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
    "v_departement_2026.csv": "513900ca23edc682ef9b912d7bfc317129eac3a7d71ff19bc22b40ea4838e6eb",
    "v_commune_comer_2026.csv": "9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8",
    "v_comer_2026.csv": "d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed",
    "v_commune_depuis_1943.csv": "08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
    "v_commune_outremer_depuis_1943.csv": "d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748",
}
DECISIONS = {
    "VALIDE_2026",
    "ARK_CONFIRME_CORRESPONDANCE_A_VALIDER",
    "A_INSTRUIRE",
}


def normaliser(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", text))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serialiser(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def sources_cog(source_dir: Path, strict: bool = True) -> dict:
    for name, expected in SHA.items():
        file = source_dir / name
        if strict and digest(file) != expected:
            raise ValueError("Empreinte COG non conforme : " + name)
    return {
        "communes": csv_lignes(source_dir / "v_commune_2026.csv",
                               {"TYPECOM", "COM", "DEP", "REG", "LIBELLE"}),
        "departements": csv_lignes(source_dir / "v_departement_2026.csv",
                                  {"DEP", "REG", "LIBELLE"}),
        "zonages": csv_lignes(source_dir / "v_commune_comer_2026.csv",
                             {"COM_COMER", "COMER", "NATURE_ZONAGE", "LIBELLE"}),
        "territoires": csv_lignes(source_dir / "v_comer_2026.csv",
                                 {"COMER", "LIBELLE"}),
        "hist_drom": csv_lignes(source_dir / "v_commune_depuis_1943.csv",
                               {"TYPECOM", "COM", "LIBELLE", "DATE_DEBUT", "DATE_FIN"}),
        "hist_comer": csv_lignes(source_dir / "v_commune_outremer_depuis_1943.csv",
                                {"COM_COMER", "NATURE_ZONAGE", "LIBELLE",
                                 "DATE_DEBUT", "DATE_FIN"}),
    }


def instructions_editoriales(directory: Path, strict: bool = True) -> dict:
    mayotte = csv_lignes(directory / "LOT-MAYOTTE-17-COMMUNES-20261115.csv",
                         {"code_insee", "ark_candidat_Pactols", "decision_editoriale",
                          "libelle_COG_2026", "URI_INSEE_existante_dans_Pactols"})
    reunion = csv_lignes(directory / "LOT-REUNION-24-COMMUNES-20261115.csv",
                         {"code_INSEE_2026", "ark_Pactols_candidat",
                          "decision_editoriale", "libelle_COG_2026",
                          "uri_INSEE_declaree_dans_Pactols"})
    decisions = {}
    for origin, rows, idfield, arkfield, urifield in (
        ("LOT_MAYOTTE_20261115", mayotte, "code_insee", "ark_candidat_Pactols",
         "URI_INSEE_existante_dans_Pactols"),
        ("LOT_REUNION_20261115", reunion, "code_INSEE_2026",
         "ark_Pactols_candidat", "uri_INSEE_declaree_dans_Pactols"),
    ):
        for row in rows:
            code, statut, ark = row[idfield], row["decision_editoriale"], row[arkfield]
            if code in decisions or statut not in DECISIONS:
                raise ValueError("Décision dupliquée ou inconnue : " + code)
            if row[urifield] != "http://id.insee.fr/geo/commune/" + code:
                raise ValueError("URI INSEE contradictoire : " + code)
            if not ark.startswith("26678/") or not ark.split("/", 1)[1]:
                raise ValueError("Identifiant ARK non conforme : " + code)
            decisions[code] = {
                "statut": statut, "ark": ark,
                "libelle_source": row["libelle_COG_2026"], "source": origin,
            }
    if strict and (len(mayotte), len(reunion)) != (17, 24):
        raise ValueError("Lots éditoriaux 2026 incomplets")
    if strict:
        vals = collections.Counter(x["statut"] for x in decisions.values())
        if vals != {"VALIDE_2026": 16,
                    "ARK_CONFIRME_CORRESPONDANCE_A_VALIDER": 2,
                    "A_INSTRUIRE": 23}:
            raise ValueError("Statuts éditoriaux différents des décisions approuvées")
        if (decisions["97607"]["ark"] != "26678/crtZcuFSJVYZU" or
            decisions["97407"]["ark"] != "26678/pcrtIKvRT9vwUl"):
            raise ValueError("ARK confirmés par l'éditeur altérés")
    return decisions


def episodes_historique(data: dict, strict: bool = True) -> dict:
    """Réunir des OBSERVATIONS par code, pas des identités intemporelles."""
    hist = collections.defaultdict(list)
    for famille, source, code_key, type_key, type_value in (
        ("COG_DROM", data["hist_drom"], "COM", "TYPECOM", "COM"),
        ("COG_COMER", data["hist_comer"], "COM_COMER", "NATURE_ZONAGE", "COM"),
    ):
        for r in source:
            if r[type_key] != type_value:
                continue
            code = r[code_key]
            first, last = r["DATE_DEBUT"], r["DATE_FIN"]
            if first:
                date.fromisoformat(first)
            if last:
                date.fromisoformat(last)
            if not first or (last and first > last):
                raise ValueError("Période COG invalide : " + code)
            # Un même code peut relever de plusieurs séries : conserver la provenance.
            hist[code].append({
                "source_famille": famille, "code": code,
                "libelle_observe": r["LIBELLE"],
                "debut_inclus": first, "fin_exclue": last or None,
                "relation_identite_avec_2026": "NON_ETABLIE",
                "geometrie_historique": None,
            })
    for code, rows in hist.items():
        rows.sort(key=lambda r: (r["debut_inclus"], r["source_famille"],
                                 r["libelle_observe"], r["fin_exclue"] or ""))
    return hist


def entree_commune(cible: dict, parents: dict, diagnostics: dict, decisions: dict,
                   episodes: dict) -> dict:
    code = cible["code"]
    meta = diagnostics[cible["cle"]]
    if cible["nature"] != "COM":
        raise ValueError("Un zonage non COM ne peut devenir une commune")
    parent = parents[cible["famille"]][cible["parent"]]
    if meta["statut"] not in ("PRESENTE_VALIDE_A_QUALIFIER",
                               "PRESENTE_INVALIDE"):
        raise ValueError("Géométrie communale absente/dupliquée : " + code)
    decision = decisions.get(code)
    if decision and normaliser(decision["libelle_source"]) != normaliser(cible["libelle_cog"]):
        raise ValueError("Libellé d'une décision Pactols différent du COG : " + code)
    pac = {"relation_2026": decision["statut"] if decision else "A_INSTRUIRE",
           "ark_valide": None, "ark_identifiant_confirme": None,
           "source_decision": decision["source"] if decision else None}
    if decision and decision["statut"] == "VALIDE_2026":
        pac["ark_valide"] = decision["ark"]
    elif decision and decision["statut"] == "ARK_CONFIRME_CORRESPONDANCE_A_VALIDER":
        pac["ark_identifiant_confirme"] = decision["ark"]
    # Les 23 ARK non approuvés des autres communes réunionnaises restent
    # exclusivement dans la recette éditoriale, pas dans l'index de recherche.
    labels = [cible["libelle_cog"], code, parent["libelle"], parent["code"]]
    if pac["ark_valide"]:
        labels.append(pac["ark_valide"])
    historique = episodes.get(code, [])
    return {
        "id": cible["cle"], "famille_COG": cible["famille"],
        "nature_COG": "COM", "niveau_recherche": "commune",
        "code_insee": code,
        "uri_insee": "http://id.insee.fr/geo/commune/" + code,
        "libelle_COG_2026": cible["libelle_cog"],
        "parent_territorial_2026": parent,
        "date_reference_COG": DATE,
        "champs_recherche": sorted({normaliser(x) for x in labels if normaliser(x)}),
        "pactols": pac,
        "historique_COG_observations": historique,
        "historique_validite_retroactive": "NON_VALIDEE",
        "geom_2026": {
            "date_edition": GEOMETRIE_DATE,
            "statut_topologie": meta["statut"],
            "source": "data.gouv.fr/contours-administratifs/2026",
            "contour_adopte_pour_publication": False,
            "geometrie": None,
        },
    }


def construire(data: dict, diagnostic: list[dict], decisions: dict,
               strict: bool = True) -> tuple[dict, dict]:
    c = cibles(data["communes"], data["zonages"], data["territoires"], strict)
    parents = {
        "DROM": {r["DEP"]: {"code": r["DEP"], "libelle": r["LIBELLE"],
                             "type": "departement", "code_region": r["REG"]}
                 for r in data["departements"] if r["DEP"] in DROM},
        "COMER": {r["COMER"]: {"code": r["COMER"], "libelle": r["LIBELLE"],
                              "type": "collectivite_territoriale_COMER"}
                  for r in data["territoires"]},
    }
    if strict and set(parents["DROM"]) != set(DROM):
        raise ValueError("Départements DROM manquants dans le COG")
    if len(diagnostic) != len(c):
        raise ValueError("Les 233 résultats géométriques sont incomplets")
    ds = {r["cle"]: r for r in diagnostic}
    if len(ds) != len(diagnostic) or set(ds) != {r["cle"] for r in c}:
        raise ValueError("Identités typées différentes du diagnostic géométrique")
    for r in c:
        d = ds[r["cle"]]
        if (d["code"], d["nature"], d["famille"], d["libelle_cog"]) != (
            r["code"], r["nature"], r["famille"], r["libelle_cog"]
        ):
            raise ValueError("Diagnostic topologique attribué à une autre entité")
    hist = episodes_historique(data, strict)
    communes = []
    autres = []
    for item in c:
        appartient = (item["famille"] == "DROM" and item["nature"] == "COM"
                      or item["famille"] == "COMER" and item["nature"] == "COM"
                      and item["parent"] in PARENTS_COMER)
        if appartient:
            communes.append(entree_commune(item, parents, ds, decisions, hist))
        else:
            autres.append({
                "id": item["cle"], "famille_COG": item["famille"],
                "nature_COG": item["nature"], "code": item["code"],
                "libelle": item["libelle_cog"], "parent_2026": item["parent"],
                "statut_geom_2026": ds[item["cle"]]["statut"],
                "niveau_recherche": None,
                "interdiction_assimilation_commune": True,
                "alignement_Pactols": None,
            })
    communes.sort(key=lambda x: x["id"])
    autres.sort(key=lambda x: x["id"])
    counts = collections.Counter(
        (x["famille_COG"], x["parent_territorial_2026"]["code"]) for x in communes)
    invalides = sorted(x["code_insee"] for x in communes
                       if x["geom_2026"]["statut_topologie"] != "PRESENTE_VALIDE_A_QUALIFIER")
    approuve = sorted(x["code_insee"] for x in communes
                     if x["pactols"]["relation_2026"] == "VALIDE_2026")
    confirmes = sorted(x["code_insee"] for x in communes
                       if x["pactols"]["ark_identifiant_confirme"])
    if strict:
        attendus = {**{("DROM", k): v for k,v in DROM.items()},
                    **{("COMER", k): v for k,v in PARENTS_COMER.items()}}
        if counts != attendus or len(communes) != 212 or len(autres) != 21:
            raise ValueError("Périmètre 212/21 ou répartition territoriale incohérent")
        if invalides != ["98745", "98805"] or len(approuve) != 16 \
           or confirmes != ["97407", "97607"]:
            raise ValueError("Géométries ou décisions éditoriales inattendues")
    meta = {
        "schema": SCHEMA, "statut": "RECETTE_NON_PUBLIEE",
        "annee_COG": 2026, "date_reference_COG": DATE,
        "date_edition_contours": GEOMETRIE_DATE,
        "statistiques": {
            "communes": len(communes), "autres_entites_COG": len(autres),
            "communes_contours_topologiquement_valides": len(communes)-len(invalides),
            "communes_contours_invalides": invalides,
            "correspondances_Pactols_COG_validees_2026": len(approuve),
            "codes_Pactols_COG_valides_2026": approuve,
            "ark_identifiants_confirmes_lien_a_valider": confirmes,
            "repartition_par_territoire": {
                f"{k[0]}:{k[1]}": v for k,v in sorted(counts.items())
            },
            "observations_historiques_COG_liees_par_code": sum(
                len(x["historique_COG_observations"]) for x in communes),
        },
        "garanties": [
            "Pactols ARK seulement si VALIDE_2026 dans la décision éditoriale.",
            "ARK confirmé sans décision = candidat non indexé comme correspondance.",
            "Index 2026 non rétropolé vers les observations historiques COG.",
            "Les noms homonymes gardent une identité COG typée et un parent.",
            "Les 21 entités non communales ne sont pas affichées comme communes.",
            "Topologie valide ne signifie pas contour adopté.",
            "Aucune géométrie ni contour historique exporté.",
            "L'index ne remplace ni le pilote PACA ni le COG temporel national.",
        ],
        "nouvelles_correspondances_inferrees": 0,
        "geometries_publiees": 0,
    }
    return {"schema": SCHEMA, "entrees": communes}, {
        "schema": SCHEMA, "entrees": autres, "manifest": meta,
    }


def rechercher(entrees: list[dict], requete: str, limite: int = 10) -> list[dict]:
    q = normaliser(requete)
    if not q or not isinstance(limite, int) or limite <= 0:
        return []
    tokens = q.split()
    results = [e for e in entrees if all(
        any(t in v for v in e["champs_recherche"]) for t in tokens)]
    def key(item):
        n = normaliser(item["libelle_COG_2026"])
        return (0 if n == q or item["code_insee"] == q else
                1 if n.startswith(q) else 2, n, item["id"])
    return sorted(results, key=key)[:limite]


def produire(cog: Path, audit: Path, decisions: Path, sortie: Path,
            strict: bool = True) -> dict:
    cog, audit, decisions, sortie = (
        Path(cog).resolve(), Path(audit).resolve(),
        Path(decisions).resolve(), Path(sortie).resolve())
    if "docs" in sortie.parts or sortie == cog or sortie.is_relative_to(cog) \
       or sortie == decisions or sortie.is_relative_to(decisions) \
       or sortie == audit or sortie.is_relative_to(audit):
        raise ValueError("Aucune sortie d'index sous docs/ ni dans les sources")
    if sortie.exists() and any(sortie.iterdir()):
        raise ValueError("Refus d'écraser un export de recette existant")
    data = sources_cog(cog, strict)
    decisions_2026 = instructions_editoriales(decisions, strict)
    diagnostic = csv_lignes(audit / "controle_233_cibles.csv",
                             {"cle","code","nature","famille","parent",
                              "libelle_cog","statut"})
    communes, complement = construire(data, diagnostic, decisions_2026, strict)
    manifest = complement["manifest"]
    manifest["sources_SHA256"] = {
        **{name: digest(cog / name) for name in SHA},
        "controle_233_cibles.csv": digest(audit / "controle_233_cibles.csv"),
        **{name: digest(decisions / name) for name in (
           "LOT-MAYOTTE-17-COMMUNES-20261115.csv",
           "LOT-REUNION-24-COMMUNES-20261115.csv")},
    }
    # Le fichier de complément est descriptif ; il n'entre pas dans l'échelon Commune.
    files = {
        "index-communes-outremer-2026.json": {
            **communes, "statut": "RECETTE_NON_PUBLIEE"},
        "index-autres-entites-ultramarines-2026.json": {
            "schema": SCHEMA, "statut": "RECETTE_NON_PUBLIEE",
            "entrees": complement["entrees"]},
    }
    for filename, obj in files.items():
        payload = serialiser(obj)
        manifest.setdefault("sorties", {})[filename] = {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "entrees": len(obj["entrees"]),
        }
    sortie.mkdir(parents=True, exist_ok=True)
    for filename, obj in files.items():
        (sortie / filename).write_bytes(serialiser(obj))
    (sortie / "manifest-index-outremer-2026.json").write_bytes(serialiser(manifest))
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("cog", "audit", "decisions", "sortie"):
        p.add_argument("--" + arg, required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(produire(**vars(a)), ensure_ascii=False, indent=2,
                     sort_keys=True))
