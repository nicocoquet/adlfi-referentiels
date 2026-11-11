"""Tests du garde-fou de publication 1.49 (aucun XLSX privé dans le dépôt)."""
import copy
import json
import unittest
from pathlib import Path
from scripts.audit_publication_historique_149 import audit, SOURCE_FILE, SOURCE_SHA

ROOT=Path(__file__).resolve().parents[1]

class AuditHistorique149Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        published=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf-8'))
        cls.baseline=copy.deepcopy(published)
        # Les tests du garde-fou restent valides après la publication 1.49 :
        # reconstruire un instantané "avant migration" sans fixture privée.
        if published['provenance']['source_filename']==SOURCE_FILE:
            ids={f'HIS-{i:04d}' for i in range(67,125)}
            for a in cls.baseline['authorities']:
                history=a['names']['history']
                old=[h for h in history if h.get('id') not in ids]
                for h in old:
                    h.pop('id',None)
                    h.pop('source',None)
                a['names']['history']=old
            old_org=next(a for a in cls.baseline['authorities'] if a['id']=='ORG-0662')
            old_org['names']['acronym']=None
            cls.baseline['provenance']['source_filename']=(
                'AdlFI_referentiel_1-47_20261111_echelons_competences_Inrap.xlsx')
            cls.baseline['provenance']['source_sha256']=(
                '1138c330f59c91c301d0cb6a5136c1e1347fbf491a75a9bddfe7d9b9fa83df51')
        assert sum(len(a['names']['history']) for a in cls.baseline['authorities']
                   if a['kind']=='ORG')==66

    def candidate(self):
        after=copy.deepcopy(self.baseline)
        after['provenance']['source_filename']=SOURCE_FILE
        after['provenance']['source_sha256']=SOURCE_SHA
        ids=['ORG-0409','ORG-0590','ORG-0670']+[
            r['id'] for r in after['authorities']
            if r['kind']=='ORG' and r['id'] not in ('ORG-0409','ORG-0590','ORG-0670')][:54]
        self.assertEqual(len(ids),57)
        indexed={x['id']:x for x in after['authorities']}
        # Le maître 1.47 contenait déjà ADERA, contrairement au JSON public.
        indexed['ORG-0662']['names']['acronym']='ADERA'
        for k in range(58):
            org=ids[k if k<57 else 56]
            kind=('designation_historique_organe' if k<48
                  else 'ancienne_denomination' if k<56 else 'variante_denomination')
            status='a_verifier' if org in ('ORG-0409','ORG-0590','ORG-0670') and k<3 else 'valide'
            indexed[org]['names']['history'].append({
                'id':f'HIS-{k+67:04d}','label':f'Historique {k}',
                'type':kind,'start':None,
                'end':'2015-03-21' if kind=='designation_historique_organe' else None,
                'validation':status,'source':'https://example.org','acronym':None})
        return after

    def test_delta_validated(self):
        result=audit(self.baseline,self.candidate(),ROOT)
        self.assertEqual(result['new_history'],58)

    def test_accept_same_relations_in_different_order(self):
        data=self.candidate()
        data['relations'].reverse()
        result=audit(self.baseline,data,ROOT)
        self.assertEqual(result['new_history'],58)

    def test_reject_relation_content_change(self):
        data=self.candidate()
        data['relations'][0]['target']='ORG-9999'
        with self.assertRaisesRegex(AssertionError,'Relation modifiée'):
            audit(self.baseline,data,ROOT)

    def test_reject_relation_duplicate(self):
        data=self.candidate()
        data['relations'][1]['id']=data['relations'][0]['id']
        with self.assertRaisesRegex(AssertionError,'dupliqués'):
            audit(self.baseline,data,ROOT)

    def test_accept_only_documented_acronym_correction(self):
        result=audit(self.baseline,self.candidate(),ROOT)
        self.assertEqual(result['correction_acronyme_publication_anterieure'],
                         ['ORG-0662: null → ADERA'])

    def test_reject_wrong_adera_acronym(self):
        data=self.candidate()
        next(x for x in data['authorities'] if x['id']=='ORG-0662')['names']['acronym']='ADERAS'
        with self.assertRaisesRegex(AssertionError,'acronyme du maître différent'):
            audit(self.baseline,data,ROOT)

    def test_reject_unrelated_acronym_correction(self):
        data=self.candidate()
        next(x for x in data['authorities'] if x['id']=='ORG-0001')['names']['acronym']='INATTENDU'
        with self.assertRaisesRegex(AssertionError,'hors historique/média'):
            audit(self.baseline,data,ROOT)

    def test_reject_sector_change(self):
        data=self.candidate()
        data['authorities'][0]['classification']['sector']='prive'
        with self.assertRaises(AssertionError):
            audit(self.baseline,data,ROOT)

    def test_reject_media_loss(self):
        data=self.candidate()
        data['authorities'][0]['presentation']['media']={'image':'assets/missing.png','logo':None}
        with self.assertRaises(AssertionError):
            audit(self.baseline,data,ROOT)

    def test_reject_validation_regression(self):
        data=self.candidate()
        r=next(x for x in data['authorities'] if x['id']=='ORG-0409')
        next(h for h in r['names']['history'] if h.get('id')=='HIS-0067')['validation']='valide'
        with self.assertRaises(AssertionError):
            audit(self.baseline,data,ROOT)

if __name__=='__main__':
    unittest.main()
