"""ISPF : tests de format et garde-fous avant publication des 98 associées."""
from __future__ import annotations
import sys,tempfile,json,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import qualifier_communes_associees_ispf as q
class TestISPF(unittest.TestCase):
 def test_structure_documentaire(self):
  self.assertEqual(set(q.HEADERS),{"Subdivision","Commune","Commune associée","Geo","Ile"})
  self.assertEqual(q.FIELD_NAMES["Commune associée"],
    ["IDComas","IDCom","IDSub","Comas","Commune","Subdivision"])
  self.assertEqual(q.FIELD_NAMES["Geo"][0],"IDGeo")
  self.assertEqual(q.FIELD_NAMES["Geo"][2],"IDComas")
  self.assertEqual(q.FIELD_NAMES["Geo"][-3:],["isCom","isComas","isIleRattachee"])
 def test_homonymie_normale(self):
  self.assertEqual(q.normaliser("Àvéra"),q.normaliser("Avera"))
  self.assertNotEqual("501","441")
  self.assertNotEqual("98750","98744")
 def test_entete_erronee(self):
  source={"feuille":"Commune associée",
    "lignes":[{"row":1,"cells":{"A":"IDComas","B":"CodeCOG","C":"IDSub",
       "D":"Comas","E":"Commune","F":"Subdivision"}},
       {"row":2,"cells":{"A":"501","B":"50","C":"2","D":"Avera",
          "E":"Taputapuatea","F":"Iles Sous-Le-Vent"}}]}
  with self.assertRaisesRegex(ValueError,"Colonnes"):q.rows(source)
 def test_fichier_change_refuse(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp)/"codes.xlsx";p.write_bytes(b"faux classeur")
   i=Path(temp)/"index.json";i.write_text("{}")
   with self.assertRaisesRegex(ValueError,"changé"):q.qualifier(p,i)
 def test_registre_non_ajoute_aux_communes_en_cas_source_invalide(self):
  self.assertNotEqual(q.SHA,"")
  self.assertEqual(q.SOURCE,
   "https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx")
if __name__=="__main__":unittest.main()
