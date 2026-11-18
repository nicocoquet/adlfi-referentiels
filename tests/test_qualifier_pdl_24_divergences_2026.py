"""Contrats de la recette des 24 divergences, sans validation automatique."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from qualifier_pdl_24_divergences_2026 import (
    SCHEMA, PUBLICATIONS, analyser_dossier
)
class DivergencesPDLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base=ROOT/"docs/data/lieux-chronologie"
        cls.publications=[json.loads((base/name).read_text(encoding="utf-8"))
                          for name in PUBLICATIONS]
    def test_1194_couples_precedents_uniques(self):
        links=[r for p in self.publications
               for r in p["alignements_Pactols_COG_valides_2026"]]
        self.assertEqual(len(links),1194)
        self.assertEqual(len({x["code_insee"] for x in links}),1194)
        self.assertEqual(len({x["ark_pactols"] for x in links}),1194)
        self.assertEqual(len(PUBLICATIONS),5)
    def test_schema_ne_publie_pas(self):
        self.assertIn("recette",SCHEMA)
        self.assertIn("24-divergences",SCHEMA)
    def test_statut_deprecie_ne_peut_etre_publie(self):
        code="49000"
        record={
          "code":code,"nom":"Commune-exemple","departement":"49",
          "preuves_RDF_exactMatch":[{
             "ark":"26678/pcrt123","prefLabels_fr":["Commune-exemple"],
             "altLabels_fr":[],"codes_communaux_cites":[code],
             "insee_exactMatch":[{"code":code,"famille":"commune",
                                    "uri":"http://id.insee.fr/geo/commune/"+code}],
             "deprecie":True,"remplace":False,
             "risque_ile_atoll_autre_type":False
          }]
        }
        extra={"26678/pcrt123":{
            "exactMatch_tous":["http://id.insee.fr/geo/commune/"+code],
            "remplacements_explicites":[],"definitions":[],
            "notes_histoire":[],"notes_portee":[],"notes":[]}}
        result=analyser_dossier(record,extra,{"periodes_com":[]})
        self.assertEqual(result["groupe_instruction"],"STATUT_OU_REMPLACEMENT")
        self.assertIn("CONCEPT_DEPRECIE",result["motifs"])
        self.assertIsNone(result["ark_retenu"])
        self.assertEqual(result["publication"],"NON_PUBLIE")
if __name__=="__main__":
    unittest.main()
