"""Le registre des 36 décisions ne transforme pas un ARK confirmé en exactMatch."""
from __future__ import annotations
import copy,csv,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from verifier_decisions_nouvelle_caledonie_spm_mayotte_2026 import lire_csv
INDEX=json.loads((ROOT/"docs/data/lieux-outremer/recherche-2026.json").read_text(encoding="utf-8"))
REG=ROOT/"recette/lieux/VALIDATIONS-NC-SPM-DEMBENI-2026.csv"
class TestDecisions(unittest.TestCase):
 def test_36_codes_uniques_et_dembeni_separee(self):
  r=lire_csv(REG,INDEX)
  self.assertEqual(len(r),36)
  self.assertEqual(sum(c.startswith("988") for c in r),33)
  self.assertEqual(r["97501"]["ark_pactols"],"26678/pcrtQAMzeGHldU")
  self.assertEqual(r["97502"]["ark_pactols"],"26678/pcrtYQmFfwxLq8")
  self.assertEqual(r["98809"]["ark_pactols"],"26678/pcrti4LqTHByEs")
  self.assertEqual(r["97607"]["ark_pactols"],"26678/crtZcuFSJVYZU")
  self.assertNotEqual(r["97607"]["statut_validation"],"VALIDE_ADLFI_2026")
  self.assertEqual(len(INDEX["pactols_valides"]),176)
 def test_aucune_promotion_dembeni_sans_preuve(self):
  raw=REG.read_text(encoding="utf-8")
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/"bad.csv"
   p.write_text(raw.replace("ARK_CONFIRME_EDITORIALEMENT_LIEN_NON_CERTIFIE_PAR_EXACTMATCH",
                            "skos:exactMatch"),encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"Dembeni"):lire_csv(p,INDEX)
 def test_aucun_ark_double(self):
  raw=REG.read_text(encoding="utf-8")
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/"bad.csv"
   p.write_text(raw.replace("26678/pcrti4LqTHByEs","26678/pcrtYQmFfwxLq8"),encoding="utf-8")
   with self.assertRaises(ValueError):lire_csv(p,INDEX)
if __name__=="__main__":unittest.main()
