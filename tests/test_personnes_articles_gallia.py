"""Garde-fous pour le futur catalogue Gallia / Gallia Préhistoire (sans données candidates)."""
import importlib.util
import json
from pathlib import Path
import hashlib
import unittest
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
# Instantanés canoniques des données v0.2 (conservés lors des extensions futures).
ORIGINAL_GALLIA_ARTICLES_SHA256 = "cf9280855af2e57b5625e4faa33efa37a59dc8123df76b101e16acd62f893511"
ORIGINAL_GALLIA_RELATIONS_SHA256 = "79ecc564847a6a266ca363d3a8166ad28c637b3c41cb17254512524f34b4bcb6"


def fingerprint(value):
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

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

    def test_normalise_ancien_http_openedition(self):
        a, r, m, p = fixture()
        a["articles"][0]["url"] = "http://journals.openedition.org/galliap/891"
        result = module.project(a, r, m, p)
        self.assertEqual(result["articles"][0]["url"],
                         "https://journals.openedition.org/galliap/891")

    def test_refuse_deux_articles_partageant_un_doi(self):
        a, r, m, p = fixture()
        second = {**a["articles"][0], "article_id": "heurist:1519:73:719",
                  "title": "Sous-section du premier article",
                  "url": "https://journals.openedition.org/gallia/124"}
        a["articles"].append(second)
        r["relations"].append({**r["relations"][0], "article_id": second["article_id"]})
        with self.assertRaisesRegex(ValueError, "DOI dupliqué"):
            module.project(a, r, m, p)

    def test_refuse_deux_articles_partageant_une_url(self):
        a, r, m, p = fixture()
        second = {**a["articles"][0], "article_id": "heurist:1519:73:719",
                  "title": "Sous-section du premier article",
                  "doi": "10.4000/gallia.124"}
        a["articles"].append(second)
        r["relations"].append({**r["relations"][0], "article_id": second["article_id"]})
        with self.assertRaisesRegex(ValueError, "URL dupliquée"):
            module.project(a, r, m, p)

    def test_refuse_url_hors_liste(self):
        a, r, m, p = fixture()
        a["articles"][0]["url"] = "https://example.net/private"
        with self.assertRaisesRegex(ValueError, "URL article"):
            module.project(a, r, m, p)


class TestCatalogueArticlesPublic(unittest.TestCase):
    def test_schema_personnes_v05_zero_adlfi(self):
        persons_schema = json.loads((ROOT / "docs/schemas/personnes.schema.json").read_text())
        data = json.loads(PERSONS.read_text(encoding="utf-8"))
        self.assertEqual(persons_schema["properties"]["schema_version"]["const"], "0.5.0")
        self.assertEqual(data["schema_version"], "0.5.0")
        authority = persons_schema["$defs"]["authority"]
        self.assertEqual(authority["properties"]["contributions_count"]["minimum"], 0)
        self.assertIn("idref", authority["properties"]["identifiers"]["required"])
        self.assertEqual(authority["properties"]["identifiers"]["properties"]["idref"]["pattern"],
                         "^[0-9]{8}[0-9X]$")

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
        article_ids, doi_ids, article_urls = set(), set(), set()
        for article in obj["articles"]:
            self.assertEqual(set(article), {"id", "journal", "title", "year", "volume",
                                           "first_page", "last_page", "url", "doi"})
            self.assertIn(article["journal"], {"gallia", "gallia_prehistoire"})
            self.assertNotIn(article["id"], article_ids)
            article_ids.add(article["id"])
            if article["doi"]:
                self.assertNotIn(article["doi"], doi_ids)
                doi_ids.add(article["doi"])
            if article["url"]:
                self.assertNotIn(article["url"], article_urls)
                article_urls.add(article["url"])
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



