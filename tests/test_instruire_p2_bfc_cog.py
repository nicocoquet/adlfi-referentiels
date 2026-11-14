"""Garanties P2 : événement daté, jamais identité par code ou libellé seul."""
import csv
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from instruire_p2_bfc_cog import EVENTS, SOURCE_TARGETS, selection_mouvements, verifier_homonymes

REPO=Path(__file__).resolve().parents[1]
def load(name):
    with (REPO/"docs/lieux/recette"/name).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f,delimiter=";"))

class InstructionP2BFC(unittest.TestCase):
    def test_cinq_candidatures_decisions_vides(self):
        rows=load("LOT-P2-BFC-5-CANDIDATURES.csv")
        self.assertEqual(len(rows),5)
        self.assertEqual(len({r["ark_source"] for r in rows}),5)
        self.assertEqual({r["code_source"] for r in rows},set(SOURCE_TARGETS))
        self.assertTrue(all(not r["decision_editoriale"] and
                            not r["verificateur"] and not r["date_validation"]
                            and r["statut_recette"]=="candidat_non_valide" for r in rows))
        self.assertEqual(
            {r["type_relation_candidate"] for r in rows},
            {"participe_creation_commune_nouvelle","rattachement_commune_associee"})
    def test_homonymie_et_code_historique_proteges(self):
        terms=load("LOT-P2-BFC-CONTEXTE-ARK-39177.csv")
        verifier_homonymes(terms)
        jura=next(x for x in terms if x["qualification_dans_cette_recette"]=="commune_nouvelle")
        cote=next(x for x in terms if x["qualification_dans_cette_recette"]=="homonyme_autre_departement")
        cran=next(x for x in terms if x["qualification_dans_cette_recette"]=="ancienne_commune_code_reutilise")
        self.assertNotEqual(jura["ark_pactols"],cote["ark_pactols"])
        self.assertNotEqual(jura["ark_pactols"],cran["ark_pactols"])
        self.assertEqual(jura["code_insee_exactMatch"],cran["code_insee_exactMatch"])
        self.assertNotEqual(jura["code_insee_exactMatch"],cote["code_insee_exactMatch"])
    def test_six_evenements_dont_suppression_delegues(self):
        self.assertEqual(len(EVENTS),6)
        self.assertEqual(sum(x["n"] for x in EVENTS),19)
        self.assertEqual(sum(x["mod"]=="32" for x in EVENTS),3)
        self.assertEqual(sum(x["mod"]=="33" for x in EVENTS),2)
        self.assertEqual(sum(x["mod"]=="35" for x in EVENTS),1)
        later=next(x for x in EVENTS if x["mod"]=="35")
        self.assertEqual((later["date"],later["reception"]),("2020-03-15","39177"))
    def test_selections_rejettent_mouvements_incomplets(self):
        ev=next(x for x in EVENTS if x["id"]=="BFC-P2-2018-25368")
        records=[
            dict(DATE_EFF="2018-01-01",MOD="32",TYPECOM_AV="COM",COM_AV="25368",
                 TYPECOM_AP="COM",COM_AP="25368",LIBELLE_AV="Marchaux",
                 LIBELLE_AP="Marchaux-Chaudefontaine"),
            dict(DATE_EFF="2018-01-01",MOD="32",TYPECOM_AV="COM",COM_AV="25137",
                 TYPECOM_AP="COM",COM_AP="25368",LIBELLE_AV="Chaudefontaine",
                 LIBELLE_AP="Marchaux-Chaudefontaine"),
        ]
        self.assertEqual(len(selection_mouvements(ev,records)),2)
        with self.assertRaises(ValueError):
            selection_mouvements(ev,records[:1])
        invalid=[dict(r) for r in records]
        invalid[1]["TYPECOM_AP"]="COMD"
        with self.assertRaises(ValueError):
            selection_mouvements(ev,invalid)

if __name__=="__main__":
    unittest.main()
