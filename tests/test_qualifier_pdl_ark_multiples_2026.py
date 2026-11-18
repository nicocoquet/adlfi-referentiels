"""Tests des qualificatifs chronologiques et des collisions Pactols."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from qualifier_pdl_ark_multiples_2026 import libelle_contemporain_compatible

class TriagePdlTests(unittest.TestCase):
    def test_identite_contemporaine_simple(self):
        self.assertTrue(libelle_contemporain_compatible("Chaumes-en-Retz", "Chaumes-en-Retz"))
        self.assertTrue(libelle_contemporain_compatible("Le Lude", "Le Lude (Sarthe)"))

    def test_statut_historique_pas_une_identite_contemporaine(self):
        self.assertFalse(libelle_contemporain_compatible(
            "Le Lion-d'Angers", "Le Lion-d'Angers (ancienne commune)"))
        self.assertFalse(libelle_contemporain_compatible(
            "Le Lude", "Le Lude (commune déléguée)"))

    def test_ancien_libelle_distinct(self):
        self.assertFalse(libelle_contemporain_compatible(
            "Chemillé-en-Anjou", "Chemillé-Melay"))
        self.assertFalse(libelle_contemporain_compatible(
            "Ingrandes-le-Fresne-sur-Loire", "Ingrandes-Le Fresne sur Loire"))

if __name__ == "__main__":
    unittest.main()
