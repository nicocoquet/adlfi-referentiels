"""Garanties des neuf collisions historiques et couverture 1212/1228."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_pdl_neuf_collisions_historiques_2026 import (
    SCHEMA,CODES,PUBS,verifier_publications
)

class NeufCollisionsPDLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog=json.loads((ROOT/"docs/data/lieux-chronologie/cog-pdl.json").read_text(encoding="utf-8"))

    def test_neuf_codes_distincts_exclus_de_1212(self):
        self.assertEqual(len(CODES),9)
        self.assertEqual(len(set(CODES)),9)
        self.assertEqual(len(PUBS),7)
        used_arks=verifier_publications(ROOT/"docs/data/lieux-chronologie")
        self.assertEqual(len(used_arks),1212)
        self.assertIn("audit",SCHEMA)

    def test_noms_cog_2026_et_mouvements(self):
        cur={r["code_insee"]:r for r in self.cog["periodes_com"]
             if r["typecom"]=="COM" and r["debut_inclus"]<="2026-01-01" and
             (r["fin_exclue"] is None or r["fin_exclue"]>"2026-01-01")}
        self.assertEqual(len(cur),1228)
        for code,nom in CODES.items():
            self.assertEqual(cur[code]["libelle"],nom)
            self.assertTrue(any(m["mod"]=="32" and m["code_apres"]==code
                                for m in self.cog["lignes_mouvements_cog"]),code)

    def test_noms_anciens_ou_reprises(self):
        expected={
           "49018":["Baugé","Baugé-en-Anjou"],
           "49160":["Ingrandes","Ingrandes-Le Fresne sur Loire",
                     "Ingrandes-le-Fresne-sur-Loire"],
           "49176":["Le Lion-d'Angers"],
           "49244":["La Pommeraye","Mauges-sur-Loire"],
           "53161":["Montsûrs","Montsûrs-Saint-Céneré","Montsûrs"],
           "53255":["Sainte-Suzanne","Sainte-Suzanne-et-Chammes"],
           "72137":["La Fresnaye-sur-Chédouet","Villeneuve-en-Perseigne"],
           "72176":["Le Lude"],
           "85084":["Les Essarts","Essarts en Bocage","Essarts-en-Bocage"],
        }
        for code,names in expected.items():
            rows=sorted([p for p in self.cog["periodes_com"]
                         if p["code_insee"]==code and p["typecom"]=="COM"],
                        key=lambda x:x["debut_inclus"])
            self.assertEqual([x["libelle"] for x in rows],names,code)

if __name__=="__main__":
    unittest.main()
