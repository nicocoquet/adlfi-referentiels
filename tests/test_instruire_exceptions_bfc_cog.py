import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from instruire_exceptions_bfc_cog import (
    CATEGORIES, EXPECTED, classe_mouvements, conserver_evenements, sha, SHA
)

class InstructionExceptionsBFC(unittest.TestCase):
    def test_les_cinq_profils_restent_distincts(self):
        self.assertEqual(len(CATEGORIES), 5)
        self.assertEqual(sum(EXPECTED.values()), 25)
        for mods, label in CATEGORIES.items():
            self.assertEqual(classe_mouvements([{"MOD": mod} for mod in mods]), label)
        with self.assertRaises(ValueError):
            classe_mouvements([{"MOD": "99"}])

    def test_preuves_conservent_avant_apres_sans_validation(self):
        from instruire_exceptions_bfc_cog import M_FIELDS
        row = {field: "" for field in M_FIELDS}
        row.update(MOD="32", DATE_EFF="2018-01-01", TYPECOM_AV="COM",
                   COM_AV="25137", LIBELLE_AV="Chaudefontaine",
                   TYPECOM_AP="COM", COM_AP="25368",
                   LIBELLE_AP="Marchaux-Chaudefontaine")
        result = conserver_evenements([row], "25137", "26678/test")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["COM_AV"], "25137")
        self.assertEqual(result[0]["COM_AP"], "25368")
        self.assertEqual(result[0]["TYPECOM_AV"], "COM")
        self.assertEqual(result[0]["TYPECOM_AP"], "COM")
        self.assertTrue(result[0]["identifiant_ligne_cog"].startswith("mvt:"))
        self.assertNotIn("validation", result[0])

    def test_sources_de_recette_immuables(self):
        base = Path(__file__).resolve().parents[1] / "docs" / "lieux" / "recette"
        self.assertEqual(
            sha(base / "codes-historiques-absents-bfc-25.csv"), SHA["codes25"]
        )
        self.assertEqual(
            sha(base / "codes-partages-ark-bfc-2.csv"), SHA["doubles"]
        )

if __name__ == "__main__":
    unittest.main()
