from scripts.recette_historique_organismes_158 import sans_a05f
"""Contrôle de la publication 1.51, sans modifier le maître privé."""
import json
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from recette_publication_organismes_151 import validate_151


class Organismes151PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=sans_a05f(json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf8')))

    @staticmethod
    def snapshot_151(data):
        """Projeter 1.52 sur le contrat historique 1.51."""
        baseline=copy.deepcopy(data)
        baseline['relations']=[r for r in baseline['relations']
                              if r['id'] not in {'RSE-0259','RSE-0260'}]
        baseline['provenance']['source_filename']='AdlFI_referentiel_1-51_affiliations_federales_20261120_RECETTE.xlsx'
        baseline['provenance']['source_sha256']='af3ee809099a28373a5b183afe70af27066aeb3d23e1776fd501a192be91e1d4'
        return baseline

    def test_151_est_conforme(self):
        self.assertEqual(validate_151(self.snapshot_151(self.data)),[])

    def test_une_relation_federale_manquante_bloque(self):
        data=self.snapshot_151(self.data)
        data['relations']=[r for r in data['relations'] if r['id']!='REL-0342']
        self.assertTrue(any('598 relations' in e or 'REL-0342' in e
                            for e in validate_151(data)))

    def test_aucune_date_initiale_inventee(self):
        data=self.snapshot_151(self.data)
        data['relations']=[dict(r, start='2023-01-01') if r['id']=='REL-0343'
                           else r for r in self.data['relations']]
        self.assertTrue(any('REL-0343' in e for e in validate_151(data)))

    def test_qualification_globale_independante_de_l_affiliation(self):
        data=self.snapshot_151(self.data)
        data['authorities']=[
            dict(a,validation={'status':'valide','established':True})
            if a['id']=='ORG-0419' else a for a in self.data['authorities']]
        self.assertTrue(any('ORG-0419' in e for e in validate_151(data)))


if __name__=='__main__':
    unittest.main()
