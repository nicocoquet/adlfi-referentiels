"""Inventaire GEO PF : garde-fous sans accès réseau."""
from __future__ import annotations
import importlib.util,io,sys,tempfile,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from inventorier_geopf_polynesie import audit

@unittest.skipUnless(importlib.util.find_spec("shapefile"), "pyshp requis")
class TestInventaireGeoPF(unittest.TestCase):
    def test_archive_synthetique(self):
        import shapefile
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            base=root/"sample"
            with shapefile.Writer(str(base),shapeType=shapefile.POLYGON) as w:
                w.field("com_id","N",10,0)
                w.field("ca_id","N",10,0)
                w.poly([[[0,0],[1,0],[1,1],[0,1],[0,0]]])
                w.record(12,120)
            path=root/"source.zip"
            with zipfile.ZipFile(path,"w") as z:
                for ext in (".shp",".shx",".dbf"):
                    z.write(str(base)+ext,"data/associee"+ext)
            report=audit(path)
            self.assertEqual(report["statut"],"RECETTE_NON_VALIDANTE")
            self.assertEqual(report["couches"][0]["entites"],1)
            self.assertEqual([f["nom"] for f in report["couches"][0]["champs"]],["com_id","ca_id"])
            self.assertEqual(report["publication"]["polygones"],0)

    def test_archive_sans_shapefile_refusee(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"incomplete.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("README.txt","missing")
            with self.assertRaisesRegex(ValueError,"SHP/SHX/DBF"):
                audit(p)

    def test_archive_chemin_dangereux(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"unsafe.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("../data.shp","not real")
            with self.assertRaisesRegex(ValueError,"dangereux"):
                audit(p)

if __name__=="__main__":unittest.main()
