"""Tests des recouvrements internes avec exemples synthétiques, sans réseau."""
from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from auditer_recouvrements_ispf_polynesie import analyser_couche, normaliser_code, CRS

def fc(polygons):
    return {"type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": CRS}},
            "features": [
                {"type": "Feature", "properties": {"IDCom": i+1},
                 "geometry": {"type": "MultiPolygon", "coordinates": [coords]}}
                for i, coords in enumerate(polygons)]}

def carre(x0, x1):
    return [[[x0, 0], [x1, 0], [x1, 1], [x0, 1], [x0, 0]]]

class TestRecouvrementsISPF(unittest.TestCase):
    def test_cle_numero_entier(self):
        self.assertEqual(normaliser_code(12.0), "12")
        for value in (None, True, 3.4, "numéro"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normaliser_code(value)

    @unittest.skipUnless(importlib.util.find_spec("shapely"), "Shapely requis")
    def test_intersection_interieurs_vs_contact_frontiere(self):
        # Ne pas imposer le contrat 48 du vrai fichier pour un exemple de 3.
        from unittest.mock import patch
        import auditer_recouvrements_ispf_polynesie as module
        with patch.dict(module.LAYERS, {"Com.GeoJSON": ("IDCom", 3)}):
            result = analyser_couche(fc([carre(0, 1), carre(1, 2),
                                         carre(0.5, 1.5)]), "Com.GeoJSON")
        self.assertEqual(result["paires_recouvrement_interieur"], 2)
        self.assertEqual(result["paires_contact_limites"], 1)
        self.assertEqual(len(result["paires_recouvrements_a_instruire"]), 2)

    @unittest.skipUnless(importlib.util.find_spec("shapely"), "Shapely requis")
    def test_rejette_crs_non_documente(self):
        from unittest.mock import patch
        import auditer_recouvrements_ispf_polynesie as module
        with patch.dict(module.LAYERS, {"Com.GeoJSON": ("IDCom", 1)}):
            data = fc([carre(0, 1)])
            data.pop("crs")
            with self.assertRaisesRegex(ValueError, "CRS"):
                analyser_couche(data, "Com.GeoJSON")

if __name__ == "__main__":
    unittest.main()
