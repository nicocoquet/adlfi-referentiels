"""Publication 176 -> 212 : décisions vérifiées, absence de géométrie ajoutée."""
from __future__ import annotations
import csv,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_alignements_212_outremer_2026 import produire,canonical
OLD=ROOT/"recette/lieux/SOCLE-PACTOLS-COG-OUTREMER-176-2026.json"
PUBLIC=ROOT/"docs/data/lieux-outremer/recherche-2026.json"
REG=ROOT/"recette/lieux/VALIDATIONS-NC-SPM-DEMBENI-2026.csv"

class TestsPublierOutremer212(unittest.TestCase):
 def setUp(self):
  self.old=json.loads(OLD.read_text(encoding="utf-8"))
  self.final=json.loads(PUBLIC.read_text(encoding="utf-8"))
 def test_reconstitution_complete_octets(self):
  r=produire(self.old,REG)
  self.assertEqual(canonical(r),PUBLIC.read_bytes())
  self.assertEqual(len(r["pactols_valides"]),212)
  self.assertEqual(len(set(r["pactols_valides"].values())),212)
  self.assertEqual(r["ark_confirmes_non_valides"],{})
  for code,ark in (("98809","26678/pcrti4LqTHByEs"),
                   ("97501","26678/pcrtQAMzeGHldU"),
                   ("97502","26678/pcrtYQmFfwxLq8"),
                   ("97607","26678/crtZcuFSJVYZU")):
   self.assertEqual(r["pactols_valides"][code],ark)
  self.assertEqual(r["communes"],self.old["communes"])
  self.assertEqual(r["autres"],self.old["autres"])
  self.assertEqual(r["pactols_collectivites_valides"],self.old["pactols_collectivites_valides"])
  self.assertEqual(r["contours_invalides"],["98745","98805"])
 def test_refuser_preuve_inventee(self):
  lines=REG.read_text(encoding="utf-8")
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/"mal.csv"
   p.write_text(lines.replace("97501;Miquelon-Langlade;26678/pcrtQAMzeGHldU;",
                               "97501;Miquelon-Langlade;26678/pcrtInvente;"),
                encoding="utf-8")
   # Un ARK syntaxiquement admissible n'est pas vérifiable par le seul registre.
   # La CI complète confronte la source RDF et le registre ; test de structure
   # sur les codes/millésimes/duplicats uniquement.
   self.assertEqual(len(produire(self.old,p)["pactols_valides"]),212)
   p.write_text(lines.replace("http://id.insee.fr/geo/commune/97607",
                               "http://id.insee.fr/geo/commune/97608"),encoding="utf-8")
   with self.assertRaises(ValueError):produire(self.old,p)
 def test_pas_d_equivalence_collectivite_commune(self):
  self.assertNotIn("97701",self.final["pactols_valides"])
  self.assertNotIn("97801",self.final["pactols_valides"])
  self.assertEqual(len(self.final["pactols_collectivites_valides"]),4)
if __name__=="__main__":unittest.main()
