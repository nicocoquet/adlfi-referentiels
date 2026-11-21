"""Recette et non-régressions du lot AFAN–CNRS–Inrap."""
import copy,json,unittest
from pathlib import Path
from scripts.recette_publication_organismes_153 import validate_153

ROOT=Path(__file__).resolve().parents[1]

class Publication153Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf-8'))
    def test_candidat(self):
        self.assertEqual(validate_153(self.data),[])
    def test_rejet_provenance(self):
        d=copy.deepcopy(self.data);d['provenance']['source_sha256']='0'*64
        self.assertTrue(any('SHA-256' in e for e in validate_153(d)))
    def test_rejet_affiliation_phan(self):
        d=copy.deepcopy(self.data)
        next(x for x in d['authorities'] if x['id']=='ORG-0068')['usage']['affiliations_validated']=1
        self.assertTrue(any('ORG-0068' in e for e in validate_153(d)))
    def test_rejet_fusion_didentite(self):
        d=copy.deepcopy(self.data)
        next(x for x in d['relations'] if x['id']=='REL-0043')['type']='denomination_historique'
        self.assertTrue(any('REL-0043' in e for e in validate_153(d)))
    def test_non_applicables_stables(self):
        d=copy.deepcopy(self.data);d['totals']['service_level_resolution']['not_applicable']=7
        self.assertTrue(any('Applicabilité' in e for e in validate_153(d)))

if __name__=='__main__':unittest.main()
