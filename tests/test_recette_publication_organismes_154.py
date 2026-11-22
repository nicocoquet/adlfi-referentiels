"""Recette positive et négative des correspondances du lot A05b."""
import copy,json,unittest
from pathlib import Path
from scripts.recette_publication_organismes_154 import validate

ROOT=Path(__file__).resolve().parents[1]
class Publication154Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        current=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf-8'))
        # Reconstituer la publication 1.54 pour conserver son contrat historique.
        cls.data=copy.deepcopy(current)
        cls.data['provenance']['source_filename']='AdlFI_referentiel_1-54_A05B_CNRS_INRAP_LABOS_CANDIDAT.xlsx'
        cls.data['provenance']['source_sha256']='32e69ba481331a0f1470c93ae40827e69dbb58cca20d739921459be30b218f15'
        for a in cls.data['authorities']:
            old={'ORG-0004':18,'ORG-0008':14,'ORG-0078':4,'ORG-0348':0,'ORG-0451':0}
            if a['id'] in old:
                a['usage']['affiliations_validated']=old[a['id']]
            if a['id']=='ORG-0348':
                a['usage']['affiliations_linked']=9
                a['usage']['source_occurrences_linked']=9
            if a['id']=='ORG-0451':
                a['usage']['affiliations_linked']=5
                a['usage']['source_occurrences_linked']=5
                a['validation']={'status':'a_verifier','established':False}
                a['activity']['active']=None
                a['activity']['start']=None
                a['geography']['cities_label']=None
                a['quality']['activity_unknown']=True
                a['quality']['city_unrecorded']=True
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
