"""Recette bloquante de la publication 1.52 depuis le maître qualifié.

Les tests négatifs vérifient que les invariants refusent les régressions ;
le maître XLSX privé ne fait pas partie du dépôt public.
"""
import copy
import json
import unittest
from pathlib import Path
from scripts.recette_publication_organismes_152 import verify

ROOT=Path(__file__).resolve().parents[1]


class Publication152Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf-8'))

    def test_candidat_152_valide(self):
        errors, levels, methods=verify(self.data)
        self.assertEqual(errors, [])
        self.assertEqual(levels['unresolved'],2)
        self.assertEqual(levels['not_applicable'],8)
        self.assertEqual(methods['inherited_historical'],33)

    def test_rattachement_historique_obligatoire(self):
        data=copy.deepcopy(self.data)
        data['relations']=[r for r in data['relations'] if r['id']!='RSE-0259']
        errors, _, _=verify(data)
        self.assertTrue(any('RSE-0259' in x for x in errors))

    def test_non_applicable_ne_peut_pas_etre_une_lacune(self):
        data=copy.deepcopy(self.data)
        ser=next(x for x in data['authorities'] if x['id']=='SER-0197')
        ser['quality']['level_unresolved']=True
        errors, _, _=verify(data)
        self.assertTrue(any('SER-0197' in x for x in errors))

    def test_riez_reste_provisoire(self):
        data=copy.deepcopy(self.data)
        next(r for r in data['relations'] if r['id']=='RSE-0258')['validation']='valide'
        errors, _, _=verify(data)
        self.assertTrue(any('RSE-0258' in x for x in errors))

    def test_maitre_non_correspondant_refuse(self):
        data=copy.deepcopy(self.data)
        data['provenance']['source_sha256']='0'*64
        errors, _, _=verify(data)
        self.assertTrue(any('SHA-256' in x for x in errors))


if __name__=='__main__':
    unittest.main()
