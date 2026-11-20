"""Le contrôle de recette 1.50 doit refuser la version publique 1.49."""
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

    def test_published_149_is_not_candidate_150(self):
        failures=validate_candidate(self.public)
        self.assertTrue(failures)
        self.assertTrue(any('934 autorités' in s for s in failures))
        self.assertTrue(any('594 relations' in s for s in failures))
        self.assertTrue(any('alias' in s for s in failures))

    def test_no_false_positive_for_orphan_relations_in_current_public(self):
        failures=validate_candidate(self.public)
        self.assertFalse(any('relation orpheline' in s for s in failures))


if __name__=='__main__':
    unittest.main()
