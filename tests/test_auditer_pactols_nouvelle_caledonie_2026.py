"""Validation synthétique du triage RDF des communes de Nouvelle-Calédonie."""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from auditer_pactols_nouvelle_caledonie_2026 import qualifier

def hit(code="98833",label="Kouaoua",other=None,deprecie=False,remplace=False):
    uris=[{"famille":"commune","code":code,
           "uri":"http://id.insee.fr/geo/commune/"+code}]
    if other:uris.append({"famille":"commune","code":other,
                          "uri":"http://id.insee.fr/geo/commune/"+other})
    return {"ark":"26678/pcrtTestNc","prefLabels_fr":[label],
            "insee_exactMatch":uris,"codes_communaux_cites":[code],
            "deprecie":deprecie,"remplace":remplace}

class TestNouvelleCaledonie(unittest.TestCase):
    def test_unicite_ark_non_deprecie_code_et_libelle(self):
        self.assertEqual(qualifier("98833","Kouaoua",[hit()]),"ELIGIBLE_SELON_REGLE")
        self.assertEqual(qualifier("98833","Kouaoua",[hit(label="Kouaoua (Nouvelle-Calédonie)")]),"ELIGIBLE_SELON_REGLE")

    def test_absence_et_doublon(self):
        self.assertEqual(qualifier("98833","Kouaoua",[]),"SANS_ASSERTION_EXPLICITE")
        self.assertEqual(qualifier("98833","Kouaoua",[hit(),hit()]),"A_INSTRUIRE_MULTIPLICITE")

    def test_mauvais_type_ou_divergence(self):
        for candidate in (hit(label="île Kouaoua"),hit(label="tribu Kouaoua"),
                          hit(other="98804"),hit(deprecie=True),hit(remplace=True),
                          hit(code="98804",label="Canala")):
            with self.subTest(candidate=candidate):
                self.assertEqual(qualifier("98833","Kouaoua",[candidate]),"A_INSTRUIRE_ONTOLOGIE_OU_DIVERGENCE")

    def test_famille_uri_non_commune_refusee(self):
        h=hit();h["insee_exactMatch"]=[{"famille":"collectiviteDOutreMer","code":"988",
                                        "uri":"http://id.insee.fr/geo/collectiviteDOutreMer/988"}]
        self.assertEqual(qualifier("98833","Kouaoua",[h]),"A_INSTRUIRE_ONTOLOGIE_OU_DIVERGENCE")

if __name__=="__main__":
    unittest.main()
