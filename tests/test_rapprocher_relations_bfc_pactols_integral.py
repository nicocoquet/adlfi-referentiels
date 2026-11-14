import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from rapprocher_relations_bfc_pactols_integral import classer,lire

def candidat(ark,signaux):
    return {"ark_candidat":ark,"signaux":signaux}

class LiensPactolsBFC(unittest.TestCase):
    def test_code_seul_jamais_suffisant(self):
        chosen,kind=classer([candidat("26678/pcrtOld","exactMatch_insee_code")])
        self.assertIsNone(chosen)
        self.assertEqual(kind,"code_seul_insuffisant")
    def test_choisir_la_commune_nouvelle_et_pas_l_ancien_ark(self):
        chosen,kind=classer([
            candidat("26678/pcrtOld","exactMatch_insee_code"),
            candidat("26678/pcrtNew","prefLabel_fr_exact"),
        ])
        self.assertEqual(chosen["ark_candidat"],"26678/pcrtNew")
        self.assertEqual(kind,"prefLabel_seul_code_absent")
    def test_departements_homonymes(self):
        chosen,kind=classer([
            candidat("26678/pcrtCoteDor","prefLabel_fr_qualifie"),
            candidat("26678/pcrtJura","prefLabel_fr_qualifie|exactMatch_insee_code"),
        ])
        self.assertEqual(chosen["ark_candidat"],"26678/pcrtJura")
        self.assertEqual(kind,"prefLabel_qualifie_et_code")
    def test_ambiguites_persistantes(self):
        chosen,kind=classer([
            candidat("26678/pcrtOne","prefLabel_fr_exact|exactMatch_insee_code"),
            candidat("26678/pcrtTwo","prefLabel_fr_exact|exactMatch_insee_code"),
        ])
        self.assertIsNone(chosen)
        self.assertEqual(kind,"plusieurs_concepts_lexicaux_ambigus")
    def test_provenance_quatorze_dossiers(self):
        p=Path(__file__).resolve().parents[1]/"docs/lieux/recette/relations-bfc-14-sans-cible-initiale.csv"
        rows=lire(p,("ark_source","code_cible_insee","preuve_cog"))
        self.assertEqual(len(rows),14)
        self.assertEqual(len({r["ark_source"] for r in rows}),14)
        self.assertEqual(len({r["code_cible_insee"] for r in rows}),8)

if __name__=="__main__":unittest.main()
