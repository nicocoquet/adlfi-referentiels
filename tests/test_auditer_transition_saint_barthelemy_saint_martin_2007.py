"""Tests synthétiques : deux changements de statut, sans code communal 97701/97801."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_transition_saint_barthelemy_saint_martin_2007 as audit

class TestAntilles2007(unittest.TestCase):
 def test_schema_codes_et_provenance(self):
  self.assertEqual(set(audit.ENTITES),{"97123","97127"})
  self.assertEqual({x["collectivite"] for x in audit.ENTITES.values()},{"977","978"})
  self.assertEqual({x["code_cinq"] for x in audit.ENTITES.values()},{"97701","97801"})
  self.assertEqual(len(audit.SHAS),7)
  self.assertTrue(all(len(digest)==64 for digest in audit.SHAS.values()))
 def fixture(self):
  return {
    "v_commune_depuis_1943.csv":[
      {"TYPECOM":"COM","COM":key,"LIBELLE":item["nom"],
       "DATE_DEBUT":"1946-03-21","DATE_FIN":"2007-02-23"}
      for key,item in audit.ENTITES.items()],
    "v_mvt_commune_2026.csv":[
      {"COM_AV":key,"COM_AP":"","DATE_EFF":"2007-02-23","MOD":"30"}
      for key in audit.ENTITES],
    "v_commune_2026.csv":[{"TYPECOM":"COM","COM":"97101","LIBELLE":"Les Abymes"}],
    "v_comer_2026.csv":[{"COMER":item["collectivite"],"LIBELLE":item["nom"]}
                          for item in audit.ENTITES.values()],
    "v_tom_depuis_1943.csv":[
      {"COMER":item["collectivite"],"LIBELLE":item["nom"],
       "DATE_DEBUT":"2007-02-23","DATE_FIN":""} for item in audit.ENTITES.values()],
    "v_commune_comer_2026.csv":[
      {"COMER":item["collectivite"],"COM_COMER":item["code_cinq"],
       "LIBELLE":item["nom"],"NATURE_ZONAGE":"COM"} for item in audit.ENTITES.values()],
    "v_commune_outremer_depuis_1943.csv":[
      {"COM_COMER":item["code_cinq"],"LIBELLE":item["nom"],
       "DATE_DEBUT":"2007-02-23","DATE_FIN":"","NATURE_ZONAGE":"COM"}
      for item in audit.ENTITES.values()]
  }
 def analyser(self,rows):
  with (patch.object(audit,"sha",side_effect=lambda p:audit.SHAS[p.name]),
        patch.object(audit,"lire",side_effect=lambda p:rows[p.name])):
   return audit.analyser(Path("/tmp/cog"))
 def test_distinction_juridique_cog(self):
  data=self.analyser(self.fixture())
  self.assertEqual(data["schema"],"adlfi.lieux.antilles2007.audit.cog2026.v1")
  self.assertEqual(data["transition_codification_INSEE"],"2007-02-23")
  self.assertEqual(data["date_entree_vigueur_loi_organique"],"2007-02-22")
  self.assertEqual(data["bilan"]["nouvelles_relations_successions_juridiques_attestees"],2)
  self.assertEqual(data["bilan"]["destinations_COM_AP_COG"],0)
  self.assertFalse(data["bilan"]["publication_docs"])
  for ligne in data["lignes"]:
   self.assertIsNone(ligne["mouvement_communal_COG"]["com_ap"])
   self.assertFalse(ligne["mouvement_communal_COG"]["successeur_code_COG_atteste_par_mouvement"])
   self.assertFalse(ligne["code_application_5_positions"]["equivalent_a_commune_actuelle"])
   self.assertFalse(ligne["succession_juridique"]["identite_conceptuelle_Pactols_inferree"])
   self.assertIsNone(ligne["succession_juridique"]["date_effet_relation_precise_inferree"])
   self.assertIn(ligne["succession_juridique"]["article"],("18-X","18-XI"))
 def test_refuser_destination_cog_inventee(self):
  data=self.fixture();data["v_mvt_commune_2026.csv"][0]["COM_AP"]="97701"
  with self.assertRaisesRegex(ValueError,"MOD 30"):
   self.analyser(data)
 def test_refuser_commune_971_actuelle(self):
  data=self.fixture();data["v_commune_2026.csv"].append(
   {"TYPECOM":"COM","COM":"97123","LIBELLE":"Saint-Barthélemy"})
  with self.assertRaisesRegex(ValueError,"courante"):
   self.analyser(data)
 def test_refuser_code_977_actuel_non_identifie(self):
  data=self.fixture();data["v_comer_2026.csv"][0]["LIBELLE"]="Saint-Barthélémy"
  with self.assertRaisesRegex(ValueError,"Collectivité 2026"):
   self.analyser(data)

if __name__=="__main__":
 unittest.main()
