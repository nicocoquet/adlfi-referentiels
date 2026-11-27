"""Garde-fous pour le futur catalogue Gallia / Gallia Préhistoire (sans données candidates)."""
import importlib.util
import json
from pathlib import Path
import unittest
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/preparer_personnes_articles_gallia.py"
PUBLIC = ROOT / "docs/data/personnes-articles.json"
PERSONS = ROOT / "docs/data/personnes.json"

spec = importlib.util.spec_from_file_location("preparer_gallia", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    source = "a" * 64
    article = {
        "article_id": "heurist:1519:73:718",
        "journal": "gallia",
        "title": "Titre test",
        "year": 2020,
        "volume": "Gallia, 77-1",
        "first_page": "1",
        "last_page": "7",
        "url": "https://journals.openedition.org/gallia/123",
        "doi": "https://doi.org/https://doi.org/10.4000/gallia.123",
        "source_doi": "https://doi.org/10.4000/gallia.123",
        "source_record_id": "718",
        "private_source_field": "NE PAS PUBLIER",
    }
    relation = {
        "article_id": article["article_id"],
        "person_id": "PER-000001",
        "role": "auteur",
        "source_field_id": 15,
        "source_person_record_id": "42",
        "source_article_record_id": "718",
        "position_in_role": 1,
    }
    wrap = lambda key, rows: {"status": "CANDIDAT_NON_VALIDE", "source_sha256": source, key: rows}
    return (
        wrap("articles", [article]),
        wrap("relations", [relation]),
        wrap("mappings", [{"person_id": "PER-000001", "idref": "028293290",
                           "source_person_record_id": "42"}]),
        {"authorities": [{"id": "PER-000001", "identifiers": {"idref": "028293290"}}]},
    )


class TestProjectionArticleHeurist(unittest.TestCase):
    def test_only_allowlisted_fields_survive(self):
        projected = module.project(*fixture())
        self.assertEqual(projected["publication_status"], "CANDIDAT_NON_VALIDE")
        self.assertEqual(projected["totals"], {"articles": 1, "contributions": 1, "authorities": 1})
        self.assertEqual(projected["articles"][0]["doi"], "10.4000/gallia.123")
        self.assertEqual(projected["contributions"][0], {
            "article_id": "heurist:1519:73:718", "person_id": "PER-000001",
            "role": "auteur", "position_in_role": 1,
        })
        result = json.dumps(projected, ensure_ascii=False)
        self.assertNotIn("NE PAS PUBLIER", result)
        self.assertNotIn("source_person_record_id", result)
        self.assertNotIn("source_field_id", result)
        self.assertNotIn("source_doi", result)

    def test_collaborateur_distinct_de_auteur(self):
        article, relation, mapping, persons = fixture()
        relation["relations"].append({**relation["relations"][0],
                                      "role": "collaborateur", "source_field_id": 1057})
        projected = module.project(article, relation, mapping, persons)
        self.assertEqual({x["role"] for x in projected["contributions"]},
                         {"auteur", "collaborateur"})
        self.assertEqual(projected["totals"]["articles"], 1)
        self.assertEqual(projected["totals"]["contributions"], 2)

    def test_refuse_role_non_autorise(self):
        a, r, m, p = fixture()
        r["relations"][0]["source_field_id"] = 9999
        r["relations"][0]["role"] = "autre"
        with self.assertRaisesRegex(ValueError, "rôles publiables"):
            module.project(a, r, m, p)

    def test_refuse_idref_incoherent(self):
        a, r, m, p = fixture()
        m["mappings"][0]["idref"] = "000000000"
        with self.assertRaisesRegex(ValueError, "IdRef"):
            module.project(a, r, m, p)

    def test_refuse_url_hors_liste(self):
        a, r, m, p = fixture()
        a["articles"][0]["url"] = "https://example.net/private"
        with self.assertRaisesRegex(ValueError, "URL article"):
            module.project(a, r, m, p)


class TestCatalogueArticlesPublic(unittest.TestCase):
    def test_schema_structure(self):
        schema = json.loads((ROOT / "docs/schemas/personnes-articles.schema.json").read_text())
        self.assertEqual(schema["properties"]["publication_status"]["const"], "PUBLIC_PILOT")
        roles = schema["properties"]["contributions"]["items"]["properties"]["role"]["enum"]
        self.assertEqual(set(roles), {"auteur", "collaborateur"})

    def test_catalogue_si_publie(self):
        if not PUBLIC.exists():
            self.skipTest("Aucun catalogue Gallia publié : pilote en attente de visa")
        obj = json.loads(PUBLIC.read_text(encoding="utf-8"))
        self.assertEqual(obj["publication_status"], "PUBLIC_PILOT")
        self.assertEqual(obj["dataset"], "adlfi-referentiels/personnes-articles")
        self.assertEqual(obj["schema_version"], "0.1.0")
        self.assertEqual(set(obj), {"schema_version", "dataset", "publication_status",
                                    "scope_note", "source_sha256", "totals",
                                    "articles", "contributions"})
        published = json.loads(PERSONS.read_text(encoding="utf-8"))
        persons = {x["id"] for x in published["authorities"]}
        article_ids = set()
        for article in obj["articles"]:
            self.assertEqual(set(article), {"id", "journal", "title", "year", "volume",
                                           "first_page", "last_page", "url", "doi"})
            self.assertIn(article["journal"], {"gallia", "gallia_prehistoire"})
            self.assertNotIn(article["id"], article_ids)
            article_ids.add(article["id"])
            if article["url"]:
                u = urlparse(article["url"])
                self.assertEqual(u.scheme, "https")
                self.assertIn(u.netloc, {"www.persee.fr", "journals.openedition.org"})
        seen = set()
        for c in obj["contributions"]:
            self.assertEqual(set(c), {"article_id", "person_id", "role", "position_in_role"})
            self.assertIn(c["article_id"], article_ids)
            self.assertIn(c["person_id"], persons)
            self.assertIn(c["role"], {"auteur", "collaborateur"})
            self.assertGreaterEqual(c["position_in_role"], 1)
            key = (c["article_id"], c["person_id"], c["role"])
            self.assertNotIn(key, seen)
            seen.add(key)
        self.assertEqual(obj["totals"], {
            "articles": len(obj["articles"]),
            "contributions": len(obj["contributions"]),
            "authorities": len({c["person_id"] for c in obj["contributions"]}),
        })


if __name__ == "__main__":
    unittest.main()
