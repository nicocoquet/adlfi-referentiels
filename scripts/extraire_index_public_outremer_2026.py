#!/usr/bin/env python3
"""Réduire l'artefact de recette COG Outre-mer 2026 en index PUBLIC sans géométries.

Reproduction depuis l'artefact du workflow PR #30, et jamais depuis
l'interface publique. À utiliser en vérification / publication explicite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

EXPECTED = {
    "971": 32, "972": 34, "973": 22, "974": 24,
    "975": 2, "976": 17, "987": 48, "988": 33,
}


def construire(archive: Path) -> bytes:
    with ZipFile(archive) as z:
        def lire(nom):
            matched = [n for n in z.namelist() if Path(n).name == nom]
            if len(matched) != 1:
                raise ValueError("Fichier ambigu ou manquant : " + nom)
            return json.loads(z.read(matched[0]))

        communes = lire("index-communes-outremer-2026.json")["entrees"]
        autres = lire("index-autres-entites-ultramarines-2026.json")["entrees"]
        manifest = lire("manifest-index-outremer-2026.json")
    if (len(communes), len(autres)) != (212, 21):
        raise ValueError("Périmètre communal incomplet")
    if manifest["statistiques"]["correspondances_Pactols_COG_validees_2026"] != 16:
        raise ValueError("Décisions Pactols incompatibles")
    if manifest["statistiques"]["communes_contours_invalides"] != ["98745", "98805"]:
        raise ValueError("Diagnostic cartographique modifié")
    groupes = {}
    for e in communes:
        code, nom = e["code_insee"], e["libelle_COG_2026"]
        if not e["id"].endswith(":COM:" + code) or e["geom_2026"]["geometrie"] is not None:
            raise ValueError("Commune COG ambiguë ou géométrie importée")
        groupes.setdefault(code[:3], []).append(code + "|" + nom)
    if {k: len(v) for k, v in groupes.items()} != EXPECTED:
        raise ValueError("Répartition COG inattendue")
    d = {
        "schema": "adlfi.lieux.recherche.outremer.public.v1",
        "cog_ref": "2026-01-01",
        "edition_geom": "2026-05-04",
        "source_audit_sha256": manifest["sources_SHA256"]["controle_233_cibles.csv"],
        "communes": {k: "\n".join(v) for k, v in sorted(groupes.items())},
        "pactols_valides": {
            e["code_insee"]: e["pactols"]["ark_valide"]
            for e in communes if e["pactols"]["ark_valide"]
        },
        "ark_confirmes_non_valides": {
            e["code_insee"]: e["pactols"]["ark_identifiant_confirme"]
            for e in communes if e["pactols"]["ark_identifiant_confirme"]
        },
        "contours_invalides": manifest["statistiques"]["communes_contours_invalides"],
        "autres": [[e["id"], e["libelle"]] for e in autres],
    }
    if len(d["pactols_valides"]) != 16 or len(d["ark_confirmes_non_valides"]) != 2:
        raise ValueError("Candidats ou correspondances éditoriales anormaux")
    return (json.dumps(d, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artefact", type=Path, required=True)
    p.add_argument("--verifier", type=Path, help="Comparer au fichier public sans le modifier")
    p.add_argument("--sortie", type=Path, help="Fichier de recette à écrire hors docs/")
    args = p.parse_args()
    if bool(args.verifier) == bool(args.sortie):
        p.error("Spécifier exactement --verifier ou --sortie")
    payload = construire(args.artefact)
    if args.verifier:
        if payload != args.verifier.read_bytes():
            raise ValueError("La publication COG diverge de l'artefact de recette")
    else:
        if "docs" in args.sortie.resolve().parts:
            raise ValueError("Génération automatique sous docs/ interdite")
        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        args.sortie.write_bytes(payload)
    print("SHA-256", hashlib.sha256(payload).hexdigest(), "taille", len(payload))


if __name__ == "__main__":
    main()
