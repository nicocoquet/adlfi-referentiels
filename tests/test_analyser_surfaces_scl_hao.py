"""Tests locaux des comptages SCL : données artificielles, aucun pixel Sentinel."""
from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyser_surfaces_scl_hao import compter_scl, verify_manifest, sha256_file

@unittest.skipUnless(all(importlib.util.find_spec(x) for x in ("rasterio","numpy","shapely","pyproj")),
                     "Dépendances SIG absentes des tests généraux")
class TestSCLSynthese(unittest.TestCase):
    def test_classes_nodata_et_hors_raster(self):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        from pyproj import Transformer
        from shapely.geometry import box
        from shapely.ops import transform as shapely_transform
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/"synthetic.tif"
            arr=np.array([
                [6,6,9,9,0],
                [6,6,9,9,0],
                [6,6,9,9,0],
                [6,6,9,9,0],
                [6,6,9,9,0],
            ],dtype=np.uint8)
            x,y=200000,8000000
            with rasterio.open(file,"w",driver="GTiff",height=5,width=5,count=1,
                                crs="EPSG:32707",dtype="uint8",
                                transform=from_origin(x,y,20,20),nodata=0) as ds:
                ds.write(arr,1)
            togeo=Transformer.from_crs("EPSG:32707","EPSG:4687",always_xy=True).transform
            shape_all=shapely_transform(togeo,box(x,y-100,x+100,y))
            shape_far=shapely_transform(togeo,box(x+500,y+500,x+600,y+600))
            with rasterio.open(file) as ds:
                result=compter_scl(ds,shape_all)
                self.assertEqual(result["pixels_centre_dans_polygone"],25)
                self.assertEqual(result["pixels_valides"],20)
                self.assertEqual(result["pixel_nodata"],5)
                self.assertEqual(result["classes"]["6"]["pixels"],10)
                self.assertEqual(result["classes"]["9"]["pixels"],10)
                self.assertEqual(result["classes"]["6"]["part_des_pixels_valides"],0.5)
                far=compter_scl(ds,shape_far)
                self.assertEqual(far["statut"],"HORS_EMPRISE_RASTER")

class TestManifest(unittest.TestCase):
    def test_checksum_produit_et_integrite(self):
        from inventorier_assets_hao_sentinel2 import ITEM_ID
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);r=d/"SCL_20m.jp2";r.write_bytes(b"test")
            m=d/"manifest-local.json"
            m.write_text(json.dumps({
                "produit":ITEM_ID,"mode":"TELECHARGEMENT_S3_AUTHENTIFIE",
                "fichiers":{"SCL_20m":{"nom_local":r.name,
                "taille_octets":4,"sha256":sha256_file(r)}}}))
            self.assertEqual(verify_manifest(m,r),sha256_file(r))
            r.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError,"Intégrité"):
                verify_manifest(m,r)

if __name__=="__main__":
    unittest.main()
