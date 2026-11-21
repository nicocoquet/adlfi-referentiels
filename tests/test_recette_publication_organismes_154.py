"""Recette positive et négative des correspondances du lot A05b."""
import copy,json,unittest
from pathlib import Path
from scripts.recette_publication_organismes_154 import validate

ROOT=Path(__file__).resolve().parents[1]
class Publication154Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf-8'))
    def test_candidat(self):
        self.assertEqual(validate(self.data),[])
    def test_provenance_obligatoire(self):
        d=copy.deepcopy(self.data)
        d['provenance']['source_sha256']='0'*64
        self.assertTrue(any('SHA-256' in x for x in validate(d)))
    def test_cnrs_non_survalide(self):
        d=copy.deepcopy(self.data)
        next(a for a in d['authorities'] if a['id']=='ORG-0004')['usage']['affiliations_validated']=19
        self.assertTrue(any('ORG-0004' in x for x in validate(d)))
    def test_inrap_non_survalide(self):
        d=copy.deepcopy(self.data)
        next(a for a in d['authorities'] if a['id']=='ORG-0008')['usage']['affiliations_validated']=15
        self.assertTrue(any('ORG-0008' in x for x in validate(d)))
    def test_laboratoires_non_perdus(self):
        d=copy.deepcopy(self.data)
        next(a for a in d['authorities'] if a['id']=='ORG-0194')['usage']['affiliations_validated']=4
        self.assertTrue(any('ORG-0194' in x for x in validate(d)))
    def test_nouvelles_tutelles_interdites(self):
        d=copy.deepcopy(self.data)
        d['relations'].append({'id':'REL-TEMP','source':'ORG-0008','target':'ORG-0010',
                               'type':'tutelle','validation':'valide'})
        self.assertTrue(any('600 relations' in x for x in validate(d)))
if __name__=='__main__':unittest.main()
