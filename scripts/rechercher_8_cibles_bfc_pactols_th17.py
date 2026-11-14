#!/usr/bin/env python3
"""Chercher les huit communes réceptrices BFC dans le RDF COMPLET Pactols-Lieux.

Source figée : Pactols_Lieux_th17_20260722.rdf (Frantiq, dépôt officiel Git
LFS, sha256:3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7).
Recherche par code exactMatch Insee et/ou prefLabel/altLabel français ;
aucune création d'ARK, aucune validation, aucune fermeture transitive.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
SKOS = "{http://www.w3.org/2004/02/skos/core#}"
OWL = "{http://www.w3.org/2002/07/owl#}"
LANG = "{http://www.w3.org/XML/1998/namespace}lang"
RDF_SHA = "3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
ARK_RE = re.compile(r"26678/[A-Za-z0-9_\-]+")
INSEE_RE = re.compile(
    r"^https?://id\.insee\.fr/geo/(commune|communeDeleguee|communeAssociee)/([0-9]{5})/?$",
    re.I,
)
CAND_FIELDS = (
    "code_cible_insee", "libelle_cible_cog", "nb_autorites_sources",
    "ark_candidat", "uri_concept_pactols", "pref_fr", "alt_fr",
    "codes_insee_exactmatch", "types_uri_insee", "uris_insee_exactmatch",
    "broader_pactols", "signaux", "concept_deprecie", "decision",
)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def norm(s):
    s = unicodedata.normalize("NFD", s.casefold())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def lire_cibles(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    req = {"code_cible_insee", "libelle_cible_cog", "nb_anciennes_autorites_source"}
    if not rows or not req <= set(rows[0]):
        raise ValueError("Colonnes des cibles BFC manquantes")
    if len(rows) != 8 or len({r["code_cible_insee"] for r in rows}) != 8:
        raise ValueError("Huit codes distincts attendus")
    if sum(int(r["nb_anciennes_autorites_source"]) for r in rows) != 14:
        raise ValueError("14 dossiers initiaux attendus")
    if any(not re.fullmatch(r"[0-9]{5}", r["code_cible_insee"]) for r in rows):
        raise ValueError("Code Insee cible mal formé")
    return rows


def apercu_concept(el):
    uri = el.get(RDF + "about", "")
    labels = collections.defaultdict(list)
    urls = []
    broaders = []
    deprecie = False
    for child in el:
        if child.tag in (SKOS + "prefLabel", SKOS + "altLabel"):
            if (child.get(LANG, "").lower().split("-")[0] == "fr") and child.text:
                kind = "pref" if child.tag == SKOS + "prefLabel" else "alt"
                labels[kind].append(child.text.strip())
        elif child.tag == SKOS + "exactMatch":
            u = child.get(RDF + "resource") or (child.text or "").strip()
            if u:
                urls.append(u)
        elif child.tag == SKOS + "broader":
            u = child.get(RDF + "resource") or (child.text or "").strip()
            if u:
                broaders.append(u)
        elif child.tag == OWL + "deprecated":
            deprecie = (child.text or "").strip().lower() in ("true", "1")
    return {
        "uri": uri,
        "ark": (ARK_RE.search(uri).group() if ARK_RE.search(uri) else ""),
        "pref_fr": sorted(set(labels["pref"])),
        "alt_fr": sorted(set(labels["alt"])),
        "urls": sorted(set(urls)),
        "broader": sorted(set(broaders)),
        "deprecie": deprecie,
    }


def types_liens(uri_list):
    by_code = collections.defaultdict(set)
    for u in uri_list:
        m = INSEE_RE.fullmatch(u)
        if m:
            by_code[m.group(2)].add(m.group(1))
    return by_code


def signals(concept, code, label):
    found = []
    matched = types_liens(concept["urls"])
    if code in matched:
        found.append("exactMatch_insee_code")
    n = norm(label)
    if any(norm(x) == n for x in concept["pref_fr"]):
        found.append("prefLabel_fr_exact")
    if any(norm(x) == n for x in concept["alt_fr"]):
        found.append("altLabel_fr_exact")
    # Un qualificatif départemental n'est pas une divergence sémantique,
    # mais reste un indice moins fort qu'un libellé identique.
    if any(norm(re.sub(r"\s*\([^)]{2,60}\)\s*$", "", x)) == n
           and norm(x) != n for x in concept["pref_fr"]):
        found.append("prefLabel_fr_qualifie")
    return found, matched


def parcourir_rdf(path, cibles):
    """Itération par noeud RDF direct : mémoire constante, pas de réseau."""
    codes = {r["code_cible_insee"] for r in cibles}
    names = {r["code_cible_insee"]: r["libelle_cible_cog"] for r in cibles}
    found = collections.defaultdict(list)
    total = 0
    depth = 0
    root_tag = None
    root = None
    for event, el in ET.iterparse(path, events=("start", "end")):
        if event == "start":
            depth += 1
            if depth == 1:
                root_tag = el.tag
                root = el
                if root_tag != RDF + "RDF":
                    raise ValueError("Le fichier doit être un graphe RDF/XML")
            continue
        if depth == 2:
            if el.tag in (SKOS + "Concept", RDF + "Description"):
                concept = apercu_concept(el)
                if concept["pref_fr"] or concept["alt_fr"] or concept["urls"]:
                    total += 1
                    for code in codes:
                        kinds, by_code = signals(concept, code, names[code])
                        if kinds:
                            found[code].append((concept, kinds, by_code))
            el.clear()
            if root is not None:
                root.clear()
        depth -= 1
    if total < 30000:
        raise ValueError(f"Export Pactols complet non reconnu : {total} concepts traités")
    return total, found


def produire(rdf, cibles, sortie):
    if sha(rdf) != RDF_SHA:
        raise ValueError("Le RDF n'est pas le snapshot th17 Frantiq 2026-07-22 attendu")
    targets = lire_cibles(cibles)
    total, matches = parcourir_rdf(rdf, targets)
    records = []
    summary = []
    for row in sorted(targets, key=lambda r: r["code_cible_insee"]):
        code = row["code_cible_insee"]
        candidates = matches[code]
        for c, types, codes in sorted(candidates, key=lambda x: x[0]["uri"]):
            insee_urls = [u for u in c["urls"] if INSEE_RE.fullmatch(u)]
            records.append({
                "code_cible_insee": code,
                "libelle_cible_cog": row["libelle_cible_cog"],
                "nb_autorites_sources": row["nb_anciennes_autorites_source"],
                "ark_candidat": c["ark"],
                "uri_concept_pactols": c["uri"],
                "pref_fr": json.dumps(c["pref_fr"], ensure_ascii=False),
                "alt_fr": json.dumps(c["alt_fr"], ensure_ascii=False),
                "codes_insee_exactmatch": json.dumps(sorted(codes), ensure_ascii=False),
                "types_uri_insee": json.dumps({k: sorted(v) for k, v in sorted(codes.items())}, ensure_ascii=False),
                "uris_insee_exactmatch": json.dumps(insee_urls, ensure_ascii=False),
                "broader_pactols": json.dumps(c["broader"], ensure_ascii=False),
                "signaux": "|".join(types),
                "concept_deprecie": "oui" if c["deprecie"] else "non",
                "decision": "a_instruire_non_valide",
            })
        exact_ark = [c["ark"] for c, evidence, _ in candidates if
                     c["ark"] and "exactMatch_insee_code" in evidence]
        name_ark = [c["ark"] for c, evidence, _ in candidates if
                    c["ark"] and ("prefLabel_fr_exact" in evidence or
                                  "altLabel_fr_exact" in evidence or
                                  "prefLabel_fr_qualifie" in evidence)]
        summary.append({
            "code_insee": code,
            "libelle": row["libelle_cible_cog"],
            "nb_dossiers": int(row["nb_anciennes_autorites_source"]),
            "nb_concepts_retrouves": len(candidates),
            "nb_ark_avec_lien_insee": len(set(exact_ark)),
            "nb_ark_avec_libelle_fr": len(set(name_ark)),
            "ark_lies_insee": json.dumps(sorted(set(exact_ark)), ensure_ascii=False),
            "ark_libelles_fr": json.dumps(sorted(set(name_ark)), ensure_ascii=False),
            "qualification": "piste_retrouvee_non_validee" if candidates else "aucun_candidat_snapshot",
        })
    output = Path(sortie)
    names = ("candidats-pactols-th17-bfc.csv", "synthese-8-cibles.csv", "rapport-recherche-pactols-bfc.json")
    if any((output / n).resolve() in {Path(rdf).resolve(), Path(cibles).resolve()} for n in names):
        raise ValueError("Une sortie écraserait une source")
    output.mkdir(parents=True, exist_ok=True)
    for name, rows, cols in ((names[0], records, CAND_FIELDS),
                             (names[1], summary, list(summary[0]))):
        with (output / name).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    report = {
        "statut": "recette_non_validante",
        "source_pactols": "https://github.com/frantiq/PACTOLS/blob/master/pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf",
        "snapshot": "2026-07-22",
        "rdf_sha256": sha(rdf),
        "cibles_communes_distinctes": len(summary),
        "dossiers_source": sum(x["nb_dossiers"] for x in summary),
        "concepts_rdf_parcourus": total,
        "candidatures_lignes": len(records),
        "cibles_avec_un_candidat": sum(x["nb_concepts_retrouves"] > 0 for x in summary),
        "cibles_avec_lien_code_insee": sum(x["nb_ark_avec_lien_insee"] > 0 for x in summary),
        "cibles_sans_concept": [x["code_insee"] for x in summary if x["nb_concepts_retrouves"] == 0],
        "nouveaux_alignements_adlfi": 0,
        "geometries_attribuees": 0,
        "avertissement": "Un concept trouvé par nom et/ou code ne constitue pas une relation de succession validée, même lorsque les deux signaux concordent.",
    }
    (output / names[2]).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for n in ("rdf", "cibles", "sortie"):
        p.add_argument("--" + n, type=Path, required=True)
    opts = p.parse_args()
    print(json.dumps(produire(opts.rdf, opts.cibles, opts.sortie), ensure_ascii=False, indent=2))
