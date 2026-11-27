"""Non-régression permanente du premier lot de 40 autorités Heurist Gallia.

Visa éditorial obtenu dans la conversation du 27 novembre 2026.
Aucune donnée de travail Heurist, aucune matrice de visa ou identité d'évaluateur.
"""
import collections
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = "de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051"
NEW_AUTH_SHA256 = "8003a010fe9cce041a87fd46a567f0d7c368b8c9389d2ba3261c15ed97f3e7dc"
NEW_ARTICLES_SHA256 = "3b60b5cb30d5d135218a502f152399061b66c3435f87334ab48d453ce401e6dd"
NEW_LINKS_SHA256 = "a988081f2d4708459e24a9403a619dc88ae8e330d460a1a53eedcbcbc27fa8f3"


def fingerprint(value):
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class TestPilote40PersonnesHeuristPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persons = json.loads((ROOT / "docs/data/personnes.json").read_text(encoding="utf-8"))
        cls.articles = json.loads((ROOT / "docs/data/personnes-articles.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))

    def test_jalon_des_40_per_et_identifiants(self):
        new = self.persons["authorities"][202:242]
        self.assertEqual(len(new), 40)
        self.assertEqual([x["id"] for x in new],
                         [f"PER-{i:06d}" for i in range(203, 243)])
        self.assertEqual(fingerprint(new), NEW_AUTH_SHA256)
        self.assertEqual({x["contributions_count"] for x in new}, {0})
        self.assertEqual(len({x["identifiers"]["idref"] for x in new}), 40)
        self.assertEqual(sum(bool(x["name_variants"]) for x in new), 5)
        self.assertEqual(sum(len(x["name_variants"]) > 1 for x in new), 4)
        self.assertTrue(all(x["name"] and x["family_name"] for x in new))

    def test_64_articles_supplementaires_et_105_relations(self):
        a = self.articles
        new_articles = a["articles"][337:401]
        new_links = a["contributions"][473:578]
        self.assertEqual(len(new_articles), 64)
        self.assertEqual(len(new_links), 105)
        self.assertEqual(fingerprint(new_articles), NEW_ARTICLES_SHA256)
        self.assertEqual(fingerprint(new_links), NEW_LINKS_SHA256)
        self.assertEqual(collections.Counter(x["journal"] for x in new_articles),
                         {"gallia": 35, "gallia_prehistoire": 29})
        self.assertEqual(collections.Counter(x["role"] for x in new_links),
                         {"auteur": 69, "collaborateur": 36})
        self.assertEqual(len({x["article_id"] for x in new_links}), 90)
        self.assertEqual(len({x["article_id"] for x in new_links}
                             & {x["id"] for x in a["articles"][:337]}), 26)
        self.assertEqual(sum(x["url"] is None for x in new_articles), 1)
        self.assertEqual(sum(x["doi"] is None for x in new_articles), 4)

    def test_catalogue_et_roles_autorises_sans_collision(self):
        d, a = self.persons, self.articles
        self.assertEqual(d["schema_version"], "0.5.0")
        self.assertEqual(a["schema_version"], "0.1.0")
        self.assertEqual(d["publication_status"], "PUBLIC_PILOT")
        self.assertEqual(a["publication_status"], "PUBLIC_PILOT")
        self.assertEqual(a["source_sha256"], SOURCE_SHA256)
        self.assertEqual(len({x["id"] for x in d["authorities"]}), len(d["authorities"]))
        self.assertEqual(len({x["id"] for x in a["articles"]}), len(a["articles"]))
        for key in ("idref", "bnf", "orcid", "idhal", "persee", "wikidata"):
            values = [x["identifiers"][key] for x in d["authorities"]
                      if x["identifiers"].get(key)]
            self.assertEqual(len(values), len(set(values)), key)
            self.assertNotIn("####", values)
        for key in ("doi", "url"):
            values = [x[key] for x in a["articles"] if x.get(key)]
            self.assertEqual(len(values), len(set(values)), key)
        ids = {x["id"] for x in d["authorities"]}
        article_ids = {x["id"] for x in a["articles"]}
        links = a["contributions"]
        self.assertEqual({x["role"] for x in links}, {"auteur", "collaborateur"})
        self.assertTrue(all(x["person_id"] in ids and x["article_id"] in article_ids
                            and isinstance(x["position_in_role"], int)
                            and x["position_in_role"] > 0 for x in links))
        self.assertEqual(len({(x["person_id"], x["article_id"], x["role"]) for x in links}),
                         len(links))
        allowed_person_keys = {"id", "name", "family_name", "name_idref",
                               "identifiers", "contributions_count", "name_variants"}
        allowed_article_keys = {"id", "journal", "title", "year", "volume",
                                "first_page", "last_page", "url", "doi"}
        allowed_relation_keys = {"article_id", "person_id", "role", "position_in_role"}
        self.assertTrue(all(set(x) == allowed_person_keys
                            for x in d["authorities"][202:242]))
        self.assertTrue(all(set(x) == allowed_article_keys
                            for x in a["articles"][337:401]))
        self.assertTrue(all(set(x) == allowed_relation_keys
                            for x in links[473:578]))

    def test_zero_adlfi_et_pont_bibliographique(self):
        d, a = self.persons, self.articles
        ids = {x["id"] for x in d["authorities"][202:242]}
        adlfi = {x["person_id"] for x in d["contributions"]}
        gallia = {x["person_id"] for x in a["contributions"]}
        self.assertEqual(ids & adlfi, set())
        self.assertEqual(ids - gallia, set())
        self.assertEqual(d["totals"]["notices"], len({x["handle"] for x in d["contributions"]}))
        self.assertEqual(d["totals"]["contributions"], len(d["contributions"]))
        self.assertEqual(d["totals"]["authorities"], len(d["authorities"]))

    def test_manifeste_et_effectifs_par_revue(self):
        d, a = self.persons, self.articles
        self.assertGreaterEqual(len(d["authorities"]), 242)
        self.assertGreaterEqual(len(a["articles"]), 401)
        self.assertGreaterEqual(len(a["contributions"]), 578)
        self.assertGreaterEqual(len(d["contributions"]), 1980)
        m = self.manifest["modules"]["personnes"]
        b = m["articles_lies"]
        self.assertEqual(m["data_schema"], d["schema_version"])
        self.assertEqual([m["autorites_validees"], m["contributions_adlfi"],
                          m["notices_adlfi"]],
                         [d["totals"][k] for k in ("authorities", "contributions", "notices")])
        self.assertEqual(b["data_schema"], a["schema_version"])
        self.assertEqual([b["articles"], b["contributions"], b["autorites_reliees"]],
                         [len(a["articles"]), len(a["contributions"]),
                          len({x["person_id"] for x in a["contributions"]})])
        self.assertEqual(b["par_revue"],
                         dict(collections.Counter(x["journal"] for x in a["articles"])))
        self.assertEqual(b["auteurs"],
                         sum(x["role"] == "auteur" for x in a["contributions"]))
        self.assertEqual(b["collaborateurs"],
                         sum(x["role"] == "collaborateur" for x in a["contributions"]))


if __name__ == "__main__":
    unittest.main()
