"""Contrats de comparaison GEO PF et ISPF, sans téléchargement de sources."""
from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from comparer_contours_geopf_ispf import aire

@unittest.skipUnless(importlib.util.find_spec("shapely") and importlib.util.find_spec("pyproj"),
                     "Contrôles géométriques réservés au workflow spatial")
class TestContoursGeoPFISPF(unittest.TestCase):
    def test_aire_collection_et_ligne(self):
        from pyproj import CRS
        from shapely.geometry import Polygon,LineString,GeometryCollection
        geod=CRS.from_epsg(4687).get_geod()
        polygon=Polygon([(-149,-17),(-148.99,-17),(-148.99,-16.99),(-149,-16.99)])
        line=LineString([(-149,-17),(-148.99,-16.99)])
        self.assertGreater(aire(polygon,geod),0)
        self.assertAlmostEqual(aire(GeometryCollection([polygon,line]),geod),
                               aire(polygon,geod),places=5)
        self.assertEqual(aire(line,geod),0)

    def test_union_geometrique_et_diff_symetrique(self):
        from shapely.geometry import box
        from shapely.ops import unary_union
        parts=[box(0,0,1,1),box(1,0,2,1)]
        aggregated=unary_union(parts)
        reference=box(0,0,2,1)
        self.assertTrue(aggregated.equals(reference))
        self.assertEqual(aggregated.symmetric_difference(reference).area,0)
        shifted=box(0.1,0,2.1,1)
        self.assertGreater(aggregated.symmetric_difference(shifted).area,0)

if __name__=="__main__":
    unittest.main()
