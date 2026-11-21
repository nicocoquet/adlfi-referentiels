"""Recette et non-régressions du lot AFAN–CNRS–Inrap."""
import copy,json,unittest
from pathlib import Path
from scripts.recette_publication_organismes_153 import validate_153

ROOT=Path(__file__).resolve().parents[1]

class Publication153Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        current=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf-8'))
        # Le contrat 1.53 doit rester testé sur son état historique, distinct du lot 1.54.
        cls.data=copy.deepcopy(current)
        cls.data['provenance']['source_filename']='AdlFI_referentiel_1-53_A05_AFAN_CNRS_INRAP_CANDIDAT.xlsx'
        cls.data['provenance']['source_sha256']='fbea8c20b5867e742fa6bf82e058409c249c1017e0d0ec61e9612f926b878415'
        before={'ORG-0001':4,'ORG-0004':10,'ORG-0008':7,'ORG-0010':0,
                'ORG-0022':3,'ORG-0076':1,'ORG-0078':2,'ORG-0081':1,
                'ORG-0147':2,'ORG-0148':1,'ORG-0151':2,'ORG-0152':1,
                'ORG-0155':2,'ORG-0194':3,'ORG-0218':1,'ORG-0264':0}
        for a in cls.data['authorities']:
            if a['id'] in before:
                a['usage']['affiliations_validated']=before[a['id']]
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
