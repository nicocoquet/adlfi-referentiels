"""Recette autonome 1.59 : activités consolidées et invariants de publication.

Ces tests portent sur le JSON courant. La comparaison exhaustive 1.58 → 1.59
des 35 cellules OOXML reste un contrôle distinct, exécuté avant publication.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "AdlFI_referentiel_1-59_activites_CANDIDAT.xlsx"
SOURCE_SHA256 = "3926b703b9e0fb20d3ed09068282ca97ea718eff14659ba8e3692b2cae0fe53e"

# Trente-trois passages documentés de non renseigné à actif.
BECOME_ACTIVE = {
    "ORG-0103", "ORG-0110", "ORG-0113", "ORG-0122", "ORG-0144",
    "ORG-0172", "ORG-0175", "ORG-0177", "ORG-0180", "ORG-0206",
    "ORG-0236", "ORG-0237", "ORG-0269", "ORG-0271", "ORG-0314",
    "ORG-0315", "ORG-0326", "ORG-0334", "ORG-0412", "ORG-0414",
    "ORG-0424", "ORG-0425", "ORG-0426", "ORG-0427", "ORG-0428",
    "ORG-0429", "ORG-0434", "ORG-0442", "ORG-0448", "ORG-0497",
    "ORG-0498", "ORG-0527", "ORG-0534",
}


class Publication159Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/data/organismes.json").read_text(encoding="utf-8"))
        cls.by_id = {a["id"]: a for a in cls.data["authorities"]}

    def test_provenance_exacte(self):
        self.assertEqual(self.data["provenance"]["source_filename"], SOURCE)
        self.assertEqual(self.data["provenance"]["source_sha256"], SOURCE_SHA256)

    def test_effectifs_et_catalogue_conserves(self):
        d = self.data
        self.assertEqual((d["totals"]["authorities"], d["totals"]["organismes"],
                          d["totals"]["services"]), (935, 735, 200))
        self.assertEqual((d["totals"]["catalog_included"], d["totals"]["catalog_excluded"]),
                         (683, 252))
        self.assertEqual(len(self.by_id), 935)
        self.assertEqual(len(d["relations"]), 600)
        self.assertEqual(len({r["id"] for r in d["relations"]}), 600)
        self.assertTrue(all(r["source"] in self.by_id and r["target"] in self.by_id
                            for r in d["relations"]))

    def test_statuts_d_activite_159(self):
        statuses = {True: 0, False: 0, None: 0}
        for authority in self.data["authorities"]:
            status = authority["activity"]["active"]
            self.assertIn(status, statuses)
            statuses[status] += 1
        self.assertEqual(statuses, {True: 709, False: 141, None: 85})
        self.assertEqual(len(BECOME_ACTIVE), 33)
        for ident in BECOME_ACTIVE:
            with self.subTest(ident=ident):
                self.assertIs(self.by_id[ident]["activity"]["active"], True)
        self.assertIs(self.by_id["ORG-0445"]["activity"]["active"], False)

    def test_date_fin_et_historiques(self):
        self.assertEqual(self.by_id["ORG-0503"]["activity"]["end"], "2008")
        org_histories = sum(len(a["names"]["history"]) for a in self.data["authorities"]
                            if a["kind"] == "ORG")
        ser_histories = sum(len(a["names"]["history"]) for a in self.data["authorities"]
                            if a["kind"] == "SER")
        self.assertEqual((org_histories, ser_histories), (143, 96))
        self.assertEqual(self.data["totals"]["service_sector_resolution"],
                         {"prive": 3, "public": 197})
        self.assertEqual(self.data["totals"]["service_level_unresolved_ids"],
                         ["SER-0178", "SER-0202"])


if __name__ == "__main__":
    unittest.main()
