"""Pays de la Loire : quatre transitions sans alignement Pactols automatique."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_pdl_quatre_sans_exactmatch_2026 import verifier_cog,compatible,CASES,SCHEMA

class PDLQuatreSansMatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cog=json.loads((ROOT/"docs/data/lieux-chronologie/cog-pdl.json").read_text(encoding="utf-8"))
  cls.publie=json.loads((ROOT/"docs/data/lieux-chronologie/pactols-pdl-2026.json").read_text(encoding="utf-8"))

 def test_quatre_histoires_distinctes(self):
  h=verifier_cog(self.cog,self.publie)
  self.assertEqual(set(h),set(CASES))
  self.assertEqual([h[k]["type_transition"] for k in CASES],[
   "RENOMMAGE_CODE_CONSERVE","RETABLISSEMENT_APRES_DEFUSION",
   "RETABLISSEMENT_APRES_DEFUSION","CREATION_COMMUNE_NOUVELLE"])
  self.assertEqual([h[k]["date_effet"] for k in CASES],[
    "2023-01-01","2024-01-01","2024-01-01","2024-01-01"])

 def test_separation_des_1140_liens_existants(self):
  a=verifier_cog(self.cog,self.publie)
  self.assertEqual(len(self.publie["alignements_Pactols_COG_valides_2026"]),1140)
  self.assertEqual(self.publie["communes_a_instruire"],88)
  codes={x["code_insee"] for x in self.publie["alignements_Pactols_COG_valides_2026"]}
  self.assertFalse(set(a)&codes)

 def test_anciens_libelles_sont_identifies_sans_valider(self):
  self.assertTrue(compatible("Grandchamps-des-Fontaines",CASES["44066"]))
  self.assertTrue(compatible("Grandchamp-des-Fontaines",CASES["44066"]))
  self.assertTrue(compatible("Thouarsais-Bouildroux",CASES["85292"]))
  self.assertTrue(compatible("Rives-du-Fougerais",CASES["85292"]))
  self.assertFalse(compatible("Saint-Sulpice-en-Pareds",CASES["85292"]))

 def test_modifier_un_evenement_cog_bloque_la_recette(self):
  cog=copy.deepcopy(self.cog)
  cog["lignes_mouvements_cog"]=[x for x in cog["lignes_mouvements_cog"]
      if not (x["code_apres"]=="85165" and x["date_effet"]=="2024-01-01")]
  with self.assertRaisesRegex(ValueError,"Mouvement"):
   verifier_cog(cog,self.publie)

if __name__=="__main__":unittest.main()
