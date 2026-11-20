"""Statuts de validation des autorités : ne pas confondre catalogue et preuve."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from export_organismes import authority_validation


class ValidationEditoriale(unittest.TestCase):
    def test_autorite_validee(self):
        self.assertEqual(authority_validation({'statut_validation':'valide'},'ORG-0751'),
            {'status':'valide','established':True})

    def test_a_verifier_peut_etre_au_catalogue(self):
        self.assertEqual(authority_validation({
            'statut_validation':'a_verifier','affichage_catalogue':'oui'},'SER-0202'),
            {'status':'a_verifier','established':False})

    def test_rejet_statut_vide_ou_inconnu(self):
        for source in ({}, {'statut_validation':'en_attente'}, {'statut_validation':''}):
            with self.subTest(source=source), self.assertRaisesRegex(ValueError,'Statut de validation'):
                authority_validation(source,'ORG-9999')

    def test_variantes_de_valide(self):
        for word in ('valide','validée','validee'):
            with self.subTest(word=word):
                self.assertTrue(authority_validation({'statut_validation':word},'ORG-0001')['established'])


if __name__=='__main__':
    unittest.main()
