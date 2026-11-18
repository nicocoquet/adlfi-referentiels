"""Contrôle des 3 créations MOD32 et de leurs anciennes COMD."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_pdl_trois_collisions_2026 import CASES,PREVIOUS,SCHEMA
class TroisCollisionsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/"docs/data/lieux-chronologie"
  read=lambda n:json.loads((base/n).read_text(encoding="utf-8"))
  cls.pub=read("pactols-pdl-trois-collisions-2026.json")
  cls.cog=read("cog-pdl.json")
  cls.prev=[read(x) for x in PREVIOUS]
 def test_publication_et_codes_uniques(self):
  p=self.pub
  self.assertEqual(p["schema"],SCHEMA)
  self.assertEqual(p["alignements_publies_precedemment"],1212)
  self.assertEqual(p["total_alignements_PDL_2026"],1215)
  self.assertEqual(p["communes_a_instruire"],13)
  old=[a for d in self.prev for a in d["alignements_Pactols_COG_valides_2026"]]
  new=p["alignements_Pactols_COG_valides_2026"]
  self.assertEqual(len(old),1212)
  self.assertEqual(len(new),3)
  self.assertEqual(len({x["code_insee"] for x in old+new}),1215)
  self.assertEqual(len({x["ark_pactols"] for x in old+new}),1215)
  self.assertFalse({x["ark_ancienne_commune_distinct"] for x in new}&
                   {x["ark_pactols"] for x in old+new})
 def test_mod32_et_comd_avec_dates(self):
  for x in self.pub["alignements_Pactols_COG_valides_2026"]:
   code=x["code_insee"]
   self.assertIn(code,CASES)
   name,old,day,ark,anc=CASES[code]
   self.assertEqual((x["libelle_COG_2026"],x["ark_pactols"],
                     x["ark_ancienne_commune_distinct"]),(name,ark,anc))
   moves=[m for m in self.cog["lignes_mouvements_cog"]
          if m["code_apres"]==code and m["date_effet"]==day and m["mod"]=="32"]
   self.assertTrue(any(m["code_avant"]==code and m["typecom_apres"]=="COM" and
       m["libelle_avant"]==old and m["libelle_apres"]==name for m in moves),code)
   self.assertTrue(any(m["code_avant"]==code and m["typecom_apres"]=="COMD" and
       m["libelle_apres"]==old for m in moves),code)
   self.assertEqual(x["portee_chronologique"],"2026_SEULEMENT")
   self.assertEqual(x["relations_historiques_inferees"],0)
 def test_aucune_geometrie_ajoutee(self):
  self.assertEqual(self.pub["nouvelles_geometries"],0)
  self.assertEqual(self.pub["liens_historiques_inferes"],0)
if __name__=="__main__":unittest.main()
