"""Les géométries des COM ne deviennent pas automatiquement des limites publiées."""
from __future__ import annotations
import sys,unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_contours_com_2026 import inventorier

def poly(code):
    return {"type":"Feature","properties":{"code":code},"geometry":{
        "type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}}

@unittest.skipUnless(importlib.util.find_spec('shapely'), 'Shapely absent du contrôle général ; recette géospatiale spécialisée')
class TestCom(unittest.TestCase):
    def test_un_polygone_valide_ne_publie_rien(self):
        out=inventorier({"type":"FeatureCollection","features":[poly("97501")]},
            {"97501":{"code":"97501","libelle_COG":"Miquelon-Langlade","territoire":"975"}},
            {"contours_invalides":["98745","98805"]})
        b=out["bilan"]
        self.assertEqual(b["geometries_valides"],1)
        self.assertEqual(b["nouvelles_geometries_publiees"],0)
        self.assertEqual(b["ark_pactols_inferes"],0)
        self.assertEqual(out["communes"][0]["publication"],"NON_PUBLIE")
        self.assertEqual(out["communes"][0]["evaluation_limite_juridique"],"NON_EFFECTUEE")
    def test_doublon_refuse(self):
        with self.assertRaisesRegex(ValueError,"dupliqué"):
            inventorier({"type":"FeatureCollection","features":[poly("97501"),poly("97501")]},
                {"97501":{"code":"97501","libelle_COG":"Miquelon-Langlade","territoire":"975"}},
                {"contours_invalides":["98745","98805"]})

if __name__=="__main__":unittest.main()
