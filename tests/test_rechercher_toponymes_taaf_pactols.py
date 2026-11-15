"""Tests du criblage des noms courts des districts TAAF dans Pactols."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from rechercher_toponymes_taaf_pactols import rechercher,RECHERCHES

XML='''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#">
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtTESTKER">
   <skos:prefLabel xml:lang="fr">Kerguelen</skos:prefLabel>
   <skos:broader rdf:resource="https://ark.frantiq.fr/ark:/26678/pcrtTESTTAAF"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtTESTTAAF">
   <skos:prefLabel xml:lang="fr">Terres australes et antarctiques françaises</skos:prefLabel>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtTESTCRO">
   <skos:altLabel xml:lang="fr">Crozet</skos:altLabel>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/01135"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtTESTOTHER">
   <skos:prefLabel xml:lang="fr">Ciel</skos:prefLabel>
 </skos:Concept>
</rdf:RDF>
'''
class RechercheTAAFTests(unittest.TestCase):
 def setUp(self):
  temp=tempfile.TemporaryDirectory()
  self.addCleanup(temp.cleanup)
  self.root=Path(temp.name)
  self.rdf=self.root/"test.rdf"
  self.rdf.write_text(XML,encoding="utf-8")
 def test_alias_kerguelen_ne_devient_pas_equivalence(self):
  n,results=rechercher(self.rdf,min_concepts=1)
  self.assertEqual(n,4)
  matches=[r for r in results if r["cible_cog"]=="COMER:DIS:98412"]
  self.assertEqual(len(matches),1)
  item=matches[0]
  self.assertEqual(item["ark_pactols"],"26678/pcrtTESTKER")
  self.assertEqual(item["label_pactols"],"Kerguelen")
  self.assertEqual(item["statut"],"indice_lexical_non_validant")
  self.assertEqual(item["avis_editorial"],"A_INSTRUIRE")
  self.assertEqual(item["qualification_contextuelle"],"concept_lie_hierarchiquement_aux_TAAF")
  self.assertEqual(item["piste_prioritaire"],"oui")
  faux=[r for r in results if r["cible_cog"]=="COMER:DIS:98413"]
  self.assertEqual(len(faux),1)
  self.assertEqual(faux[0]["qualification_contextuelle"],"homonyme_de_commune_exterieure")
  self.assertEqual(faux[0]["piste_prioritaire"],"non")
  self.assertIn("pcrtTESTTAAF",item["relations_broader_litterales"])
  self.assertEqual(len([r for r in results if r["cible_cog"]=="COMER:TERRITOIRE:984"]),1)
  self.assertEqual(len([r for r in results if r["cible_cog"]=="COMER:DIS:98413"]),1)
  self.assertFalse(any("Ciel" in r["label_pactols"] for r in results))
 def test_termes_recherche_ne_sont_pas_des_altlabels_ajoutes(self):
  self.assertIn("Kerguelen",RECHERCHES["COMER:DIS:98412"])
  self.assertNotIn("Kerguelen",RECHERCHES["COMER:DIS:98411"])
 def test_interdit_faux_rdf_integral(self):
  with self.assertRaisesRegex(ValueError,"intégral non reconnu"):
   rechercher(self.rdf)
if __name__=="__main__": unittest.main()
