"""SPM Pactols : tester exactMatch, homonymie et statut du concept RDF."""
from __future__ import annotations
import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_pactols_saint_pierre_miquelon_2026 as aud

PREFIX="""<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#">"""
END="</rdf:RDF>"
CONCEPTS="""
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtMIQUELON">
 <skos:prefLabel xml:lang="fr">Miquelon-Langlade</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97501"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtSAINTPIERRE">
 <skos:prefLabel xml:lang="fr">Saint-Pierre (Saint-Pierre-et-Miquelon)</skos:prefLabel>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtHOMONYME">
 <skos:prefLabel xml:lang="fr">Saint-Pierre</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/02691"/>
</skos:Concept>
"""
class Audits(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.path=Path(self.tmp.name)/"pactols.rdf"
  self.path.write_text(PREFIX+CONCEPTS+END,encoding="utf-8")
 def tearDown(self):self.tmp.cleanup()
 def test_matching_labels(self):
  self.assertTrue(aud.label_compatible("97501","Miquelon-Langlade"))
  self.assertTrue(aud.label_compatible("97502","Saint-Pierre (Saint-Pierre-et-Miquelon)"))
  self.assertFalse(aud.label_compatible("97502","Saint-Pierre (La Réunion)"))
  self.assertTrue(aud.label_compatible("97502","Saint-Pierre"))
  self.assertFalse(aud.label_compatible("97501","Miquelon"))
 def test_ne_pas_prendre_homonyme_pour_un_exactmatch(self):
  scan=aud.candidats_rdf(self.path)
  self.assertEqual(scan["concepts_rdf_inspectes"],3)
  self.assertEqual(len(scan["explicites"]["97501"]),1)
  self.assertEqual(scan["explicites"]["97501"][0]["ark"],"26678/pcrtMIQUELON")
  self.assertEqual(scan["explicites"]["97502"],[])
  self.assertEqual(scan["homonymes_prefLabel_saint_pierre_non_retenus"],1)
  self.assertEqual([x["ark"] for x in scan["lexicaux_qualifies"]],
                   ["26678/pcrtSAINTPIERRE"])
 def test_eligibilite_explicitement_bornee(self):
  with patch.object(aud,"sha",side_effect=lambda p:aud.RDF_SHA),\
       patch.object(aud,"verifier_cog",return_value=None):
   report=aud.rapport(self.path,Path(self.tmp.name)/"cog.csv")
  self.assertEqual(report["bilan"]["codes_eligibles"],1)
  self.assertEqual(report["bilan"]["codes_sans_exactMatch"],1)
  self.assertEqual(report["bilan"]["validations_publiees"],0)
  self.assertEqual(report["lignes"][0]["statut"],"ELIGIBLE_A_VALIDATION_EDITORIALE")
  self.assertEqual(report["lignes"][1]["statut"],"AUCUN_EXACTMATCH_ATTESTE")
  self.assertEqual(report["candidats_lexicaux_qualifies_non_valides"][0]["ark"],"26678/pcrtSAINTPIERRE")
 def test_exactmatch_ile_saint_pierre_ne_valide_pas_commune(self):
  label='<skos:prefLabel xml:lang="fr">Saint-Pierre (Saint-Pierre-et-Miquelon)</skos:prefLabel>'
  patch_label='''<skos:prefLabel xml:lang="fr">île Saint-Pierre (Saint-Pierre-et-Miquelon)</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97502"/>'''
  self.path.write_text(PREFIX+CONCEPTS.replace(label,patch_label)+END,encoding="utf-8")
  with patch.object(aud,"sha",side_effect=lambda p:aud.RDF_SHA),\\
       patch.object(aud,"verifier_cog",return_value=None):
   r=aud.rapport(self.path,Path(self.tmp.name)/"cog.csv")
  self.assertEqual(r["lignes"][1]["statut"],"A_INSTRUIRE")
  self.assertTrue(r["lignes"][1]["alerte_confusion_ile_commune"])
  self.assertEqual(r["bilan"]["codes_eligibles"],1)
  self.assertEqual(r["bilan"]["validations_publiees"],0)
 def test_concept_deprecie_n_est_pas_eligible(self):
  val=CONCEPTS.replace('</skos:Concept>','<owl:deprecated>true</owl:deprecated></skos:Concept>',1)
  self.path.write_text(PREFIX+val+END,encoding="utf-8")
  with patch.object(aud,"sha",side_effect=lambda p:aud.RDF_SHA),\
       patch.object(aud,"verifier_cog",return_value=None):
   r=aud.rapport(self.path,Path(self.tmp.name)/"cog.csv")
  self.assertEqual(r["lignes"][0]["statut"],"A_INSTRUIRE")
  self.assertEqual(r["bilan"]["codes_eligibles"],0)
if __name__=="__main__":unittest.main()
