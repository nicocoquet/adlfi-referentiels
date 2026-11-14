#!/usr/bin/env python3
"""Qualifier des candidatures de relations ARK/COG de Bourgogne-Franche-Comté.

Entrées : sorties de recette de l'audit des 25 codes historiques, des deux
codes partagés et d'Antorpe/Frettes ; inventaire XML–Pactols de 736 ARK.
Aucun lien ne vaut alignement validé et aucun contour n'est inféré.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

EXPECTED_SHA = {
    "inventaire": "efba75a28e0de837ef8832deff2ce5a5eb20e75132f3406e06cdc7ab6904fcad",
    "anciens": "e1954d9ee2eb76d04b3ed3dc90de3eaa67de35bddfcd5824b22099b46d1164a3",
    "preuves": "6d37c8483bfaf07fb2ba959a0455e483d4dc94114eae393a2fe396341326fd82",
    "partages": "dcae8e515e6cb923169a7cbe6a3d8fa3320a72ee8f7a769e001c9204cb428cdd",
    "associes": "c985f090295fa121236b79eddd7e13686ede64268ff05c43f1d5c13642ddc309",
}
OUTPUT_COLS = (
    "id_candidature", "famille_relation", "ark_source", "libelle_source",
    "code_source", "typecom_source", "code_cible_insee",
    "libelle_cible_mouvement", "date_evenement", "modalite_cog",
    "preuve_cog", "arks_sur_code_cible", "ark_cible_propose",
    "libelle_cible_pactols", "indice_lexical", "statut_instruction",
    "validation_adlfi"
)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for buf in iter(lambda: f.read(1 << 20), b""):
            h.update(buf)
    return h.hexdigest()


def lire(path, champs):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        header = f.readline()
        f.seek(0)
        rd = csv.DictReader(f, delimiter=";" if header.count(";") > header.count(",") else ",")
        if not set(champs) <= set(rd.fieldnames or []):
            raise ValueError("Colonnes manquantes " + str(path))
        return list(rd)


def normaliser(libelle):
    """Comparaison *lexicale* tolérant espaces, accents et tirets, sans sémantique."""
    d = unicodedata.normalize("NFD", libelle.casefold())
    d = "".join(c for c in d if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", d)


def candidates_pactols(code, libelle_insee, par_code):
    """Retourne une ARK seulement si le libellé est unique et concordant."""
    options = sorted(par_code.get(code, ()), key=lambda r: r["ark_pactols"])
    matches = [r for r in options if normaliser(r["pref_fr_pactols"]) == normaliser(libelle_insee)]
    if len(matches) == 1:
        return "accord_lexical_univoque_non_valide", matches[0], options
    if options:
        return "code_sans_concordance_lexicale", None, options
    return "cible_absente_corpus_terminal", None, options


def generer(inventaire, anciens, preuves, partages, associes, sortie):
    sources = dict(inventaire=Path(inventaire), anciens=Path(anciens),
                   preuves=Path(preuves), partages=Path(partages),
                   associes=Path(associes))
    for key, path in sources.items():
        if sha(path) != EXPECTED_SHA[key]:
            raise ValueError("Source de recette non conforme : " + key)

    inv = lire(inventaire, ["ark_pactols", "codes_insee_skos", "pref_fr_pactols"])
    old = lire(anciens, ["ark_pactols", "libelle_pactols", "code_historique_pactols"])
    moves = lire(preuves, ["ark_pactols", "code_suivi", "identifiant_ligne_cog",
                          "MOD", "DATE_EFF", "TYPECOM_AV", "COM_AV", "TYPECOM_AP",
                          "COM_AP", "LIBELLE_AP"])
    doubles = lire(partages, ["code_partage", "ark_et_libelles_pactols",
                              "libelle_com_historique", "libelle_com_2026",
                              "date_commune_nouvelle"])
    associations = lire(associes, ["libelle_pactols", "code_historique",
                                   "comparent_cog2026", "commune_parente_cog2026",
                                   "date_fusion_association", "type_cog2026"])
    if tuple(map(len, (inv, old, moves, doubles, associations))) != (736, 25, 42, 2, 2):
        raise ValueError("Cardinalités d'entrée inattendues")

    par_code = collections.defaultdict(list)
    ark_index = {}
    for r in inv:
        codes = json.loads(r["codes_insee_skos"])
        if not isinstance(codes, list) or len(codes) > 1:
            raise ValueError("Assertions de code Pactols non conformes")
        if r["ark_pactols"] in ark_index:
            raise ValueError("ARK de l'inventaire dupliqué")
        ark_index[r["ark_pactols"]] = r
        for code in codes:
            par_code[code].append(r)

    preuves_ark = collections.defaultdict(list)
    for m in moves:
        preuves_ark[m["ark_pactols"]].append(m)
    rows = []
    classifications = collections.Counter()

    def ajouter(*, famille, ark_source, libelle_source, code_source, typecom_source,
                code_cible, libelle_cible, date, modalite, preuves_ids,
                strategie="rechercher", ark_cible=None):
        if ark_source not in ark_index:
            raise ValueError("ARK source hors corpus : " + ark_source)
        statut, cible, options = candidates_pactols(code_cible, libelle_cible, par_code)
        if strategie == "exiger_ark":
            if ark_cible is None or cible is None or cible["ark_pactols"] != ark_cible:
                raise ValueError("Rattachement entre deux concepts non corroboré lexicalement")
        elif strategie != "rechercher":
            raise ValueError("Stratégie inconnue")
        classifications[(famille, statut)] += 1
        token = hashlib.sha256(
            (famille + "|" + ark_source + "|" + code_cible + "|" + date +
             "|" + modalite + "|" + ",".join(sorted(preuves_ids))).encode("utf8")
        ).hexdigest()[:20]
        rows.append({
            "id_candidature": "candidate:" + token,
            "famille_relation": famille,
            "ark_source": ark_source,
            "libelle_source": libelle_source,
            "code_source": code_source,
            "typecom_source": typecom_source,
            "code_cible_insee": code_cible,
            "libelle_cible_mouvement": libelle_cible,
            "date_evenement": date,
            "modalite_cog": modalite,
            "preuve_cog": "|".join(sorted(preuves_ids)),
            "arks_sur_code_cible": json.dumps(
                [{"ark": x["ark_pactols"], "libelle": x["pref_fr_pactols"]} for x in options],
                ensure_ascii=False),
            "ark_cible_propose": cible["ark_pactols"] if cible else "",
            "libelle_cible_pactols": cible["pref_fr_pactols"] if cible else "",
            "indice_lexical": statut,
            "statut_instruction": "candidature_non_validante",
            "validation_adlfi": "non_valide",
        })

    # Une ligne COM -> COM de destination pour chacun des 25 dossiers :
    # les transitions COM -> COMD/COMA, MOD 35, MOD 34 et MOD 10 demeurent
    # dans les 42 lignes originales, sans être prises pour une seconde
    # relation historique entre ARK.
    for item in sorted(old, key=lambda v: v["code_historique_pactols"]):
        ark = item["ark_pactols"]
        code = item["code_historique_pactols"]
        possibles = [m for m in preuves_ark[ark]
                     if m["COM_AV"] == code and m["TYPECOM_AV"] == "COM"
                     and m["TYPECOM_AP"] == "COM"
                     and m["COM_AP"] != code and m["MOD"] in ("31", "32", "33")]
        if len(possibles) != 1 or code != preuves_ark[ark][0]["code_suivi"]:
            raise ValueError("Transition COM principale non univoque : " + code)
        m = possibles[0]
        ajouter(famille="reception_administrative_immediate",
                ark_source=ark, libelle_source=item["libelle_pactols"],
                code_source=code, typecom_source="COM",
                code_cible=m["COM_AP"], libelle_cible=m["LIBELLE_AP"],
                date=m["DATE_EFF"], modalite=m["MOD"],
                preuves_ids=[m["identifiant_ligne_cog"]])

    # Une réutilisation de code est une *candidate de succession entre
    # concepts*, non une fusion automatique des deux ARK.
    for d in sorted(doubles, key=lambda v: v["code_partage"]):
        concepts = json.loads(d["ark_et_libelles_pactols"])
        before = [v for v in concepts if normaliser(v["libelle"]) == normaliser(d["libelle_com_historique"])]
        after = [v for v in concepts if normaliser(v["libelle"]) == normaliser(d["libelle_com_2026"])]
        if len(before) != 1 or len(after) != 1 or before[0]["ark"] == after[0]["ark"]:
            raise ValueError("Codes partagés ne documentent pas deux ARK distincts")
        ajouter(famille="reutilisation_code_commune_nouvelle",
                ark_source=before[0]["ark"], libelle_source=before[0]["libelle"],
                code_source=d["code_partage"], typecom_source="COM",
                code_cible=d["code_partage"], libelle_cible=after[0]["libelle"],
                date=d["date_commune_nouvelle"], modalite="32",
                preuves_ids=["table_BFC_codes_partages_2"], strategie="exiger_ark",
                ark_cible=after[0]["ark"])

    # Pour COMA, la relation de rattachement est vérifiée au COG 2026 ;
    # la date de fusion-association est une information HISTORIQUE distincte.
    for a in sorted(associations, key=lambda v: v["code_historique"]):
        code = a["code_historique"]
        sources_ark = [x for x in par_code[code]
                       if normaliser(x["pref_fr_pactols"]) == normaliser(a["libelle_pactols"])]
        if len(sources_ark) != 1 or a["type_cog2026"] != "COMA":
            raise ValueError("Commune associée Pactols non univoque : " + code)
        ajouter(famille="rattachement_COMA_au_COG2026",
                ark_source=sources_ark[0]["ark_pactols"],
                libelle_source=a["libelle_pactols"],
                code_source=code, typecom_source="COMA",
                code_cible=a["comparent_cog2026"],
                libelle_cible=a["commune_parente_cog2026"],
                date=a["date_fusion_association"], modalite="33",
                preuves_ids=["table_BFC_antorpe_frettes_COMPARENT_2026"],
                strategie="exiger_ark",
                ark_cible=None if not par_code[a["comparent_cog2026"]] else
                    next((x["ark_pactols"] for x in par_code[a["comparent_cog2026"]]
                          if normaliser(x["pref_fr_pactols"]) == normaliser(a["commune_parente_cog2026"])), None))

    if len(rows) != 29 or len({r["id_candidature"] for r in rows}) != 29:
        raise ValueError("Candidatures non uniques ou incomplètes")
    initial = rows[:25]
    categories = collections.Counter(r["indice_lexical"] for r in initial)
    attendu = {"accord_lexical_univoque_non_valide": 11,
               "code_sans_concordance_lexicale": 9,
               "cible_absente_corpus_terminal": 5}
    if dict(categories) != attendu:
        raise ValueError("Répartition des 25 codes inattendue " + str(categories))
    if len([r for r in rows if r["ark_cible_propose"]]) != 15:
        raise ValueError("Nombre de candidatures ARK -> ARK inattendu")
    output = Path(sortie)
    names = ("candidatures-relations-bfc-29.csv", "candidatures-ark-ark-bfc-15.csv",
             "dossiers-sans-cible-univoque-bfc-14.csv", "rapport-relations-bfc.json")
    if any((output / n).resolve() in {p.resolve() for p in sources.values()} for n in names):
        raise ValueError("Une sortie écraserait une entrée")
    output.mkdir(parents=True, exist_ok=True)
    def save(path, records):
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, delimiter=";", fieldnames=OUTPUT_COLS)
            w.writeheader()
            w.writerows(records)
    rows.sort(key=lambda r: (r["famille_relation"], r["code_source"], r["date_evenement"]))
    save(output / names[0], rows)
    save(output / names[1], [r for r in rows if r["ark_cible_propose"]])
    save(output / names[2], [r for r in rows if not r["ark_cible_propose"]])
    report = {
        "etat": "recette_non_validante",
        "candidatures_administratives_total": len(rows),
        "relations_entre_ark_candidates_non_validees": 15,
        "candidatures_sans_ark_cible_univoque": 14,
        "anciens_codes": 25,
        "anciens_avec_libelle_cible_univoque": 11,
        "anciens_avec_code_seul": 9,
        "anciens_sans_ark_cible_dans_corpus": 5,
        "reutilisations_code_avec_deux_ark": 2,
        "rattachements_COMA_2026": 2,
        "preuves_mouvements_25": 42,
        "sha256_entrees": {k: sha(v) for k, v in sources.items()},
        "nouvelles_validations_adlfi": 0,
        "geometries_historiques_attribuees": 0,
        "limites": [
            "Les 15 propositions ARK-ARK sont des candidatures de recette, non des successeurs validés.",
            "La concordance lexicale n'établit pas l'identité d'un concept avec une entité administrative.",
            "Les 42 lignes avant/après (incluant COMD, COMA, MOD35 et MOD10) restent dans la preuve source.",
            "Le rattachement COMPARENT est observé en 2026 ; sa date de formation est instruite séparément.",
            "Absence d'ARK cible signifie absence parmi les 736 terminaux, non absence dans Pactols.",
        ],
    }
    (output / names[3]).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("inventaire", "anciens", "preuves", "partages", "associes", "sortie"):
        p.add_argument("--" + name, required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(generer(**vars(a)), ensure_ascii=False, indent=2))
