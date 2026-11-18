"""Contrats de qualification P374 Wikidata et triage sans publication."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from croiser_pdl_17_wikidata_p374_2026 import (
    SCHEMA,p374_qualifies,liste_qids,qualifier
)

class WikidataP374Tests(unittest.TestCase):
    def claim(self,code,rank="normal",debut=None,fin=None):
        qual={}
        for key,date in (("P580",debut),("P582",fin)):
            if date:
                qual[key]=[{"snaktype":"value","datavalue":{"value":{
                  "time":"+"+date+"T00:00:00Z"}}}]
        return {"rank":rank,"mainsnak":{"snaktype":"value",
                  "datavalue":{"value":code}},"qualifiers":qual}
    def test_p374_courant_exclut_l_historique(self):
        entity={"claims":{"P374":[
            self.claim("11111",fin="2024-12-31"),
            self.claim("22222",debut="2025-01-01")
        ]}}
        claims=p374_qualifies(entity)
        self.assertEqual([x["code"] for x in claims if x["actif_2026"]],["22222"])

    def test_p374_deprecie_exclu(self):
        d={"claims":{"P374":[self.claim("11111",rank="deprecated"),
                              self.claim("22222")]}}
        self.assertEqual([x["code"] for x in p374_qualifies(d) if x["actif_2026"]],["22222"])

    def test_schema_non_validant(self):
        self.assertIn("prequalification",SCHEMA)
        source={"schema":"adlfi.lieux.pdl.17-ark-sans-insee.prequalification.2026.v1",
                "dossiers":[
                    {"code_insee":f"{i:05d}",
                     "rdf":{"exactMatch_tous":[f"https://www.wikidata.org/wiki/Q{i+1}"]}}
                    for i in range(17)]}
        self.assertEqual(len(liste_qids(source)),17)
        source["dossiers"][0]["rdf"]["exactMatch_tous"].append(
            "http://id.insee.fr/geo/commune/00000")
        with self.assertRaisesRegex(ValueError,"URI INSEE"):
            liste_qids(source)

if __name__=="__main__":
    unittest.main()
