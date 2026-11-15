"""Vérifications non validantes de la tranche des 24 communes de La Réunion."""
import csv
import unittest
from collections import Counter
from pathlib import Path

CSV = Path(__file__).resolve().parents[1] / "recette" / "lieux" / "LOT-REUNION-24-COMMUNES-20261115.csv"


class Reunion24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CSV.open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f, delimiter=";"))
        cls.by_code = {r["code_INSEE_2026"]: r for r in cls.rows}

    def test_24_codes_actuels_uniques(self):
        self.assertEqual(len(self.rows), 24)
        self.assertEqual(set(self.by_code), {f"974{i:02d}" for i in range(1, 25)})
        self.assertEqual(len({r["ark_Pactols_candidat"] for r in self.rows}), 24)

    def test_24_uri_insee_et_aucun_lien_valide_par_l_audit(self):
        for r in self.rows:
            code = r["code_INSEE_2026"]
            self.assertEqual(r["uri_INSEE_declaree_dans_Pactols"],
                             "http://id.insee.fr/geo/commune/" + code)
            if code == "97407":
                self.assertEqual(r["decision_editoriale"],
                                 "ARK_CONFIRME_CORRESPONDANCE_A_VALIDER")
                self.assertIn("26678/pcrtIKvRT9vwUl",
                              r["justification_editoriale"])
            else:
                self.assertEqual(r["decision_editoriale"], "A_INSTRUIRE")
                self.assertEqual(r["justification_editoriale"], "")
            self.assertTrue(r["ark_Pactols_candidat"].startswith("26678/pcrt"))
            self.assertIn(r["avis_preinstruction"], (
                "FAVORABLE_2026_SOUS_CONFIRMATION", "INSTRUCTION_COMPLEMENTAIRE"
            ))

    def test_trois_dossiers_distincts(self):
        cat = Counter(r["nature_instruction"] for r in self.rows)
        self.assertEqual(cat, {
            "STANDARD_2026": 21,
            "DIVISION_1965": 2,
            "HOMONYMIE_LE_PORT": 1,
        })
        self.assertEqual(self.by_code["97414"]["libelle_COG_2026"], "Saint-Louis")
        self.assertEqual(self.by_code["97424"]["libelle_COG_2026"], "Cilaos")
        self.assertEqual(self.by_code["97414"]["premiere_attestation_code_COG"],
                         "1946-03-21")
        self.assertEqual(self.by_code["97424"]["premiere_attestation_code_COG"],
                         "1965-02-05")
        self.assertEqual(self.by_code["97407"]["ark_Pactols_candidat"],
                         "26678/pcrtIKvRT9vwUl")
        self.assertEqual(self.by_code["97407"]["prefLabel_fr_Pactols"],
                         "Le Port (La Réunion)")
        self.assertEqual(self.by_code["97407"]["decision_editoriale"],
                         "ARK_CONFIRME_CORRESPONDANCE_A_VALIDER")
        self.assertEqual(self.by_code["97407"]["avis_preinstruction"],
                         "ARK_CONFIRME_EDITEUR_LIEN_A_VALIDER")


if __name__ == "__main__":
    unittest.main()
