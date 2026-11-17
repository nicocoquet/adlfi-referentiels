"""Tests géométriques Hao hors réseau : composantes, trous et emprises."""
import importlib.util
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from auditer_hao_ispf_geopf import (
    HAO_GEO, HAO_COMAS, HAO_ILE, polygones, statistiques_geometriques,
    differences,
)

class TestIdsHao(unittest.TestCase):
    def test_rattachements_attendus(self):
        self.assertEqual((HAO_GEO,HAO_COMAS,HAO_ILE),("20200","202","23"))

@unittest.skipUnless(importlib.util.find_spec("shapely") and importlib.util.find_spec("pyproj"),
                     "Nécessite Shapely + pyproj")
class TestGeometrieHao(unittest.TestCase):
    def setUp(self):
        from pyproj import CRS
        self.geod=CRS.from_epsg(4687).get_geod()

    def test_trou_non_confondu_avec_une_ile(self):
        from shapely.geometry import Polygon
        external=[(-141,-18),(-140,-18),(-140,-17),(-141,-17),(-141,-18)]
        hole=[(-140.7,-17.7),(-140.3,-17.7),(-140.3,-17.3),(-140.7,-17.3),(-140.7,-17.7)]
        polygon=Polygon(external,[hole])
        r=statistiques_geometriques(polygon,self.geod)
        self.assertEqual(r["composantes_polygonales"],1)
        self.assertEqual(r["anneaux_interieurs"],1)
        self.assertGreater(r["surface_trous_m2"],0)
        self.assertGreater(r["surface_anneaux_exterieurs_m2"],r["surface_polygonale_nette_m2"])

    def test_differences_symetriques_orientees(self):
        from shapely.geometry import box
        g1=box(-140.5,-17.5,-140.3,-17.3)
        g2=box(-140.4,-17.5,-140.2,-17.3)
        r=differences(g1,g2,self.geod)
        self.assertGreater(r["a_hors_b_m2"],0)
        self.assertGreater(r["b_hors_a_m2"],0)
        self.assertEqual(r["nombre_composantes_a_hors_b"],1)
        self.assertEqual(r["nombre_composantes_b_hors_a"],1)
        self.assertEqual(len(list(polygones(g1))),1)

if __name__=="__main__":
    unittest.main()
