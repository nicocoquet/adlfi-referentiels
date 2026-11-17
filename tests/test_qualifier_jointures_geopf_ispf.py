"""Vérifications de normalisation des identifiants GEO PF, hors réseau."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from qualifier_jointures_geopf_ispf import code

class TestsCodesGeoPF(unittest.TestCase):
    def test_codes_geo_et_associes(self):
        self.assertEqual(code("20303",5),"20303")
        self.assertEqual(code(203.0,3),"203")
        self.assertEqual(code("20",2),"20")
        self.assertEqual(code(69),"69")
    def test_refus_codes_ambigus(self):
        for v in (None,False,3.1,"12a",""):
            with self.subTest(v=v),self.assertRaises(ValueError):
                code(v)

if __name__=="__main__":unittest.main()
