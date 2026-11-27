#!/usr/bin/env python3
"""Contrôler un pilote Personnes Heurist AVANT visa, sans produire de catalogue public.

Lit des projections préfiltrées, jamais l'export source contenant des champs internes.
Aucun PER n'est créé. Toutes les relations doivent provenir des seuls champs
bibliographiques auteur/collaborateur, déjà contrôlés au niveau de la source.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROLE = {"auteur", "collaborateur"}
JOURNAL = {"gallia", "gallia_prehistoire"}
IDENTIFIERS = {
    "idref": r"[0-9]{8}[0-9X]",
    "bnf": r"cb[0-9]{8}[0-9a-z]",
    "orcid": r"[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9X]{4}",
    "idhal": r"[A-Za-z0-9_-]+",
    "persee": r"[0-9]+",
    "wikidata": r"Q[1-9][0-9]*",
}
ARTICLE_FIELDS = {"id", "journal", "title", "year", "volume", "first_page", "last_page", "url", "doi"}
RELATION_FIELDS = {"heurist_article_id", "heurist_person_id", "journal", "role", "position_in_role"}
PERSON_FIELDS = {"heurist_person_id", "strate_technique", "statut", "per_propose", "autorite_candidat", "relations_par_revue_role"}
PUBLIC_AUTHORITY_FIELDS = {"name", "family_name", "name_idref", "identifiers", "contributions_count", "name_variants"}
PERSON_VARIANT_FIELDS = {"value", "kind", "source"}
ALLOWED_ARTICLE_HOSTS = {"journals.openedition.org", "www.persee.fr"}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def validate(people_doc, article_doc, relation_doc, current_people, current_articles):
    """Retourne les effectifs contrôlés, sans aucune allocation de PER."""
    sources = (people_doc, article_doc, relation_doc)
    require(all(x.get("status") == "CANDIDAT_NON_VALIDE" for x in sources), "Statut privé manquant")
    hashes = {x.get("source_sha256") for x in sources}
    require(len(hashes) == 1, "Provenances Heurist divergentes")
    source_hash = hashes.pop()
    require(isinstance(source_hash, str) and re.fullmatch(r"[0-9a-f]{64}", source_hash), "Empreinte invalide")
    require(current_articles.get("source_sha256") == source_hash, "Export Heurist non concordant avec le catalogue publié")
    require(current_people.get("publication_status") == "PUBLIC_PILOT", "Catalogue Personnes non publié")
    require(current_articles.get("publication_status") == "PUBLIC_PILOT", "Catalogue bibliographique non publié")

    ids = set()
    external = set()
    for row in current_people["authorities"]:
        for k, v in row["identifiers"].items():
            external.add((k, v))
    people = people_doc["authorities"]
    require(people_doc["authority_count"] == len(people) and len(people) > 0, "Effectif de candidatures incorrect")
    for c in people:
        require(set(c) == PERSON_FIELDS, "Champs d'autorité Heurist hors liste blanche")
        pid = c["heurist_person_id"]
        require(isinstance(pid, str) and pid.isdigit() and pid not in ids, "Doublon ou ID Heurist invalide")
        ids.add(pid)
        require(c["per_propose"] is None and c["statut"] == "CANDIDAT_NON_VALIDE", "PER alloué sans visa")
        require(isinstance(c["strate_technique"], str) and c["strate_technique"], "Strate vide")
        profile = c["autorite_candidat"]
        require(set(profile) == PUBLIC_AUTHORITY_FIELDS, "Champ de profil non public")
        require(profile["contributions_count"] == 0, "Contribution AdlFI fictive")
        require(profile["name_idref"] == "", "Forme IdRef non validée")
        require(isinstance(profile["name"], str) and profile["name"].strip(), "Nom vide")
        require(isinstance(profile["family_name"], str) and profile["family_name"].strip(), "Patronyme vide")
        identifiers = profile["identifiers"]
        require("idref" in identifiers and identifiers.keys() <= IDENTIFIERS.keys(), "Identifiants hors périmètre")
        for kind, value in identifiers.items():
            require(isinstance(value, str) and re.fullmatch(IDENTIFIERS[kind], value), "Identifiant invalide : " + kind)
            require((kind, value) not in external, "Collision d'identifiant : " + kind)
            external.add((kind, value))
        for variant in profile["name_variants"]:
            require(set(variant) == PERSON_VARIANT_FIELDS, "Variante non normalisée")
            require(variant["kind"] == "autre_forme_attestee" and variant["source"] == "Heurist" and
                    isinstance(variant["value"], str) and bool(variant["value"].strip()), "Variante non attestée")
        summary = c["relations_par_revue_role"]
        require(set(summary) == JOURNAL, "Revues non publiques dans le bilan")
        for j in JOURNAL:
            require(set(summary[j]) == ROLE and all(type(n) is int and n >= 0 for n in summary[j].values()),
                    "Comptage de rôle invalide")

    known_articles = {}
    uri_index = {"doi": set(), "url": set()}
    for article in current_articles["articles"]:
        known_articles[article["id"]] = article
        for key in uri_index:
            if article[key]:
                require(article[key] not in uri_index[key], "Doublon ancien : " + key)
                uri_index[key].add(article[key])
    reused = article_doc["existing_articles_reused"]
    require(len(reused) == len(set(reused)) and all(x in known_articles for x in reused),
            "Article de référence inconnu ou répété")
    new_articles = article_doc["new_articles"]
    new_ids = set()
    for a in new_articles:
        require(set(a) == ARTICLE_FIELDS, "Champ bibliographique hors liste blanche")
        aid = a["id"]
        require(isinstance(aid, str) and re.fullmatch(r"heurist:[0-9]+:73:[0-9]+", aid) and
                aid not in known_articles and aid not in new_ids, "Article nouveau non distinct")
        new_ids.add(aid)
        require(a["journal"] in JOURNAL and isinstance(a["title"], str) and a["title"].strip(),
                "Article non qualifié")
        require(a["year"] is None or type(a["year"]) is int and 1900 <= a["year"] <= 2100, "Année non valide")
        for f in ("volume", "first_page", "last_page"):
            require(a[f] is None or isinstance(a[f], str), "Pagination ou volume invalide")
        url = a["url"]
        if url is not None:
            require(isinstance(url, str), "URL invalide")
            parsed = urlparse(url)
            require(parsed.scheme == "https" and parsed.hostname in ALLOWED_ARTICLE_HOSTS and parsed.username is None and
                    parsed.password is None and not parsed.query and not parsed.fragment and bool(parsed.path) and
                    parsed.netloc == parsed.hostname, "URL bibliographique hors liste blanche")
        doi = a["doi"]
        require(doi is None or isinstance(doi, str) and re.fullmatch(r"10\.[0-9]{4,9}/\S+", doi), "DOI non canonique")
        for field in uri_index:
            if a[field]:
                require(a[field] not in uri_index[field], "Doublon de " + field)
                uri_index[field].add(a[field])
        known_articles[aid] = a
    permitted_articles = set(reused) | new_ids
    require(not (set(reused) & new_ids), "Article candidat déjà présent")
    relations = relation_doc["relations"]
    require(isinstance(relations, list), "Relations absentes")
    seen = set()
    by_person = defaultdict(Counter)
    used_articles = set()
    for r in relations:
        require(set(r) == RELATION_FIELDS, "Champ de relation non publié")
        pid, aid, role, journal = r["heurist_person_id"], r["heurist_article_id"], r["role"], r["journal"]
        aid = "heurist:1519:73:" + aid
        require(pid in ids, "Auteur non sélectionné")
        require(aid in permitted_articles, "Article non présent dans le candidat")
        require(role in ROLE and journal == known_articles[aid]["journal"], "Rôle ou revue non publiable")
        require(type(r["position_in_role"]) is int and r["position_in_role"] > 0, "Position invalide")
        pair = (pid, aid, role)
        require(pair not in seen, "Relation personne-article répétée")
        seen.add(pair)
        used_articles.add(aid)
        by_person[pid][(journal, role)] += 1
    require(used_articles == permitted_articles, "Article non rattaché à une relation")
    require(set(by_person) == ids, "Personne sans contribution bibliographique")
    for c in people:
        pid = c["heurist_person_id"]
        for j in JOURNAL:
            for role in ROLE:
                require(by_person[pid][(j, role)] == c["relations_par_revue_role"][j][role],
                        "Compteur de contribution de la personne incohérent")

    counts = Counter(r["role"] for r in relations)
    journals = Counter(a["journal"] for a in new_articles)
    return {"statut": "CANDIDAT_NON_VALIDE", "personnes": len(people),
            "relations": len(relations), "auteurs": counts["auteur"], "collaborateurs": counts["collaborateur"],
            "nouveaux_articles": len(new_articles), "articles_deja_publies_reutilises": len(reused),
            "articles_gallia_nouveaux": journals["gallia"],
            "articles_gallia_prehistoire_nouveaux": journals["gallia_prehistoire"],
            "per_attribues": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("candidatures", "articles", "relations", "personnes_publiees", "articles_publies"):
        parser.add_argument("--" + arg.replace("_", "-"), type=Path, required=True)
    args = parser.parse_args()
    def load(p):
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    result = validate(load(args.candidatures), load(args.articles), load(args.relations),
                      load(args.personnes_publiees), load(args.articles_publies))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
