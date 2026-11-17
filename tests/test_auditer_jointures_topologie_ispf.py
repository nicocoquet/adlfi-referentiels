"""Garde-fous sur les codes de jointure ISPF : aucun rapprochement lexical."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from auditer_jointures_topologie_ispf import code, indexer
from shapely.geometry import Polygon
from shapely.validation import explain_validity

class TestJointuresISPF(unittest.TestCase):
    def test_codes_zero_padding(self):
        self.assertEqual(code(11.0, 2), "11")
        self.assertEqual(code("011", 3), "011")
        self.assertEqual(code(1, 3), "001")

    def test_refus_code_fractionnaire(self):
        for value in (1.2, None, True, "11.0", "X11"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                code(value, 3)

    def test_duplicate_non_efface(self):
        found, duplicates = indexer([{"IDComas": 111}, {"IDComas": 111.0}], "IDComas", 3)
        self.assertEqual(len(found), 1)
        self.assertEqual(duplicates, ["111"])

    def test_topologie_ogc_reconnait_auto_intersection(self):
        bowtie = Polygon([(0,0), (2,2), (0,2), (2,0), (0,0)])
        self.assertFalse(bowtie.is_valid)
        self.assertIn("intersect", explain_validity(bowtie).lower())

if __name__ == "__main__":
    unittest.main()
