#!/usr/bin/env python3
"""Projection PRIVÉE du pilote Heurist vers le schéma bibliographique public.

Lit uniquement les trois fichiers déjà filtrés du pilote, jamais l'export Heurist brut.
Le résultat reste CANDIDAT_NON_VALIDE ; une décision éditoriale distincte est
nécessaire pour publier une projection dans docs/data/.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_ROLES = {15: "auteur", 1057: "collaborateur"}
JOURNALS = {"gallia", "gallia_prehistoire"}
HOSTS = {"journals.openedition.org", "www.persee.fr"}
STATUS = "CANDIDAT_NON_VALIDE"


def load(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def canonical_doi(value):
    if not value:
        return None
    value = str(value).strip()
    while value.lower().startswith("https://doi.org/"):
        value = value[len("https://doi.org/"):]
    if not value.lower().startswith("10.") or "/" not in value:
        raise ValueError("DOI non canonique")
    return value


def safe_article_url(value):
    if not value:
        return None
    url = urlparse(value)
    # Uniformisation contrôlée d'anciennes URL HTTP du domaine OpenEdition ;
    # l'accessibilité de la page doit encore être vérifiée en recette.
    if url.scheme == "http" and url.netloc == "journals.openedition.org":
        value = "https://" + value[len("http://"):]
        url = urlparse(value)
    if url.scheme != "https" or url.netloc not in HOSTS or not url.path.startswith("/"):
        raise ValueError("URL article hors des deux hébergeurs autorisés")
    if url.username or url.password or url.query or url.fragment:
        raise ValueError("URL article non normalisée")
    return value


def project(articles_doc, relations_doc, mapping_doc, persons_doc):
    sources = [articles_doc, relations_doc, mapping_doc]
    if any(x.get("status") != STATUS for x in sources):
        raise ValueError("Entrée de pilote inattendue")
    hashes = {x.get("source_sha256") for x in sources}
    if len(hashes) != 1 or len(next(iter(hashes))) != 64:
        raise ValueError("Provenance de source divergente")
    source_hash = hashes.pop()
    published_ids = {x["id"]: x["identifiers"]["idref"] for x in persons_doc["authorities"]}
    mappings = mapping_doc["mappings"]
    if len({x["person_id"] for x in mappings}) != len(mappings):
        raise ValueError("Pont PER multiple")
    for row in mappings:
        if published_ids.get(row["person_id"]) != row["idref"]:
            raise ValueError("Pont IdRef–PER incohérent")
    allowed_persons = {x["person_id"] for x in mappings}

    articles = []
    article_by_id = {}
    for raw in articles_doc["articles"]:
        if raw["journal"] not in JOURNALS:
            raise ValueError("Revue hors du périmètre")
        article = {
            "id": raw["article_id"],
            "journal": raw["journal"],
            "title": raw["title"],
            "year": raw["year"],
            "volume": raw["volume"],
            "first_page": raw["first_page"],
            "last_page": raw["last_page"],
            "url": safe_article_url(raw.get("url")),
            "doi": canonical_doi(raw.get("doi")),
        }
        if not article["title"] or article["id"] in article_by_id:
            raise ValueError("Article absent ou en double")
        article_by_id[article["id"]] = article
        articles.append(article)

    contributions, keys = [], set()
    for raw in relations_doc["relations"]:
        role = ALLOWED_ROLES.get(raw["source_field_id"])
        if role is None or raw["role"] != role:
            raise ValueError("Relation hors des rôles publiables")
        if raw["person_id"] not in allowed_persons:
            raise ValueError("Personne absente des ponts PER")
        if raw["article_id"] not in article_by_id:
            raise ValueError("Article inconnu")
        key = (raw["person_id"], raw["article_id"], role)
        if key in keys:
            raise ValueError("Contribution répétée")
        keys.add(key)
        position = raw["position_in_role"]
        if not isinstance(position, int) or isinstance(position, bool) or position < 1:
            raise ValueError("Position de rôle incorrecte")
        contributions.append({
            "article_id": raw["article_id"],
            "person_id": raw["person_id"],
            "role": role,
            "position_in_role": position,
        })
    if {r["article_id"] for r in contributions} != set(article_by_id):
        raise ValueError("Article sans relation pilote")
    used_persons = {x["person_id"] for x in contributions}
    return {
        "schema_version": "0.1.0",
        "dataset": "adlfi-referentiels/personnes-articles",
        "publication_status": STATUS,
        "scope_note": "Projection candidate Gallia / Gallia Préhistoire ; visa éditorial non accordé.",
        "source_sha256": source_hash,
        "totals": {
            "articles": len(articles),
            "contributions": len(contributions),
            "authorities": len(used_persons),
        },
        "articles": articles,
        "contributions": contributions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--articles", type=Path, required=True)
    parser.add_argument("--relations", type=Path, required=True)
    parser.add_argument("--ponts", type=Path, required=True)
    parser.add_argument("--personnes", type=Path, required=True)
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    output = args.sortie.resolve()
    docs = Path(__file__).resolve().parents[1] / "docs"
    if output == docs or docs in output.parents:
        parser.error("Une projection non validée ne peut pas être écrite sous docs/")
    result = project(load(args.articles), load(args.relations),
                     load(args.ponts), load(args.personnes))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("CANDIDAT NON PUBLIÉ :", result["totals"])


if __name__ == "__main__":
    main()
