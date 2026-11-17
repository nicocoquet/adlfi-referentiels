"""Garde-fous: exactMatch COG 2026 de trois régions, sans validation automatique."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_pactols_cog_regions_prioritaires_2026 import qualifier, communes_actuelles,REGIONS

def preuve(code="2A004",pref="Ajaccio",extra=None,dep=False):
    uris=[{"famille":"commune","code":code,
           "uri":"http://id.insee.fr/geo/commune/"+code}]
    if extra:
        uris.append({"famille":"commune","code":extra,
                    "uri":"http://id.insee.fr/geo/commune/"+extra})
    return {"ark":"26678/pcrtTest","prefLabels_fr":[pref],"altLabels_fr":[],
            "insee_exactMatch":uris,"codes_communaux_cites":[code],
            "deprecie":dep,"remplace":False}

class TestRegionsPrioritaires(unittest.TestCase):
    def test_regions_2026_codes_corrects(self):
        self.assertEqual(REGIONS,{"94":"Corse","52":"Pays de la Loire",
                                  "27":"Bourgogne-Franche-Comté"})
    def test_exactmatch_univoque(self):
        self.assertEqual(qualifier("2A004","Ajaccio",[preuve()]),"ELIGIBLE_SELON_REGLE")
    def test_absence_et_homonymies(self):
        self.assertEqual(qualifier("2A004","Ajaccio",[]),"SANS_EXACTMATCH")
        self.assertEqual(qualifier("2A004","Ajaccio",[preuve(),preuve()]),
                         "A_INSTRUIRE_PLUSIEURS_ARK")
    def test_contradictions(self):
        for v in [preuve(extra="2A005"),preuve(dep=True),
                  preuve(pref="Île Ajaccio"),preuve(pref="Nantes"),
                  preuve(code="2A005",pref="Ajaccio")]:
            with self.subTest(v=v):
                self.assertEqual(qualifier("2A004","Ajaccio",[v]),
                                 "A_INSTRUIRE_LIBELLE_STATUT_OU_URI")
    def test_uri_autre_type(self):
        p=preuve()
        p["insee_exactMatch"]=[{"famille":"departement","code":"2A",
                                "uri":"http://id.insee.fr/geo/departement/2A"}]
        self.assertEqual(qualifier("2A004","Ajaccio",[p]),
                         "A_INSTRUIRE_LIBELLE_STATUT_OU_URI")
    def test_fichier_COG_non_epingle_refuse(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"f.csv"
            f.write_text("TYPECOM,COM,LIBELLE,REG,DEP\nCOM,2A004,Ajaccio,94,2A\n",
                         encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Empreinte COG"):
                communes_actuelles(f)

if __name__=="__main__":unittest.main()
