"""Le contrat 1.50 exige une validation positive et rejette une régression 1.49."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from recette_publication_organismes_150 import validate_candidate


class Publication150Gates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf8'))

    @staticmethod
    def snapshot_150(data):
        """Le contrat 1.50 reste vérifié sur son sous-ensemble historique."""
        baseline=copy.deepcopy(data)
        additions={'REL-0341','REL-0342','REL-0343','REL-0344'}
        baseline['relations']=[r for r in baseline['relations'] if r['id'] not in additions]
        return baseline

    def test_published_candidate_150_passes_all_business_checks(self):
        self.assertEqual(validate_candidate(self.snapshot_150(self.public)),[])

    def test_regression_149_would_be_rejected(self):
        old=self.snapshot_150(self.public)
        old['authorities']=[a for a in old['authorities']
                            if a['id'] not in {'ORG-0747','ORG-0748','ORG-0749',
                            'ORG-0750','ORG-0751','ORG-0752','ORG-0753',
                            'ORG-0754','ORG-0755','SER-0197','SER-0198',
                            'SER-0199','SER-0200','SER-0201','SER-0202'}]
        old['relations']=[r for r in old['relations']
                          if r['id'] not in {'REL-0338','REL-0339','REL-0340',
                          'RSE-0253','RSE-0254','RSE-0255','RSE-0256',
                          'RSE-0257','RSE-0258'}]
        old['aliases']=[]
        failures=validate_candidate(old)
        self.assertTrue(any('934 autorités' in s for s in failures))
        self.assertTrue(any('594 relations' in s for s in failures))
        self.assertTrue(any('alias' in s for s in failures))

    def test_no_orphan_relationships_in_published_candidate(self):
        self.assertFalse(any('relation orpheline' in s
                             for s in validate_candidate(self.snapshot_150(self.public))))


if __name__=='__main__':
    unittest.main()
