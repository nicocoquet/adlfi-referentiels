"""Tests de logique des surfaces et des proportions sans accéder aux sources GEO PF."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from auditer_composition_geopf_top5 import CIBLES, ratio

class TestsComposition(unittest.TestCase):
    def test_cibles_provenant_de_pr84(self):
        self.assertEqual(CIBLES,("190","202","112","263","264"))
    def test_part_surface(self):
        self.assertEqual(ratio(25,100),.25)
        self.assertEqual(ratio(0,100),0)
        with self.assertRaises(ValueError):
            ratio(1,0)

if __name__=="__main__":
    unittest.main()