class TestPiloteGalliaV02Publication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.articles = json.loads(PUBLIC.read_text(encoding="utf-8"))
        cls.persons = json.loads(PERSONS.read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))

    def test_jalon_source_et_effectifs(self):
        obj = self.articles
        # Verrouiller le pilote publié sans bloquer les futurs lots Heurist.
        self.assertRegex(obj["source_sha256"], r"^[0-9a-f]{64}$")
        self.assertGreaterEqual(obj["totals"]["articles"], 337)
        self.assertGreaterEqual(obj["totals"]["contributions"], 473)
        self.assertGreaterEqual(obj["totals"]["authorities"], 193)
        self.assertEqual(fingerprint(obj["articles"][:337]), ORIGINAL_GALLIA_ARTICLES_SHA256)
        self.assertEqual(fingerprint(obj["contributions"][:473]), ORIGINAL_GALLIA_RELATIONS_SHA256)

    def test_article_section_documentee(self):
        by_id = {a["id"]: a for a in self.articles["articles"]}
        self.assertIn("heurist:1519:73:872", by_id)
        self.assertNotIn("heurist:1519:73:1392", by_id)
        self.assertEqual(by_id["heurist:1519:73:872"]["doi"], "10.3406/galia.1998.3258")
        self.assertEqual([a["id"] for a in self.articles["articles"] if not a["url"]],
                         ["heurist:1519:73:942"])

    def test_identites_et_champs_publics(self):
        from collections import Counter
        obj = self.articles
        valid = {p["id"] for p in self.persons["authorities"]}
        self.assertGreaterEqual(len(valid), 202)
        self.assertEqual({c["person_id"] for c in obj["contributions"]}.difference(valid), set())
        self.assertEqual(len({(c["article_id"], c["person_id"], c["role"])
                              for c in obj["contributions"]}), len(obj["contributions"]))
        self.assertEqual(len({a["doi"] for a in obj["articles"] if a["doi"]}),
                         sum(bool(a["doi"]) for a in obj["articles"]))
        self.assertEqual(len({a["url"] for a in obj["articles"] if a["url"]}),
                         sum(bool(a["url"]) for a in obj["articles"]))
        public_roles = {c["role"] for c in obj["contributions"]}
        self.assertEqual(public_roles, {"auteur", "collaborateur"})
        self.assertTrue(all(c["position_in_role"] > 0 for c in obj["contributions"]))
        self.assertEqual(obj["publication_status"], "PUBLIC_PILOT")

    def test_comptage_adlfi_et_autorites_sans_notice_adlfi(self):
        # Les articles Gallia ne doivent jamais gonfler contributions_count.
        from collections import Counter
        published_adlfi = Counter(c["person_id"] for c in self.persons["contributions"])
        gallia_people = {c["person_id"] for c in self.articles["contributions"]}
        all_people = {a["id"] for a in self.persons["authorities"]}
        self.assertEqual(len(all_people), len(self.persons["authorities"]))
        self.assertEqual(self.persons["schema_version"], "0.5.0")
        for authority in self.persons["authorities"]:
            per = authority["id"]
            count = published_adlfi.get(per, 0)
            with self.subTest(per=per):
                self.assertEqual(authority["contributions_count"], count)
                if count == 0:
                    self.assertIn(per, gallia_people)

    def test_manifest_bibliographique(self):
        obj = self.articles
        module = self.manifest["modules"]["personnes"]
        complement = module["articles_lies"]
        self.assertEqual(complement["data"], "data/personnes-articles.json")
        self.assertEqual(complement["data_schema"], obj["schema_version"])
        self.assertEqual(complement["status"], "pilote")
        self.assertEqual([complement["articles"], complement["contributions"],
                          complement["autorites_reliees"]],
                         [obj["totals"][k] for k in ("articles", "contributions", "authorities")])
        from collections import Counter
        roles = Counter(c["role"] for c in obj["contributions"])
        journals = Counter(a["journal"] for a in obj["articles"])
        self.assertEqual(complement["auteurs"], roles["auteur"])
        self.assertEqual(complement["collaborateurs"], roles["collaborateur"])
        self.assertEqual(complement["par_revue"], dict(journals))
        self.assertGreaterEqual(module["autorites_validees"], 202)
        self.assertEqual(module["contributions_adlfi"], 1980)
        self.assertEqual(module["notices_adlfi"], 1779)



if __name__ == "__main__":
    unittest.main()
