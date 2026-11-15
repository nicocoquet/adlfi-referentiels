"""Vérification éditoriale de la revue La Réunion (21 standards + 2 historiques + Le Port)."""
import csv
import unittest
from collections import Counter
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"recette"/"lieux"

def lire(name):
    with (BASE/name).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f,delimiter=";"))

class RevueReunionCOG2026Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source={r["code_INSEE_2026"]:r for r in lire("LOT-REUNION-24-COMMUNES-20261115.csv")}
        cls.revue={r["code_INSEE_2026"]:r for r in lire("REVUE-REUNION-24-COG2026-20261115.csv")}

    def test_périmètre_et_integrite_des_codes(self):
        expected={f"974{i:02d}" for i in range(1,25)}
        self.assertEqual(set(self.source),expected)
        self.assertEqual(set(self.revue),expected)
        self.assertEqual(len({x["ark_Pactols_candidat"] for x in self.revue.values()}),24)
        for code,r in self.revue.items():
            source=self.source[code]
            for key in ("libelle_COG_2026","ark_Pactols_candidat",
                        "prefLabel_fr_Pactols","uri_INSEE_declaree_dans_Pactols",
                        "decision_editoriale"):
                self.assertEqual(r[key],source[key])
            self.assertEqual(r["uri_INSEE_declaree_dans_Pactols"],
                             "http://id.insee.fr/geo/commune/"+code)

    def test_21_standards_a_valider_pas_automatiquement(self):
        counter=Counter(r["categorie"] for r in self.revue.values())
        self.assertEqual(counter,{
            "STANDARD_SANS_MOUVEMENT_POST1946":21,
            "DIVISION_1965":2,
            "ARK_CONFIRME_PORT":1,
        })
        standard=[r for r in self.revue.values()
                  if r["categorie"]=="STANDARD_SANS_MOUVEMENT_POST1946"]
        self.assertTrue(all(x["decision_editoriale"]=="A_INSTRUIRE" for x in standard))
        self.assertTrue(all(x["debut_episode_COG"]=="1946-03-21" for x in standard))
        self.assertTrue(all(x["preuve_mouvement_COG_post1946"].startswith("aucun")
                            for x in standard))
        self.assertTrue(all(x["avis_documentaire_2026"]==
                            "FAVORABLE_2026_SOUMIS_VALIDATION" for x in standard))

    def test_un_seul_evenement_1965_pour_saint_louis_et_cilaos(self):
        sl=self.revue["97414"]
        ci=self.revue["97424"]
        self.assertEqual(sl["ark_Pactols_candidat"],"26678/pcrtBwoUOdthOV")
        self.assertEqual(ci["ark_Pactols_candidat"],"26678/pcrtp3m5MZ822i")
        self.assertEqual(sl["debut_episode_COG"],"1946-03-21")
        self.assertEqual(ci["debut_episode_COG"],"1965-02-05")
        self.assertEqual(sl["preuve_mouvement_COG_post1946"],
                         ci["preuve_mouvement_COG_post1946"])
        self.assertIn("1965-02-05",sl["preuve_mouvement_COG_post1946"])
        self.assertEqual(sl["decision_editoriale"],"A_INSTRUIRE")
        self.assertEqual(ci["decision_editoriale"],"A_INSTRUIRE")

    def test_le_port_confirme_mais_lien_pas_valide(self):
        port=self.revue["97407"]
        self.assertEqual(port["ark_Pactols_candidat"],"26678/pcrtIKvRT9vwUl")
        self.assertEqual(port["categorie"],"ARK_CONFIRME_PORT")
        self.assertEqual(port["decision_editoriale"],
                         "ARK_CONFIRME_CORRESPONDANCE_A_VALIDER")
        self.assertEqual(port["avis_documentaire_2026"],
                         "ARK_CONFIRME_97407_LIEN_A_VALIDER")

if __name__=="__main__":
    unittest.main()
