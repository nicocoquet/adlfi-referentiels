"""Lot 06 Heurist : verrouillage du visa et de la publication append-only.

Ce test ne contient pas les matrices privées Heurist ni les identifiants internes
des personnes. Les empreintes canoniques assurent que les 200 autorités, 237 articles
et 452 relations effectivement publiés correspondent à la projection visée.
"""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PEOPLE = ROOT / "docs/data/personnes.json"
ARTICLES = ROOT / "docs/data/personnes-articles.json"
MANIFEST = ROOT / "docs/data/manifest.json"

SNAPSHOT = {
    "people": "b9d6fc885160987692269e5ab59876a7253fdfe5eb9e740bd0757cea68a7cd6e",
    "articles": "50dd78e4e653a60efa2a6f67a573ea3a23cd90261e85ee62a4a27ec7ddff85bc",
    "relations": "dd2da90a342a7ccd825bafab97adff8ff89144042b70411d11fb9404961c62a5",
}
SOURCE = "de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051"


def canonical_sha256(rows):
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def valid_ppn(ppn):
    if not isinstance(ppn, str) or len(ppn) != 9 or not ppn[:8].isdigit():
        return False
    if not (ppn[8].isdigit() or ppn[8] == "X"):
        return False
    return sum((10 if char == "X" else int(char)) * (9 - i)
               for i, char in enumerate(ppn)) % 11 == 0


class TestPublicationHeuristLot06(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PEOPLE.read_text(encoding="utf-8"))
        cls.a = json.loads(ARTICLES.read_text(encoding="utf-8"))
        cls.m = json.loads(MANIFEST.read_text(encoding="utf-8"))["modules"]["personnes"]

    def test_jalon_append_only_et_empreintes(self):
        p, a = self.p, self.a
        self.assertGreaterEqual(len(p["authorities"]), 1002)
        self.assertGreaterEqual(len(a["articles"]), 1755)
        self.assertGreaterEqual(len(a["contributions"]), 2891)
        self.assertEqual(canonical_sha256(p["authorities"][802:1002]), SNAPSHOT["people"])
        self.assertEqual(canonical_sha256(a["articles"][1518:1755]), SNAPSHOT["articles"])
        self.assertEqual(canonical_sha256(a["contributions"][2439:2891]), SNAPSHOT["relations"])
        self.assertEqual(a["source_sha256"], SOURCE)

    def test_identites_et_adlfi(self):
        p = self.p
        lot = p["authorities"][802:1002]
        self.assertEqual(
            [x["id"] for x in lot],
            [f"PER-{i:06d}" for i in range(803, 1003)],
        )
        self.assertEqual((lot[0]["name"], lot[0]["identifiers"]["idref"]),
                         ("Jean Le Gall", "032843410"))
        self.assertEqual((lot[-1]["name"], lot[-1]["identifiers"]["idref"]),
                         ("Amable Audin", "068967926"))
        self.assertTrue(all(x["contributions_count"] == 0 for x in lot))
        self.assertEqual(sum(bool(x["name_variants"]) for x in lot), 25)
        self.assertTrue(all(v["kind"] == "autre_forme_attestee"
                            for x in lot for v in x["name_variants"]))
        all_ppn = [x["identifiers"]["idref"] for x in p["authorities"]]
        self.assertEqual(len(all_ppn), len(set(all_ppn)))
        self.assertTrue(all(valid_ppn(ppn) for ppn in all_ppn[802:1002]))
        self.assertEqual(p["totals"]["contributions"], 1980)
        self.assertEqual(p["totals"]["notices"], 1779)
        self.assertEqual(len(p["contributions"]), 1980)
        self.assertTrue(all(x["person_id"] not in {y["id"] for y in lot}
                            for x in p["contributions"]))

    def test_relations_articles_et_roles(self):
        art = self.a
        new_articles = art["articles"][1518:1755]
        new_links = art["contributions"][2439:2891]
        self.assertEqual(Counter(x["journal"] for x in new_articles),
                         {"gallia": 208, "gallia_prehistoire": 29})
        self.assertEqual(Counter(x["role"] for x in new_links),
                         {"auteur": 388, "collaborateur": 64})
        self.assertEqual(len({x["article_id"] for x in new_links}), 398)
        self.assertEqual(len({x["article_id"] for x in new_links}.intersection(
            {x["id"] for x in art["articles"][:1518]})), 161)
        self.assertEqual(sum(x["doi"] is None for x in new_articles), 72)
        self.assertTrue(all(x["url"] and x["url"].startswith("https://")
                            for x in new_articles))
        self.assertTrue(all(x["first_page"] is not None and x["last_page"] is not None
                            for x in new_articles))
        ids = {x["id"] for x in self.p["authorities"]}
        aids = {x["id"] for x in art["articles"]}
        triples = [(x["article_id"], x["person_id"], x["role"]) for x in art["contributions"]]
        self.assertEqual(len(triples), len(set(triples)))
        self.assertTrue(all(aid in aids and pid in ids
                            for aid, pid, _ in triples))
        self.assertEqual(art["totals"], {
            "articles": len(art["articles"]),
            "contributions": len(art["contributions"]),
            "authorities": len({x["person_id"] for x in art["contributions"]}),
        })

    def test_reserves_https_et_manifeste(self):
        articles = {x["id"]: x for x in self.a["articles"]}
        self.assertEqual(articles["heurist:1519:73:42134"]["url"],
                         "https://journals.openedition.org/galliap/668")
        self.assertEqual(articles["heurist:1519:73:42134"]["doi"],
                         "10.4000/galliap.668")
        self.assertEqual(articles["heurist:1519:73:42140"]["url"],
                         "https://journals.openedition.org/galliap/590")
        self.assertEqual(articles["heurist:1519:73:42140"]["doi"],
                         "10.4000/galliap.590")
        m, p, a = self.m, self.p, self.a
        self.assertEqual(m["autorites_validees"], p["totals"]["authorities"])
        self.assertEqual(m["contributions_adlfi"], p["totals"]["contributions"])
        self.assertEqual(m["notices_adlfi"], p["totals"]["notices"])
        b = m["articles_lies"]
        self.assertEqual(b["articles"], a["totals"]["articles"])
        self.assertEqual(b["contributions"], a["totals"]["contributions"])
        self.assertEqual(b["autorites_reliees"], a["totals"]["authorities"])
        self.assertEqual(Counter(x["role"] for x in a["contributions"]),
                         {"auteur": b["auteurs"], "collaborateur": b["collaborateurs"]})
        self.assertEqual(dict(Counter(x["journal"] for x in a["articles"])), b["par_revue"])


if __name__ == "__main__":
    unittest.main()
