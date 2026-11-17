"""Tests sans réseau du préflight Copernicus Hao."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from inventorier_imagerie_hao_stac import interroger, make_url, summarise_feature, auditer, POINTS

def fake_feature(fid,geometry,bbox):
    return {
      "type":"Feature","id":fid,"collection":"sentinel-2-l2a",
      "properties":{"datetime":"2025-06-15T17:20:00Z","eo:cloud_cover":12},
      "bbox":bbox,"geometry":geometry,
      "links":[{"rel":"self","href":"https://example.invalid/stac/"+fid}]
    }

class TestCatalogueHao(unittest.TestCase):
    def test_url_avec_emprise_et_fenetre(self):
        url=make_url("2025-01-01T00:00:00Z","2025-12-31T23:59:59Z")
        self.assertIn("bbox=",url)
        self.assertIn("datetime=",url)
        self.assertIn("sentinel-2-l2a",url)

    def test_empreinte_couvrant_cinq_points(self):
        geometry={"type":"Polygon","coordinates":[[
          [-141.1,-18.5],[-140.6,-18.5],[-140.6,-18.0],[-141.1,-18.0],[-141.1,-18.5]
        ]]}
        f=fake_feature("scene-test",geometry,[-141.1,-18.5,-140.6,-18.0])
        one=summarise_feature(f)
        self.assertEqual(one["points_couverts_par_empreinte"],[1,2,3,4,5])
        self.assertEqual(one["cloud_cover_tuile_pourcent"],12)
        result=interroger("2025-01-01T00:00:00Z","2025-12-31T23:59:59Z",
                         lambda url:{"type":"FeatureCollection","features":[f],"links":[]})
        self.assertEqual(result["points_sans_scene"],[])
        self.assertTrue(result["consultation_exhaustive"])

    def test_pas_de_date_inventee(self):
        with self.assertRaisesRegex(ValueError,"date"):
            summarise_feature({"properties":{},"geometry":None})

    def test_erreur_serveur_ne_devient_pas_non_couverture(self):
        def invalid(url):
            raise ConnectionError("Service temporairement inaccessible")
        r=auditer(fetch=invalid)
        self.assertEqual(len(r["fenetres"]),2)
        self.assertTrue(all(x["statut"]=="CATALOGUE_INACCESSIBLE_OU_INEXPLOITABLE" for x in r["fenetres"]))
        self.assertTrue(all(x["points_sans_scene"] is None for x in r["fenetres"]))
        self.assertEqual(r["publication"]["imagery"],0)

if __name__=="__main__":
    unittest.main()
