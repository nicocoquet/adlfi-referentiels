"""Préflight STAC Hao : tests synthétiques, accès réseau interdit."""
from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from inventorier_assets_hao_sentinel2 import audit, describe_asset, safe_host, ITEM_ID

class TestDescription(unittest.TestCase):
    def test_pas_de_jeton_ni_query_string_en_sortie(self):
        r=safe_host("https://example.org/some/B02.jp2?token=secret")
        self.assertEqual(r,{"scheme":"https","host":"example.org","path_suffix":".jp2"})
        self.assertNotIn("secret",str(r))

    def test_asset_sans_href(self):
        d=describe_asset("SCL",{"type":"image/jp2","proj:epsg":32707})
        self.assertEqual(d["verification_des_pixels"],"NON_REALISEE")
        self.assertFalse(d["href_existe"])

@unittest.skipUnless(importlib.util.find_spec("shapely"),"Shapely requis")
class TestFootprint(unittest.TestCase):
    def item(self):
        return {"id":ITEM_ID,"collection":"sentinel-2-l2a",
                "properties":{"datetime":"2022-12-26T19:38:51.024Z","eo:cloud_cover":3.53},
                "geometry":{"type":"Polygon","coordinates":[[
                    [-141.1,-18.5],[-140.6,-18.5],[-140.6,-18.0],
                    [-141.1,-18.0],[-141.1,-18.5]]]},
                "assets":{"B04":{"href":"https://example.org/B04.jp2","type":"image/jp2"},
                          "SCL":{"href":"https://example.org/SCL.jp2","proj:epsg":32707}}}
    def test_item_verifie_et_masque_non_assimile_pixels(self):
        r=audit(self.item())
        self.assertEqual(r["points_couverts_par_empreinte"],[1,2,3,4,5])
        self.assertEqual(r["nombre_assets"],2)
        self.assertEqual(r["publication"]["raster"],0)
        self.assertEqual(r["classification_geographique"],"NON_ETABLIE")

    def test_scene_differente_refusee(self):
        i=self.item()
        i["id"]="UNKNOWN"
        with self.assertRaises(ValueError):
            audit(i)

if __name__=="__main__":
    unittest.main()
