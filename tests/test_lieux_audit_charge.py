"""Contrats du préflight de charge GeoJSON (sans dépendance réseau)."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from auditer_charge_carte_lieux import auditer_couche, audit  # noqa: E402


def fixture(code="12345", millesime=2026, lon=2):
    return {
        "type": "FeatureCollection",
        "provenance": {"millesime": millesime, "nombre_contours": 1, "schema": "fixture"},
        "features": [{
            "type": "Feature", "properties": {"code": code, "niveau": "commune"},
            "geometry": {"type": "Polygon", "coordinates": [[
                [lon, 46], [lon + 0.1, 46], [lon + 0.1, 46.1],
                [lon, 46.1], [lon, 46],
            ]]},
        }],
    }


class AuditChargeLieuxTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.relative = "lieux-chronologie/test.geojson"
        self.path = self.root / "docs" / "data" / self.relative
        self.path.parent.mkdir(parents=True)

    def write(self, value):
        self.path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")

    def test_mesure_reproductible_et_non_validante(self):
        self.write(fixture())
        first = auditer_couche(self.root / "docs" / "data", "test", self.relative)
        second = auditer_couche(self.root / "docs" / "data", "test", self.relative)
        self.assertEqual(first, second)
        self.assertEqual(first["communes_cartographiees"], 1)
        self.assertEqual(first["sommets_coordonnees"], 5)
        self.assertEqual(first["emprise_lon_lat"], [2.0, 46.0, 2.1, 46.1])
        result = audit(self.root, (("test", self.relative),))
        self.assertEqual(result["total"]["communes_cartographiees"], 1)
        self.assertEqual(result["total"]["octets_gzip_simules"], first["octets_gzip_simules"])
        self.assertEqual(result["statut"], "MESURE_STATIQUE_NON_PUBLIANTE")

    def test_code_duplique_refuse(self):
        doc = fixture()
        doc["features"].append(doc["features"][0].copy())
        doc["provenance"]["nombre_contours"] = 2
        self.write(doc)
        with self.assertRaisesRegex(ValueError, "dupliqué"):
            auditer_couche(self.root / "docs" / "data", "test", self.relative)

    def test_millesime_non_2026_refuse(self):
        self.write(fixture(millesime=2025))
        with self.assertRaisesRegex(ValueError, "Millésime incompatible"):
            auditer_couche(self.root / "docs" / "data", "test", self.relative)

    def test_coordonnees_hors_bornes_refusees(self):
        self.write(fixture(lon=181))
        with self.assertRaisesRegex(ValueError, "hors bornes"):
            auditer_couche(self.root / "docs" / "data", "test", self.relative)


if __name__ == "__main__":
    unittest.main()
