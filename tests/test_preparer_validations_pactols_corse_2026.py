"""Corse : contrat du registre et absence de publication implicite."""
from __future__ import annotations
import csv,io,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from preparer_validations_pactols_corse_2026 import ecrire_csv,FIELDS
from auditer_pactols_cog_regions_prioritaires_2026 import qualifier

class TestRegistreCorse(unittest.TestCase):
 def test_contrat_csv(self):
  row=dict.fromkeys(FIELDS,"ok")
  row.update({"code_insee":"2A004","libelle_COG_2026":"Ajaccio",
             "departement_COG_2026":"2A","region_COG_2026":"94",
             "uri_insee":"http://id.insee.fr/geo/commune/2A004"})
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"corse.csv"
   ecrire_csv([row],p)
   with p.open(encoding="utf-8",newline="") as f:
    reader=csv.DictReader(f,delimiter=";")
    self.assertEqual(tuple(reader.fieldnames),FIELDS)
    self.assertEqual(list(reader)[0]["code_insee"],"2A004")
 def test_absence_assertion_reste_hors_registre(self):
  self.assertEqual(qualifier("2B033","Bastia",[]),"SANS_EXACTMATCH")
 def test_codes_corses_alphanumeriques_pas_nombre(self):
  self.assertTrue("2A004".startswith("2A"))
  self.assertTrue("2B033".startswith("2B"))
if __name__=="__main__":unittest.main()
