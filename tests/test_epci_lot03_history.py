"""Non-régression du lot 03 EPCI : identité, transitions et données inchangées."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/data/organismes.json'
EXPECTED = {
    'ORG-0219': [('communaute_communes','1994','2012-12-31'),
                 ('communaute_agglomeration','2013-01-01','2015-12-31')],
    'ORG-0415': [('communaute_communes','1999','2016-12-31')],
    'ORG-0658': [('syndicat_intercommunal_vocation_unique','1998-12-28','2015-12-31')],
    'ORG-0190': [('district','1992','2000'),('communaute_agglomeration','2001','2008'),
                 ('communaute_urbaine','2009','2014')],
    'ORG-0242': [('district','1991','2000'),('communaute_urbaine','2001-01-01','2014-12-31')],
    'ORG-0516': [('communaute_communes','1999','2001'),
                 ('communaute_agglomeration','2002-01-01','2016-12-31'),
                 ('communaute_urbaine','2017-01-01','2017-04-30')],
}


class Lot03HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(SOURCE.read_text(encoding='utf-8'))
        cls.by={r['id']:r for r in cls.d['authorities']}

    def test_new_historical_records_have_source_and_distinct_ids(self):
        expected={f'STH-{i:04d}' for i in range(31,43)}
        rows=[(a,h) for a in self.d['authorities']
              for h in a['names']['legal_status_history'] if h['id'] in expected]
        self.assertEqual(len(rows),12)
        self.assertEqual({h['id'] for a,h in rows},expected)
        for authority,h in rows:
            self.assertEqual(authority['kind'],'ORG')
            self.assertEqual(h['type'],'epci')
            self.assertEqual(h['sector'],'public')
            self.assertEqual(h['bsr'],'COL')
            self.assertEqual(h['validation'],'valide')
            self.assertTrue(h['source'].startswith('https://'))

    def test_six_institutional_histories_are_coherent(self):
        for ident,periods in EXPECTED.items():
            self.assertEqual(
                [(h['legal_form'],h['start'],h['end'])
                  for h in self.by[ident]['names']['legal_status_history']
                  if 31 <= int(h['id'][4:]) <= 42],periods,ident)
        for ident,periods in [
            ('ORG-0190',[('metropole_epci','2015-01-01')]),
            ('ORG-0242',[('metropole_epci','2015-01-01')]),
            ('ORG-0516',[('metropole_epci','2017-05-01')]),
        ]:
            current=self.by[ident]['names']['legal_status_history']
            for form,start in periods:
                self.assertIn((form,start),[(h['legal_form'],h['start']) for h in current])

    def test_institution_births_not_misread_as_metropolisation(self):
        for ident,year in [('ORG-0190','1992'),('ORG-0242','1991'),('ORG-0516','1999')]:
            rec=self.by[ident]
            self.assertEqual(rec['activity']['start'],year)
            self.assertEqual(rec['classification']['type'],'epci')
            self.assertEqual(rec['classification']['level'],'intercommunal')
        self.assertEqual(self.by['ORG-0190']['activity']['active'],True)
        self.assertEqual(self.by['ORG-0242']['activity']['active'],None)
        self.assertEqual(self.by['ORG-0516']['activity']['active'],True)

    def test_riom_dissolution_is_documented_not_inferred_from_status(self):
        riom=self.by['ORG-0415']
        self.assertEqual(riom['activity']['start'],'1999')
        self.assertEqual(riom['activity']['end'],'2016-12-31')
        self.assertFalse(riom['activity']['active'])
        self.assertFalse(riom['quality']['activity_unknown'])
        self.assertFalse(riom['quality']['end_missing'])

    def test_other_ids_and_historical_continuities_preserved(self):
        self.assertEqual(self.d['totals']['authorities'],829)
        self.assertEqual(self.d['totals']['organismes'],655)
        self.assertEqual(self.d['totals']['services'],174)
        self.assertEqual(self.d['totals']['catalog_included'],591)
        self.assertEqual(len(self.d['relations']),531)
        rels={r['id']:r for r in self.d['relations']}
        for key,source,target in [
            ('REL-0292','ORG-0658','ORG-0659'),
            ('REL-0293','ORG-0659','ORG-0660'),
            ('REL-0299','ORG-0219','ORG-0220')
        ]:
            self.assertEqual((rels[key]['source'],rels[key]['target']), (source,target))
        self.assertEqual(self.by['ORG-0633']['names']['legal_status_history'][0]['id'],'STH-0026')
        self.assertEqual(self.by['ORG-0659']['classification']['type'],'syndicat_mixte')
        self.assertEqual(self.by['ORG-0162']['classification']['type'],'epci')
        self.assertEqual(self.by['ORG-0093']['usage']['source_occurrences_linked'],181)


if __name__=='__main__':
    unittest.main()
