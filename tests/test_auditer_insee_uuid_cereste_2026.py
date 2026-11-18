"""Céreste : ne valider que le triplet RDF officiel du sujet UUID vers code 04045."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_insee_uuid_cereste_2026 import URI,CODE_PRED,preuve_directe

def row(s,p,o,type="literal"):
    return {"s":{"type":"uri","value":s},"p":{"type":"uri","value":p},
            "o":{"type":type,"value":o}}

class CeresTeUuidTests(unittest.TestCase):
    def test_assertion_insee_directe_permet_preuve(self):
        result=preuve_directe([row(URI,CODE_PRED,"04045")])
        self.assertTrue(result["preuve_directe_code_04045"])

    def test_nom_seul_est_insuffisant(self):
        result=preuve_directe([row(URI,"http://www.w3.org/2000/01/rdf-schema#label",
                                   "Céreste-en-Luberon")])
        self.assertFalse(result["preuve_directe_code_04045"])

    def test_code_autre_sujet_refuse(self):
        result=preuve_directe([row("http://id.insee.fr/geo/commune/04045",CODE_PRED,"04045")])
        self.assertFalse(result["preuve_directe_code_04045"])

    def test_code_concurrent_refuse(self):
        result=preuve_directe([
            row(URI,CODE_PRED,"04045"),row(URI,CODE_PRED,"05045")])
        self.assertFalse(result["preuve_directe_code_04045"])

    def test_uri_uuid_ne_produit_pas_de_validation_sans_preuve(self):
        self.assertFalse(preuve_directe([])["preuve_directe_code_04045"])

if __name__=="__main__":
    unittest.main()
