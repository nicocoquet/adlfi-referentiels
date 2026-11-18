"""PDL : trois UUID INSEE officiels résolus et 1143 correspondances sans rétroprojection."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_pdl_trois_uuid_resolus_2026 import publier

def sources():
 paths={
  "audit":"recette/lieux/PDL-TROIS-UUID-INSEE-RESOLUTIONS-2026.json",
  "previous":"docs/data/lieux-chronologie/pactols-pdl-2026.json",
  "cog":"docs/data/lieux-chronologie/cog-pdl.json",
  "preflight":"recette/lieux/PDL-QUATRE-SANS-EXACTMATCH-RDF-2026.json"
 }
 return {k:json.loads((ROOT/v).read_text(encoding="utf-8")) for k,v in paths.items()}

class TestPublicationPDLUUID(unittest.TestCase):
 def test_1143_liens_et_85_exceptions(self):
  src=sources();frozen=copy.deepcopy(src)
  d=publier(**src);entries=d["alignements_Pactols_COG_valides_2026"]
  self.assertEqual(d["total_alignements_PDL_2026"],1143)
  self.assertEqual(d["communes_a_instruire"],85)
  self.assertEqual(d["cas_Rives_du_Fougerais_exclu"],"85292")
  self.assertEqual([x["code_insee"] for x in entries],["44066","85165","85212"])
  self.assertEqual(len({x["ark_pactols"] for x in entries}),3)
  self.assertTrue(all(x["portee_chronologique"]=="2026_SEULEMENT" for x in entries))
  self.assertTrue(all(x["nature_validation"]=="INSEE_RDF_UUID_codeINSEE_owl_sameAs" for x in entries))
  self.assertEqual(d["identites_historiques_inferees"],0)
  self.assertEqual(src,frozen)

 def test_uuid_ne_suffit_pas_sans_codeINSEE(self):
  s=sources();s["audit"]["dossiers"][0]["rdf_insee"]["codeINSEE"]=[]
  with self.assertRaisesRegex(ValueError,"triple preuve"):
   publier(**s)

 def test_code_COG_rdf_divergent_bloquant(self):
  s=sources();s["audit"]["dossiers"][1]["rdf_insee"]["owl_sameAs"]=[
   "http://id.insee.fr/geo/commune/85084"]
  with self.assertRaisesRegex(ValueError,"triple preuve"):
   publier(**s)

 def test_ressource_historique_ne_devient_pas_contrematch_courant(self):
  s=sources();s["audit"]["dossiers"][2]["rdf_insee"]["nom_officiel_dans_RDF"]=[
    "Sainte-Florence (Gironde)"]
  with self.assertRaisesRegex(ValueError,"triple preuve"):
   publier(**s)

 def test_suppression_de_cog_historique_bloquante(self):
  s=sources()
  s["cog"]["periodes_com"]=[x for x in s["cog"]["periodes_com"] if not (
   x["code_insee"]=="85165" and x["fin_exclue"]=="2016-01-01")]
  with self.assertRaisesRegex(ValueError,"Défusion"):
   publier(**s)

 def test_rives_du_fougerais_non_publiee(self):
  s=sources();d=publier(**s)
  self.assertNotIn("85292",{x["code_insee"] for x in d["alignements_Pactols_COG_valides_2026"]})

if __name__=="__main__":unittest.main()
