"""Garde-fous pour les correspondances d'identifiants du maître ORG/SER."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from export_organismes import collect_identity_aliases


class AliasIdentifiers(unittest.TestCase):
    def setUp(self):
        self.existing={'ORG-0300','SER-0148','ORG-0747','ORG-0120'}
        self.rows=[
            {'Identifiant retiré':'ORG-0395','Identifiant canonique':'ORG-0300',
             'Décision':'Fusion de doublons','Source':'source administrative'},
            {'Identifiant retiré':'SER-0139','Identifiant canonique':'SER-0148'},
            {'Identifiant retiré':'SER-0063','Identifiant canonique':'ORG-0747',
             'Décision':'Correction de typologie SER → ORG'},
        ]

    def test_deux_fusions_et_reclassement(self):
        actual=collect_identity_aliases(self.rows,self.existing)
        self.assertEqual(actual,[
            {'from':'ORG-0395','to':'ORG-0300'},
            {'from':'SER-0139','to':'SER-0148'},
            {'from':'SER-0063','to':'ORG-0747'},
        ])
        self.assertNotIn('Décision',str(actual),'Le JSON ne publie pas les commentaires internes')
        self.assertNotIn('Source',str(actual))

    def test_feuille_absente_facultative(self):
        self.assertEqual(collect_identity_aliases([],self.existing),[])

    def test_doublon_id_retire(self):
        with self.assertRaisesRegex(ValueError,'dupliqué'):
            collect_identity_aliases(self.rows+[self.rows[2]],self.existing)

    def test_refuser_alias_vers_cible_absente(self):
        with self.assertRaisesRegex(ValueError,'Cible canonique absente'):
            collect_identity_aliases([{'Identifiant retiré':'SER-0063',
                                       'Identifiant canonique':'ORG-9000'}],self.existing)

    def test_refuser_id_retire_encore_actif(self):
        with self.assertRaisesRegex(ValueError,'encore canonique'):
            collect_identity_aliases([{'Identifiant retiré':'ORG-0300',
                                       'Identifiant canonique':'ORG-0747'}],self.existing)

    def test_refuser_les_alias_incomplets(self):
        with self.assertRaisesRegex(ValueError,'Alias incomplet'):
            collect_identity_aliases([{'Identifiant retiré':'SER-0063'}],self.existing)

    def test_refuser_un_format_invalide(self):
        with self.assertRaisesRegex(ValueError,'Alias invalide'):
            collect_identity_aliases([{'Identifiant retiré':'6-3',
                                       'Identifiant canonique':'ORG-0747'}],self.existing)


if __name__=='__main__':
    unittest.main()
