"""Préflight non validant : événements MOD32 et MOD21 de 2024."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_pdl_ingrandes_essarts_2024 import CODES,PUBS,SCHEMA
class Instruction2024(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/"docs/data/lieux-chronologie"
  cls.data=[json.loads((base/x).read_text(encoding="utf-8")) for x in PUBS]
  cls.cog=json.loads((base/"cog-pdl.json").read_text(encoding="utf-8"))
 def test_publications_existantes(self):
  links=[a for d in self.data for a in d["alignements_Pactols_COG_valides_2026"]]
  self.assertEqual(len(links),1215)
  self.assertEqual(len({x["code_insee"] for x in links}),1215)
  self.assertEqual(len({x["ark_pactols"] for x in links}),1215)
  self.assertTrue(set(CODES).isdisjoint(x["code_insee"] for x in links))
 def test_deux_evenements_distincts(self):
  movements=self.cog["lignes_mouvements_cog"]
  self.assertTrue(any(x["mod"]=="32" and x["code_avant"]=="49160" and x["code_apres"]=="49160" and x["date_effet"]=="2024-01-01" for x in movements))
  self.assertTrue(any(x["mod"]=="21" and x["code_avant"]=="85084" and x["code_apres"]=="85084" and x["date_effet"]=="2024-01-01" for x in movements))
  self.assertEqual(CODES["49160"]["ark_candidat"],"26678/pcrtj64zr6gnns4mnfd2828b")
  self.assertEqual(CODES["85084"]["ark_candidat"],"26678/pcrt0PrU3oVWxo")
  self.assertIn("audit",SCHEMA)
if __name__=="__main__":unittest.main()
