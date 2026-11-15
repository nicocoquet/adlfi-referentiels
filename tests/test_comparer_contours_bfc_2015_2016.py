"""Tests de l'écart entre représentations, sans conclusion historique."""
import json
import importlib.util
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from comparer_contours_bfc_2015_2016 import comparer,ecrire

def fea(code,year,x):
    coords=[[x,47],[x+0.1,47],[x+0.1,47.1],[x,47.1],[x,47]]
    return {"type":"Feature","geometry":{"type":"Polygon","coordinates":[coords]},
        "properties":{"code_region":code,"millesime_geometrie":year,"pactols_valide":False}}

def fc(year,features):
    return {"type":"FeatureCollection","provenance":{
        "annee":year,"absence_de_retroprojection":True,
    },"features":features}

@unittest.skipUnless(importlib.util.find_spec("shapely") and importlib.util.find_spec("pyproj"),
                     "Tests géospatiaux exécutés dans la CI spécialisée avec shapely et pyproj")
class ComparaisonBFC(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup)
        self.d=Path(d.name)
        self.a=self.d/"2015.geojson";self.b=self.d/"2016.geojson"
        self.a.write_text(json.dumps(fc(2015,[fea("26",2015,4.3),fea("43",2015,5.3)])))
        self.b.write_text(json.dumps(fc(2016,[fea("27",2016,4.3)])))
    def test_mesure_ne_devient_pas_changement_administratif(self):
        r=comparer(self.a,self.b)
        self.assertEqual(r["geometries_historiques_reconstruites"],0)
        self.assertEqual(r["nouveaux_alignements_pactols"],0)
        self.assertEqual(r["changement_reel_de_surface"],"NON_INFERABLE")
        self.assertTrue(0<r["taux_recouvrement_iou_pourcent"]<100)
        self.assertGreater(r["surface_difference_symetrique_km2"],0)
    def test_refus_millesime_incompatible(self):
        d=json.loads(self.a.read_text())
        d["provenance"]["annee"]=2026
        self.a.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,"Millésime"):
            comparer(self.a,self.b)
    def test_refus_dune_correspondance_pactols_inferree(self):
        d=json.loads(self.b.read_text())
        d["features"][0]["properties"]["pactols_valide"]=True
        self.b.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,"validation Pactols"):
            comparer(self.a,self.b)
    def test_refus_export_dans_pages(self):
        with self.assertRaisesRegex(ValueError,"docs"):
            ecrire({},self.d/"docs"/"rapport.json")

if __name__=="__main__":
    unittest.main()
