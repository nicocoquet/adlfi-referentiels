"""Polynésie : 48 communes COG ≠ communes associées / subdivisions / îles."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_cog_polynesie_2026 as a
class AuditPolynesieTest(unittest.TestCase):
 def fixture(self):
  names={f"987{i}":f"Commune test {i}" for i in range(11,59)}
  return names,{
   "v_comer_2026.csv":[{"COMER":"987","LIBELLE":"Polynésie française"}],
   "v_commune_comer_2026.csv":[
    {"COMER":"987","COM_COMER":code,"LIBELLE":label,"NATURE_ZONAGE":"COM"}
    for code,label in names.items()],
   "v_tom_depuis_1943.csv":[
    {"COMER":"987","LIBELLE":"Polynésie française","DATE_DEBUT":"1985-01-01","DATE_FIN":""}],
   "v_commune_outremer_depuis_1943.csv":[
    {"COM_COMER":code,"LIBELLE":label,"NATURE_ZONAGE":"COM",
      "DATE_DEBUT":"1972-05-17","DATE_FIN":""}
    for code,label in names.items()]+
    [{"COM_COMER":"98799","LIBELLE":"Clipperton","NATURE_ZONAGE":"COM",
      "DATE_DEBUT":"1972-05-17","DATE_FIN":"2007-02-22"}],
   "v_commune_2026.csv":[{"COM":"97101"}],
   "v_commune_depuis_1943.csv":[{"COM":"97101"}]
  }
 def run_audit(self,rows):
  names,table=rows
  with (patch.object(a,"sha",side_effect=lambda p:a.SHAS[p.name]),
        patch.object(a,"read",side_effect=lambda p:table[p.name]),
        patch.object(a,"codes_publics",return_value=names)):
   return a.analyser(Path("/tmp/cog"),Path("/tmp/public.json"))
 def test_comptage_et_categories_independantes(self):
  d=self.run_audit(self.fixture())
  self.assertEqual(d["rapport"]["communes_COG_2026"],48)
  self.assertEqual(d["rapport"]["episodes_communes_COG"],48)
  self.assertEqual(d["rapport"]["communes_associees_ISPF_a_documenter_separement"],98)
  self.assertEqual(d["rapport"]["communes_avec_associees_ISPF"],30)
  self.assertEqual(d["rapport"]["communes_sans_associees_ISPF"],18)
  self.assertEqual(d["rapport"]["subdivisions_administratives_etat"],5)
  self.assertEqual(d["rapport"]["autres_codes_historiques_COG"],1)
  self.assertEqual(d["autres_codes_historiques_a_instruire"][0]["code"],"98799")
  self.assertEqual(d["rapport"]["nouveaux_alignements_Pactols"],0)
  self.assertFalse(d["rapport"]["creation_de_toutes_les_communes_en_1972_inferree"])
  self.assertFalse(d["rapport"]["historique_des_communes_associees_COG_inferre"])
  self.assertFalse(d["rapport"]["publication_docs"])
 def test_refuser_nature_coma_comme_commune_principale(self):
  names,t=self.fixture()
  t["v_commune_comer_2026.csv"][0]["NATURE_ZONAGE"]="COMA"
  with self.assertRaisesRegex(ValueError,"divergent"):
   self.run_audit((names,t))
 def test_refuser_commune_987_dans_table_drom(self):
  names,t=self.fixture();t["v_commune_2026.csv"].append({"COM":"98711"})
  with self.assertRaisesRegex(ValueError,"DROM"):
   self.run_audit((names,t))
 def test_refuser_historique_incomplet(self):
  names,t=self.fixture();t["v_commune_outremer_depuis_1943.csv"].pop(0)
  with self.assertRaisesRegex(ValueError,"incomplet"):
   self.run_audit((names,t))
 def test_refuser_annee_bizarre(self):
  with self.assertRaisesRegex(ValueError,"Dates"):
   a.episode({"COM_COMER":"98711","LIBELLE":"Anaa","NATURE_ZONAGE":"COM",
    "DATE_DEBUT":"1985-01-01","DATE_FIN":"1972-05-17"},"COM_COMER","COMMUNE")
if __name__=="__main__":unittest.main()
