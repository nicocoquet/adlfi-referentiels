"""Rives-du-Fougerais : code 85292 contre code ancien Cezais 85041."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_pdl_rives_fougerais_loterre_2026 import (
    SCHEMA,URI,CODE,OLD,NEW_ARK,analyser_rdf,instruction
)
def fake(code='85292'):
    return ('''<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:geo="http://rdf.insee.fr/def/geo#"
      xmlns:owl="http://www.w3.org/2002/07/owl#">
      <rdf:Description rdf:about="'''+URI+'''">
        <rdf:type rdf:resource="http://rdf.insee.fr/def/geo#Commune"/>
        <owl:sameAs rdf:resource="http://id.insee.fr/geo/commune/'''+code+'''"/>
        <geo:codeINSEE>'''+code+'''</geo:codeINSEE>
        <geo:nom>Rives-du-Fougerais</geo:nom>
      </rdf:Description>
    </rdf:RDF>''').encode("utf-8")

class RivesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog=json.loads((ROOT/"docs/data/lieux-chronologie/cog-pdl.json").read_text(encoding="utf-8"))
        cls.recette=json.loads((ROOT/"recette/lieux/PDL-QUATRE-SANS-EXACTMATCH-RDF-2026.json").read_text(encoding="utf-8"))
        cls.publication=json.loads((ROOT/"docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json").read_text(encoding="utf-8"))

    def test_ressource_INSEE_UUID_et_code_exacts(self):
        d=analyser_rdf(fake())
        self.assertTrue(d["identite_85292_confirmee_OFFICIELLEMENT"])
        self.assertFalse(d["code_85041_affirme_par_INSEE"])
        self.assertEqual(d["geo_codeINSEE"],["85292"])

    def test_code_85041_n_est_pas_la_commune_nouvelle(self):
        d=analyser_rdf(fake(code="85041"))
        self.assertFalse(d["identite_85292_confirmee_OFFICIELLEMENT"])
        self.assertTrue(d["code_85041_affirme_par_INSEE"])

    def test_analyse_sans_validation_et_avec_sources_distinctes(self):
        d=instruction(self.cog,self.recette,self.publication,fake())
        self.assertEqual(d["schema"],SCHEMA)
        self.assertEqual(d["identite_COG"]["code_courant"],CODE)
        self.assertEqual(d["anomalie_source"]["code_chez_Pactols_et_Loterre"],OLD)
        self.assertEqual(d["anomalie_source"]["concept_Pactols"],NEW_ARK)
        self.assertFalse(d["lien_Loterre_non_Pactols"]["lien_Pactols_vers_Loterre_atteste"])
        self.assertEqual(d["conclusion"]["nouveaux_ARK_valides"],0)

    def test_code_COG_source_non_substituable(self):
        d=instruction(self.cog,self.recette,self.publication,fake(code="85041"))
        self.assertFalse(d["conclusion"]["code_COG_85292_resolu_par_UUID_Loterre"])
        self.assertEqual(d["conclusion"]["validation_editeur_Pactols_2026"],"A_INSTRUIRE")

if __name__=="__main__":unittest.main()
