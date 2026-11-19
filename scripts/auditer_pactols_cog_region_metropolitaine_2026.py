#!/usr/bin/env python3
"""Audit non publiant Pactols–COG des communes d'une région métropolitaine 2026.

En option, croiser les ARK terminaux réellement présents dans les notices AdlFI
avec les candidats COG 2026. Les exports des notices ne sont JAMAIS copiés vers
le dépôt ni réémis dans les résultats : seulement des agrégats et empreintes.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

from auditer_pactols_polynesie_2026 import analyser_rdf, RDF_SHA, RDF_COMMIT
from auditer_pactols_cog_regions_prioritaires_2026 import qualifier
from preparer_index_cog_national_temporel import SOURCES as COG_SHA

REGIONS = {
    "11": "Île-de-France", "24": "Centre-Val de Loire", "27": "Bourgogne-Franche-Comté",
    "28": "Normandie", "32": "Hauts-de-France", "44": "Grand Est", "52": "Pays de la Loire",
    "53": "Bretagne", "75": "Nouvelle-Aquitaine", "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes", "93": "Provence-Alpes-Côte d’Azur", "94": "Corse",
}
SCHEMA = "adlfi.lieux.audit-pactols-cog-region-2026.v1"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def reader(path: Path, required: tuple[str, ...]):
    with path.open(encoding="utf-8-sig", newline="") as file:
        records = csv.DictReader(file, delimiter=";", strict=True)
        missing = set(required) - set(records.fieldnames or [])
        if missing:
            raise ValueError("Colonnes manquantes : " + ", ".join(sorted(missing)))
        yield from records


def communes_region(cog: Path, code_region: str) -> dict:
    if code_region not in REGIONS:
        raise ValueError("Code région COG 2026 inconnu : " + code_region)
    if sha(cog) != COG_SHA["courant"]:
        raise ValueError("Empreinte du COG 2026 non conforme")
    communes = {}
    with cog.open(encoding="utf-8-sig", newline="") as file:
        rows = csv.DictReader(file)
        if not {"TYPECOM", "COM", "LIBELLE", "REG", "DEP"}.issubset(rows.fieldnames or []):
            raise ValueError("Schéma COG absent")
        for r in rows:
            if r["TYPECOM"] != "COM" or r["REG"] != code_region:
                continue
            code = r["COM"]
            if not code or len(code) != 5 or code in communes or not r["DEP"] or not r["LIBELLE"]:
                raise ValueError("Commune COG dupliquée ou mal formée : " + code)
            communes[code] = {"code": code, "nom": r["LIBELLE"], "departement": r["DEP"]}
    if not communes:
        raise ValueError("Aucune commune dans la région")
    return communes


def audit(rdf: Path, cog: Path, code_region: str) -> dict:
    if sha(rdf) != RDF_SHA:
        raise ValueError("Empreinte RDF Pactols non conforme")
    current = communes_region(cog, code_region)
    scan = analyser_rdf(rdf, {code: r["nom"] for code, r in current.items()})
    rows = []
    for code, r in sorted(current.items()):
        hits = scan["explicites"][code]
        status = qualifier(code, r["nom"], hits)
        rows.append({
            **r, "statut_candidat": status,
            "preuves_RDF_exactMatch": hits,
            "candidats_lexicaux_non_validants":
                scan["lexicaux_sans_exactMatch_987"].get(code, []),
            "decision_editoriale": "NON_PRISE",
            "publication": "NON_PUBLIE",
        })
    counts = collections.Counter(r["statut_candidat"] for r in rows)
    return {
        "schema": SCHEMA,
        "statut": "AUDIT_NON_VALIDANT",
        "code_region_COG_2026": code_region,
        "region": REGIONS[code_region],
        "cog": {"millesime": "2026-01-01", "fichier": "v_commune_2026.csv",
                "sha256": COG_SHA["courant"]},
        "pactols": {"commit": RDF_COMMIT, "sha256": RDF_SHA,
                    "fichier": "Pactols_Lieux_th17_20260722.rdf"},
        "bilan": {
            "communes_COG_2026": len(rows),
            "codes_avec_exactMatch_Pactols": sum(bool(r["preuves_RDF_exactMatch"]) for r in rows),
            "concepts_RDF_examines": scan["concepts_RDF_examines"],
            "statuts": dict(sorted(counts.items())),
            "nouveaux_alignements_valides": 0,
            "nouvelles_geometries": 0,
            "retroprojections_historiques": 0,
        },
        "communes": rows,
        "limitations": [
            "La région du COG est sélectionnée par REG et TYPECOM=COM, pas par préfixe de code.",
            "Un exactMatch de Pactols est une preuve candidate pour 2026, jamais une validation historique.",
            "Les codes des communes nouvelles hérités d'anciennes communes nécessitent l'examen des ARK concurrents.",
            "Les limites cartographiques ne sont ni créées ni validées par cet audit.",
            "Les sources Pactols et COG doivent correspondre à leurs empreintes SHA-256 archivées.",
        ],
    }


def croiser_corpus(report: dict, autorites: Path, occurrences: Path) -> dict:
    """Répartition agrégée des occurrences AdlFI par statut de preuve RDF 2026."""
    auth = {}
    for r in reader(autorites, ("ark_pactols", "nombre_occurrences", "nombre_notices_distinctes")):
        ark = r["ark_pactols"]
        if not ark or ark in auth:
            raise ValueError("ARK dupliqué dans l'export d'autorités")
        auth[ark] = (int(r["nombre_occurrences"]), int(r["nombre_notices_distinctes"]))
    corpus_total = collections.Counter()
    notices_by_ark = collections.defaultdict(set)
    normandie = collections.Counter()
    region_notices = set()
    region_name = report["region"]
    region_arks = set()
    for r in reader(occurrences, ("ark_terminal", "notice_id", "chaine_libelles_fr")):
        ark, notice = r["ark_terminal"], r["notice_id"]
        if not ark or not notice:
            raise ValueError("Occurrence sans ARK ni notice")
        corpus_total[ark] += 1
        notices_by_ark[ark].add(notice)
        chain = json.loads(r["chaine_libelles_fr"])
        if not isinstance(chain, list) or not all(isinstance(x, str) for x in chain):
            raise ValueError("Hiérarchie Pactols invalide")
        if "France métropolitaine" not in chain:
            continue
        i = chain.index("France métropolitaine") + 1
        if i >= len(chain) or chain[i] != region_name:
            continue
        normandie[ark] += 1
        region_notices.add(notice)
        region_arks.add(ark)
    if auth.keys() != corpus_total.keys():
        raise ValueError("Les exports autorités et occurrences n'ont pas les mêmes ARK")
    if any(corpus_total[a] != n[0] or len(notices_by_ark[a]) != n[1]
           for a, n in auth.items()):
        raise ValueError("Comptage incohérent dans les exports AdlFI")

    by_ark = collections.defaultdict(list)
    for r in report["communes"]:
        for p in r["preuves_RDF_exactMatch"]:
            by_ark[p["ark"]].append((r["code"], r["statut_candidat"]))

    statuses = collections.Counter()
    occurrences_by_status = collections.Counter()
    for ark in region_arks:
        codes = by_ark.get(ark, [])
        if len(codes) == 1 and codes[0][1] == "ELIGIBLE_SELON_REGLE":
            category = "EXACTMATCH_UNIVOQUE_ELIGIBLE_SELON_REGLE"
        elif codes:
            category = "EXACTMATCH_COG_2026_A_INSTRUIRE"
        else:
            category = "AUCUN_EXACTMATCH_VERS_COMMUNE_REGION_2026"
        statuses[category] += 1
        occurrences_by_status[category] += normandie[ark]
    return {
        "schema": "adlfi.lieux.croisement-adlfi-pactols-cog-2026.aggregate.v1",
        "region": region_name, "code_region_COG_2026": report["code_region_COG_2026"],
        "statut": "CROISEMENT_DOCUMENTAIRE_NON_VALIDANT",
        "sources_privees_SHA256": {
            "autorites_lieux.csv": sha(autorites),
            "occurrences_lieux.csv": sha(occurrences),
        },
        "autorites_terminales_dans_region": len(region_arks),
        "occurrences_dans_region": sum(normandie.values()),
        "notices_distinctes_dans_region": len(region_notices),
        "autorites_par_statut": dict(sorted(statuses.items())),
        "occurrences_par_statut": dict(sorted(occurrences_by_status.items())),
        "limitations": [
            "Le classement exprime l'existence d'un lien RDF et son admissibilité stricte pour 2026, pas une décision éditoriale.",
            "Les ARK sans lien à une commune actuelle peuvent désigner d'anciennes communes, subdivisions ou autres lieux ; ne pas les qualifier automatiquement d'erreurs.",
            "Un code réutilisé ou un ARK concurrent n'est jamais assimilé par continuité supposée.",
            "Aucun identifiant de notice, ARK individuel, chemin de fichier ni ligne de l'export n'est publié dans cet agrégat.",
        ],
    }


def write_result(path: Path, data: dict) -> None:
    output = path.resolve()
    if "docs" in output.parts:
        raise ValueError("Écriture de recette hors docs/ uniquement")
    if output.exists():
        raise ValueError("Sortie existante : ne pas écraser une recette")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", required=True, choices=sorted(REGIONS))
    parser.add_argument("--rdf", required=True, type=Path)
    parser.add_argument("--cog", required=True, type=Path)
    parser.add_argument("--sortie", required=True, type=Path)
    parser.add_argument("--autorites", type=Path)
    parser.add_argument("--occurrences", type=Path)
    parser.add_argument("--sortie-corpus", type=Path)
    args = parser.parse_args()
    opts = (args.autorites, args.occurrences, args.sortie_corpus)
    if any(opts) and not all(opts):
        parser.error("--autorites, --occurrences et --sortie-corpus vont ensemble")
    result = audit(args.rdf, args.cog, args.region)
    corpus = croiser_corpus(result, args.autorites, args.occurrences) if all(opts) else None
    write_result(args.sortie, result)
    if corpus is not None:
        write_result(args.sortie_corpus, corpus)
    print("LIEUX_REGION_COG", json.dumps(result["bilan"], ensure_ascii=False, sort_keys=True))
    if corpus is not None:
        print("LIEUX_REGION_CORPUS", json.dumps({
            k: corpus[k] for k in (
                "region", "autorites_terminales_dans_region", "occurrences_dans_region",
                "notices_distinctes_dans_region", "autorites_par_statut",
                "occurrences_par_statut")
        }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
