"""Contrôle structurel de la tranche éditoriale de Mayotte (16 correspondances 2026 validées et ARK Dembeni confirmé)."""
import csv
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "recette" / "lieux" / "LOT-MAYOTTE-17-COMMUNES-20261115.csv"


class Mayotte17Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SOURCE.open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f, delimiter=";"))

    def test_17_codes_uniques_pour_2026(self):
        self.assertEqual(len(self.rows), 17)
        codes = {r["code_insee"] for r in self.rows}
        self.assertEqual(codes, {f"976{i:02d}" for i in range(1, 18)})
        self.assertEqual(len({r["ark_candidat_Pactols"] for r in self.rows}), 17)

    def test_liens_numeriques_sans_inference(self):
        for r in self.rows:
            code = r["code_insee"]
            self.assertEqual(r["URI_INSEE_existante_dans_Pactols"],
                             f"http://id.insee.fr/geo/commune/{code}")
            self.assertIn(r["decision_editoriale"], (
                "VALIDE_2026", "ARK_CONFIRME_CORRESPONDANCE_A_VALIDER"))
            self.assertTrue(r["justification_editoriale"])
            self.assertEqual(r["date_debut_COMER_incluse"], "2007-02-23")
            self.assertEqual(r["date_fin_COMER_exclue"], "2011-03-31")
            self.assertEqual(r["date_debut_DROM_incluse"], "2011-03-31")

    def test_reserve_sur_dembeni_sans_reecriture(self):
        dembeni = next(r for r in self.rows if r["code_insee"] == "97607")
        self.assertEqual(dembeni["libelle_COG_2026"], "Dembeni")
        self.assertEqual(dembeni["ark_candidat_Pactols"], "26678/crtZcuFSJVYZU")
        self.assertEqual(dembeni["avis_preinstruction"],
                         "FAVORABLE_2026_ARK_CONFIRME")
        self.assertEqual(dembeni["decision_editoriale"],
                         "ARK_CONFIRME_CORRESPONDANCE_A_VALIDER")
        self.assertIn("CONFIRMEE", dembeni["alerte_identifiant"])
        self.assertIn("crt", dembeni["alerte_identifiant"])
        other = [r for r in self.rows if r["code_insee"] != "97607"]
        self.assertEqual(len(other), 16)
        self.assertTrue(all(r["ark_candidat_Pactols"].startswith("26678/pcrt")
                            for r in other))
        self.assertTrue(all(r["avis_preinstruction"] == "FAVORABLE_2026"
                            for r in other))
        self.assertTrue(all(r["decision_editoriale"] == "VALIDE_2026"
                            for r in other))


if __name__ == "__main__":
    unittest.main()
