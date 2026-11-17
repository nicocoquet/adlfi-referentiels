"""Reproduction autonome des 4 alignements collectifs en conservant les communes."""
from __future__ import annotations
import csv,json,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from extraire_index_public_outremer_2026 import appliquer_validations_collectivites
REG=ROOT/"recette/lieux/COLLECTIVITES-COMER-VALIDATIONS-PACTOLS-COG-2026.csv"
PUBLIC=ROOT/"recette/lieux/SOCLE-PACTOLS-COG-OUTREMER-176-2026.json"
class TestBuilderCollectivites(unittest.TestCase):
 def base(self):
  x=json.loads(PUBLIC.read_text(encoding="utf-8"))
  del x["pactols_collectivites_valides"]
  return x
 def test_quatre_autorites_ajoutees_sans_modifier_les_communes(self):
  socle=self.base()
  old=json.dumps(socle["pactols_valides"],sort_keys=True)
  applied=appliquer_validations_collectivites(socle,REG)
  self.assertEqual(applied["pactols_collectivites_valides"],{
   "977":"26678/pcrtrGdtY56gmH",
   "978":"26678/pcrty5LooX8FgU",
   "986":"26678/pcrtwFq5jKHO3k",
   "987":"26678/pcrt4K8nLVxWOP"})
  self.assertEqual(json.dumps(applied["pactols_valides"],sort_keys=True),old)
  self.assertEqual(len(applied["autres"]),21)
  self.assertEqual(applied["contours_invalides"],["98745","98805"])
  self.assertEqual(applied["ark_confirmes_non_valides"],{"97607":"26678/crtZcuFSJVYZU"})
  self.assertEqual(applied,json.loads(PUBLIC.read_text()))
  with self.assertRaisesRegex(ValueError,"déjà publiées"):
   appliquer_validations_collectivites(applied,REG)
 def test_refuser_transfert_pour_code_97701(self):
  content=REG.read_text(encoding="utf-8")
  with TemporaryDirectory() as tmp:
   filename=Path(tmp)/"fake.csv"
   filename.write_text(content.replace("977;Saint-Barthélemy;","97701;Saint-Barthélemy;"),
                       encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"Quatre codes"):
    appliquer_validations_collectivites(self.base(),filename)
 def test_refuser_confusion_des_familles_INSEE(self):
  content=REG.read_text(encoding="utf-8")
  with TemporaryDirectory() as tmp:
   filename=Path(tmp)/"fake.csv"
   filename.write_text(content.replace(
    "http://id.insee.fr/geo/collectiviteDOutreMer/986",
    "http://id.insee.fr/geo/commune/98611"),encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"Preuve de collectivité"):
    appliquer_validations_collectivites(self.base(),filename)
if __name__=="__main__":unittest.main()
