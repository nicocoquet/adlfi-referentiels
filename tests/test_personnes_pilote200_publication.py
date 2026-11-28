"""Garde-fous permanents : cinquième lot Heurist Gallia / Gallia Préhistoire."""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "docs/data/personnes.json"
B = ROOT / "docs/data/personnes-articles.json"
M = ROOT / "docs/data/manifest.json"

# Empreintes des listes publiques antérieures au cinquième lot.
FIRST_602_PPN_SHA256 = "926d8871230d197d986fd8a5f740cb50cfa3b5938d2d62424dbd1b7b86236b25"
FIRST_1286_ARTICLES_SHA256 = "ab0f8e7187666723a07a2ae1fe81d2c1c29d3713dd7f2b40810c994c9a60a47c"

def digest(values):
    value = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

class PublicationPilote200(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(P.read_text(encoding="utf-8"))
        cls.b = json.loads(B.read_text(encoding="utf-8"))
        cls.m = json.loads(M.read_text(encoding="utf-8"))["modules"]["personnes"]

    def test_jalon_public_et_conservation(self):
        self.assertGreaterEqual(len(self.p["authorities"]), 802)
        self.assertGreaterEqual(len(self.b["articles"]), 1518)
        self.assertGreaterEqual(len(self.b["contributions"]), 2439)
        self.assertEqual(self.p["totals"]["contributions"], 1980)
        self.assertEqual(self.p["totals"]["notices"], 1779)
        self.assertEqual(len(self.p["contributions"]), 1980)
        self.assertEqual(digest([p["identifiers"]["idref"] for p in self.p["authorities"][:602]]),
                         FIRST_602_PPN_SHA256)
        self.assertEqual(digest([a["id"] for a in self.b["articles"][:1286]]),
                         FIRST_1286_ARTICLES_SHA256)

    def test_identifiants_et_articles_du_lot(self):
        new = self.p["authorities"][602:802]
        self.assertEqual([x["id"] for x in new],
                         [f"PER-{i:06d}" for i in range(603,803)])
        self.assertTrue(all(x["contributions_count"] == 0 for x in new))
        self.assertEqual(sum(bool(x["name_variants"]) for x in new), 25)
        self.assertEqual(len({x["identifiers"]["idref"] for x in self.p["authorities"]}),
                         len(self.p["authorities"]))
        newa = self.b["articles"][1286:1518]
        self.assertEqual(Counter(a["journal"] for a in newa),
                         {"gallia": 63, "gallia_prehistoire": 169})
        self.assertEqual(sum(not a["doi"] for a in newa), 102)
        self.assertEqual(sum(not a["url"] for a in newa), 1)
        self.assertEqual(len({x["id"] for x in self.b["articles"]}),
                         len(self.b["articles"]))

    def test_roles_et_integrite_des_relations(self):
        newids = {f"PER-{i:06d}" for i in range(603,803)}
        links = self.b["contributions"][1960:2439]
        self.assertEqual(len(links), 479)
        self.assertEqual(Counter(c["role"] for c in links),
                         {"auteur": 419, "collaborateur": 60})
        self.assertEqual(len({c["article_id"] for c in links}), 413)
        self.assertTrue(all(c["person_id"] in newids for c in links))
        article_ids = {a["id"] for a in self.b["articles"]}
        person_ids = {p["id"] for p in self.p["authorities"]}
        self.assertTrue(all(c["article_id"] in article_ids and c["person_id"] in person_ids
                            for c in self.b["contributions"]))
        self.assertEqual(len({(c["article_id"], c["person_id"], c["role"])
                              for c in self.b["contributions"]}),
                         len(self.b["contributions"]))
        self.assertEqual(self.b["totals"]["authorities"],
                         len({c["person_id"] for c in self.b["contributions"]}))
        self.assertEqual(self.m["articles_lies"]["articles"], self.b["totals"]["articles"])
        self.assertEqual(self.m["articles_lies"]["contributions"],
                         self.b["totals"]["contributions"])
        self.assertEqual(self.m["autorites_validees"],
                         self.p["totals"]["authorities"])

    def test_aucun_champ_interne(self):
        as_text = json.dumps({"p": self.p, "b": self.b}, ensure_ascii=False)
        for key in ["heurist_person_id", "rec_ID", "source_person_record_id",
                    "source_field_id", "private_source_field", "strate_technique"]:
            self.assertNotIn('"'+key+'"', as_text)

if __name__ == "__main__":
    unittest.main()
