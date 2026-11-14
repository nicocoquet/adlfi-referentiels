"""Recette du moteur national COG : durée, statuts et préfixes d'ID."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from preparer_index_cog_national_temporel import (
  segment,actif,vues_premier_janvier,SCHEMA
)

class NationalTemporel(unittest.TestCase):
 def test_prefixe_code_ne_vaut_pas_localisation(self):
  self.assertEqual(segment("39012"),"39") # Antorpe associée à Saint-Vit (25)
  self.assertEqual(segment("52210"),"52") # Frettes associée à Champlitte (70)
  self.assertEqual(segment("2A001"),"2A")
  self.assertEqual(segment("97101"),"97")
  with self.assertRaises(ValueError):segment("3901")
 def test_instant_premier_janvier_et_fin_exclue(self):
  sample={"periodes_COM":[
    dict(code_insee="25368",libelle="Marchaux",debut_inclus="1943-01-01",fin_exclue="2018-01-01"),
    dict(code_insee="25368",libelle="Marchaux-Chaudefontaine",debut_inclus="2018-01-01",fin_exclue=None)],
   "periodes_ARM":[],
   "observations_COMA_COMD_2026":[dict(code_insee="39012",typecom="COMA",libelle="Antorpe")],
   "mouvements":[dict(id="m1",date_effet="2018-01-01"),dict(id="m2",date_effet="2020-03-15")]}
  a=vues_premier_janvier(sample,2017);b=vues_premier_janvier(sample,2018)
  self.assertEqual([x["libelle"] for x in a["COM"]],["Marchaux"])
  self.assertEqual([x["libelle"] for x in b["COM"]],["Marchaux-Chaudefontaine"])
  self.assertEqual(len(vues_premier_janvier(sample,2020)["mouvements_survenus"]),1)
  self.assertEqual(len(vues_premier_janvier(sample,2021)["mouvements_survenus"]),2)
  self.assertEqual(vues_premier_janvier(sample,2017)["COMA_COMD_observes"],[])
  self.assertEqual(len(vues_premier_janvier(sample,2026)["COMA_COMD_observes"]),1)
  self.assertEqual(vues_premier_janvier(sample,2026)["contours_historiques"],[])
 def test_annees_hors_borne(self):
  for x in (1942,2027,2025.0,True,"2025"):
   with self.assertRaises(ValueError):vues_premier_janvier(
      {"periodes_COM":[],"periodes_ARM":[],"observations_COMA_COMD_2026":[],
       "mouvements":[]},x)
if __name__=="__main__":unittest.main()
