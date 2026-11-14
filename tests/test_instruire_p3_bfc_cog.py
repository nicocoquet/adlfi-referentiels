"""Tests de recette P3 : déduplication des événements et maintien des états."""
import csv
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from instruire_p3_bfc_cog import (
    AFTER,AFTER_SOURCE,EXISTING_P2,MOV,group_later,read,stable_id
)

class P3BFC(unittest.TestCase):
    def test_lot_vingt_dossiers_sans_decision(self):
        p=ROOT/"docs/lieux/recette/LOT-P3-BFC-20-CANDIDATURES.csv"
        rows=read(p,("niveau_priorite","id_candidature","code_source",
                     "ark_cible_candidat","decision_editoriale","date_validation"),";")
        self.assertEqual(len(rows),20)
        self.assertEqual(len({r["id_candidature"] for r in rows}),20)
        self.assertEqual(len({r["code_source"] for r in rows}),20)
        self.assertTrue(all(r["niveau_priorite"].startswith("P3") and
                            not r["decision_editoriale"] and not r["date_validation"]
                            and r["ark_cible_candidat"] for r in rows))
        from collections import Counter
        self.assertEqual(Counter(r["modalite_insee"] for r in rows),
                         {"31":4,"32":15,"33":1})
        groups={(r["date_evenement_insee"],r["modalite_insee"],
                 r["code_receptrice"]) for r in rows}
        self.assertEqual(len(groups),16)
    def test_evenements_p2_reutilises_strictement(self):
        self.assertEqual(stable_id(("2018-01-01","32","25368")),"BFC-P2-2018-25368")
        self.assertEqual(stable_id(("2016-01-01","32","25529")),"BFC-P2-2016-25529")
        self.assertEqual(len(EXISTING_P2),2)
        self.assertEqual(len(AFTER),6)
        self.assertEqual(len(AFTER_SOURCE),8)
    def test_suppression_COMD_n_est_pas_fusion(self):
        key=("2021-03-15","35","25078")
        records=[{"DATE_EFF":"2021-03-15","MOD":"35",
                  "COM_AV":"25587","TYPECOM_AV":"COMD","COM_AP":"25078",
                  "TYPECOM_AP":"COM","LIBELLE_AV":"Vauchamps",
                  "LIBELLE_AP":"Bouclans"}]
        records=[{**{f:"" for f in MOV},**r} for r in records]
        out,kind=group_later(key,records)
        self.assertEqual(len(out),1)
        self.assertEqual(kind,"suppression_statut_COMD")
        wrong=[dict(records[0],TYPECOM_AP="COMD")]
        with self.assertRaises(ValueError):group_later(key,wrong)
    def test_vaeire_succession_d_etats_et_non_egalite(self):
        key=("2016-06-01","32","25575")
        rows=[
            dict(DATE_EFF="2016-06-01",MOD="32",COM_AV="25575",COM_AP="25575",
                 TYPECOM_AV="COM",TYPECOM_AP="COM",
                 LIBELLE_AV="Vaire-Arcier",LIBELLE_AP="Vaire"),
            dict(DATE_EFF="2016-06-01",MOD="32",COM_AV="25576",COM_AP="25575",
                 TYPECOM_AV="COM",TYPECOM_AP="COM",
                 LIBELLE_AV="Vaire-le-Petit",LIBELLE_AP="Vaire"),
        ]
        rows=[{**{f:"" for f in MOV},**r} for r in rows]
        self.assertEqual(len(group_later(key,rows)[0]),2)
        with self.assertRaises(ValueError):
            group_later(key,[dict(r,LIBELLE_AV="Vaire") for r in rows])
    def test_rattachements_ulterieurs_partages_par_plusieurs_sources(self):
        self.assertEqual(AFTER_SOURCE["39215"],AFTER_SOURCE["39488"])
        self.assertEqual(AFTER_SOURCE["39215"],AFTER_SOURCE["39544"])
        self.assertNotEqual(AFTER_SOURCE["39215"],AFTER_SOURCE["39564"])
        self.assertEqual(AFTER_SOURCE["70270"][1],"34")

if __name__=="__main__":unittest.main()
