"""Contrôles de non-fusion des concepts Pactols dans le lot P1 BFC."""
import csv
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"docs"/"lieux"/"recette"
def read(name):
    with (ROOT/name).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f,delimiter=";"))

class TestP1BFC(unittest.TestCase):
    def test_quatre_candidatures_deux_evenements(self):
        a=read("LOT-P1-BFC-4-CANDIDATURES.csv")
        e=read("LOT-P1-BFC-2-EVENEMENTS.csv")
        self.assertEqual((len(a),len(e)),(4,2))
        self.assertEqual({x["evenement_id"] for x in a},
                         {x["evenement_id"] for x in e})
        self.assertTrue(all(not x["decision_editoriale"] and
                            not x["date_validation"] for x in a))
        self.assertTrue(all(x["etat"]=="a_instruire_non_valide" for x in a))
    def test_six_mouvements_avec_reutilisation_codes(self):
        e=read("LOT-P1-BFC-2-EVENEMENTS.csv")
        m=read("LOT-P1-BFC-6-TRANSITIONS-COG.csv")
        self.assertEqual(len(m),6)
        for ev in e:
            found=[x for x in m if x["evenement_id"]==ev["evenement_id"]]
            self.assertEqual({x["COM_AV"] for x in found},
                             set(ev["codes_communes_precedentes"].split("|")))
            self.assertEqual(len(found),4 if ev["code_commune_nouvelle"]=="39137" else 2)
            self.assertTrue(all(x["MOD"]=="32" and x["TYPECOM_AV"]=="COM" and
                        x["TYPECOM_AP"]=="COM" and
                        x["COM_AP"]==ev["code_commune_nouvelle"] for x in found))
            self.assertEqual(len([x for x in found if x["COM_AV"]==x["COM_AP"]]),1)
    def test_concepts_distincts_meme_si_code_identique(self):
        a=read("LOT-P1-BFC-4-CANDIDATURES.csv")
        s=[x for x in a if x["code_cible"]=="39137"]
        self.assertEqual(len(s),3)
        self.assertEqual(len({x["ark_source"] for x in s}),3)
        self.assertEqual({x["ark_cible_propose"] for x in s},
            {"26678/pcrt80xbz0p4vht8kdd4mtdx"})
        v=[x for x in a if x["code_cible"]=="71566"]
        self.assertEqual(len(v),1)
        self.assertEqual(v[0]["ark_cible_propose"],"")

if __name__=="__main__":unittest.main()
