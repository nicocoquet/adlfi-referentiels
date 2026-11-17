"""Pactols : source explicite ≠ alignement vers ancienne commune ou code applicatif."""
from __future__ import annotations
import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_pactols_collectivites_antilles_2007 as a

PREFIX='''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#">'''
END='</rdf:RDF>'
BODY='''
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtOld97123">
 <skos:prefLabel xml:lang="fr">Saint-Barthélemy (Guadeloupe)</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97123"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtApp97701">
 <skos:prefLabel xml:lang="fr">Saint-Barthélemy</skos:prefLabel>
 <skos:exactMatch rdf:resource="https://id.insee.fr/geo/commune/97701"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtCollect977">
 <skos:prefLabel xml:lang="fr">Saint-Barthélemy (collectivité)</skos:prefLabel>
 <skos:exactMatch rdf:resource="https://id.insee.fr/geo/collectivite/977"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtLexical">
 <skos:prefLabel xml:lang="fr">Saint-Martin (Guadeloupe)</skos:prefLabel>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtHomonym">
 <skos:prefLabel xml:lang="fr">Saint-Martin</skos:prefLabel>
</skos:Concept>'''
class TestAntillesPactols(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.rdf=Path(self.tmp.name)/"pactols.rdf"
  self.rdf.write_text(PREFIX+BODY+END,encoding="utf-8")
 def tearDown(self):self.tmp.cleanup()
 def test_codes_administratifs_distincts(self):
  self.assertEqual(set(a.CODE),{'97123','97127','977','978','97701','97801'})
  self.assertEqual(a.CODE['97701'][1],"CODE_APPLICATION_NON_COMMUNAL")
  self.assertEqual(a.CODE['97123'][1],"ANCIENNE_COMMUNE")
  self.assertEqual(a.CODE['977'][1],"COLLECTIVITE")
 def test_classifier_les_uri_en_2011_et_codes_5_positions(self):
  result=a.analyser_rdf(self.rdf)
  self.assertEqual(result["concepts_examines"],5)
  self.assertEqual(result["codes"]["97123"][0]["ark"],"26678/pcrtOld97123")
  self.assertEqual(result["codes"]["97701"][0]["ark"],"26678/pcrtApp97701")
  self.assertEqual(result["codes"]["97701"][0]["exactMatch_INSEE_cibles"][0]["famille"],"commune")
  self.assertEqual(result["codes"]["977"][0]["exactMatch_INSEE_cibles"][0]["famille"],"collectivite")
  self.assertEqual(result["codes"]["97127"],[])
  self.assertEqual(result["codes"]["978"],[])
  self.assertEqual([x["ark"] for x in result["lexicaux_non_validants"]],["26678/pcrtLexical"])
 def test_une_uri_explicite_ne_sert_pas_a_valider_automatiquement(self):
  with (patch.object(a,"empreinte",return_value=a.RDF_SHA),
        patch.object(a,"verifier_cog",return_value=None)):
   result=a.rapport(self.rdf,Path(self.tmp.name)/"cog.csv")
  self.assertEqual(result["bilan"]["codes_verifies"],6)
  self.assertEqual(result["bilan"]["liens_RDF_explicites"],3)
  self.assertEqual(result["bilan"]["codes_avec_exactMatch"],3)
  self.assertEqual(result["bilan"]["validations_autorisees_automatiquement"],0)
  self.assertEqual(result["bilan"]["nouveaux_alignements_pactols"],0)
  for line in result["codes_instruits"]:
   self.assertFalse(line["lien_pactols_publie_par_audit"])
  self.assertEqual(result["codes_instruits"][4]["statut"],"A_INSTRUIRE_ONTOLOGIQUEMENT")
 def test_ne_pas_accepter_rdf_corrompu(self):
  self.rdf.write_text("<invalid/>",encoding="utf-8")
  with self.assertRaises(ValueError):
   a.analyser_rdf(self.rdf)
if __name__=="__main__":unittest.main()
