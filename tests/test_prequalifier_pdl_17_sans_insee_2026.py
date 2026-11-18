"""Tests de garde-fou : 17 candidats lexicalement courants, 0 validation."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from prequalifier_pdl_17_sans_insee_2026 import (
    SCHEMA, REGISTRE_SCHEMA, PUBLICATIONS
)
from auditer_pactols_polynesie_2026 import norm


class SansInseePDLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
        cls.registry=read("recette/lieux/PDL-24-DIVERGENCES-NOMINATIF-2026.json")
        cls.published=[read("docs/data/lieux-chronologie/"+p) for p in PUBLICATIONS]
        cls.pdl=read("docs/data/lieux-chronologie/cog-pdl.json")

    def test_six_publications_univoques(self):
        all_rows=[r for d in self.published
                  for r in d["alignements_Pactols_COG_valides_2026"]]
        self.assertEqual(len(all_rows),1195)
        self.assertEqual(len({r["code_insee"] for r in all_rows}),1195)
        self.assertEqual(len({r["ark_pactols"] for r in all_rows}),1195)
        self.assertEqual(len(PUBLICATIONS),6)
        self.assertEqual(self.pdl["millesime_cog"],2026)

    def test_restants_17_et_uree_mod50_deja_publie(self):
        self.assertEqual(self.registry["schema"],REGISTRE_SCHEMA)
        self.assertEqual(len(self.registry["dossiers"]),24)
        current_codes={r["code_insee"] for d in self.published
                       for r in d["alignements_Pactols_COG_valides_2026"]}
        already={r["code_insee"] for r in self.registry["dossiers"]} & current_codes
        self.assertEqual(already,{"49126"})
        chosen=[r for r in self.registry["dossiers"] if
                r["code_insee"] not in current_codes and r["candidat_actuel"] and
                r["candidat_actuel"]["situation_URI_INSEE"]=="AUCUN_EXACTMATCH_INSEE"]
        self.assertEqual(len(chosen),17)
        self.assertEqual(len({r["candidat_actuel"]["ark"] for r in chosen}),17)
        self.assertNotIn("49080",{r["code_insee"] for r in chosen})
        self.assertNotIn("49126",{r["code_insee"] for r in chosen})
        self.assertTrue(all(norm(r["libelle_COG_2026"])==
                            norm(r["candidat_actuel"]["prefLabels_fr"][0])
                            for r in chosen))
        self.assertIn("prequalification",SCHEMA)

    def test_cinq_sans_ark_et_historique_independant(self):
        missing=[r for r in self.registry["dossiers"] if r["candidat_actuel"] is None]
        self.assertEqual({r["code_insee"] for r in missing},
                         {"72155","72382","85076","85223","85289"})
        self.assertTrue(all(r["decision_editoriale"]=="NON_PRISE" and
                            r["publication"]=="NON_PUBLIE"
                            for r in self.registry["dossiers"]))


if __name__=="__main__":
    unittest.main()
