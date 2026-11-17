"""Non-régression du diagnostique raster Hao sans aucune donnée Sentinel téléchargée."""
from __future__ import annotations
import importlib.util
import tempfile
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from diagnostiquer_pixels_hao_l2a import BANDS, inspect_dataset, auditer, SCL

class TestContract(unittest.TestCase):
    def test_classification_ne_prouve_pas_un_motu(self):
        self.assertEqual(SCL[6],"WATER")
        self.assertIn("CLOUD",SCL[9])
        self.assertEqual(len(BANDS),5)

@unittest.skipUnless(importlib.util.find_spec("rasterio") and importlib.util.find_spec("numpy"),
                     "rasterio/numpy requis pour tests synthétiques de pixels")
class TestRasters(unittest.TestCase):
    def test_points_utm_et_no_data(self):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        from rasterio.warp import transform
        xs,ys=transform("EPSG:4326","EPSG:32707",[-140.7412651],[-18.3624007])
        x,y=xs[0],ys[0]
        # Pour un test synthétique, le pixel central recouvre précisément P1.
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"synthetic.tif"
            arr=np.full((11,11),7,dtype=np.uint16)
            with rasterio.open(p,"w",driver="GTiff",width=11,height=11,count=1,
                    dtype="uint16",crs="EPSG:32707",
                    transform=from_origin(x-55,y+55,10,10),nodata=0) as ds:
                ds.write(arr,1)
            values=inspect_dataset(p)
            point=next(v for v in values["points"] if v["rang"]==1)
            self.assertEqual(point["etat"],"PIXEL_PRESENT")
            self.assertEqual(point["valeur"],7)
            self.assertEqual(values["crs_raster"],"EPSG:32707")

    def test_refus_jeu_incomplet(self):
        with self.assertRaisesRegex(ValueError,"Cinq bandes"):
            auditer({"B02_10m":Path("/inconnu")})

if __name__=="__main__":
    unittest.main()
