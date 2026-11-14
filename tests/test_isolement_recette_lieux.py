"""Garde-fou contre l'exposition involontaire des dossiers de recette.

Tout fichier sous docs/ est servi statiquement par GitHub Pages. Les
candidatures et rapports internes doivent être versionnés hors docs/.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class IsolementRecetteLieux(unittest.TestCase):
    def test_aucune_recette_lieux_dans_pages(self):
        for forbidden in ("docs/lieux/recette","docs/lieux/rapports"):
            root=ROOT/forbidden
            files=[p for p in root.rglob("*") if p.is_file()] if root.exists() else []
            self.assertFalse(files,"Dossiers Lieux publics à déplacer hors de docs/: "+
                             ", ".join(str(p.relative_to(ROOT)) for p in files[:8]))
    def test_registre_paca_hors_pages(self):
        dossier=ROOT/"recette/lieux/paca"
        self.assertTrue((dossier/"paca-sept-candidatures-20261114.csv").is_file())
        self.assertFalse((ROOT/"docs/lieux/recette/paca-sept-candidatures-20261114.csv").exists())
if __name__=="__main__":
    unittest.main()
