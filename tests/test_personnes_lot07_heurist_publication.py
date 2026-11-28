"""Lot 07 Heurist : non-régression et publication publique contrôlée.

Les matrices privées et identifiants internes Heurist ne sont pas publiés.
Les empreintes canoniques portent uniquement sur les blocs publics ajoutés.
Les lots précédents restent également protégés par leurs propres tests.
"""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = {
    "people": "9654f6b1219d44e70bf5d29866d7c9f3b1e67de5aca5ea0b4ce39c6d991a3b87",
    "articles": "368f9446a96486adad513d4c6cbf76b3659f9723fb8f2f3e00408d967b163317",
    "relations": "1ce8f48443199a7a2e0da59478fee24a088e9b13aee9d661d4722f8875769b1d",
}
SOURCE = "de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051"


def fingerprint(rows):
    text = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def valid_ppn(ppn):
    return (
        isinstance(ppn, str)
        and len(ppn) == 9
        and ppn[:8].isdigit()
        and (ppn[8].isdigit() or ppn[8] == "X")
        and sum((10 if ch == "X" else int(ch)) * (9-i)
                for i, ch in enumerate(ppn)) % 11 == 0
    )


class TestPublicationHeuristLot07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads((ROOT / "docs/data/personnes.json").read_text(encoding="utf-8"))
        cls.a = json.loads((ROOT / "docs/data/personnes-articles.json").read_text(encoding="utf-8"))
        cls.m = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))["modules"]["personnes"]

    def test_jalon_et_empreintes_canoniques(self):
        p, a = self.p, self.a
        self.assertGreaterEqual(len(p["authorities"]), 1202)
        self.assertGreaterEqual(len(a["articles"]), 2103)
        self.assertGreaterEqual(len(a["contributions"]), 3477)
        self.assertEqual(fingerprint(p["authorities"][1002:1202]), SNAPSHOT["people"])
        self.assertEqual(fingerprint(a["articles"][1755:2103]), SNAPSHOT["articles"])
        self.assertEqual(fingerprint(a["contributions"][2891:3477]), SNAPSHOT["relations"])
        self.assertEqual(a["source_sha256"], SOURCE)

    def test_autorites_et_conservation_adlfi(self):
        persons = self.p["authorities"][1002:1202]
        self.assertEqual([x["id"] for x in persons],
                         [f"PER-{i:06d}" for i in range(1003, 1203)])
        self.assertEqual((persons[0]["name"], persons[0]["identifiers"]["idref"]),
                         ("Guillaume Asselin", "24997472X"))
        self.assertEqual((persons[-1]["name"], persons[-1]["identifiers"]["idref"]),
                         ("Sandrine Paradis-Grenouillet", "176957502"))
        self.assertEqual(sum(bool(x["name_variants"]) for x in persons), 8)
        self.assertTrue(all(v["kind"] == "autre_forme_attestee"
                            for x in persons for v in x["name_variants"]))
        self.assertTrue(all(x["contributions_count"] == 0 for x in persons))
        all_ids = [x["id"] for x in self.p["authorities"]]
        all_ppns = [x["identifiers"]["idref"] for x in self.p["authorities"]]
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertEqual(len(all_ppns), len(set(all_ppns)))
        self.assertTrue(all(valid_ppn(x["identifiers"]["idref"]) for x in persons))
        self.assertEqual(self.p["totals"]["contributions"], 1980)
        self.assertEqual(self.p["totals"]["notices"], 1779)
        self.assertEqual(len(self.p["contributions"]), 1980)
        new_ids = set(x["id"] for x in persons)
        self.assertFalse(any(c["person_id"] in new_ids for c in self.p["contributions"]))

    def test_articles_relations_roles_et_lacunes(self):
        a = self.a
        new_articles = a["articles"][1755:2103]
        new_links = a["contributions"][2891:3477]
        self.assertEqual(Counter(x["journal"] for x in new_articles),
                         {"gallia": 319, "gallia_prehistoire": 29})
        self.assertEqual(Counter(x["role"] for x in new_links),
                         {"auteur": 545, "collaborateur": 41})
        affected = {x["article_id"] for x in new_links}
        self.assertEqual(len(affected), 530)
        old_ids = {x["id"] for x in a["articles"][:1755]}
        self.assertEqual(len(affected & old_ids), 182)
        self.assertEqual(sum(not x["doi"] for x in new_articles), 141)
        self.assertTrue(all(x["url"] and x["url"].startswith("https://")
                            for x in new_articles))
        self.assertTrue(all(x["first_page"] is not None and x["last_page"] is not None
                            for x in new_articles))
        self.assertEqual(len({x["id"] for x in new_articles}), 348)
        person_ids = {x["id"] for x in self.p["authorities"]}
        article_ids = {x["id"] for x in a["articles"]}
        triples = [(x["article_id"], x["person_id"], x["role"]) for x in a["contributions"]]
        self.assertEqual(len(triples), len(set(triples)))
        self.assertTrue(all(art_id in article_ids and per_id in person_ids
                            for art_id, per_id, _ in triples))
        dois = [x["doi"] for x in a["articles"] if x["doi"]]
        urls = [x["url"] for x in a["articles"] if x["url"]]
        self.assertEqual(len(dois), len(set(dois)))
        self.assertEqual(len(urls), len(set(urls)))
        self.assertEqual(a["totals"], {"articles": len(a["articles"]),
                                      "contributions": len(a["contributions"]),
                                      "authorities": len({x["person_id"] for x in a["contributions"]})})

    def test_manifeste_et_exclusion_des_champs_prives(self):
        p, a, m = self.p, self.a, self.m
        self.assertEqual((m["autorites_validees"], m["contributions_adlfi"], m["notices_adlfi"]),
                         (p["totals"]["authorities"], 1980, 1779))
        linked = m["articles_lies"]
        self.assertEqual((linked["articles"], linked["contributions"], linked["autorites_reliees"]),
                         (a["totals"]["articles"], a["totals"]["contributions"], a["totals"]["authorities"]))
        self.assertEqual(dict(Counter(x["role"] for x in a["contributions"])),
                         {"auteur": linked["auteurs"], "collaborateur": linked["collaborateurs"]})
        self.assertEqual(dict(Counter(x["journal"] for x in a["articles"])), linked["par_revue"])
        forbidden = {"heurist_person_id", "heurist_article_id", "source_field_id",
                     "source_person_record_id", "rec_ID", "visa_identite",
                     "visa_alignements", "visa_relation", "visa_bibliographie",
                     "expert", "evaluateur", "strate_technique", "per_propose"}
        for block in (p["authorities"][1002:1202], a["articles"][1755:2103],
                      a["contributions"][2891:3477]):
            self.assertTrue(all(not forbidden.intersection(row.keys()) for row in block))


if __name__ == "__main__":
    unittest.main()
