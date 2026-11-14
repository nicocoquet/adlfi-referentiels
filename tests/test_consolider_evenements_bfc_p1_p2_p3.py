"""Tests de non-fusion et traçabilité de la consolidation P1–P3 BFC."""
import csv
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from consolider_evenements_bfc_p1_p2_p3 import (
    FOLLOW_UP,INSEE_SHA,KIND,MOVE,P2_LEGACY,PROPS,SOURCE_FOLLOWUP,
    canonical,mvt_id,read,selected,state,
)

class TransversalBFC(unittest.TestCase):
    def test_p1_p2_p3_recette_29_sans_decisions(self):
        base=ROOT/"recette/lieux"
        p1=read(base/"LOT-P1-BFC-4-CANDIDATURES.csv",
            ("id_candidature","date_effet","decision_editoriale","ark_cible_propose"))
        p2=read(base/"LOT-P2-BFC-5-CANDIDATURES.csv",
            ("id_candidature","date_evenement","decision_editoriale"))
        p3=read(base/"LOT-P3-BFC-20-CANDIDATURES.csv",
            ("id_candidature","date_evenement_insee","decision_editoriale"))
        self.assertEqual(tuple(map(len,(p1,p2,p3))),(4,5,20))
        self.assertEqual(len({r["id_candidature"] for r in p1+p2+p3}),29)
        self.assertTrue(all(not r["decision_editoriale"] for r in p1+p2+p3))
        self.assertEqual(sum(not r["ark_cible_propose"] for r in p1),1)
        self.assertTrue(all("71566" not in r["ark_cible_propose"] for r in p1))
    def test_identifiant_canonique_deux_anciens_alias(self):
        self.assertEqual(canonical(("2016-01-01","32","25529")),
                         "BFC-COG-2016-01-01-32-25529")
        self.assertNotEqual(P2_LEGACY[("2016-01-01","32","25529")],
                            canonical(("2016-01-01","32","25529")))
        self.assertEqual(len(P2_LEGACY),6)
        self.assertEqual(len(FOLLOW_UP),7)
        self.assertEqual(len(SOURCE_FOLLOWUP),9)
    def test_distinction_etats_meme_code(self):
        old=state("COM","39137","Chemilla")
        new=state("COM","39137","Saint-Hymetière-sur-Valouse")
        self.assertNotEqual(old["id"],new["id"])
        self.assertEqual(old["code"],new["code"])
        self.assertEqual(PROPS["33"],"rattachement_par_fusion_association")
        self.assertNotEqual(KIND["34"],KIND["35"])
    def test_selection_insee_avec_statut_commune_deleguee(self):
        a={k:"" for k in MOVE}
        main=dict(a,MOD="32",DATE_EFF="2016-01-01",TYPECOM_AV="COM",
                  COM_AV="39332",LIBELLE_AV="Mirebel",TYPECOM_AP="COM",
                  COM_AP="39177",LIBELLE_AP="Hauteroche")
        comd=dict(main,TYPECOM_AP="COMD",COM_AP="39332",LIBELLE_AP="Mirebel")
        cran=dict(main,COM_AV="39177",LIBELLE_AV="Crançot")
        grang=dict(main,COM_AV="39260",LIBELLE_AV="Granges-sur-Baume")
        rows=[main,comd,cran,grang]
        self.assertEqual(len(selected(("2016-01-01","32","39177"),rows,False)),4)
        rows.extend([
          dict(cran,TYPECOM_AP="COMD",COM_AP="39177",LIBELLE_AP="Crançot"),
          dict(grang,TYPECOM_AP="COMD",COM_AP="39260",LIBELLE_AP="Granges-sur-Baume")])
        self.assertEqual(len(selected(("2016-01-01","32","39177"),rows,False)),6)
    def test_mouvement_identique_reutilise_son_id(self):
        row={k:"" for k in MOVE}
        row.update(MOD="32",DATE_EFF="2018-01-01",COM_AV="25368",
                   TYPECOM_AV="COM",COM_AP="25368",TYPECOM_AP="COM",
                   LIBELLE_AV="Marchaux",LIBELLE_AP="Marchaux-Chaudefontaine")
        self.assertEqual(mvt_id(row),mvt_id(dict(reversed(list(row.items())))))
        self.assertNotEqual(
            mvt_id(dict(row,TYPECOM_AP="COMD")),mvt_id(row))

if __name__=="__main__":unittest.main()
