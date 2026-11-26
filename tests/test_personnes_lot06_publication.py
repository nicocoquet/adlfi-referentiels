"""Non-régression du lot 06 du référentiel Personnes AdlFI.
Seuils historiques compatibles avec les enrichissements futurs.
"""
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOT06 = {f"PER-{i:06d}" for i in range(133, 163)}

class TestPersonnesLot06(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/data/personnes.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))
        cls.a = cls.data["authorities"]
        cls.c = cls.data["contributions"]

    def test_effectifs_manifest(self):
        self.assertGreaterEqual(len(self.a), 162)
        self.assertGreaterEqual(len(self.c), 1842)
        handles = {x["handle"] for x in self.c}
        self.assertGreaterEqual(len(handles), 1688)
        self.assertEqual(self.data["totals"], {
            "authorities": len(self.a), "contributions": len(self.c), "notices": len(handles),
        })
        m = self.manifest["modules"]["personnes"]
        self.assertEqual((m["autorites_validees"], m["contributions_adlfi"], m["notices_adlfi"]),
                         (len(self.a), len(self.c), len(handles)))

    def test_unicite_identifiants(self):
        per = [x["id"] for x in self.a]
        self.assertEqual(len(per), len(set(per)))
        self.assertTrue(LOT06.issubset(per))
        self.assertEqual(len({x["identifiers"]["idref"] for x in self.a}), len(self.a))
        self.assertEqual(len({(x["person_id"], x["handle"]) for x in self.c}), len(self.c))

    def test_lot06_contributions_roles(self):
        lot = [x for x in self.c if x["person_id"] in LOT06]
        self.assertEqual(len(lot), 140)
        self.assertEqual(Counter(tuple(x["roles"]) for x in lot),
                         {("aut", "fld"): 82, ("aut",): 58})
        self.assertEqual(len({x["handle"] for x in lot}), 133)

    def test_reunions_de_notices(self):
        old = [x for x in self.c if int(x["person_id"].split("-")[1]) <= 132]
        new = [x for x in self.c if x["person_id"] in LOT06]
        oldh = {x["handle"] for x in old}
        newh = {x["handle"] for x in new}
        self.assertEqual(len(old), 1702)
        self.assertEqual(len(oldh), 1590)
        self.assertEqual(len(oldh & newh), 35)
        self.assertEqual(len(newh - oldh), 98)

    def test_aucun_champ_interne_dans_projection(self):
        private = {"id_mention_xml", "source_xml", "sha256_preuve_tei",
                   "reference_visa", "publication_autorisee", "erratum_lot06"}
        self.assertFalse(private.intersection(self.data))
        self.assertTrue(all(not private.intersection(x) for x in self.a+self.c))

if __name__ == "__main__":
    unittest.main()
