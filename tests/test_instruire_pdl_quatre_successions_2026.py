"""Préflight des quatre créations successives des Pays de la Loire."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from instruire_pdl_quatre_successions_2026 import CAS, ARKS, SCHEMA

class QuatreSuccessionsPDLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog=json.loads((ROOT/"docs/data/lieux-chronologie/cog-pdl.json").read_text(encoding="utf-8"))

    def test_quatre_codes_et_neuf_arks_distincts(self):
        self.assertEqual(set(CAS),{"49018","49092","49160","53161"})
        self.assertEqual(sum(map(len,ARKS.values())),9)
        self.assertEqual(len(set.union(*ARKS.values())),9)

    def test_deux_dates_mod32_pour_chacun(self):
        for code,(nom,probleme,dates) in CAS.items():
            all_dates={x["date_effet"] for x in self.cog["lignes_mouvements_cog"]
                       if x["mod"]=="32" and x["code_apres"]==code}
            self.assertEqual(all_dates,set(dates),code)
            self.assertTrue(probleme)

    def test_reemploi_de_nom_et_limites_des_periodes(self):
        per=self.cog["periodes_com"]
        def courant(code):
            return [x for x in per if x["code_insee"]==code and
                x["typecom"]=="COM"]
        self.assertEqual([x["libelle"] for x in courant("49092")],
                         ["Chemillé","Chemillé-Melay","Chemillé-en-Anjou"])
        self.assertEqual([x["libelle"] for x in courant("49160")],
                         ["Ingrandes","Ingrandes-Le Fresne sur Loire","Ingrandes-le-Fresne-sur-Loire"])
        self.assertEqual([x["libelle"] for x in courant("53161")],
                         ["Montsûrs","Montsûrs-Saint-Céneré","Montsûrs"])
        self.assertEqual(courant("49018")[-1]["debut_inclus"],"2013-01-01")
        self.assertIsNone(courant("49018")[-1]["fin_exclue"])
        self.assertEqual(SCHEMA,"adlfi.lieux.pdl.quatre-creations-successives.2026.recette.v1")
if __name__=="__main__":
    unittest.main()
