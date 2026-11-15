"""Vérifier le filtrage conservateur des homonymies Pactols ultramarines."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from qualifier_candidats_pactols_outremer import classifier,norm

def candidat(famille,niveau,code,parent,pref,signaux):
 return {
   "famille":famille,"niveau":niveau,"code_cog":code,
   "code_parent_comer":parent,"pref_fr":json.dumps([pref]),
   "alt_fr":"[]","hidden_fr":"[]","signaux":signaux,
 }

class QualifierCandidatsOutremer(unittest.TestCase):
 def test_saint_barthelemy_landais_ne_devient_pas_antillais(self):
  row=candidat("COMER","collectivite_ou_territoire","977","",
      "Saint-Barthélemy (Landes)","pref_fr_qualifie")
  x=classifier(row)
  self.assertEqual(x["qualif"],"qualificatif_incompatible")
  self.assertEqual(x["a_examiner_prioritairement"],"non")
  self.assertEqual(x["statut_decision"],"A_INSTRUIRE_NON_VALIDE")
 def test_saint_barthelemy_antilles_et_lien_code_reste_candidat(self):
  x=classifier(candidat("COMER","collectivite_ou_territoire","977","",
       "Saint-Barthélemy (Antilles Françaises)",
       "lien_insee_code_meme_valeur|pref_fr_qualifie"))
  self.assertEqual(x["qualif"],"code_et_libelle")
  self.assertEqual(x["a_examiner_prioritairement"],"oui")
 def test_guadeloupe_contexte_compatible_sans_code(self):
  x=classifier(candidat("DROM","commune","97122","",
       "Port-Louis (Guadeloupe)","pref_fr_qualifie"))
  self.assertEqual(x["qualif"],"nom_qualifie_compatible")
 def test_code_contradiction_reste_visible(self):
  x=classifier(candidat("DROM","commune","97225","",
       "Saint-Pierre (La Réunion)","lien_insee_code_meme_valeur|pref_fr_qualifie"))
  self.assertEqual(x["qualif"],"code_seul_ou_nom_different")
  self.assertEqual(x["alerte_qualificatif"],"contexte_incompatible_avec_code")
 def test_clippertton_code_sans_identite_lexicale(self):
  x=classifier(candidat("COMER","subdivision","98901","989",
       "Île de Clipperton","lien_insee_code_meme_valeur"))
  self.assertEqual(x["qualif"],"code_seul_ou_nom_different")
  self.assertEqual(x["statut_decision"],"A_INSTRUIRE_NON_VALIDE")
 def test_accents(self):
  self.assertEqual(norm("Terre-Adélie"),"terre adelie")

if __name__=="__main__":
 unittest.main()
