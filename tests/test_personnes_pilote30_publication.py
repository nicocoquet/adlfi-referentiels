"""Publication du pilote IdRef Heurist 30 : empreintes et invariants publics.

Les preuves sources et matrices de qualification sont conservées hors GitHub.
Les enregistrements publics sont vérifiés par des empreintes canoniques.
"""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINGERPRINTS = {
    "people": "09f84b5e13c02e1f7348bda9982002f32b96c91c08ae7fd8011e9244e885dc56",
    "articles": "ddd0dc85498f7f8480a1fbc9f0290b09c762fae030bb2e4c2154533bdcbdcdb2",
    "relations": "7f3511d1eeaf82f04f65ce612aa54fababa6c3cecba245f256c4a794a26ce77c",
}
SOURCE_SHA256 = "de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051"


def fingerprint(rows):
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class TestPiloteHeurist30Publication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persons = json.loads((ROOT / "docs/data/personnes.json").read_text(encoding="utf-8"))
        cls.biblio = json.loads((ROOT / "docs/data/personnes-articles.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))["modules"]["personnes"]

    def test_jalon_et_empreintes_immuables(self):
        p, a = self.persons, self.biblio
        self.assertGreaterEqual(len(p["authorities"]), 1432)
        self.assertGreaterEqual(len(a["articles"]), 2208)
        self.assertGreaterEqual(len(a["contributions"]), 3778)
        self.assertEqual(fingerprint(p["authorities"][1402:1432]), FINGERPRINTS["people"])
        self.assertEqual(fingerprint(a["articles"][2193:2208]), FINGERPRINTS["articles"])
        self.assertEqual(fingerprint(a["contributions"][3738:3778]), FINGERPRINTS["relations"])
        self.assertEqual(a["source_sha256"], SOURCE_SHA256)

    def test_autorites_identifiants_et_conservation_adlfi(self):
        p = self.persons
        new = p["authorities"][1402:1432]
        self.assertEqual([x["id"] for x in new],
                         [f"PER-{i:06d}" for i in range(1403, 1433)])
        self.assertTrue(all(x["contributions_count"] == 0 and not x["name_variants"]
                            for x in new))
        self.assertEqual(len({x["identifiers"]["idref"] for x in p["authorities"]}),
                         len(p["authorities"]))
        self.assertEqual(len({x["id"] for x in p["authorities"]}), len(p["authorities"]))
        self.assertEqual(len(p["contributions"]), 1980)
        self.assertEqual(p["totals"], {"authorities": len(p["authorities"]),
                                      "contributions": 1980, "notices": 1779})
        pids = {x["id"] for x in new}
        self.assertFalse(any(c["person_id"] in pids for c in p["contributions"]))
        self.assertEqual(sum(len(x["identifiers"]) for x in new), 59)

    def test_articles_roles_et_reemplois(self):
        p, a = self.persons, self.biblio
        new_articles = a["articles"][2193:2208]
        new_links = a["contributions"][3738:3778]
        self.assertEqual(Counter(x["journal"] for x in new_articles),
                         {"gallia": 3, "gallia_prehistoire": 12})
        self.assertEqual(Counter(x["role"] for x in new_links),
                         {"auteur": 30, "collaborateur": 10})
        newids = {x["id"] for x in new_articles}
        affected = {x["article_id"] for x in new_links}
        self.assertEqual(len(affected), 39)
        self.assertEqual(len(affected & newids), 15)
        self.assertEqual(len(affected - newids), 24)
        self.assertEqual(len({x["person_id"] for x in new_links}), 30)
        self.assertTrue(all(x["doi"] and x["url"] and x["first_page"]
                            and x["last_page"] for x in new_articles))
        self.assertEqual(len({x["doi"] for x in a["articles"] if x.get("doi")}),
                         sum(bool(x.get("doi")) for x in a["articles"]))
        self.assertEqual(len({x["url"] for x in a["articles"] if x.get("url")}),
                         sum(bool(x.get("url")) for x in a["articles"]))
        pids = {x["id"] for x in p["authorities"]}
        aids = {x["id"] for x in a["articles"]}
        triples = [(x["article_id"], x["person_id"], x["role"]) for x in a["contributions"]]
        self.assertEqual(len(triples), len(set(triples)))
        self.assertTrue(all(article in aids and person in pids for article, person, _ in triples))
        self.assertEqual(a["totals"], {"articles": len(a["articles"]),
                                      "contributions": len(a["contributions"]),
                                      "authorities": len({x["person_id"] for x in a["contributions"]})})

    def test_manifest(self):
        m, p, a = self.manifest, self.persons, self.biblio
        self.assertEqual(m["autorites_validees"], len(p["authorities"]))
        self.assertEqual(m["contributions_adlfi"], 1980)
        self.assertEqual(m["notices_adlfi"], 1779)
        b = m["articles_lies"]
        self.assertEqual((b["articles"], b["contributions"], b["autorites_reliees"]),
                         (len(a["articles"]), len(a["contributions"]), a["totals"]["authorities"]))
        roles = Counter(x["role"] for x in a["contributions"])
        self.assertEqual((b["auteurs"], b["collaborateurs"]),
                         (roles["auteur"], roles["collaborateur"]))
        self.assertEqual(b["par_revue"], dict(Counter(x["journal"] for x in a["articles"])))


if __name__ == "__main__":
    unittest.main()
