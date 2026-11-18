"""Contrôle de la proposition éditoriale du lot PDL n° 01."""
import csv
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class PropositionPdlLot01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/"recette/lieux/PDL-LOT01-CINQ-ARK-2026.csv").open(
                encoding="utf-8", newline="") as f:
            cls.propositions=list(csv.DictReader(f,delimiter=";"))
        cls.cog=json.loads((ROOT/"docs/data/lieux-chronologie/cog-pdl.json").read_text(
            encoding="utf-8"))

    def test_exactement_cinq_codes_et_deux_ark_distincts(self):
        self.assertEqual(len(self.propositions),5)
        self.assertEqual(len({r["code_COG_2026"] for r in self.propositions}),5)
        for row in self.propositions:
            self.assertNotEqual(row["ark_candidat_actuel"],row["ark_concept_ancien"])
            self.assertEqual(row["statut"],"PROPOSITION_A_CONTROLER")
            self.assertEqual(row["portee"],"2026-01-01")

    def test_creation_actuelle_et_commune_deleguee_documentees_cog(self):
        mouvements=self.cog["lignes_mouvements_cog"]
        for row in self.propositions:
            code=row["code_COG_2026"]
            date=row["date_MOD32"]
            self.assertTrue(any(
                e["mod"]=="32" and e["date_effet"]==date and
                e["code_apres"]==code and e["libelle_apres"]==row["nom_COG_2026"] and
                e["typecom_apres"]=="COM"
                for e in mouvements),code)
            self.assertTrue(any(
                e["mod"]=="32" and e["date_effet"]==date and
                e["code_avant"]==code and e["code_apres"]==code and
                e["libelle_apres"]==row["libelle_concept_ancien"] and
                e["typecom_apres"]=="COMD"
                for e in mouvements),code)

if __name__=="__main__":
    unittest.main()
