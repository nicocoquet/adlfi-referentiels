"""Contrôle de non-régression des preuves COG du lot 001 (aucune validation ARK)."""
import collections
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREUVES = ROOT / "docs/lieux/recette/lot-001-preuves-cog"
LOT = ROOT / "docs/lieux/recette/lot-001-prearbitrages.csv"


def csv_lignes(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


class PreuvesCOGLot001(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rapport = json.loads((PREUVES / "rapport_evenements_lot001.json").read_text(encoding="utf-8"))
        cls.codes = csv_lignes(PREUVES / "transitions_code_a_verifier.csv")
        cls.movements = csv_lignes(PREUVES / "evenements_communaux_particuliers.csv")
        cls.lot = csv_lignes(LOT)
        cls.par_ark = {row["ark"]: row for row in cls.lot}

    def test_effectifs_et_sources(self):
        self.assertEqual((len(self.lot), len(self.par_ark)), (100, 100))
        self.assertEqual(len(self.codes), self.rapport["transitions_codes_candidats"])
        self.assertEqual(len(self.codes), self.rapport["transitions_avec_evenement_direct_exact"])
        self.assertEqual(len(self.codes), 8)
        self.assertEqual(self.rapport["transitions_sans_evenement_direct_exact"], 0)
        self.assertEqual(len(self.movements), self.rapport["evenements_cog_releves_pour_deux_dossiers_speciaux"])
        self.assertEqual(len(self.movements), 15)
        self.assertEqual(self.rapport["lignes_evenements_source"], 13734)
        self.assertRegex(self.rapport["sources"]["v_mvt_commune_2026.csv"], r"^[0-9a-f]{64}$")

    def test_huit_changements_departement_attestes(self):
        for row in self.codes:
            with self.subTest(commune=row["libelle_documentaire"]):
                self.assertEqual(row["codes_MOD"], "41")
                self.assertEqual(row["nombre_evenements_exacts"], "1")
                self.assertEqual(row["statut_preuve"], "mouvement_cog_direct_atteste")
                self.assertEqual(row["statut_validation_pactols"], "non_valide")
                self.assertEqual(self.par_ark[row["ark_pactols"]]["code"], row["code_apres"])
                preuve = json.loads(row["preuve_lignes_cog"])
                self.assertEqual(len(preuve), 1)
                e = preuve[0]
                for col, attendu in {
                    "MOD": "41", "DATE_EFF": row["date_jointive"],
                    "TYPECOM_AV": "COM", "TYPECOM_AP": "COM",
                    "COM_AV": row["code_avant"], "COM_AP": row["code_apres"],
                }.items():
                    self.assertEqual(e[col], attendu)
                self.assertEqual(e["LIBELLE_AV"], e["LIBELLE_AP"])

    def test_quinze_lignes_trois_operations(self):
        repartition = collections.Counter(
            (x["dossier"], x["DATE_EFF"], x["MOD"]) for x in self.movements
        )
        self.assertEqual(repartition, {
            ("Allaines-Mervilliers", "2019-01-01", "32"): 6,
            ("Aigondigné", "2017-01-01", "32"): 4,
            ("Aigondigné", "2019-01-01", "32"): 5,
        })
        self.assertTrue(all(x["statut_validation_pactols"] == "non_valide" for x in self.movements))

    def test_allaines_distingue_statut_et_rattachement(self):
        ev = {(x["TYPECOM_AV"], x["COM_AV"], x["TYPECOM_AP"], x["COM_AP"])
              for x in self.movements if x["dossier"] == "Allaines-Mervilliers"}
        self.assertIn(("COM", "28002", "COMD", "28002"), ev)
        self.assertIn(("COM", "28002", "COM", "28199"), ev)
        self.assertIn(("COMA", "28244", "COM", "28199"), ev)

    def test_aigondigne_code_reemploye_pour_trois_noms(self):
        ev = {(x["DATE_EFF"], x["COM_AV"], x["LIBELLE_AV"], x["COM_AP"], x["LIBELLE_AP"])
              for x in self.movements if x["dossier"] == "Aigondigné"}
        self.assertIn(("2017-01-01", "79185", "Mougon", "79185", "Mougon-Thorigné"), ev)
        self.assertIn(("2019-01-01", "79185", "Mougon-Thorigné", "79185", "Aigondigné"), ev)
        self.assertIn(("2019-01-01", "79004", "Aigonnay", "79185", "Aigondigné"), ev)
        self.assertIn(("2019-01-01", "79240", "Sainte-Blandine", "79185", "Aigondigné"), ev)

    def test_pas_de_nouvelle_validation_pactols(self):
        for row in self.lot:
            self.assertTrue(row["validation"].startswith("NON VALIDÉ"), row["ark"])
        special = {x["ark_pactols"] for x in self.movements}
        self.assertEqual(len(special), 2)
        self.assertTrue(special <= self.par_ark.keys())


if __name__ == "__main__":
    unittest.main()
