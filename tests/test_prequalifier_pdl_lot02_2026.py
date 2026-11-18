"""Socle numérique immuable de la préqualification PDL après Chemillé."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from prequalifier_pdl_lot02_2026 import SCHEMA,BASE

class PrequalificationPDLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
        cls.data=[
          read("docs/data/lieux-chronologie/pactols-pdl-2026.json"),
          read("docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json"),
          read("docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot01-2026.json"),
          read("docs/data/lieux-chronologie/pactols-pdl-chemille-2026.json")
        ]
    def test_unicite_et_1149(self):
        entries=[x for d in self.data for x in d["alignements_Pactols_COG_valides_2026"]]
        self.assertEqual(len(entries),1149)
        self.assertEqual(len({x["code_insee"] for x in entries}),1149)
        self.assertEqual(len({x["ark_pactols"] for x in entries}),1149)
        self.assertTrue(set(BASE)<={x["code_insee"] for x in entries})
    def test_schema_audit_pas_publication(self):
        self.assertIn("recette",SCHEMA)
        self.assertEqual(len(BASE),6)
        self.assertEqual(len(set(BASE)),6)
if __name__=="__main__":
    unittest.main()
