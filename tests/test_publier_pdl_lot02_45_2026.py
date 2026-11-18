"""Préflight : 45 communes nouvelles, 1149 + 45 = 1194, sans rétroprojection."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_pdl_lot02_45_2026 import SCHEMA
class PDL45PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
        cls.pub=read("docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot02-2026.json")
        cls.earlier=[
         read("docs/data/lieux-chronologie/pactols-pdl-2026.json"),
         read("docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json"),
         read("docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot01-2026.json"),
         read("docs/data/lieux-chronologie/pactols-pdl-chemille-2026.json")
        ]
        cls.cog=read("docs/data/lieux-chronologie/cog-pdl.json")
    def test_45_candidats_et_uniques(self):
        p=self.pub
        self.assertEqual(p["schema"],SCHEMA)
        self.assertEqual(p["alignements_publies_precedemment"],1149)
        self.assertEqual(p["nouveaux_alignements"],45)
        self.assertEqual(p["total_alignements_PDL_2026"],1194)
        self.assertEqual(p["communes_a_instruire"],34)
        self.assertEqual(p["codes_multiples_restant_a_instruire"],9)
        entries=p["alignements_Pactols_COG_valides_2026"]
        prev=[a for d in self.earlier for a in d["alignements_Pactols_COG_valides_2026"]]
        self.assertEqual(len(entries),45)
        self.assertEqual(len(prev),1149)
        self.assertEqual(len({a["code_insee"] for a in entries+prev}),1194)
        self.assertEqual(len({a["ark_pactols"] for a in entries+prev}),1194)
        ancient={a["ark_ancienne_commune_distinct"] for a in entries}
        self.assertEqual(len(ancient),45)
        self.assertFalse(ancient & {a["ark_pactols"] for a in entries+prev})
    def test_date_et_ancienne_comd_pour_chacun(self):
        events=self.cog["lignes_mouvements_cog"]
        for e in self.pub["alignements_Pactols_COG_valides_2026"]:
            code=e["code_insee"];day=e["date_evenement_COG"]
            self.assertTrue(any(m["mod"]=="32" and m["code_apres"]==code and
                m["date_effet"]==day and m["typecom_apres"]=="COM" and
                m["libelle_apres"]==e["libelle_COG_2026"] for m in events),code)
            self.assertTrue(any(m["mod"]=="32" and m["code_avant"]==code and
                m["code_apres"]==code and m["date_effet"]==day and
                m["typecom_avant"]=="COM" and m["typecom_apres"]=="COMD" and
                m["libelle_apres"]==e["libelle_ancienne_commune"] for m in events),code)
            self.assertEqual(e["portee_chronologique"],"2026_SEULEMENT")
            self.assertEqual(e["relations_historiques_inferees"],0)
    def test_nouveaux_contours_absents(self):
        self.assertEqual(self.pub["nouvelles_geometries"],0)
        self.assertEqual(self.pub["liens_historiques_inferes"],0)
        self.assertEqual(self.pub["cas_Rives_du_Fougerais_exclu"],"85292")
if __name__=="__main__":
    unittest.main()
