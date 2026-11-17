"""Préflight GeoJSON : jeux synthétiques uniquement."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from auditer_geojson_ispf_polynesie import analyser_couche, coordonnees

class TestGeojsonISPF(unittest.TestCase):
    def test_polygone_et_proprietes(self):
        data = {"type": "FeatureCollection", "features": [{
            "type": "Feature", "properties": {"IDCom": "11", "nom": "Essai"},
            "geometry": {"type": "Polygon", "coordinates": [
                [[-150, -17], [-149, -17], [-149, -16], [-150, -17]]]}
        }]}
        report = analyser_couche(data, "Com.GeoJSON")
        self.assertEqual(report["features"], 1)
        self.assertEqual(report["types_geometriques"]["Polygon"], 1)
        self.assertEqual(report["emprise_coordonnees_brutes"], [-150, -17, -149, -16])
        self.assertEqual({k["nom"] for k in report["proprietes"]}, {"IDCom", "nom"})

    def test_null_ne_devient_pas_contour(self):
        r = analyser_couche({"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": None}]}, "Ile.GeoJSON")
        self.assertEqual(r["geometries_nulles"], 1)
        self.assertIsNone(r["emprise_coordonnees_brutes"])

    def test_rejette_collection_invalide(self):
        with self.assertRaises(ValueError):
            analyser_couche({"type": "Feature", "features": []}, "Comas.GeoJSON")

    def test_rejette_coordonnees_non_finies(self):
        with self.assertRaises(ValueError):
            list(coordonnees([[float("nan"), 1.0]]))

if __name__ == "__main__":
    unittest.main()
