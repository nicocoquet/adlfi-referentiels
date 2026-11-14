"""Relations AdlFI–COG : une coïncidence de code ne valide aucun ARK."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from qualifier_relations_ark_bfc import candidates_pactols, normaliser


class RelationsBFC(unittest.TestCase):
    def test_normalisation_typographique_non_semantique(self):
        self.assertEqual(normaliser("Saint-Hymetière-sur-Valouse"),
                         normaliser("SAINT HYMETIERE SUR VALOUSE"))
        self.assertNotEqual(normaliser("Chemilla"),
                            normaliser("Saint-Hymetière-sur-Valouse"))

    def test_un_code_plusieurs_ark_ne_permet_pas_une_fusion(self):
        idx = {"25368": [
            {"ark_pactols": "ark:ancien", "pref_fr_pactols": "Marchaux"},
            {"ark_pactols": "ark:nouveau", "pref_fr_pactols": "Marchaux-Chaudefontaine"},
        ]}
        statut, cible, options = candidates_pactols("25368", "Marchaux-Chaudefontaine", idx)
        self.assertEqual(statut, "accord_lexical_univoque_non_valide")
        self.assertEqual(cible["ark_pactols"], "ark:nouveau")
        self.assertEqual(len(options), 2)

    def test_code_identique_mais_libelle_different_aucune_ark_proposee(self):
        idx = {"39137": [
            {"ark_pactols": "ark:chemilla", "pref_fr_pactols": "Chemilla"},
        ]}
        statut, cible, options = candidates_pactols(
            "39137", "Saint-Hymetière-sur-Valouse", idx
        )
        self.assertEqual(statut, "code_sans_concordance_lexicale")
        self.assertIsNone(cible)
        self.assertEqual(len(options), 1)

    def test_destination_hors_corpus(self):
        statut, cible, options = candidates_pactols("39021", "La Chailleuse", {})
        self.assertEqual(statut, "cible_absente_corpus_terminal")
        self.assertIsNone(cible)
        self.assertEqual(options, [])

    def test_deux_libelles_concordants_restent_ambigus(self):
        idx = {"25001": [
            {"ark_pactols": "ark:a", "pref_fr_pactols": "Lieu"},
            {"ark_pactols": "ark:b", "pref_fr_pactols": "Lieu"},
        ]}
        statut, cible, options = candidates_pactols("25001", "Lieu", idx)
        self.assertIsNone(cible)
        self.assertEqual(len(options), 2)
        self.assertEqual(statut, "code_sans_concordance_lexicale")


if __name__ == "__main__":
    unittest.main()
