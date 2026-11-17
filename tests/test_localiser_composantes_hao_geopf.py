"""Localiser des parties polygonales sans leur attribuer de toponyme."""
from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from localiser_composantes_hao_geopf import classer_pieces

@unittest.skipUnless(importlib.util.find_spec("shapely") and importlib.util.find_spec("pyproj"),
                     "Shapely et pyproj requis")
class TestsLocalisationHao(unittest.TestCase):
    def test_classement_et_points_interieurs(self):
        from pyproj import CRS
        from shapely.geometry import MultiPolygon,box,Point
        geod=CRS.from_epsg(4687).get_geod()
        a=box(-141,-18,-140.99,-17.99)
        b=box(-141.1,-18,-141.098,-17.998)
        output=classer_pieces(MultiPolygon([b,a]),geod)
        self.assertEqual(len(output),2)
        self.assertGreater(output[0]["surface_m2"],output[1]["surface_m2"])
        self.assertEqual(output[0]["interpretation_geographique"],"NON_QUALIFIEE")
        for record in output:
            lon,lat=record["point_interieur_lon_lat"]
            self.assertTrue(a.buffer(0.000001).covers(Point(lon,lat)) or
                            b.buffer(0.000001).covers(Point(lon,lat)))

    def test_points_et_lignes_non_comptes(self):
        from pyproj import CRS
        from shapely.geometry import GeometryCollection,LineString,Point,box
        geom=GeometryCollection([box(-141,-18,-140.99,-17.99),
                                 LineString([(-141,-18),(-140,-18)]),Point(-141,-18)])
        self.assertEqual(len(classer_pieces(geom,CRS.from_epsg(4687).get_geod())),1)

if __name__=="__main__":
    unittest.main()
