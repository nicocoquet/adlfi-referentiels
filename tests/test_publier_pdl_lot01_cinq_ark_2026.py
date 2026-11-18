"""Tests de cohérence de la publication PDL : cinq communes nouvelles."""
import json
import sys
import unittest
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_pdl_lot01_cinq_ark_2026 import SCHEMA,CODES

class Lot01PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
        cls.pub=read("docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot01-2026.json")
        cls.cog=read("docs/data/lieux-chronologie/cog-pdl.json")
        cls.previous=read("docs/data/lieux-chronologie/pactols-pdl-2026.json")
        cls.uuid=read("docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json")

    def test_cinq_candidats_et_anciennes_communes_distinctes(self):
        entries=self.pub["alignements_Pactols_COG_valides_2026"]
        self.assertEqual(self.pub["schema"],SCHEMA)
        self.assertEqual({x["code_insee"] for x in entries},CODES)
        self.assertEqual(len(entries),5)
        self.assertEqual(self.pub["total_alignements_PDL_2026"],1148)
        self.assertEqual(self.pub["communes_a_instruire"],80)
        old={x["ark_ancienne_commune_distinct"] for x in entries}
        new={x["ark_pactols"] for x in entries}
        previous=self.previous["alignements_Pactols_COG_valides_2026"]+self.uuid["alignements_Pactols_COG_valides_2026"]
        self.assertFalse(old&new)
        self.assertFalse(old&{x["ark_pactols"] for x in previous})
        self.assertFalse(new&{x["ark_pactols"] for x in previous})
        self.assertFalse(CODES&{x["code_insee"] for x in previous})
        self.assertEqual(len(previous),1143)

    def test_mouvements_cog_2016_deux_etats(self):
        events=self.cog["lignes_mouvements_cog"]
        for x in self.pub["alignements_Pactols_COG_valides_2026"]:
            date=x["date_evenement_COG"]
            code=x["code_insee"]
            self.assertEqual(date,"2016-01-01")
            self.assertTrue(any(m["code_apres"]==code and m["mod"]=="32" and
                m["date_effet"]==date and m["libelle_apres"]==x["libelle_COG_2026"] and
                m["typecom_apres"]=="COM" for m in events),code)
            self.assertTrue(any(m["code_avant"]==code and m["code_apres"]==code and
                m["mod"]=="32" and m["date_effet"]==date and
                m["libelle_apres"]==x["libelle_ancienne_commune"] and
                m["typecom_apres"]=="COMD" for m in events),code)

    def test_pas_de_geometrie_ou_episode_inferes(self):
        self.assertEqual(self.pub["nouvelles_geometries"],0)
        self.assertEqual(self.pub["liens_historiques_inferes"],0)
        for x in self.pub["alignements_Pactols_COG_valides_2026"]:
            self.assertEqual(x["portee_chronologique"],"2026_SEULEMENT")
            self.assertEqual(x["relations_historiques_inferees"],0)
            self.assertEqual(x["predicat_source"],"skos:exactMatch")
if __name__=="__main__":
    unittest.main()
