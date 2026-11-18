"""PACA : valider 7 nouvelles communes sans confondre les 8 anciens ARK."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_paca_sept_communes_nouvelles_2026 import produire,ARKS
def sources():
 p={
 "audit":"recette/lieux/PACA-HUIT-COMMUNES-NOUVELLES-RDF-2026.json",
 "pilote":"docs/data/lieux.json",
 "complement":"docs/data/lieux-chronologie/pactols-paca-2026.json",
 "renommages":"docs/data/lieux-chronologie/pactols-paca-renommages-2026.json",
 "cog":"docs/data/lieux-chronologie/cog-paca.json"}
 return {n:json.loads((ROOT/f).read_text(encoding="utf-8")) for n,f in p.items()}
class SeptCommunesTests(unittest.TestCase):
 def test_exact_match_creation_documentee(self):
  a=sources()
  frozen=copy.deepcopy(a)
  r=produire(**a)
  self.assertEqual(r["alignements_total_PACA_2026"],945)
  self.assertEqual(r["communes_a_instruire"],1)
  self.assertEqual(r["exceptions_restantes"],["05001"])
  self.assertEqual(r["pilote_valide_conserve"],103)
  self.assertEqual(r["complements_conserves"],832)
  self.assertEqual(r["renommages_conserves"],3)
  self.assertEqual(len(r["alignements_Pactols_COG_valides_2026"]),7)
  self.assertEqual({x["code_insee"]:x["ark_pactols"] for x in r["alignements_Pactols_COG_valides_2026"]},ARKS)
  self.assertTrue(all(x["portee_chronologique"]=="2026_SEULEMENT" for x in r["alignements_Pactols_COG_valides_2026"]))
  self.assertEqual(len(r["ARK_anciens_concepts_non_promus"]),8)
  self.assertEqual(a,frozen)

 def test_concept_ancien_ne_devient_pas_concept_nouveau(self):
  a=sources()
  dossier=next(x for x in a["audit"]["dossiers"] if x["code_COG_2026"]=="04033")
  nouveau=next(x for x in dossier["candidats_Pactols"] if x["qualification_de_recette"]=="CANDIDAT_IDENTITE_COMMUNE_NOUVELLE_SELON_LIBELLE")
  nouveau["prefLabels_fr"]=["La Bréole"]
  with self.assertRaisesRegex(ValueError,"Preuve de commune nouvelle"):
   produire(**a)

 def test_history_note_doit_attester_date_et_creation(self):
  a=sources()
  dossier=next(x for x in a["audit"]["dossiers"] if x["code_COG_2026"]=="05101")
  nouveau=next(x for x in dossier["candidats_Pactols"] if x["qualification_de_recette"]=="CANDIDAT_IDENTITE_COMMUNE_NOUVELLE_SELON_LIBELLE")
  nouveau["notes"]=[]
  with self.assertRaisesRegex(ValueError,"Preuve de commune nouvelle"):
   produire(**a)

 def test_cereste_reste_conserve_et_abries_non_publie(self):
  a=sources()
  r=produire(**a)
  self.assertEqual(next(x for x in a["renommages"]["alignements_Pactols_COG_valides_2026"] if x["code_insee"]=="04045")["ark_pactols"],"26678/pcrtHxveTzUMik")
  self.assertNotIn("05001",{x["code_insee"] for x in r["alignements_Pactols_COG_valides_2026"]})
  self.assertNotIn("26678/pcrtGQ7nGPZN7K",{x["ark_pactols"] for x in r["alignements_Pactols_COG_valides_2026"]})
if __name__=="__main__":unittest.main()
