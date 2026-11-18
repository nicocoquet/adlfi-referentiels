"""PACA huit fusions : distinguer identité historique et commune nouvelle 2026."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_paca_huit_communes_nouvelles_2026 import CASES,reconstruire_cog,classer

class FusionEtARKTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog=json.loads((ROOT/"docs/data/lieux-chronologie/cog-paca.json").read_text(encoding="utf-8"))

    def test_huit_fusions_cog_et_dates(self):
        historique=reconstruire_cog(self.cog)
        self.assertEqual(set(historique),set(CASES))
        self.assertEqual(len(historique),8)
        for code,d in historique.items():
            self.assertEqual(d["nature_evenement"],"MOD32_FUSION_COMMUNE_NOUVELLE")
            self.assertEqual(d["date_creation_commune_nouvelle"],CASES[code]["date"])
            self.assertGreaterEqual(len(d["communes_sources"]),2)
            self.assertIn(code,{x["code"] for x in d["communes_sources"]})
            self.assertEqual(d["ancienne_periode"]["fin"],CASES[code]["date"])

    def test_code_conserve_n_identifie_pas_une_commune_nouvelle(self):
        proof={"prefLabels_fr":["Pelvoux"],"altLabels_fr":["Vallouise-Pelvoux"],
               "owl_deprecated":False,"dct_isReplacedBy":[]}
        self.assertEqual(classer("ark",proof,"Vallouise-Pelvoux",["Pelvoux","Vallouise"],"05101"),
                         "IDENTITE_ANCIENNE_COMMUNE_PORTEUSE_CODE")

    def test_nom_exact_nouveau_seulement_candidat(self):
        proof={"prefLabels_fr":["Vallouise-Pelvoux"],"altLabels_fr":["Pelvoux"],
               "owl_deprecated":False,"dct_isReplacedBy":[]}
        self.assertEqual(classer("ark",proof,"Vallouise-Pelvoux",["Pelvoux","Vallouise"],"05101"),
                         "CANDIDAT_IDENTITE_COMMUNE_NOUVELLE_SELON_LIBELLE")

    def test_concept_deprecie_a_instruire(self):
        proof={"prefLabels_fr":["Vallouise-Pelvoux"],"altLabels_fr":[],
               "owl_deprecated":True,"dct_isReplacedBy":[]}
        self.assertEqual(classer("ark",proof,"Vallouise-Pelvoux",["Pelvoux","Vallouise"],"05101"),
                         "CONCEPT_DEPRECIE_OU_REMPLACE_A_INSTRUIRE")

    def test_homonymie_non_resolue(self):
        proof={"prefLabels_fr":["Un autre village"],"altLabels_fr":[],
               "owl_deprecated":False,"dct_isReplacedBy":[]}
        self.assertEqual(classer("ark",proof,"Vallouise-Pelvoux",["Pelvoux","Vallouise"],"05101"),
                         "IDENTITE_NON_RESOLUE")

if __name__=="__main__":
    unittest.main()
