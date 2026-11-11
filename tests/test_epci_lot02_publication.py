"""Non-régression du lot 02 EPCI / formes juridiques et de la facette."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/data/organismes.json'
JS = ROOT / 'docs/assets/organismes.js'
TYPES_CHANGED = (
    'ORG-0103 ORG-0110 ORG-0113 ORG-0161 ORG-0162 ORG-0163 ORG-0180 '
    'ORG-0190 ORG-0213 ORG-0214 ORG-0219 ORG-0220 ORG-0242 ORG-0244 '
    'ORG-0339 ORG-0403 ORG-0415 ORG-0424 ORG-0425 ORG-0426 ORG-0427 '
    'ORG-0428 ORG-0516 ORG-0636 ORG-0658'
).split()
LEVELS_CHANGED = ('ORG-0161 ORG-0163 ORG-0190 ORG-0242 ORG-0516').split()


class EPCI42PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))
        cls.byid = {r['id']:r for r in cls.data['authorities']}

    def test_types_are_epci_without_identity_loss(self):
        self.assertEqual(len(TYPES_CHANGED),25)
        self.assertEqual(len(set(TYPES_CHANGED)),25)
        for ident in TYPES_CHANGED:
            record=self.byid[ident]
            self.assertEqual(record['kind'],'ORG')
            self.assertEqual(record['classification']['type'],'epci',ident)
            self.assertEqual(record['classification']['level'],'intercommunal',ident)
        self.assertEqual(self.data['totals']['organismes'],654)
        self.assertEqual(self.data['totals']['services'],166)

    def test_metropole_is_a_form_not_an_echelon(self):
        self.assertEqual(len(LEVELS_CHANGED),5)
        for ident in LEVELS_CHANGED:
            self.assertEqual(self.byid[ident]['classification']['level'],'intercommunal',ident)
            history=self.byid[ident]['names']['legal_status_history']
            self.assertIn('metropole_epci',[x['legal_form'] for x in history],ident)
        self.assertFalse(any(r['classification']['level']=='metropole'
                             for r in self.data['authorities'] if r['kind']=='ORG'))
        lyon=self.byid['ORG-0650']
        self.assertEqual(lyon['classification']['type'],'collectivite_territoriale')
        self.assertEqual(lyon['classification']['level'],'metropolitain')

    def test_dated_legal_forms_are_sourced_and_uniquely_numbered(self):
        rows=[(r['id'],h,r) for r in self.data['authorities'] if r['kind']=='ORG'
              for h in r['names']['legal_status_history']
              if h['id'].startswith('STH-') and 7<=int(h['id'][4:])<=30]
        self.assertEqual(len(rows),24)
        self.assertEqual({h['id'] for _,h,_ in rows},
                         {f'STH-{n:04d}' for n in range(7,31)})
        for ident,h,record in rows:
            self.assertEqual(h['type'],record['classification']['type'],ident)
            self.assertEqual(h['validation'],'valide')
            self.assertTrue(h['source'].startswith('https://'))
            self.assertEqual(len(h['start']),10)
        self.assertEqual(
            self.byid['ORG-0652']['names']['legal_status_history'][0]['legal_form'],
            'communaute_urbaine')
        self.assertEqual(
            self.byid['ORG-0244']['names']['legal_status_history'][0]['legal_form'],
            'syndicat_intercommunal_vocation_unique')

    def test_mixed_syndicates_and_san_remain_to_audit(self):
        # Une correction de typologie ne constitue pas une histoire juridique complète.
        self.assertEqual(self.byid['ORG-0162']['classification']['type'],'epci')
        self.assertEqual(self.byid['ORG-0162']['names']['legal_status_history'],[])
        self.assertEqual(self.byid['ORG-0659']['classification']['type'],'syndicat_mixte')
        self.assertEqual(self.byid['ORG-0659']['classification']['level'],'intercommunal')
        self.assertEqual(self.byid['ORG-0675']['classification']['level'],None)
        self.assertEqual(self.byid['ORG-0093']['usage']['source_occurrences_linked'],181)
        self.assertEqual(self.byid['ORG-0675']['usage']['source_occurrences_linked'],0)

    def test_ui_facets_do_not_hide_corrected_epci(self):
        source=JS.read_text(encoding='utf-8')
        self.assertIn("key:'level',label:'Échelon institutionnel'",source)
        self.assertIn("'collectivite_territoriale','epci','musee','etablissement_public'",source)
        self.assertIn("INSTITUTIONAL_LEVEL_TYPES.has(r.classification.type)",source)
        self.assertNotIn("r.classification.type==='collectivite_territoriale' && r.classification.level",source)
        # No SER level inference without dated institutional attachment.
        self.assertIn("if(k==='level')return r.classification.level ? [r.classification.level] : [];",source)


if __name__=='__main__':
    unittest.main()
