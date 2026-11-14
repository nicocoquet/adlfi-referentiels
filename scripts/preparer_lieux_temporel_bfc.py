#!/usr/bin/env python3
"""Prépare le modèle JSON temporel BFC pour un curseur annuel UNIQUE.

Recette non publiée : un curseur sélectionne le 1er janvier de l'année.
Les périodes COM du COG, les statuts COMA/COMD *observés en 2026* et les
mouvements datés restent des objets distincts. AUCUNE géométrie ancienne et
AUCUNE relation Pactols-COG non validée n'est rendue publique.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from datetime import date
from pathlib import Path

COG_HASHES = {
    "historique": "08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
    "courant": "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
}
ANNEE_DEBUT = 1943
ANNEE_FIN = 2026
SCHEMA = "adlfi.lieux.temps.recette.v1"


def empreinte(path):
    sha = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1048576), b""):
            sha.update(block)
    return sha.hexdigest()


def lire_csv(path, champs):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=",")
        if not set(champs).issubset(set(reader.fieldnames or [])):
            raise ValueError("Colonnes COG absentes dans " + str(path))
        return list(reader)


def est_actif_etat(etat, reference):
    return etat["debut_inclus"] <= reference and (
        etat["fin_exclue"] is None or reference < etat["fin_exclue"])


def etats_au_premier_janvier(model, annee):
    if type(annee) is not int or not ANNEE_DEBUT <= annee <= ANNEE_FIN:
        raise ValueError("Année hors bornes ou invalide")
    reference = f"{annee:04d}-01-01"
    actifs = sorted(
        (e for e in model["periodes_COM"] if est_actif_etat(e, reference)),
        key=lambda e: (e["code_insee"], e["libelle"], e["debut_inclus"]))
    # Les entités COMA/COMD n'ont PAS de séries historiques continues dans
    # v_commune_depuis_1943.csv : on ne montre que l'observation millésimée.
    annexes = model["entites_complementaires_2026"] if annee == ANNEE_FIN else []
    events = sorted(
        (e["id"] for e in model["evenements_COG"]
         if e["date_effet"] <= reference))
    return {
        "annee": annee,
        "date_reference": reference,
        "nombre_COM_attestees": len(actifs),
        "COM": [{"code_insee": x["code_insee"], "libelle": x["libelle"],
                 "debut_inclus": x["debut_inclus"],
                 "fin_exclue": x["fin_exclue"]} for x in actifs],
        "complementaires_2026": annexes,
        "ids_evenements_deja_suivis": events,
        "contours_historiques": [],
    }


def construire(graphe, historique, courant, sortie):
    chemins = {"graphe": Path(graphe), "historique": Path(historique),
               "courant": Path(courant)}
    for name, expected in COG_HASHES.items():
        if empreinte(chemins[name]) != expected:
            raise ValueError("Empreinte officielle inattendue pour " + name)
    graph = json.loads(chemins["graphe"].read_text(encoding="utf8"))
    if graph.get("schema") != "adlfi.lieux.bfc.historique.transversal.recette.v1":
        raise ValueError("Graphe transversal de recette non reconnu")
    if (len(graph["relations_candidates"]), len(graph["evenements"]),
        len(graph["mouvements"])) != (29, 28, 86):
        raise ValueError("Données P1/P2/P3 incomplètes")
    if graph["nouvelles_validations"] or graph["geometries_historiques"]:
        raise ValueError("Un graphe de recette ne doit pas contenir de validation")
    if any(x["statut_validation"] != "a_instruire_non_valide" or
           x["decision_editoriale"] for x in graph["relations_candidates"]):
        raise ValueError("Candidature éditorialement validée dans la source")
    codes = {r["code_source"] for r in graph["relations_candidates"]}
    codes.update(r["code_cible"] for r in graph["relations_candidates"])
    for r in graph["mouvements"]:
        codes.update((r["COM_AV"], r["COM_AP"]))
    if len(codes) != 53 or any(len(c) != 5 or not c.isdigit() for c in codes):
        raise ValueError("Périmètre des 53 codes COG modifié")

    periods = []
    for r in lire_csv(historique, ("TYPECOM", "COM", "LIBELLE",
                                  "DATE_DEBUT", "DATE_FIN")):
        if r["COM"] not in codes or r["TYPECOM"] != "COM":
            continue
        debut, fin = r["DATE_DEBUT"], r["DATE_FIN"] or None
        date.fromisoformat(debut)
        if fin:
            date.fromisoformat(fin)
            if debut >= fin:
                raise ValueError("Période COM vide ou négative : " + r["COM"])
        periods.append({
            "code_insee": r["COM"], "typecom": "COM", "libelle": r["LIBELLE"],
            "debut_inclus": debut, "fin_exclue": fin,
            "source": "insee_COG2026_v_commune_depuis_1943"})
    periods.sort(key=lambda r: (r["code_insee"], r["debut_inclus"], r["libelle"]))
    if len(periods) != 69 or len({x["code_insee"] for x in periods}) != 53:
        raise ValueError("Séries historiques incomplètes pour le jeu BFC")
    per_code = collections.defaultdict(list)
    for p in periods:
        for earlier in per_code[p["code_insee"]]:
            if earlier["fin_exclue"] is None or earlier["fin_exclue"] > p["debut_inclus"]:
                raise ValueError("Périodes COM chevauchantes : " + p["code_insee"])
        per_code[p["code_insee"]].append(p)

    current = collections.defaultdict(list)
    for r in lire_csv(courant, ("TYPECOM", "COM", "LIBELLE", "COMPARENT", "DEP")):
        if r["COM"] in codes:
            current[r["COM"]].append(r)
    annexes = []
    for code in sorted(codes):
        for r in current[code]:
            if r["TYPECOM"] not in ("COMA", "COMD"):
                continue
            if not r["COMPARENT"]:
                raise ValueError("Entité complémentaire sans COMPARENT : " + code)
            annexes.append({"code_insee": code, "typecom": r["TYPECOM"],
                            "libelle": r["LIBELLE"], "comparent": r["COMPARENT"],
                            "date_observation": "2026-01-01",
                            "source": "insee_COG2026_v_commune_2026"})
    if len(annexes) != 3:
        raise ValueError("Nombre d'entités COMA/COMD actuelles inattendu")
    # L'état actuel COM doit être le dernier état à DATE_FIN vide.
    for code, recs in current.items():
        for r in recs:
            if r["TYPECOM"] == "COM":
                matches = [p for p in per_code[code] if
                           p["fin_exclue"] is None and p["libelle"] == r["LIBELLE"]]
                if len(matches) != 1:
                    raise ValueError("COG courant incompatible avec la période ouverte : " + code)

    # Les événements datés proviennent de mouvements officiels. Aucun ARK ni
    # lien éditorial n'est inséré dans cette couche temporelle affichable.
    events = [
        {"id": e["id"], "date_effet": e["date_effet"], "MOD": e["MOD"],
         "nature": e["nature"], "phase": e["phase"],
         "code_recepteur": e["code_recepteur"],
         "libelle_recepteur_au_mouvement": e["libelle_recepteur_au_mouvement"],
         "ids_mouvements": e["ids_mouvements"]}
        for e in graph["evenements"]]
    events.sort(key=lambda x: (x["date_effet"], x["MOD"], x["code_recepteur"]))
    model = {
        "schema": SCHEMA, "etat": "recette_non_publiee",
        "domaine": "etats_administratifs_COG_pour_jeu_test_BFC",
        "reference_temporelle": {
            "mode": "instant_au_1er_janvier",
            "annee_min": ANNEE_DEBUT, "annee_max": ANNEE_FIN,
            "annee_initiale": ANNEE_FIN,
            "debut_inclus": True, "fin_exclue": True},
        "codes_COG_jeu_test": sorted(codes),
        "periodes_COM": periods,
        "entites_complementaires_2026": annexes,
        "evenements_COG": events,
        "provenance": {name: empreinte(path) for name, path in chemins.items()},
        "regles_de_presentation": {
            "commune_nom_et_code": "état COM officiellement attesté à la date",
            "COMA_COMD": "observation 2026 uniquement, aucune période passée inférée",
            "recherche": "noms historiques recherchables indépendamment du curseur",
            "Pactols": "ARK et relations candidates maintenus dans le graphe de recette séparé",
            "geometries": "aucune géométrie historique attribuée",
        },
        "validations_editoriales": [], "geometries_historiques": []}

    targets = Path(sortie)
    names = ["lieux-temporel-bfc-recette.json", "rapport-temporel-bfc.json",
             "exemples-curseur-bfc.json"]
    if any((targets / name).resolve() in {p.resolve() for p in chemins.values()}
           for name in names):
        raise ValueError("Risque d'écrasement d'une source")
    exemples = {}
    for yr in (1943, 1974, 2016, 2017, 2018, 2019, 2020, 2025, 2026):
        snap = etats_au_premier_janvier(model, yr)
        selection = {x["code_insee"]: x["libelle"] for x in snap["COM"]}
        exemples[str(yr)] = {
            "date_reference": snap["date_reference"],
            "nombre_COM_attestees": snap["nombre_COM_attestees"],
            "cas_temoins": {c: selection.get(c) for c in
                ("25368", "25137", "39137", "39089", "71566", "71131", "25575")},
            "complementaires_2026": snap["complementaires_2026"],
            "nombre_evenements_deja_survenus": len(snap["ids_evenements_deja_suivis"])}
    report = {
        "statut": "recette_non_publiee",
        "codes_cog_couverts": len(codes),
        "periodes_COM": len(periods),
        "statuts_complementaires_observes_uniquement_en_2026": len(annexes),
        "evenements_COG": len(events),
        "borne_min": ANNEE_DEBUT, "borne_max": ANNEE_FIN,
        "instant_de_reference": "AAAA-01-01",
        "sources_sha256": model["provenance"],
        "nouvelles_validations": 0, "geometries_historiques": 0,
        "note": "Un état COM absent ne signifie pas qu'un lieu est inexistant : COMA/COMD ne disposent pas de série historique continue dans le fichier des couples code-libellé."
    }
    targets.mkdir(parents=True, exist_ok=True)
    (targets / names[0]).write_text(
        json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    (targets / names[1]).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    (targets / names[2]).write_text(
        json.dumps(exemples, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("graphe", "historique", "courant", "sortie"):
        parser.add_argument("--" + name, type=Path, required=True)
    a = parser.parse_args()
    print(json.dumps(construire(**vars(a)), ensure_ascii=False, indent=2))
