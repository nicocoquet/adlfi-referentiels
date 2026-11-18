"""Tests de validation COG MOD50 pour Orée d'Anjou 2026."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_pdl_oree_anjou_mod50_2026 import (
    SCHEMA,CODE,ANCIEN_CODE,NOM,ARK_ACTUEL,ARK_DRAIN,ARK_HAUTS_2016
)
class OreeMod50Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
        prefix="docs/data/lieux-chronologie/"
        cls.cog=read(prefix+"cog-pdl.json")
        cls.pub=read(prefix+"pactols-pdl-oree-anjou-mod50-2026.json")
        cls.prev=[read(prefix+x) for x in (
          "pactols-pdl-2026.json",
          "pactols-pdl-uuid-resolus-2026.json",
          "pactols-pdl-communes-nouvelles-lot01-2026.json",
          "pactols-pdl-chemille-2026.json",
          "pactols-pdl-communes-nouvelles-lot02-2026.json")]
    def test_1194_plus_une_commune_nouvelle_source_différente(self):
        p=self.pub
        self.assertEqual(p["schema"],SCHEMA)
        self.assertEqual(p["total_alignements_PDL_2026"],1195)
        self.assertEqual(p["communes_a_instruire"],33)
        self.assertEqual(p["alignements_publies_precedemment"],1194)
        self.assertEqual(p["nouveaux_alignements"],1)
        previous=[a for r in self.prev for a in r["alignements_Pactols_COG_valides_2026"]]
        self.assertEqual(len(previous),1194)
        x=p["alignements_Pactols_COG_valides_2026"][0]
        self.assertEqual(x["ark_pactols"],ARK_ACTUEL)
        self.assertEqual(x["ark_ancienne_commune_distinct"],ARK_DRAIN)
        self.assertEqual(x["code_insee"],CODE)
        self.assertEqual(x["uri_insee_RDF_Pactols"],"http://id.insee.fr/geo/commune/"+ANCIEN_CODE)
        self.assertEqual(x["uri_insee_courante"],"http://id.insee.fr/geo/commune/"+CODE)
        self.assertNotIn(CODE,{a["code_insee"] for a in previous})
        self.assertFalse({ARK_ACTUEL,ARK_DRAIN,ARK_HAUTS_2016}&
                         {a["ark_pactols"] for a in previous})
        self.assertEqual(len({a["code_insee"] for a in previous+[x]}),1195)
        self.assertEqual(len({a["ark_pactols"] for a in previous+[x]}),1195)
    def test_mod50_et_non_mod32(self):
        x=self.cog["lignes_mouvements_cog"]
        m=[z for z in x if z["date_effet"]=="2025-01-01" and
           z["code_avant"]==ANCIEN_CODE and z["code_apres"]==CODE]
        self.assertEqual(len(m),1)
        self.assertEqual(m[0]["mod"],"50")
        self.assertEqual((m[0]["libelle_avant"],m[0]["libelle_apres"]),(NOM,NOM))
        self.assertEqual((m[0]["typecom_avant"],m[0]["typecom_apres"]),("COM","COM"))
        per=[z for z in self.cog["periodes_com"] if
             z["typecom"]=="COM" and z["libelle"]==NOM and z["code_insee"] in (CODE,ANCIEN_CODE)]
        self.assertEqual(len(per),2)
        self.assertEqual({(z["code_insee"],z["debut_inclus"],z["fin_exclue"]) for z in per},
            {(ANCIEN_CODE,"2015-12-15","2025-01-01"),(CODE,"2025-01-01",None)})
    def test_ni_geometrie_ni_equivalence_reconstruite(self):
        self.assertEqual(self.pub["nouvelles_geometries"],0)
        self.assertEqual(self.pub["liens_historiques_inferes"],0)
        self.assertEqual(self.pub["alignements_Pactols_COG_valides_2026"][0]["relations_historiques_inferees"],0)
        self.assertEqual(self.pub["alignements_Pactols_COG_valides_2026"][0]["portee_chronologique"],"2026_SEULEMENT")
if __name__=="__main__":
    unittest.main()
