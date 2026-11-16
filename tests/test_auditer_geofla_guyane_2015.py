"""Garde-fous de l'audit géométrique GEOFLA Guyane 2015."""
import sys
import unittest
from pathlib import Path
from shapely.geometry import Polygon

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_geofla_guyane_2015 import reconnaitre_code, comparer_geometries,SCHEMA


class GEOFLAGuyaneTests(unittest.TestCase):
    def test_code_communal_explicite(self):
        self.assertEqual(reconnaitre_code({"CODE_INSEE":"97306"}),("97306","CODE_INSEE"))
        self.assertEqual(reconnaitre_code({"insee_com":"97301"}),("97301","INSEE_COM"))
        self.assertEqual(reconnaitre_code({"CODE_INSEE":"97306","INSEE_COM":"97306"})[0],"97306")

    def test_homonymie_ou_contradiction_ne_produit_pas_code(self):
        self.assertEqual(reconnaitre_code({"NOM_COM":"Mana"}),(None,None))
        self.assertEqual(reconnaitre_code({"CODE_INSEE":"75056"}),(None,None))
        self.assertEqual(reconnaitre_code({"CODE_INSEE":"97306","INSEE_COM":"97351"}),(None,None))

    def test_differences_surfaciques_symetriques(self):
        a=Polygon([(0,0),(1000,0),(1000,1000),(0,1000)])
        b=Polygon([(500,0),(1500,0),(1500,1000),(500,1000)])
        r=comparer_geometries(a,b)
        self.assertAlmostEqual(r["source2015_km2"],1)
        self.assertAlmostEqual(r["national2026_km2"],1)
        self.assertAlmostEqual(r["difference_symetrique_km2"],1)
        self.assertAlmostEqual(r["source2015_hors_2026_km2"],0.5)
        self.assertAlmostEqual(r["national2026_hors_2015_km2"],0.5)
        self.assertAlmostEqual(r["jaccard_pct"],33.333333,places=5)

    def test_geom_invalide_refusee(self):
        invalide=Polygon([(0,0),(2,2),(0,2),(2,0)])
        saine=Polygon([(0,0),(2,0),(2,2),(0,2)])
        with self.assertRaisesRegex(ValueError,"non valide"):
            comparer_geometries(invalide,saine)


if __name__=="__main__":
    unittest.main()
