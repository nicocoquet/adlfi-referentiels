"""Lot 08 Heurist : contrôle des 200 autorités, 90 articles et 261 relations.

La publication conserve strictement les lots antérieurs et ne contient aucune
matrice privée ni donnée d'expertise éditoriale.
"""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = {
    "people": "d32b8f2abc9da6b0f64f379bf05688772b5e6d93114a5625580f31ab128e6cf7",
    "articles": "273369ac7435171705ee17d14690214d132aec99a9c969855cf4c75aded63d28",
    "relations": "5c9c18b4f6d0d9a962ee49e2db527213d4a24d086fc38fb670d8a44f6ce03a97"
}
SOURCE = "de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051"


def fingerprint(rows):
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def valid_ppn(ppn):
    return (isinstance(ppn, str) and len(ppn) == 9 and ppn[:8].isdigit()
            and (ppn[8].isdigit() or ppn[8] == "X")
            and sum((10 if ch == "X" else int(ch)) * (9-i)
                    for i, ch in enumerate(ppn)) % 11 == 0)


class TestPublicationHeuristLot08(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads((ROOT / "docs/data/personnes.json").read_text(encoding="utf-8"))
        cls.a = json.loads((ROOT / "docs/data/personnes-articles.json").read_text(encoding="utf-8"))
        cls.m = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))["modules"]["personnes"]

    def test_jalon_et_empreintes_canoniques(self):
        p, a = self.p, self.a
        self.assertGreaterEqual(len(p["authorities"]), 1402)
        self.assertGreaterEqual(len(a["articles"]), 2193)
        self.assertGreaterEqual(len(a["contributions"]), 3738)
        self.assertEqual(fingerprint(p["authorities"][1202:1402]), SNAPSHOT["people"])
        self.assertEqual(fingerprint(a["articles"][2103:2193]), SNAPSHOT["articles"])
        self.assertEqual(fingerprint(a["contributions"][3477:3738]), SNAPSHOT["relations"])
        self.assertEqual(a["source_sha256"], SOURCE)

    def test_autorites_et_conservation_adlfi(self):
        persons = self.p["authorities"][1202:1402]
        self.assertEqual([x["id"] for x in persons], [f"PER-{i:06d}" for i in range(1203, 1403)])
        self.assertEqual((persons[0]["name"], persons[0]["identifiers"]["idref"]),
                         ("Benoît Mille", "184050375"))
        self.assertEqual((persons[-1]["name"], persons[-1]["identifiers"]["idref"]),
                         ("Richard Boudet", "030005108"))
        self.assertTrue(all(not x["name_variants"] and x["contributions_count"] == 0 for x in persons))
        all_ids = [x["id"] for x in self.p["authorities"]]
        all_ppns = [x["identifiers"]["idref"] for x in self.p["authorities"]]
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertEqual(len(all_ppns), len(set(all_ppns)))
        self.assertTrue(all(valid_ppn(x["identifiers"]["idref"]) for x in persons))
        self.assertEqual(self.p["totals"], {"authorities": len(self.p["authorities"]),
                                            "contributions": 1980, "notices": 1779})
        self.assertEqual(len(self.p["contributions"]), 1980)
        ids = set(x["id"] for x in persons)
        self.assertFalse(any(c["person_id"] in ids for c in self.p["contributions"]))

    def test_relations_articles_roles_et_lacunes(self):
        a = self.a
        articles = a["articles"][2103:2193]
        links = a["contributions"][3477:3738]
        self.assertEqual(Counter(x["journal"] for x in articles),
                         {"gallia": 83, "gallia_prehistoire": 7})
        self.assertEqual(Counter(x["role"] for x in links),
                         {"auteur": 241, "collaborateur": 20})
        affected = {x["article_id"] for x in links}
        self.assertEqual(len(affected), 222)
        self.assertEqual(len(affected & {x["id"] for x in a["articles"][:2103]}), 132)
        self.assertEqual(sum(not x["doi"] for x in articles), 17)
        self.assertEqual([x["id"] for x in articles if not x["url"]], ["heurist:1519:73:1026"])
        self.assertTrue(all(x["first_page"] is not None and x["last_page"] is not None
                            for x in articles))
        self.assertTrue(all(x["url"].startswith("https://") for x in articles if x["url"]))
        pids = {x["id"] for x in self.p["authorities"]}
        aids = {x["id"] for x in a["articles"]}
        triples = [(x["article_id"], x["person_id"], x["role"]) for x in a["contributions"]]
        self.assertEqual(len(triples), len(set(triples)))
        self.assertTrue(all(article in aids and person in pids for article, person, _ in triples))
        dois = [x["doi"] for x in a["articles"] if x["doi"]]
        urls = [x["url"] for x in a["articles"] if x["url"]]
        self.assertEqual(len(dois), len(set(dois)))
        self.assertEqual(len(urls), len(set(urls)))
        self.assertEqual(a["totals"], {"articles": len(a["articles"]),
                                        "contributions": len(a["contributions"]),
                                        "authorities": len({x["person_id"] for x in a["contributions"]})})

    def test_manifest_et_absence_de_donnees_privees(self):
        p, a, m = self.p, self.a, self.m
        self.assertEqual((m["autorites_validees"], m["contributions_adlfi"], m["notices_adlfi"]),
                         (len(p["authorities"]), 1980, 1779))
        linked = m["articles_lies"]
        self.assertEqual((linked["articles"], linked["contributions"], linked["autorites_reliees"]),
                         (a["totals"]["articles"], a["totals"]["contributions"], a["totals"]["authorities"]))
        self.assertEqual(dict(Counter(x["role"] for x in a["contributions"])),
                         {"auteur": linked["auteurs"], "collaborateur": linked["collaborateurs"]})
        self.assertEqual(dict(Counter(x["journal"] for x in a["articles"])), linked["par_revue"])
        forbidden = {"heurist_person_id", "heurist_article_id", "rec_ID", "source_person_record_id",
                     "source_article_record_id", "source_field_id", "reference_visa",
                     "visa_identite", "visa_alignements", "visa_relation", "visa_bibliographie",
                     "expert", "reviewer", "private_source_field"}
        public_rows = (p["authorities"][1202:1402] + a["articles"][2103:2193]
                       + a["contributions"][3477:3738])
        self.assertTrue(all(not forbidden.intersection(x) for x in public_rows))
        self.assertEqual(p["publication_status"], "PUBLIC_PILOT")
        self.assertEqual(a["publication_status"], "PUBLIC_PILOT")


if __name__ == "__main__":
    unittest.main()
