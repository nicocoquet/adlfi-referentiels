#!/usr/bin/env python3
"""Instruction non validante des 25 codes anciens et quatre dossiers ciblés BFC.

Sources : inventaire Pactols de recette et fichiers officiels du COG 2026.
Les événements bruts sont préservés ; les successeurs sont des candidats
administratifs immédiats, jamais des équivalences ARK éditorialement validées.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

SHA = {
    "codes25": "3c47cd64db71dba11f8f757900c1f8a261dc2f83b339127f164b1093da112031",
    "doubles": "d4966989dfe0db567ff0d45ff02e3302e81b3c687497e9714c08b1a692cabee7",
    "communes": "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
    "historique": "08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
    "mouvements": "8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
}
M_FIELDS = ("MOD", "DATE_EFF", "TYPECOM_AV", "COM_AV", "TNCC_AV", "NCC_AV",
            "NCCENR_AV", "LIBELLE_AV", "TYPECOM_AP", "COM_AP", "TNCC_AP",
            "NCC_AP", "NCCENR_AP", "LIBELLE_AP")
P_FIELDS = ("TYPECOM", "COM", "TNCC", "NCC", "NCCENR", "LIBELLE", "DATE_DEBUT", "DATE_FIN")
ATYPICAL = {"39012": ("Antorpe", "25527"), "52210": ("Frettes", "70122")}
CATEGORIES = {
    ("31",): "fusion_simple",
    ("32",): "creation_commune_nouvelle",
    ("32", "35"): "commune_nouvelle_puis_suppression_statut_delegue",
    ("33", "34"): "fusion_association_puis_fusion_simple",
    ("10", "32"): "changement_nom_puis_commune_nouvelle",
}
EXPECTED = {
    "fusion_simple": 4,
    "creation_commune_nouvelle": 12,
    "commune_nouvelle_puis_suppression_statut_delegue": 7,
    "fusion_association_puis_fusion_simple": 1,
    "changement_nom_puis_commune_nouvelle": 1,
}

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()

def lire(path, colonnes):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        first = f.readline()
        f.seek(0)
        rd = csv.DictReader(f, delimiter=";" if first.count(";") > first.count(",") else ",")
        missing = set(colonnes) - set(rd.fieldnames or [])
        if missing:
            raise ValueError(f"Colonnes absentes dans {path}: {sorted(missing)}")
        return list(rd)

def sauver_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def classe_mouvements(mouvements):
    mods = tuple(sorted({x["MOD"] for x in mouvements}))
    if mods not in CATEGORIES:
        raise ValueError(f"Combinaison de modalités non documentée : {mods}")
    return CATEGORIES[mods]

def conserver_evenements(rows, code, ark):
    output = []
    for r in sorted(rows, key=lambda v: (v["DATE_EFF"], v["MOD"], v["TYPECOM_AV"],
                                          v["COM_AV"], v["TYPECOM_AP"], v["COM_AP"])):
        payload = {k: r[k] for k in M_FIELDS}
        token = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
        output.append({"ark_pactols": ark, "code_suivi": code,
                       "identifiant_ligne_cog": "mvt:" + token, **payload})
    return output

def produire(codes25, doubles, communes, historique, mouvements, sortie):
    sources = dict(codes25=Path(codes25), doubles=Path(doubles),
                   communes=Path(communes), historique=Path(historique),
                   mouvements=Path(mouvements))
    for key, path in sources.items():
        if sha(path) != SHA[key]:
            raise ValueError(f"Empreinte SHA-256 inattendue pour {key}")
    historical = lire(codes25, ["ark_pactols", "libelle_pactols", "code_skos_historique",
                               "departement_hierarchie"])
    shared = lire(doubles, ["code_partage", "ark_pactols", "libelle"])
    if len(historical) != 25 or len(shared) != 4:
        raise ValueError("Cardinalités 25 / 4 non conformes")
    if len({r["code_skos_historique"] for r in historical}) != 25:
        raise ValueError("Codes historiques dupliqués")
    if {r["code_partage"] for r in shared} != {"25368", "25529"}:
        raise ValueError("Codes partagés inattendus")
    current = collections.defaultdict(list)
    for r in lire(communes, ["COM", "TYPECOM", "LIBELLE", "COMPARENT", "DEP", "REG"]):
        current[r["COM"]].append(r)
    periods = collections.defaultdict(list)
    for r in lire(historique, P_FIELDS):
        periods[r["COM"]].append(r)
    movements_index = collections.defaultdict(list)
    all_movements = lire(mouvements, M_FIELDS)
    for r in all_movements:
        for code in {r["COM_AV"], r["COM_AP"]} - {""}:
            movements_index[code].append(r)

    results = []
    events = []
    classes = collections.Counter()
    for r in sorted(historical, key=lambda v: v["code_skos_historique"]):
        code = r["code_skos_historique"]
        if not re.fullmatch(r"[0-9]{5}", code) or current[code]:
            raise ValueError(f"Code absent du COG 2026 attendu : {code}")
        lines = movements_index[code]
        if not lines:
            raise ValueError(f"Aucun mouvement Insee : {code}")
        category = classe_mouvements(lines)
        classes[category] += 1
        evs = conserver_evenements(lines, code, r["ark_pactols"])
        events.extend(evs)
        receivers = sorted({(x["COM_AP"], x["LIBELLE_AP"])
                            for x in lines if x["COM_AV"] == code
                            and x["TYPECOM_AP"] == "COM" and x["COM_AP"] != code})
        receiver_data = [{"code": c, "libelle_apres_mouvement": name,
                          "type_cog2026": "|".join(sorted({v["TYPECOM"] for v in current[c]})) or "absent",
                          "libelle_cog2026": "|".join(sorted({v["LIBELLE"] for v in current[c] if v["TYPECOM"] == "COM"}))}
                         for c, name in receivers]
        results.append({
            "ark_pactols": r["ark_pactols"], "libelle_pactols": r["libelle_pactols"],
            "departement_hierarchie": r["departement_hierarchie"],
            "code_historique_pactols": code, "type_cog2026": "absent",
            "profil_administratif": category,
            "modalites_insee": "|".join(sorted({x["MOD"] for x in lines})),
            "dates_mouvements": "|".join(sorted({x["DATE_EFF"] for x in lines})),
            "periodes_code_libelle": json.dumps(
                [{k: x[k] for k in P_FIELDS} for x in sorted(periods[code], key=lambda v: v["DATE_DEBUT"])],
                ensure_ascii=False),
            "nombre_lignes_mouvements": len(evs),
            "receptions_communales_immediates": json.dumps(receiver_data, ensure_ascii=False),
            "statut_candidature": "a_instruire_non_valide"
        })
    if classes != EXPECTED or len(events) != 42:
        raise ValueError(f"Profil 25 codes inattendu : {dict(classes)} ; {len(events)} lignes")

    pairs = []
    for code in ("25368", "25529"):
        group = sorted((r for r in shared if r["code_partage"] == code),
                       key=lambda x: x["ark_pactols"])
        if len(group) != 2:
            raise ValueError("Deux ARK requis par code partagé")
        current_com = [r for r in current[code] if r["TYPECOM"] == "COM"]
        if len(current_com) != 1:
            raise ValueError(f"Une COM actuelle attendue : {code}")
        datelines = [r for r in movements_index[code] if r["MOD"] == "32"]
        before = sorted({r["LIBELLE_AV"] for r in datelines if r["COM_AV"] == code})
        incoming = sorted({r["COM_AV"] + ":" + r["LIBELLE_AV"]
                           for r in datelines if r["COM_AV"] != code and r["COM_AP"] == code})
        if len(before) != 1 or not incoming:
            raise ValueError(f"Transition non conforme : {code}")
        pairs.append({"code_partage": code, "ark_et_libelles_pactols": json.dumps(
            [{"ark": x["ark_pactols"], "libelle": x["libelle"]} for x in group],
            ensure_ascii=False), "libelle_com_historique": before[0],
            "libelle_com_2026": current_com[0]["LIBELLE"],
            "codes_entrants": "|".join(incoming),
            "date_commune_nouvelle": "|".join(sorted({r["DATE_EFF"] for r in datelines})),
            "nombre_lignes_de_mouvement": len(datelines),
            "decision": "conserver_deux_ark_non_fusionnes"})

    cross = []
    for code, (label, parent) in sorted(ATYPICAL.items()):
        associated = [r for r in current[code] if r["TYPECOM"] == "COMA"]
        parents = [r for r in current[parent] if r["TYPECOM"] == "COM"]
        if len(associated) != 1 or associated[0]["COMPARENT"] != parent or len(parents) != 1:
            raise ValueError("État interdépartemental inattendu : " + code)
        evs = movements_index[code]
        to_associated = [v for v in evs if v["MOD"] == "33" and v["COM_AV"] == code
                         and v["TYPECOM_AV"] == "COM" and v["COM_AP"] == code
                         and v["TYPECOM_AP"] == "COMA"]
        to_parent = [v for v in evs if v["MOD"] == "33" and v["COM_AV"] == code
                     and v["TYPECOM_AP"] == "COM" and v["COM_AP"] == parent]
        if len(to_associated) != 1 or len(to_parent) != 1 or to_associated[0]["DATE_EFF"] != to_parent[0]["DATE_EFF"]:
            raise ValueError("Épisode fusion-association absent : " + code)
        cross.append({"libelle_pactols": label, "code_historique": code,
            "type_initial": "COM", "type_cog2026": "COMA", "comparent_cog2026": parent,
            "commune_parente_cog2026": parents[0]["LIBELLE"],
            "date_fusion_association": to_associated[0]["DATE_EFF"],
            "departement_parent_2026": parents[0]["DEP"],
            "statut": "code_historique_conserve_non_valide"})

    out = Path(sortie)
    names = ("instruction-25-codes-historiques.csv", "preuves-mouvements-25.csv",
             "deux-codes-partages-ark.csv", "antorpe-frettes.csv",
             "rapport-instruction-bfc.json")
    if any((out / n).resolve() in {p.resolve() for p in sources.values()} for n in names):
        raise ValueError("Une sortie écraserait une source")
    out.mkdir(parents=True, exist_ok=True)
    sauver_csv(out / names[0], results, list(results[0]))
    sauver_csv(out / names[1], events, list(events[0]))
    sauver_csv(out / names[2], pairs, list(pairs[0]))
    sauver_csv(out / names[3], cross, list(cross[0]))
    report = {"etat": "recette_non_validante", "nombre_codes_historiques": len(results),
        "repartition_profils": dict(sorted(classes.items())),
        "lignes_evenements_officiels": len(events),
        "codes_partages_ark_documentes": len(pairs),
        "communes_associees_interdepartementales": len(cross),
        "sources_sha256": {key: sha(path) for key, path in sources.items()},
        "nouveaux_alignements_valides": 0, "geometries_historiques_attribuees": 0,
        "limites": [
            "Une destination COM après événement est un destinataire administratif immédiat, pas une équivalence Pactols.",
            "Un événement daté peut avoir plusieurs lignes avant/après ; les 42 lignes ne sont pas 42 actes indépendants.",
            "Le profil de mouvement ne suffit pas à reconstruire tous les épisodes successifs ni les contours historiques."
        ]}
    (out / names[4]).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for field in ("codes25", "doubles", "communes", "historique", "mouvements", "sortie"):
        p.add_argument("--" + field.replace("_", "-"), required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(produire(**vars(args)), ensure_ascii=False, indent=2))
