"""Non-régression du deuxième pilote Heurist Gallia / Gallia Préhistoire (80 PER).

Visa du dossier prépublication du 28 novembre 2026 ; seules les données
bibliographiques publiques et les alignements validés sont vérifiés.
Les sources nominatives de recette et les liens d'évaluation restent privés.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = "de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051"
AUTH_SHA256 = "0ab2d44606675e08ca31908449f21bda9ec00e9258850b70bb4dbe43ec738a9d"
ART_SHA256 = "3c03609cd94de6816ec2dab6fecae9440ec056e947f27944f7b4d5e2770fc2bb"
LINK_SHA256 = "a5ca244539eeb0182fe6e4b7259da0f19fc8574ee6f32cc45227d439c4c0fde9"


def fingerprint(value):
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def ppn_mod11_valid(ppn):
    if not re.fullmatch(r"[0-9]{8}[0-9X]", ppn):
        return False
    digits = [int(x) if x != "X" else 10 for x in ppn]
    return sum(value * (len(digits) - i) for i, value in enumerate(digits)) % 11 == 0


class TestHeuristPilote80Publication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persons = json.loads((ROOT / "docs/data/personnes.json").read_text(encoding="utf-8"))
        cls.works = json.loads((ROOT / "docs/data/personnes-articles.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))

    def test_80_autorites_visa_et_ids_stables(self):
        new = self.persons["authorities"][242:322]
        self.assertEqual(len(new), 80)
        self.assertEqual([x["id"] for x in new],
                         [f"PER-{i:06d}" for i in range(243, 323)])
        self.assertEqual(fingerprint(new), AUTH_SHA256)
        self.assertEqual({x["contributions_count"] for x in new}, {0})
        self.assertEqual(sum(bool(x["name_variants"]) for x in new), 14)
        self.assertTrue(all(x["name"] and x["family_name"] and
                            x["name_idref"] == "" for x in new))
        self.assertTrue(all(ppn_mod11_valid(x["identifiers"]["idref"]) for x in new))
        allowed = {"id", "name", "family_name", "name_idref",
                   "identifiers", "contributions_count", "name_variants"}
        self.assertTrue(all(set(x) == allowed for x in new))

    def test_191_articles_nouveaux_et_integrite(self):
        new = self.works["articles"][401:592]
        self.assertEqual(len(new), 191)
        self.assertEqual(fingerprint(new), ART_SHA256)
        self.assertEqual(Counter(x["journal"] for x in new),
                         {"gallia": 107, "gallia_prehistoire": 84})
        self.assertEqual(sum(x["doi"] is None for x in new), 28)
        self.assertEqual(sum(x["url"] is None for x in new), 1)
        self.assertEqual([x["id"] for x in new if x["url"] is None],
                         ["heurist:1519:73:4790"])
        allowed = {"id", "journal", "title", "year", "volume",
                   "first_page", "last_page", "url", "doi"}
        self.assertTrue(all(set(x) == allowed for x in new))

    def test_333_liens_auteur_collaborateur(self):
        links = self.works["contributions"][578:911]
        self.assertEqual(len(links), 333)
        self.assertEqual(fingerprint(links), LINK_SHA256)
        self.assertEqual(Counter(x["role"] for x in links),
                         {"auteur": 295, "collaborateur": 38})
        new_per = {f"PER-{i:06d}" for i in range(243, 323)}
        self.assertEqual({x["person_id"] for x in links}, new_per)
        self.assertEqual(len({x["article_id"] for x in links}), 286)
        previous = {x["id"] for x in self.works["articles"][:401]}
        self.assertEqual(len({x["article_id"] for x in links} & previous), 95)
        self.assertEqual(len({x["article_id"] for x in links} - previous), 191)
        self.assertTrue(all(x["position_in_role"] > 0 for x in links))
        self.assertTrue(all(set(x) == {"article_id", "person_id",
                                      "role", "position_in_role"} for x in links))

    def test_identifiants_articles_et_liens_uniques(self):
        p, a = self.persons, self.works
        self.assertEqual(p["schema_version"], "0.5.0")
        self.assertEqual(a["schema_version"], "0.1.0")
        self.assertEqual(p["publication_status"], "PUBLIC_PILOT")
        self.assertEqual(a["publication_status"], "PUBLIC_PILOT")
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
        keys = set()
        for row in a["contributions"]:
            self.assertIn(row["person_id"], per_ids)
            self.assertIn(row["article_id"], article_ids)
            self.assertIn(row["role"], {"auteur", "collaborateur"})
            signature = (row["person_id"], row["article_id"], row["role"])
            self.assertNotIn(signature, keys)
            keys.add(signature)

    def test_zero_adlfi_et_comptages_mis_a_jour(self):
        p, a = self.persons, self.works
        self.assertGreaterEqual(p["totals"]["authorities"], 322)
        self.assertEqual(p["totals"]["contributions"], 1980)
        self.assertEqual(p["totals"]["notices"], 1779)
        self.assertGreaterEqual(a["totals"]["articles"], 592)
        self.assertGreaterEqual(a["totals"]["contributions"], 911)
        self.assertGreaterEqual(a["totals"]["authorities"], 313)
        new_per = {f"PER-{i:06d}" for i in range(243, 323)}
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
