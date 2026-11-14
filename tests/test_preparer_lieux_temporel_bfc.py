"""Le curseur Lieux représente un instant, pas une année d'activité."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from preparer_lieux_temporel_bfc import (
    est_actif_etat, etats_au_premier_janvier, SCHEMA
)

class TempsBFC(unittest.TestCase):
    def setUp(self):
        self.demo = {
            "schema": SCHEMA,
            "periodes_COM": [
                {"code_insee":"25368","typecom":"COM","libelle":"Marchaux",
                 "debut_inclus":"1943-01-01","fin_exclue":"2018-01-01"},
                {"code_insee":"25368","typecom":"COM","libelle":"Marchaux-Chaudefontaine",
                 "debut_inclus":"2018-01-01","fin_exclue":None},
                {"code_insee":"25137","typecom":"COM","libelle":"Chaudefontaine",
                 "debut_inclus":"1943-01-01","fin_exclue":"2018-01-01"}
            ],
            "entites_complementaires_2026":[
                {"code_insee":"39012","typecom":"COMA","libelle":"Antorpe",
                 "comparent":"25527","date_observation":"2026-01-01"}],
            "evenements_COG":[
                {"id":"evt1974","date_effet":"1974-06-01"},
                {"id":"evt2018","date_effet":"2018-01-01"},
                {"id":"evt2020","date_effet":"2020-03-15"},
            ]
        }

    def test_borne_fin_exclue_changement_2018(self):
        before = etats_au_premier_janvier(self.demo, 2017)
        after = etats_au_premier_janvier(self.demo, 2018)
        self.assertEqual({v["code_insee"]:v["libelle"] for v in before["COM"]},
                         {"25368":"Marchaux","25137":"Chaudefontaine"})
        self.assertEqual({v["code_insee"]:v["libelle"] for v in after["COM"]},
                         {"25368":"Marchaux-Chaudefontaine"})

    def test_pas_de_futur_mouvement_de_mars_en_janvier(self):
        in_january = etats_au_premier_janvier(self.demo, 2020)
        in_2021 = etats_au_premier_janvier(self.demo, 2021)
        self.assertNotIn("evt2020",in_january["ids_evenements_deja_suivis"])
        self.assertIn("evt2020",in_2021["ids_evenements_deja_suivis"])

    def test_coma_2026_non_retroprojetee(self):
        self.assertEqual(etats_au_premier_janvier(self.demo, 1975)["complementaires_2026"],[])
        self.assertEqual(len(etats_au_premier_janvier(self.demo, 2026)["complementaires_2026"]),1)
        self.assertEqual(etats_au_premier_janvier(self.demo, 2026)["contours_historiques"],[])

    def test_bornes_et_types(self):
        for value in (1942,2027,"2017",2017.0,True):
            with self.assertRaises(ValueError):
                etats_au_premier_janvier(self.demo,value)

    def test_intervalles_semi_ouverts(self):
        state = {"debut_inclus":"1974-04-01","fin_exclue":"2016-06-01"}
        self.assertFalse(est_actif_etat(state,"1974-01-01"))
        self.assertTrue(est_actif_etat(state,"2016-01-01"))
        self.assertFalse(est_actif_etat(state,"2017-01-01"))

if __name__=="__main__":unittest.main()
