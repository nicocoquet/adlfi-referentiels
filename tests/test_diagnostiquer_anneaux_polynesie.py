"""Recette sans modification de géométries : anneaux intérieurs et IoU."""
import importlib.util
import sys
import unittest
from pathlib import Path

@unittest.skipUnless(importlib.util.find_spec("shapely"), "Shapely chargé par le workflow spatial spécialisé")
class AnneauxPolynesieTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from shapely.geometry import Polygon
        from diagnostiquer_anneaux_polynesie import audit_anneaux, silhouette_sans_trous, iou
        self.Polygon = Polygon
        self.audit = audit_anneaux
        self.fill = silhouette_sans_trous
        self.iou = iou

    def test_remplissage_synthetique_uniquement_simule(self):
        outer = [(0,0),(10,0),(10,10),(0,10),(0,0)]
        inner = [(1,1),(9,1),(9,9),(1,9),(1,1)]
        polygon = self.Polygon(outer,[inner])
        count, area = self.audit(polygon)
        self.assertEqual(count,1)
        self.assertGreater(area,0)
        filled = self.fill(polygon)
        self.assertAlmostEqual(self.iou(polygon,filled),0.36)
        self.assertTrue(polygon.is_valid)
        self.assertEqual(len(polygon.interiors),1)  # l'original n'est jamais modifié
        self.assertEqual(len(filled.interiors),0)

    def test_aucun_trou_ne_change_pas_la_surface(self):
        polygon = self.Polygon([(0,0),(2,0),(2,2),(0,2)])
        self.assertEqual(self.audit(polygon)[0],0)
        self.assertAlmostEqual(self.iou(polygon,self.fill(polygon)),1.0)

    def test_pas_de_geometrie_non_polygonale(self):
        from shapely.geometry import Point
        with self.assertRaisesRegex(ValueError,"Type inattendu"):
            self.audit(Point(1,2))

if __name__=="__main__":
    unittest.main()
