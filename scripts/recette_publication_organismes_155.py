#!/usr/bin/env python3
"""Contrats bloquants du JSON public Organismes 1.55 (lot A05c)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SOURCE = "AdlFI_referentiel_1-55_A05C_GAVS_PRETECH_INRAP_CANDIDAT.xlsx"
SOURCE_SHA = "2bd1df994401624fe84c0d696d1ecb1d13266d9b03cadb7ef76e3b65d3ae3c35"
COUNTS = {
    "ORG-0004": (173, 19, 326),   # CNRS
    "ORG-0008": (46, 17, 270),    # Inrap
    "ORG-0078": (46, 6, 120),     # CRAHAM
    "ORG-0348": (10, 1, 11),      # PréTech
    "ORG-0451": (6, 3, 7),        # GAVS
}

def validate(data: dict) -> list[str]:
    problems = []
    def check(condition, message):
        if not condition:
            problems.append(message)

    p = data.get("provenance", {})
    check(p.get("source_filename") == SOURCE, "Nom du maître 1.55")
    check(p.get("source_sha256") == SOURCE_SHA, "SHA-256 du maître 1.55")
    check(p.get("exported_at_utc") == "2026-11-22T00:00:00+00:00", "Datation du lot 1.55")
    auth = data.get("authorities", [])
    by = {x["id"]: x for x in auth}
    rels = data.get("relations", [])
    check(len(auth) == len(by) == 934, "934 autorités uniques")
    check(sum(x.get("kind") == "ORG" for x in auth) == 734, "734 ORG")
    check(sum(x.get("kind") == "SER" for x in auth) == 200, "200 SER")
    check(sum(bool(x.get("presentation", {}).get("visible")) for x in auth) == 682, "682 fiches visibles")
    check(sum(x.get("validation", {}).get("established") is True for x in auth) == 569, "569 autorités validées")
    check(len(rels) == 600, "600 relations inchangées")
    check(len({r["id"] for r in rels}) == 600, "Identifiants de relations uniques")

    for ident, count in COUNTS.items():
        usage = by.get(ident, {}).get("usage", {})
        actual = (usage.get("affiliations_linked"), usage.get("affiliations_validated"),
                  usage.get("source_occurrences_linked"))
        check(actual == count, f"{ident}: compteurs AFF attendus {count}")

    gavs = by.get("ORG-0451", {})
    check(gavs.get("validation") == {"status": "valide", "established": True},
          "GAVS: validation institutionnelle")
    check(gavs.get("classification", {}).get("type") == "association", "GAVS: association")
    check(gavs.get("classification", {}).get("bsr") == "ASS", "GAVS: catégorie ASS")
    check(gavs.get("classification", {}).get("sector") == "prive", "GAVS: secteur privé")
    check(gavs.get("activity", {}).get("active") is True, "GAVS: actif")
    check(gavs.get("activity", {}).get("start") == "1976", "GAVS: fondation (précision annuelle)")
    check(gavs.get("geography", {}).get("cities_label") == "Notre-Dame-de-Bliquetuit", "GAVS: ville de référence")
    check(gavs.get("quality", {}).get("activity_unknown") is False, "GAVS: activité connue")
    check(gavs.get("quality", {}).get("city_unrecorded") is False, "GAVS: ville renseignée")
    check(not any("ORG-0451" in (r.get("source"), r.get("target")) for r in rels),
          "GAVS: aucune relation institutionnelle inférée")

    pretech = by.get("ORG-0348", {})
    check(pretech.get("identifiers", {}).get("lab") == "UMR 7055", "PréTech: identifiant UMR 7055")
    check(pretech.get("activity", {}).get("end") == "2021-12-31", "PréTech: fin historique inchangée")
    temps = by.get("ORG-0539", {})
    check(temps.get("identifiers", {}).get("lab") == "UMR 8068", "TEMPS: identifiant UMR 8068")
    check(temps.get("activity", {}).get("start") == "2022-01-01", "TEMPS: début 2022")
    rel_by = {r["id"]: r for r in rels}
    check(all(rel_by.get(rid, {}).get("type") == "succession_partielle" and
              rel_by[rid].get("target") == "ORG-0539"
              for rid in ("REL-0144", "REL-0145")), "Filiations partielles conservées")
    totals = data.get("totals", {})
    check(totals.get("service_sector_resolution") == {"public": 197, "prive": 3},
          "Secteurs SER inchangés")
    check(totals.get("service_level_unresolved_ids") == ["SER-0178", "SER-0202"],
          "Échelons SER en suspens inchangés")
    check(totals.get("authorities") == 934 and totals.get("organismes") == 734
          and totals.get("services") == 200, "Totaux institutionnels inchangés")
    return problems

def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/data/organismes.json")
    errors = validate(json.loads(path.read_text(encoding="utf-8")))
    for error in errors:
        print("ÉCHEC :", error, file=sys.stderr)
    if errors:
        return 1
    print("OK — 1.55 : 934 autorités, 569 validées, 600 relations ; GAVS, PréTech, Inrap.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
