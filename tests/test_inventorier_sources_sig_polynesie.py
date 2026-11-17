"""Tests sans réseau pour l'inventaire de sources SIG de Polynésie."""
from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path
from zipfile import ZipFile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inventorier_sources_sig_polynesie import analyser_archive

class TestInventaireSIG(unittest.TestCase):
    def test_zip_bien_forme(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "source.zip"
            with ZipFile(p, "w") as z:
                z.writestr("geojson/iles.geojson", '{"type":"FeatureCollection","features":[]}')
            r = analyser_archive(p, "https://example.org/source.zip")
            self.assertEqual(r["nombre_membres"], 1)
            self.assertEqual(r["inventaire"][0]["extension"], ".geojson")
            self.assertEqual(r["decision"], "AUCUNE_GEOMETRIE_HOMOLOGUEE")

    def test_zip_traversal_interdit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "source.zip"
            with ZipFile(p, "w") as z:
                z.writestr("../danger.geojson", "{}")
            with self.assertRaisesRegex(ValueError, "dangereux"):
                analyser_archive(p, "https://example.org/source.zip")

    def test_zip_invalide(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "source.zip"
            p.write_text("pas une archive")
            with self.assertRaisesRegex(ValueError, "ZIP"):
                analyser_archive(p, "https://example.org/source.zip")

if __name__ == "__main__":
    unittest.main()
