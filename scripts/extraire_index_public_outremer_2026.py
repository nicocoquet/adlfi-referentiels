#!/usr/bin/env python3
"""Réduire l'artefact de recette COG Outre-mer 2026 en index PUBLIC sans géométries.

Reproduction depuis l'artefact du workflow PR #30, et jamais depuis
l'interface publique. À utiliser en vérification / publication explicite.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import unicodedata
import json
from pathlib import Path
from zipfile import ZipFile

EXPECTED = {
    "971": 32, "972": 34, "973": 22, "974": 24,
    "975": 2, "976": 17, "987": 48, "988": 33,
}


def normaliser(v: object) -> str:
    txt=unicodedata.normalize("NFKD",str(v or "").casefold())
    return re.sub(r"[^a-z0-9]+"," ","".join(c for c in txt
             if not unicodedata.combining(c))).strip()


def appliquer_validations(data: dict, fichiers: list[Path]) -> dict:
    """Compléter la recette par des décisions 2026 explicitement documentées.

    Une référence INSEE sous closeMatch, relatedMatch ou autre relation
    n'est jamais promue automatiquement. Aucune frontière n'est ajoutée.
    """
    actuel={}
    for zone,lignes in data["communes"].items():
        for ligne in lignes.split("\n"):
            code,label=ligne.split("|",1)
            if code in actuel or not code.startswith(zone):
                raise ValueError("COG 2026 ambigu : "+code)
            actuel[code]=label
    original_valides=data["pactols_valides"]
    non_valides=data["ark_confirmes_non_valides"]
    all_arks=set(original_valides.values())|set(non_valides.values())
    if len(all_arks)!=len(original_valides)+len(non_valides):
        raise ValueError("ARK dupliqué dans le socle documentaire")
    requis={"code_insee","libelle_COG_2026","ark_pactols","uri_insee",
            "predicat_source","concept_deprecie","statut_validation",
            "portee_COG","prefLabel_fr_pactols"}
    for file in fichiers:
        with Path(file).open(encoding="utf-8-sig",newline="") as fd:
            reader=csv.DictReader(fd,delimiter=";")
            if set(reader.fieldnames or ()) != requis:
                raise ValueError("Colonnes de décisions éditoriales incompatibles : "+str(file))
            rows=list(reader)
        if not rows:
            raise ValueError("Fichier de validations vide : "+str(file))
        seen=set()
        for row in rows:
            if None in row or any(v is None or not v.strip() for v in row.values()):
                raise ValueError("Décision éditoriale CSV incomplète")
            code=row["code_insee"]
            ark=row["ark_pactols"]
            # Cas documenté : promotion du seul ARK déjà confirmé pour Le Port,
            # après preuve exactMatch et décision millésimée ; Dembeni reste exclue.
            promotion_port=(code=="97407" and code in non_valides and
                            ark==non_valides[code]=="26678/pcrtIKvRT9vwUl")
            if (code in seen or code not in actuel or code in original_valides
                or (code in non_valides and not promotion_port)):
                raise ValueError("Code non courant, dupliqué ou déjà arbitré : "+code)
            if (not re.fullmatch(r"[0-9]{5}",code)
                or not re.fullmatch(r"26678/[A-Za-z0-9]+",ark)
                or ark in all_arks
                or row["libelle_COG_2026"]!=actuel[code]
                or row["uri_insee"]!="http://id.insee.fr/geo/commune/"+code
                or row["predicat_source"]!="exactMatch"
                or row["concept_deprecie"]!="non"
                or row["statut_validation"]!="VALIDE_ADLFI_2026"
                or row["portee_COG"]!="2026-01-01"):
                raise ValueError("Preuve exactMatch COG 2026 insuffisante : "+code)
            source_label=normaliser(row["prefLabel_fr_pactols"])
            target_label=normaliser(actuel[code])
            if source_label!=target_label and not (
                row["prefLabel_fr_pactols"].startswith(actuel[code]+" (")
                and row["prefLabel_fr_pactols"].endswith(")")
            ):
                raise ValueError("Libellé divergent à instruire avant validation : "+code)
            seen.add(code)
            if promotion_port:
                # Le statut confirmé mais non validé disparaît uniquement
                # après l'ensemble des vérifications éditoriales.
                del non_valides[code]
            all_arks.add(ark)
            original_valides[code]=ark
    return data


def construire(archive: Path, validations: list[Path] | None = None) -> bytes:
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
        raise ValueError("Socle éditorial source anormal")
    appliquer_validations(d,validations or [])
    return (json.dumps(d, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artefact", type=Path, required=True)
    p.add_argument("--verifier", type=Path, help="Comparer au fichier public sans le modifier")
    p.add_argument("--sortie", type=Path, help="Fichier de recette à écrire hors docs/")
    p.add_argument("--validations", type=Path, action="append", default=[],
                   help="CSV d'alignements 2026 approuvés (option répétable)")
    args = p.parse_args()
    if bool(args.verifier) == bool(args.sortie):
        p.error("Spécifier exactement --verifier ou --sortie")
    payload = construire(args.artefact, args.validations)
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
