"""Tests ontologiques : 986 territoire, 3 CIR, aucun code communal."""
from __future__ import annotations
import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_pactols_wallis_futuna_2026 as a
PREFIX='''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#">'''
BODY='''
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtWallisTest">
 <skos:prefLabel xml:lang="fr">Wallis-et-Futuna</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/collectiviteDOutreMer/986"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtAloTest">
 <skos:prefLabel xml:lang="fr">royaume Alo (Futuna)</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/98611"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtOld98607">
 <skos:prefLabel xml:lang="fr">Nouvelle-Calédonie</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/territoire/98607"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtLexical">
 <skos:prefLabel xml:lang="fr">Uvea (Wallis-et-Futuna)</skos:prefLabel>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtAloAmbigu">
 <skos:prefLabel xml:lang="fr">Alo</skos:prefLabel>
</skos:Concept>
'''
class TestPactolsWallis(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.rdf=Path(self.temp.name)/"pactols.rdf"
  self.rdf.write_text(PREFIX+BODY+"</rdf:RDF>",encoding="utf-8")
 def tearDown(self):self.temp.cleanup()
 def test_codes_et_types(self):
  self.assertEqual(set(a.TARGET),{"986","98611","98612","98613"})
  self.assertEqual(a.TARGET["98611"][1],"CIRCONSCRIPTION")
  self.assertEqual(a.HISTORIC["98607"],"ANCIEN_CODE_NOUVELLE_CALEDONIE_NON_ADOPTE")
  self.assertTrue(a.candidat_lexical_qualifie("Uvea (Wallis-et-Futuna)"))
  self.assertFalse(a.candidat_lexical_qualifie("Alo"))
 def test_exactmatch_non_validant_malgre_une_voie_commune(self):
  d=a.scan_rdf(self.rdf)
  self.assertEqual(d["concepts_examines"],5)
  self.assertEqual(d["explicites"]["986"][0]["ark"],"26678/pcrtWallisTest")
  self.assertEqual(d["explicites"]["98611"][0]["ark"],"26678/pcrtAloTest")
  self.assertEqual(d["explicites"]["98611"][0]["exactMatch_INSEE_cibles"][0]["famille"],"commune")
  self.assertTrue(d["explicites"]["98611"][0]["reserve_categorie_ile_royaume"])
  self.assertEqual(d["explicites"]["98612"],[])
  self.assertEqual(d["explicites"]["98613"],[])
  self.assertEqual(d["explicites"]["98607"][0]["ark"],"26678/pcrtOld98607")
  self.assertEqual(d["explicites"]["98609"],[])
  self.assertEqual(len(d["lexicaux_non_validants"]),1)
  self.assertEqual(d["homonymes_sans_contexte_qualifie"],1)
 def test_audit_ne_publie_ni_historique_ni_commune(self):
  with (patch.object(a,"digest",return_value=a.RDF_SHA),
        patch.object(a,"verifier_cog",return_value=None)):
   d=a.rapport(self.rdf,Path(self.temp.name))
  self.assertEqual(d["bilan"]["territoires"],1)
  self.assertEqual(d["bilan"]["circonscriptions"],3)
  self.assertEqual(d["bilan"]["communes"],0)
  self.assertEqual(d["bilan"]["codes_avec_exactMatch"],2)
  self.assertEqual(d["bilan"]["validations_autorisees_automatiquement"],0)
  self.assertEqual(d["bilan"]["nouveaux_alignements_pactols"],0)
  self.assertEqual(d["anciens_codes_exclus_de_validation"][1]["code_COG"],"98607")
  self.assertFalse(d["anciens_codes_exclus_de_validation"][1]["susceptible_d_equivalence_986_ou_CIR"])
  self.assertTrue(all(not x["alignement_publie"] for x in d["lignes"]))
 def test_refuser_rdf_invalide(self):
  self.rdf.write_text("<not-rdf/>",encoding="utf-8")
  with self.assertRaisesRegex(ValueError,"RDF/XML"):a.scan_rdf(self.rdf)
if __name__=="__main__":unittest.main()
