"""PACA : préserver 103 validations 2026 et 7 décisions encore ouvertes."""
import csv
import tempfile
import unittest
from pathlib import Path
from scripts.auditer_lieux_paca_historique import (
    charger_valides,charger_candidats,mouvement_id,HISTORIC_SOURCE_COMMIT
)

ROOT=Path(__file__).resolve().parents[1]
PILOT=ROOT/"docs/data/lieux.json"
CAND=ROOT/"recette/lieux/paca/paca-sept-candidatures-20261114.csv"

class ParitePaca(unittest.TestCase):
    def test_pilote_et_candidats_separes(self):
        old=charger_valides(PILOT)
        pending=charger_candidats(CAND)
        self.assertEqual((len(old),len(pending)),(103,7))
        self.assertEqual(len(set(x["ark_pactols"] for x in old+pending)),110)
        self.assertEqual(len(set(x["code_cog_propose"] for x in old+pending)),110)
        self.assertEqual({x["validation_millesime_2026"] for x in old},
                         {"valide_et_conservee"})
        self.assertEqual({x["validation_millesime_2026"] for x in pending},
                         {"non_valide"})
    def test_arbitrage_non_premature(self):
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d)/"candidates.csv"
            raw=CAND.read_text(encoding="utf-8")
            tmp.write_text(raw.replace("candidat_non_valide;;;;",
                                       "candidat_non_valide;valider;;;"),encoding="utf-8")
            with self.assertRaises(ValueError):
                charger_candidats(tmp)
    def test_source_et_qualifications(self):
        with CAND.open(encoding="utf-8-sig",newline="") as f:
            records=list(csv.DictReader(f,delimiter=";"))
        self.assertEqual({r["origine_github_commit"] for r in records},
                         {HISTORIC_SOURCE_COMMIT})
        self.assertEqual([r["libelle_pactols"] for r in records],
                         ["La Ciotat","Hyères","Villefranche-sur-Mer",
                          "Martigues","Cannes","Nice","Marseille"])
        self.assertTrue(all(not r["date_validation"] for r in records))
    def test_mouvement_stable(self):
        source={key:"" for key in (
            "MOD","DATE_EFF","TYPECOM_AV","COM_AV","TNCC_AV","NCC_AV",
            "NCCENR_AV","LIBELLE_AV","TYPECOM_AP","COM_AP","TNCC_AP",
            "NCCENR_AP","LIBELLE_AP")}
        source.update({"MOD":"32","DATE_EFF":"2018-01-01",
                       "COM_AV":"13055","COM_AP":"13055"})
        self.assertEqual(mouvement_id(source),mouvement_id(dict(reversed(list(source.items())))))
        self.assertNotEqual(mouvement_id(source),mouvement_id(dict(source,MOD="31")))
if __name__=="__main__":
    unittest.main()
