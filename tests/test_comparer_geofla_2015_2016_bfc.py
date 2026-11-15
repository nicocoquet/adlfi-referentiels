"""Validation sans réseau du modèle GEOFLA 2015–2016 du pilote BFC."""
import sys
import unittest
from pathlib import Path
from shapely.geometry import Polygon
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from comparer_geofla_2015_2016_bfc import (
    BFC_2015,BFC_2016,verifier_hierarchie,mesures,exporter)

class Geofla2016Tests(unittest.TestCase):
    def test_succession_cog_de_8_departements(self):
        self.assertEqual(set(BFC_2015),{"26","43"})
        self.assertEqual(BFC_2016["27"],{"21","25","39","58","70","71","89","90"})
    def test_hierarchie_2016_rejete_anciens_codes_reg(self):
        fake={code:("26",None) for code in BFC_2016["27"]}
        with self.assertRaisesRegex(ValueError,"Rattachement GEOFLA 2016 incorrect"):
            verifier_hierarchie(fake,BFC_2016,"2016")
    def test_identite_geometrique_donne_100pct_recouvrement(self):
        a=Polygon([(0,0),(1000,0),(1000,1000),(0,1000)])
        r=mesures(a,a)
        self.assertEqual(r["intersection_sur_union_pct"],100)
        self.assertEqual(r["difference_symetrique_km2"],0)
    def test_difference_cartographique_nest_pas_deduite_de_la_fusion(self):
        a=Polygon([(0,0),(1000,0),(1000,1000),(0,1000)])
        b=Polygon([(10,0),(1010,0),(1010,1000),(10,1000)])
        r=mesures(a,b)
        self.assertGreater(r["difference_symetrique_km2"],0)
        self.assertLess(r["intersection_sur_union_pct"],100)
    def test_interdiction_de_publier(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"docs"):
                exporter({}, {}, Path(d)/"docs"/"bfc")
if __name__=="__main__":
    unittest.main()
