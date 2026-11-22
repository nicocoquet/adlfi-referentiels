"""Contrat du vérificateur de parité 1.57/1.58, sans accès aux XLSX privés en CI."""
import unittest
from scripts.recette_parite_maitres_157_158 import SOURCES, OFFICIAL_CODE, differences

class ParitesOfficiellesTests(unittest.TestCase):
    def test_les_deux_maitres_et_les_deux_refs_sont_distincts(self):
        self.assertEqual(set(SOURCES), {"1.57", "1.58"})
        old, new = SOURCES["1.57"], SOURCES["1.58"]
        self.assertNotEqual(old["filename"], new["filename"])
        self.assertNotEqual(old["sha256"], new["sha256"])
        self.assertNotEqual(old["ref"], new["ref"])
        self.assertEqual(len(old["sha256"]), 64)
        self.assertEqual(len(new["sha256"]), 64)
        self.assertEqual(old["counts"], (934, 734, 682, 600))
        self.assertEqual(new["counts"], (935, 735, 683, 600))

    def test_exporteur_et_dependances_versionnes_obligatoires(self):
        self.assertEqual(set(OFFICIAL_CODE), {
            "scripts/export_organismes.py",
            "scripts/sector_inheritance.py",
            "scripts/level_inheritance.py"})

    def test_differents_champs_et_nouvelles_autorites_detectes(self):
        a={"authorities":[{"id":"ORG-0156","usage":{"affiliations_validated":1}}]}
        b={"authorities":[{"id":"ORG-0156","usage":{"affiliations_validated":2}},
                           {"id":"ORG-0756","usage":{"affiliations_validated":1}}]}
        errors=differences(a,b)
        self.assertTrue(any("affiliations_validated" in x for x in errors))
        self.assertTrue(any("entrées" in x for x in errors))
        self.assertEqual(differences(a,a),[])

if __name__=="__main__":
    unittest.main()
