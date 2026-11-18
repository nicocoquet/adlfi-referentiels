"""Cohérence de la publication Chemillé 49092 au millésime 2026."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_pdl_chemille_49092_2026 import ARKS,SCHEMA,CODE,URI

class Chemille2026Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
        cls.pub=read("docs/data/lieux-chronologie/pactols-pdl-chemille-2026.json")
        cls.cog=read("docs/data/lieux-chronologie/cog-pdl.json")
        cls.earlier=[
         read("docs/data/lieux-chronologie/pactols-pdl-2026.json"),
         read("docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json"),
         read("docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot01-2026.json")
        ]

    def test_trois_arks_distincts_un_seul_publie(self):
        p=self.pub
        self.assertEqual(p["schema"],SCHEMA)
        self.assertEqual(p["alignements_publies_precedemment"],1148)
        self.assertEqual(p["nouveaux_alignements"],1)
        self.assertEqual(p["total_alignements_PDL_2026"],1149)
        self.assertEqual(p["communes_a_instruire"],79)
        rows=p["alignements_Pactols_COG_valides_2026"]
        self.assertEqual(len(rows),1)
        x=rows[0]
        self.assertEqual(x["ark_pactols"],ARKS["Chemillé-en-Anjou"])
        self.assertEqual(x["ark_ancienne_Chemille"],ARKS["Chemillé"])
        self.assertEqual(x["ark_ancienne_Chemille_Melay"],ARKS["Chemillé-Melay"])
        self.assertEqual(x["uri_insee"],URI)
        self.assertEqual(len(set(ARKS.values())),3)
        prev=[y for data in self.earlier for y in data["alignements_Pactols_COG_valides_2026"]]
        self.assertEqual(len(prev),1148)
        self.assertNotIn(CODE,{y["code_insee"] for y in prev})
        self.assertFalse(set(ARKS.values())&{y["ark_pactols"] for y in prev})

    def test_trois_episodes_com_conserves(self):
        com=sorted((r for r in self.cog["periodes_com"] if r["code_insee"]==CODE and r["typecom"]=="COM"),key=lambda x:x["debut_inclus"])
        self.assertEqual([(r["libelle"],r["debut_inclus"],r["fin_exclue"]) for r in com],[
         ("Chemillé","1943-01-01","2013-01-01"),
         ("Chemillé-Melay","2013-01-01","2015-12-15"),
         ("Chemillé-en-Anjou","2015-12-15",None)
        ])
        self.assertEqual(self.pub["alignements_Pactols_COG_valides_2026"][0]["dates_MOD32"],
                         ["2013-01-01","2015-12-15"])

    def test_les_geometries_et_l_histoire_restent_independantes(self):
        self.assertEqual(self.pub["nouvelles_geometries"],0)
        self.assertEqual(self.pub["liens_historiques_inferes"],0)
        self.assertEqual(self.pub["alignements_Pactols_COG_valides_2026"][0]["portee_chronologique"],"2026_SEULEMENT")
        self.assertEqual(self.pub["alignements_Pactols_COG_valides_2026"][0]["relations_historiques_inferees"],0)
if __name__=="__main__":
    unittest.main()
