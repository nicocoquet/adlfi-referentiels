"""Trois UUID INSEE de Pays de la Loire : preuve du sujet et du code, pas de nom seul."""
import copy
import json
import sys
import unittest
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_pdl_trois_uuid_insee_2026 import (
 CASES,GEO,OWL,RDF,URI_BASE,SCHEMA,source_uri,endpoint,verifier_xml
)

def xml_for(code:str,other_code=None,other_name=None,missing_sameas=False):
 c=other_code or code
 s=CASES[code]
 nom=escape(other_name if other_name is not None else s["nom"])
 same="" if missing_sameas else '<owl:sameAs rdf:resource="'+URI_BASE+c+'"/>'
 return ('''<?xml version="1.0" encoding="UTF-8"?>
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:owl="http://www.w3.org/2002/07/owl#"
  xmlns:geo="http://rdf.insee.fr/def/geo#">
  <rdf:Description rdf:about="'''+source_uri(code)+'''">
    <rdf:type rdf:resource="'''+GEO+'''Commune"/>
    '''+same+'''
    <geo:codeINSEE>'''+c+'''</geo:codeINSEE>
    <geo:nom>'''+nom+'''</geo:nom>
  </rdf:Description></rdf:RDF>''').encode("utf-8")

class PDLUUIDTests(unittest.TestCase):
 def test_trois_preuves_directes_du_meme_sujet(self):
  for code in CASES:
   with self.subTest(code=code):
    proof=verifier_xml(xml_for(code),code)
    self.assertTrue(proof["assertions_code_2026_concordantes"])
    self.assertEqual(proof["codeINSEE"],[code])
    self.assertEqual(proof["owl_sameAs"],[URI_BASE+code])
    self.assertEqual(proof["sujet_URI_UUID"],source_uri(code))
    self.assertTrue(endpoint(code).startswith("https://rdf.insee.fr/sparql?query="))

 def test_code_different_interdit(self):
  proof=verifier_xml(xml_for("44066",other_code="85165"),"44066")
  self.assertFalse(proof["assertions_code_2026_concordantes"])

 def test_sameAs_absent_interdit(self):
  proof=verifier_xml(xml_for("85165",missing_sameas=True),"85165")
  self.assertFalse(proof["assertions_code_2026_concordantes"])

 def test_noms_anciens_tolerables_uniquement_pour_renommage(self):
  proof=verifier_xml(xml_for("44066",other_name="Grandchamps-des-Fontaines"),"44066")
  self.assertTrue(proof["assertions_code_2026_concordantes"])
  proof=verifier_xml(xml_for("85165",other_name="Essarts en Bocage"),"85165")
  self.assertFalse(proof["assertions_code_2026_concordantes"])

 def test_autres_sujets_uuid_non_validants(self):
  b=xml_for("85212").replace(source_uri("85212").encode(),
                             source_uri("85165").encode())
  with self.assertRaisesRegex(ValueError,"Sujet UUID officiel absent"):
   verifier_xml(b,"85212")

 def test_profil_attendu_ne_produit_pas_de_validation_automatique(self):
  self.assertEqual(SCHEMA,"adlfi.lieux.pdl.trois_uuid_insee.2026.audit.v1")
  self.assertEqual(len(CASES),3)

if __name__=="__main__":
 unittest.main()
