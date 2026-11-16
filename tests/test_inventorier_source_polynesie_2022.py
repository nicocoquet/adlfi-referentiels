"""Tests d'inventaire (non validant) du shapefile polynésien 2022."""
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inventorier_source_polynesie_2022 import analyser, normaliser, shapefile


class SansDependance(unittest.TestCase):
    def test_noms_avec_apostrophes(self):
        self.assertEqual(normaliser("Taha'a"), "tahaa")
        self.assertEqual(normaliser("TAHAA"), "tahaa")


@unittest.skipUnless(shapefile is not None, "pyshp réservé à la CI dédiée")
class ArchiveShapefile(unittest.TestCase):
    def test_inventaire_deux_features_sans_geometry_publique(self):
        shp, shx, dbf = io.BytesIO(), io.BytesIO(), io.BytesIO()
        w = shapefile.Writer(shp=shp, shx=shx, dbf=dbf, shapeType=shapefile.POLYGON)
        w.field("IDCom", "N", 5)
        w.field("Com", "C", 40)
        for code, name, lon in [(45,"TAHAA",-151), (46,"UTUROA",-151.3)]:
            w.poly([[[lon,-16],[lon+0.1,-16],[lon+0.1,-16.1],[lon,-16.1],[lon,-16]]])
            w.record(code, name)
        w.close()
        with tempfile.TemporaryDirectory() as temp:
            archive=Path(temp)/"polynesie.zip"
            with zipfile.ZipFile(archive, "w") as z:
                for name,data in (("couches/communes.shp",shp.getvalue()),
                                  ("couches/communes.shx",shx.getvalue()),
                                  ("couches/communes.dbf",dbf.getvalue()),
                                  ("couches/communes.prj",b'GEOGCS["WGS 84"]')):
                    z.writestr(name,data)
            result=analyser(archive)
            self.assertEqual(len(result["couches"]),1)
            self.assertEqual(result["couches"][0]["nombre_enregistrements"],2)
            self.assertEqual(len(result["couches"][0]["occurrences_tahaa"]),1)
            self.assertEqual(result["couches"][0]["occurrences_tahaa"][0]
                             ["identifiants_et_libelles"]["IDCom"],"45")
            self.assertEqual(result["geometries_publiees"],0)
            self.assertEqual(result["alignements_cog_crees"],0)


if __name__ == "__main__":
    unittest.main()
