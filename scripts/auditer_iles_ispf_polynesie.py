#!/usr/bin/env python3
"""Audit descriptif des îles ISPF et de leurs relations aux unités fines.

Exploite exclusivement le rapport source non validant produit par
qualifier_communes_associees_ispf.py (SHA-256 et cardinalités vérifiés).
Aucune inférence d'identifiant, d'ARK, de contour ni de validité historique.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
import hashlib
from pathlib import Path
from inspecter_nomenclature_geographique_ispf import read_xlsx
from qualifier_communes_associees_ispf import SHA as SOURCE_SHA, rows as lire_lignes

SCHEMA_IN = "adlfi.lieux.polynesie.ispf.associees.audit.v1"
SCHEMA_OUT = "adlfi.lieux.polynesie.ispf.iles.audit.v1"

def analyser(audit: dict, source_xlsx: Path | None = None) -> dict:
    if audit.get("schema") != SCHEMA_IN or audit.get("statut") != "RECETTE_ISPF_NON_VALIDANTE":
        raise ValueError("Rapport ISPF source non qualifié")
    bilan = audit["bilan"]
    if any(bilan[k] != v for k, v in {
        "communes_COG": 48, "communes_associees_ISPF": 98,
        "communes_ISPF_sans_associees": 18, "iles_ISPF_dans_classeur": 119,
        "codes_geographiques_ISPF": 179}.items()):
        raise ValueError("Contrat de cardinalité ISPF modifié")
    units = {r["id_comas_ISPF"]: r for r in
        audit["communes_associees"] + audit["unites_conventionnelles_non_associees"]}
    if len(units) != 116:
        raise ValueError("Unités ISPF non uniques")
    geo = audit["codes_geographiques"]
    if len(geo) != 179:
        raise ValueError("Nombre de lignes Geo différent de la recette")
    by_island: dict[str, list] = defaultdict(list)
    flags = Counter()
    for r in geo:
        code, unit, island = r["IDGeo"], r["IDComas"].zfill(3), r["IDIle"]
        if unit not in units or len(code) != 5 or not code.isdecimal():
            raise ValueError("Relation Geo sans unité de rattachement fiable")
        if r["IDCom"].zfill(2) != units[unit]["id_commune_ISPF"]:
            raise ValueError("Relation Geo hors parent ISPF")
        for flag in ("isCom", "isComas", "isIleRattachee"):
            if r[flag] not in ("0", "1"):
                raise ValueError("Indicateur Geo invalide : " + flag)
            flags[flag + "=" + r[flag]] += 1
        by_island[island].append(r)
    referentiel_iles = None
    if source_xlsx is not None:
        sha = hashlib.sha256(source_xlsx.read_bytes()).hexdigest()
        if sha != SOURCE_SHA or sha != audit["source"]["sha256"]:
            raise ValueError("Empreinte de la source ISPF incohérente")
        sheets = {x["feuille"]: x for x in read_xlsx(source_xlsx)}
        if set(sheets) != {"Geo", "Subdivision", "Commune", "Commune associée", "Ile"}:
            raise ValueError("Feuilles ISPF absentes ou nouvelles")
        ile_rows = lire_lignes(sheets["Ile"])
        if len(ile_rows) != 119:
            raise ValueError("Registre Ile différent des 119 lignes contrôlées")
        referentiel_iles = {}
        for r in ile_rows:
            code = r["IDIle"]
            if code in referentiel_iles:
                raise ValueError("IDIle dupliqué dans la feuille Ile : " + code)
            referentiel_iles[code] = r
        for r in geo:
            entry = referentiel_iles.get(r["IDIle"])
            if entry is None:
                raise ValueError("IDIle de Geo absent de la nomenclature Ile : " + r["IDIle"])
            if (entry["Ile"] != r["Ile"] or entry["IDSub"] != r["IDSub"] or
                entry["Subdivision"] != r["Subdivision"]):
                raise ValueError("Désaccord Ile/Geo sur code, nom ou subdivision : " + r["IDIle"])
    islands = []
    for island, rows in sorted(by_island.items()):
        names = sorted({r["Ile"] for r in rows})
        if len(names) != 1:
            raise ValueError("Libellés contradictoires pour IDIle " + island)
        units_here = sorted({r["IDComas"].zfill(3) for r in rows})
        communes = sorted({units[x]["code_commune_COG"] for x in units_here})
        subdivisions = sorted({r["IDSub"] for r in rows})
        islands.append({
            "id_ile_ISPF": island,
            "libelle_ISPF": names[0],
            "nombre_lignes_geo": len(rows),
            "unites_fines_ISPF": units_here,
            "communes_COG_rattachement": communes,
            "subdivisions_ISPF": subdivisions,
            "codgeo_explicites": sorted(r["IDGeo"] for r in rows),
            "rattachement_plusieurs_unites": len(units_here) > 1,
            "rattachement_plusieurs_communes": len(communes) > 1,
            "rattachement_plusieurs_subdivisions": len(subdivisions) > 1,
        })
    exceptions = [{
        "CODGEO": r["IDGeo"], "IDComas": r["IDComas"],
        "IDIle": r["IDIle"], "libelle": r["Geo"],
        "motif": "PREFIXE_CODGEO_DIFFERENT_IDCOMAS",
    } for r in geo if r["IDGeo"][:3] != r["IDComas"].zfill(3)]
    if {(e["CODGEO"], e["IDComas"]) for e in exceptions} != {
        ("43001", "431"), ("44001", "441")}:
        raise ValueError("Exceptions de préfixe CODGEO non prévues")
    present = {i["id_ile_ISPF"] for i in islands}
    missing = (sorted(set(referentiel_iles) - present)
               if referentiel_iles is not None else None)
    unused = ([referentiel_iles[code] for code in missing]
              if missing is not None else None)
    # Une absence de Geo ne signifie jamais absence d'île.
    return {
        "schema": SCHEMA_OUT, "statut": "RECETTE_GEOGRAPHIQUE_NON_VALIDANTE",
        "source": audit["source"],
        "comptages": {
            "iles_nomenclature_feuille_Ile": 119,
            "codes_iles_distincts_observes_dans_Geo": len(present),
            "codes_iles_absents_de_Geo": len(missing) if missing is not None else None,
            "comparaison_exhaustive_feuille_Ile_Geo": referentiel_iles is not None,
            "lignes_Geo": len(geo),
            "iles_plusieurs_unites": sum(i["rattachement_plusieurs_unites"] for i in islands),
            "iles_plusieurs_communes": sum(i["rattachement_plusieurs_communes"] for i in islands),
            "iles_plusieurs_subdivisions": sum(i["rattachement_plusieurs_subdivisions"] for i in islands),
            "exceptions_prefixes_CODGEO": len(exceptions),
            "indicateurs_Geo": dict(sorted(flags.items())),
            "nouvelles_geometries": 0, "nouveaux_ARK": 0,
            "nouvelles_autorites_publiees": 0,
        },
        "iles_observees_dans_Geo": islands,
        "iles_nomenclature_absentes_de_Geo": unused,
        "exceptions_CODGEO": exceptions,
        "alertes_documentaires": [
            "119 codes d'îles dans la feuille Ile ; 121 îles annoncées sur la page ISPF : périmètres à vérifier",
            "Les codes présents dans Ile mais absents de Geo sont conservés sans inférence administrative",
            "Gambier : unité 190 présente administrativement, sans ligne Geo 19000 ; vérifier séparément les lignes 19001–19016",
            "Aucune géométrie ne peut être déduite d'un CODGEO ou d'un rattachement administratif",
        ],
    }

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rapport-ispf", required=True, type=Path)
    p.add_argument("--source-xlsx", type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    args = p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Ne pas écraser ni publier un rapport d'audit dans docs/")
    audit = json.loads(args.rapport_ispf.read_text(encoding="utf-8"))
    result = analyser(audit, args.source_xlsx)
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("ISPF_ILES_BILAN", json.dumps(result["comptages"], sort_keys=True, ensure_ascii=False))
    print("ISPF_ILES_MULTIUNITES", json.dumps([
        {"code": x["id_ile_ISPF"], "nom": x["libelle_ISPF"],
         "communes": x["communes_COG_rattachement"],
         "unites": x["unites_fines_ISPF"]}
        for x in result["iles_observees_dans_Geo"]
        if x["rattachement_plusieurs_unites"]
    ], ensure_ascii=False, sort_keys=True))
    print("ISPF_ILES_MULTICOMMUNES", json.dumps([
        {"code": x["id_ile_ISPF"], "nom": x["libelle_ISPF"],
         "communes": x["communes_COG_rattachement"],
         "unites": x["unites_fines_ISPF"]}
        for x in result["iles_observees_dans_Geo"]
        if x["rattachement_plusieurs_communes"]
    ], ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
