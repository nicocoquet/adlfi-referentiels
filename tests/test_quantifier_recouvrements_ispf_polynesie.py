"""Calculs ellipsoïdaux et géométries mixtes, sans réseau."""
from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from quantifier_recouvrements_ispf_polynesie import aire_geodesique

@unittest.skipUnless(importlib.util.find_spec("shapely") and importlib.util.find_spec("pyproj"),
                     "Shapely et pyproj requis pour la mesure géodésique")
class TestAiresGeodesiques(unittest.TestCase):
    def test_surface_positive_et_collection(self):
        from shapely.geometry import Polygon, LineString, GeometryCollection
        from pyproj import CRS
        geod=CRS.from_epsg(4687).get_geod()
        poly=Polygon([(-149,-17),(-148.999,-17),(-148.999,-16.999),(-149,-16.999)])
        value=aire_geodesique(poly,geod)
        self.assertGreater(value,0)
        mix=GeometryCollection([poly,LineString([(-149,-17),(-148,-17)])])
        self.assertAlmostEqual(aire_geodesique(mix,geod),value,places=5)

    def test_ligne_sans_aire(self):
        from shapely.geometry import LineString
        from pyproj import CRS
        self.assertEqual(aire_geodesique(LineString([(0,0),(1,1)]),CRS.from_epsg(4687).get_geod()),0.0)

if __name__=="__main__":
    unittest.main()
