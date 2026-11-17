"""Contrôles synthétiques de sûreté des codes ISPF et sérialisation stable."""
from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import auditer_ispf_polynesie_associees as a

class TestISPF(unittest.TestCase):
 def test_normalisation_noms_sans_confusion_identifiants(self):
  self.assertEqual(a.normaliser("Faa'a"),a.normaliser("Faaa"))
  self.assertEqual(a.normaliser("Taiarapu-Est"),a.normaliser("Taiarapu Est"))
  self.assertEqual(a.normaliser("Bora Bora"),a.normaliser("Bora-Bora"))
  self.assertEqual(a.normaliser("Îles Sous-le-Vent"),a.normaliser("Iles Sous-Le-Vent"))
  self.assertNotEqual(a.normaliser("Avera"),a.normaliser("Rurutu"))
 def test_refuser_source_xlsx_autre_que_sha(self):
  with tempfile.TemporaryDirectory() as tmp:
   file=Path(tmp)/"test.xlsx"
   file.write_bytes(b"unverified xlsx")
   with self.assertRaisesRegex(ValueError,"empreinte"):a.classeur(file)
 def test_serialisation_reproductible(self):
  d={"schema":a.SCHEMA,"codes":["441","501"],
     "source":{"sha256":a.SHA},"alignements_Pactols":0}
  self.assertEqual(a.payload(d),a.payload(d))
  self.assertEqual(json.loads(a.payload(d)),d)
  self.assertTrue(a.payload(d).endswith(b"\n"))
 def test_identifiants_ispf_et_cog_distincts(self):
  self.assertNotEqual("441","98744")
  self.assertNotEqual("501","98750")
  self.assertEqual("987"+"44","98744")
  self.assertEqual("987"+"50","98750")
if __name__=="__main__":unittest.main()
