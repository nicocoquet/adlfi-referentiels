"""Préinstruction 986 : circonscriptions non communes et statuts distincts."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_cog_wallis_futuna_2026 as a
class TestWallisFutuna(unittest.TestCase):
 def fixture(self):
  return {
   "v_comer_2026.csv":[{"COMER":"986","LIBELLE":"Wallis-et-Futuna"}],
   "v_commune_comer_2026.csv":[
     {"COMER":"986","COM_COMER":code,"LIBELLE":name,"NATURE_ZONAGE":"CIR"}
     for code,name in a.EXPECTED.items()],
   "v_tom_depuis_1943.csv":[
     {"COMER":"986","LIBELLE":"Wallis-et-Futuna","DATE_DEBUT":"1985-01-01","DATE_FIN":""},
     {"COMER":"98609","LIBELLE":"Wallis-et-Futuna","DATE_DEBUT":"1961-07-30","DATE_FIN":"1985-01-01"}],
   "v_commune_outremer_depuis_1943.csv":[
     {"COM_COMER":code,"LIBELLE":name,"NATURE_ZONAGE":"CIR",
      "DATE_DEBUT":"1985-01-01","DATE_FIN":""}
     for code,name in a.EXPECTED.items()],
   "v_commune_2026.csv":[{"COM":"97101","TYPECOM":"COM"}],
   "v_commune_depuis_1943.csv":[{"COM":"97101","TYPECOM":"COM"}]
  }
 def analyse(self,table):
  with (patch.object(a,"sha",side_effect=lambda p:a.SHAS[p.name]),
        patch.object(a,"read",side_effect=lambda p:table[p.name])):
   return a.analyser(Path("/tmp/cog"))
 def test_invariants(self):
  d=self.analyse(self.fixture())
  self.assertEqual(d["territoire_2026"]["nombre_communes"],0)
  self.assertEqual(d["territoire_2026"]["nombre_circonscriptions"],3)
  self.assertEqual({c["code"] for c in d["circonscriptions_2026"]},{"98611","98612","98613"})
  self.assertEqual(len(d["episodes_circonscriptions_COG"]),3)
  self.assertEqual(d["bilan"]["nouveaux_alignements_Pactols"],0)
  self.assertFalse(d["bilan"]["publication_docs"])
  self.assertTrue(d["distinctions"]["distinction_circonscription_royaume_coutumier"])
  self.assertFalse(d["distinctions"]["equivalence_98607_98609_986_inferree"])
  self.assertEqual(d["anciens_codes_territoriaux_a_qualifier"][0]["code"],"98609")
 def test_enregistrer_ancien_code_sans_inferer_succession(self):
  t=self.fixture();t["v_tom_depuis_1943.csv"].append({
    "COMER":"98607","LIBELLE":"Wallis et Futuna (historique)",
    "DATE_DEBUT":"1943-01-01","DATE_FIN":"1961-07-30"})
  d=self.analyse(t)
  self.assertEqual(len(d["anciens_codes_territoriaux_a_qualifier"]),2)
  self.assertEqual(d["bilan"]["successions_de_codes_inferrees"],0)
 def test_refuser_commune_inventee(self):
  t=self.fixture();t["v_commune_2026.csv"].append({"COM":"98611","TYPECOM":"COM"})
  with self.assertRaisesRegex(ValueError,"commune courante"):self.analyse(t)
 def test_refuser_circonscriptions_incompletes(self):
  t=self.fixture();t["v_commune_comer_2026.csv"].pop()
  with self.assertRaisesRegex(ValueError,"trois circonscriptions"):self.analyse(t)
 def test_refuser_nature_non_cir(self):
  t=self.fixture();t["v_commune_comer_2026.csv"][0]["NATURE_ZONAGE"]="COM"
  with self.assertRaisesRegex(ValueError,"trois circonscriptions"):self.analyse(t)
 def test_dates_non_creatrices(self):
  with self.assertRaisesRegex(ValueError,"Période COG"):
   a.to_episode({"COM_COMER":"98611","LIBELLE":"Alo","NATURE_ZONAGE":"CIR",
                 "DATE_DEBUT":"1985-01-01","DATE_FIN":"1984-01-01"},
                "COM_COMER","CIRCONSCRIPTION_COG")

if __name__=="__main__":unittest.main()
