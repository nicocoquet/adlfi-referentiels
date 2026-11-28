"""Non-régression du troisième pilote Heurist de 120 autorités (visa 2026-11-28).

Contrôle de la projection publique uniquement ; source brute et matrices privées exclues.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = "de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051"
AUTH_SHA256 = "630f4a55d01d8f22cb83785270d91fc2ae6caeae583f3f4ead6dcceee5307a99"
ART_SHA256 = "32520c1b0ca5926fd73dac847fe29e0e05e4352fbf096d6fc806a05af8a428fe"
LINK_SHA256 = "9d2b0fc0e4fabf682ceb56c4142f8613e41a65ef43c7fcb80a304e822735d2be"


def fingerprint(obj):
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def ppn_valid(ppn):
    if not re.fullmatch(r"[0-9]{8}[0-9X]", ppn):
        return False
    digits = [10 if c == "X" else int(c) for c in ppn]
    return sum(d * (9-i) for i, d in enumerate(digits)) % 11 == 0


class TestTroisiemePiloteHeuristPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persons = json.loads((ROOT / "docs/data/personnes.json").read_text(encoding="utf-8"))
        cls.works = json.loads((ROOT / "docs/data/personnes-articles.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))

    def test_120_per_sans_relation_adlfi(self):
        group = self.persons["authorities"][322:442]
        self.assertEqual(len(group), 120)
        self.assertEqual([x["id"] for x in group],
                         [f"PER-{i:06d}" for i in range(323, 443)])
        self.assertEqual(fingerprint(group), AUTH_SHA256)
        self.assertEqual({x["contributions_count"] for x in group}, {0})
        self.assertEqual(sum(bool(x["name_variants"]) for x in group), 18)
        self.assertEqual(sum(len(x["name_variants"]) > 1 for x in group), 0)
        self.assertTrue(all(x["name"] and x["family_name"] and
                            x["name_idref"] == "" for x in group))
        self.assertTrue(all(ppn_valid(x["identifiers"]["idref"]) for x in group))
        allowed = {"id", "name", "family_name", "name_idref",
                   "identifiers", "contributions_count", "name_variants"}
        self.assertTrue(all(set(x) == allowed for x in group))

    def test_343_articles_nouveaux_et_lacunes_conservees(self):
        new = self.works["articles"][592:935]
        self.assertEqual(len(new), 343)
        self.assertEqual(fingerprint(new), ART_SHA256)
        self.assertEqual(Counter(x["journal"] for x in new),
                         {"gallia": 218, "gallia_prehistoire": 125})
        self.assertEqual(sum(x["doi"] is None for x in new), 150)
        self.assertEqual(sum(x["url"] is None for x in new), 6)
        self.assertEqual(sum(not x["first_page"] or not x["last_page"] for x in new), 3)
        self.assertEqual(new[0]["id"].startswith("heurist:1519:73:"), True)
        allowed = {"id", "journal", "title", "year", "volume",
                   "first_page", "last_page", "url", "doi"}
        self.assertTrue(all(set(x) == allowed for x in new))

    def test_498_liens_roles_et_articles_reutilises(self):
        links = self.works["contributions"][911:1409]
        self.assertEqual(len(links), 498)
        self.assertEqual(fingerprint(links), LINK_SHA256)
        self.assertEqual(Counter(x["role"] for x in links),
                         {"auteur": 444, "collaborateur": 54})
        new_per = {f"PER-{i:06d}" for i in range(323, 443)}
        self.assertEqual({x["person_id"] for x in links}, new_per)
        used = {x["article_id"] for x in links}
        old_articles = {x["id"] for x in self.works["articles"][:592]}
        self.assertEqual(len(used), 450)
        self.assertEqual(len(used & old_articles), 107)
        self.assertEqual(len(used - old_articles), 343)
        self.assertTrue(all(type(x["position_in_role"]) is int and
                            x["position_in_role"] > 0 for x in links))
        self.assertTrue(all(set(x) == {"article_id", "person_id",
                                      "role", "position_in_role"} for x in links))

    def test_integrite_globale_les_roles_et_l_unicite(self):
        p, a = self.persons, self.works
        self.assertEqual((p["schema_version"], a["schema_version"]), ("0.5.0", "0.1.0"))
        self.assertEqual((p["publication_status"], a["publication_status"]),
                         ("PUBLIC_PILOT", "PUBLIC_PILOT"))
        self.assertEqual(a["source_sha256"], SOURCE_SHA256)
        per_ids = {x["id"] for x in p["authorities"]}
        article_ids = {x["id"] for x in a["articles"]}
        self.assertEqual(len(per_ids), len(p["authorities"]))
        self.assertEqual(len(article_ids), len(a["articles"]))
        for key in ("idref", "bnf", "orcid", "idhal", "persee", "wikidata"):
            values = [x["identifiers"][key] for x in p["authorities"]
                      if x["identifiers"].get(key)]
            self.assertEqual(len(values), len(set(values)), key)
            self.assertNotIn("####", values)
        for key in ("url", "doi"):
            values = [x[key] for x in a["articles"] if x.get(key)]
            self.assertEqual(len(values), len(set(values)), key)
        signatures = set()
        for row in a["contributions"]:
            self.assertIn(row["person_id"], per_ids)
            self.assertIn(row["article_id"], article_ids)
            self.assertIn(row["role"], {"auteur", "collaborateur"})
            signature = (row["person_id"], row["article_id"], row["role"])
            self.assertNotIn(signature, signatures)
            signatures.add(signature)

    def test_zero_adlfi_et_parite_manifeste(self):
        p, a = self.persons, self.works
        self.assertGreaterEqual(p["totals"]["authorities"], 442)
        self.assertEqual(p["totals"]["contributions"], 1980)
        self.assertEqual(p["totals"]["notices"], 1779)
        self.assertGreaterEqual(a["totals"]["articles"], 935)
        self.assertGreaterEqual(a["totals"]["contributions"], 1409)
        self.assertGreaterEqual(a["totals"]["authorities"], 433)
        new_per = {f"PER-{i:06d}" for i in range(323, 443)}
        self.assertFalse(new_per & {x["person_id"] for x in p["contributions"]})
        self.assertTrue(new_per <= {x["person_id"] for x in a["contributions"]})
        m = self.manifest["modules"]["personnes"]
        b = m["articles_lies"]
        self.assertEqual([m["autorites_validees"], m["contributions_adlfi"],
                          m["notices_adlfi"]],
                         [p["totals"][k] for k in ("authorities", "contributions", "notices")])
        self.assertEqual([b["articles"], b["contributions"], b["autorites_reliees"]],
                         [a["totals"][k] for k in ("articles", "contributions", "authorities")])
        self.assertEqual(b["par_revue"],
                         dict(Counter(x["journal"] for x in a["articles"])))
        self.assertEqual(b["auteurs"],
                         sum(x["role"] == "auteur" for x in a["contributions"]))
        self.assertEqual(b["collaborateurs"],
                         sum(x["role"] == "collaborateur" for x in a["contributions"]))


if __name__ == "__main__":
    unittest.main()
