"""Contrôle de la publication 1.51, sans modifier le maître privé."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from recette_publication_organismes_151 import validate_151


class Organismes151PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf8'))

    def test_151_est_conforme(self):
        self.assertEqual(validate_151(self.data),[])

    def test_une_relation_federale_manquante_bloque(self):
        data=dict(self.data)
        data['relations']=[r for r in data['relations'] if r['id']!='REL-0342']
        self.assertTrue(any('598 relations' in e or 'REL-0342' in e
                            for e in validate_151(data)))

    def test_aucune_date_initiale_inventee(self):
        data=dict(self.data)
        data['relations']=[dict(r, start='2023-01-01') if r['id']=='REL-0343'
                           else r for r in self.data['relations']]
        self.assertTrue(any('REL-0343' in e for e in validate_151(data)))

    def test_qualification_globale_independante_de_l_affiliation(self):
        data=dict(self.data)
        data['authorities']=[
            dict(a,validation={'status':'valide','established':True})
            if a['id']=='ORG-0419' else a for a in self.data['authorities']]
        self.assertTrue(any('ORG-0419' in e for e in validate_151(data)))


if __name__=='__main__':
    unittest.main()
