"""PACA : Abriès-Ristolas, une validation éditoriale indirecte et datée."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_paca_abries_ristolas_editorial_2026 import construire

def sources():
 paths={
 "audit":"recette/lieux/PACA-ABRIES-RISTOLAS-AUDIT-2026.json",
 "pilote":"docs/data/lieux.json",
 "complement":"docs/data/lieux-chronologie/pactols-paca-2026.json",
 "renommages":"docs/data/lieux-chronologie/pactols-paca-renommages-2026.json",
 "nouvelles":"docs/data/lieux-chronologie/pactols-paca-communes-nouvelles-2026.json",
 "cog":"docs/data/lieux-chronologie/cog-paca.json"
 }
 return {key:json.loads((ROOT/name).read_text(encoding="utf-8")) for key,name in paths.items()}

class PACAAbrièsRistolasTests(unittest.TestCase):
 def test_946_et_preuves_indirectes(self):
  args=sources();immutable=copy.deepcopy(args);d=construire(**args)
  self.assertEqual(d["total_PACA_alignements_2026"],946)
  self.assertEqual(d["exceptions_restantes"],[])
  self.assertEqual([d["alignements_pilote_conserves"],
                    d["alignements_exactMatch_direct_conserves"],
                    d["renommages_conserves"],
                    d["communes_nouvelles_explicites_conservees"]],[103,832,3,7])
  self.assertEqual(d["propriete_Wikidata_code_INSEE"],"P374")
  self.assertEqual(d["valeur_Wikidata_P374"],"05001")
  self.assertTrue(d["information_Wikidata_non_autorite_INSEE"])
  link=d["alignements_Pactols_COG_valides_2026"][0]
  self.assertEqual(link["ark_pactols"],"26678/pcrtm96gvvfnwmggc9z0wrxn")
  self.assertIsNone(link["uri_insee_exactMatch_direct_pactols"])
  self.assertEqual(link["uri_exactMatch_pactols_wikidata"],"https://www.wikidata.org/wiki/Q57664391")
  self.assertEqual(link["ark_ancienne_commune_distinct"],"26678/pcrtGQ7nGPZN7K")
  self.assertEqual(link["portee_chronologique"],"2026_SEULEMENT")
  self.assertEqual([d["geometries_ajoutees"],d["relations_historiques_inferrees"]],[0,0])
  self.assertEqual(args,immutable)

 def test_exactmatch_INSEE_absent_ne_peut_etre_invente(self):
  a=sources()
  a["audit"]["rdf"]["concept_actuel"]["exactMatch_INSEE"]=["http://id.insee.fr/geo/commune/05001"]
  with self.assertRaisesRegex(ValueError,"Contradiction"):
   construire(**a)

 def test_reference_wikidata_distincte_ne_peut_etre_substituee(self):
  a=sources()
  a["audit"]["rdf"]["concept_actuel"]["skos_relations"]["exactMatch"]=["https://www.wikidata.org/wiki/Q331508"]
  with self.assertRaisesRegex(ValueError,"Contradiction"):
   construire(**a)

 def test_concept_ancien_ne_peut_pas_etre_promu(self):
  a=sources()
  a["audit"]["rdf"]["concept_actuel"]["ark_pactols"]="26678/pcrtGQ7nGPZN7K"
  with self.assertRaisesRegex(ValueError,"Contradiction"):
   construire(**a)

 def test_cog_2019_est_une_condition(self):
  a=sources()
  a["cog"]["periodes_com"]=[x for x in a["cog"]["periodes_com"]
                            if not(x["code_insee"]=="05001" and x["debut_inclus"]=="2019-01-01")]
  with self.assertRaisesRegex(ValueError,"Chronologie|Historique"):
   construire(**a)

if __name__=="__main__":unittest.main()
