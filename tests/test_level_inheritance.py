"""Recette sans données privées : héritages courants, historiques et non-applicabilité."""
import unittest
from datetime import date
from scripts.level_inheritance import apply_level_inheritance, NOT_APPLICABLE_TYPES
AS_OF = date(2026, 11, 21)

def org(id, level, **activity):
    return {'id': id, 'kind': 'ORG', 'classification': {'level': level}, 'activity': activity, 'quality': {}}

def ser(id, level=None, **activity):
    return {'id': id, 'kind': 'SER', 'classification': {'level': level}, 'activity': activity, 'quality': {}}

def link(id, src, dst, **overrides):
    return {'id': id, 'source': src, 'target': dst, 'type': 'rattachement_service', 'validation': 'valide', **overrides}

class LevelInheritanceTests(unittest.TestCase):
    def run_case(self, entities, relations, expected, method, reason=None):
        apply_level_inheritance(entities, relations, as_of=AS_OF)
        c = entities[-1]['classification']
        self.assertEqual(c['level'], expected)
        self.assertEqual(c['level_origin']['method'], method)
        if reason: self.assertEqual(c['level_origin']['reason'], reason)

    def test_current(self):
        self.run_case([org('O','regional'),ser('S',active=True)],[link('R','S','O')],'regional','inherited')
    def test_historical(self):
        self.run_case([org('O','regional',start='1977',end='2015-12-31'),ser('S',active=False,start='1991',end='2015-12-31')],[link('R','S','O',start='1991',end='2015-12-31')],'regional','inherited_historical')
    def test_closed_active(self):
        self.run_case([org('O','regional'),ser('S',active=True)],[link('R','S','O',end='2020')],None,'unresolved','no_validated_current_attachment')
    def test_unknown_activity(self):
        self.run_case([org('O','regional'),ser('S',active=None)],[link('R','S','O',end='2020')],None,'unresolved','no_validated_current_attachment')
    def test_rejected(self):
        self.run_case([org('O','regional'),ser('S',active=False)],[link('R','S','O',validation='rejete')],None,'unresolved','no_validated_historical_attachment')
    def test_provisional(self):
        self.run_case([org('O','regional'),ser('S',active=False)],[link('R','S','O',validation='a_verifier')],None,'unresolved','no_validated_historical_attachment')
    def test_succession(self):
        self.run_case([org('O','regional'),ser('S',active=False)],[link('R','S','O',type='succession_service')],None,'unresolved','no_validated_historical_attachment')
    def test_disjoint_lifetimes(self):
        self.run_case([org('O','regional',start='2016'),ser('S',active=False,end='2015-12-31')],[link('R','S','O')],None,'unresolved','historical_temporal_uncertainty')
    def test_future_relation(self):
        self.run_case([org('O','regional'),ser('S',active=False)],[link('R','S','O',start='2030')],None,'unresolved','historical_temporal_uncertainty')
    def test_missing_level(self):
        self.run_case([org('O',None),ser('S',active=False)],[link('R','S','O')],None,'unresolved','missing_parent_level')
    def test_conflict(self):
        self.run_case([org('O','regional'),org('P','national'),ser('S',active=False)],[link('R','S','O',end='2000'),link('T','S','P',start='2001')],None,'unresolved','conflicting_parent_levels')
    def test_explicit(self):
        self.run_case([org('O','regional'),ser('S','national',active=False)],[link('R','S','O')],'national','explicit')
    def test_undated(self):
        self.run_case([org('O','communal'),ser('S',active=False,start='1978',end='2016')],[link('R','S','O')],'communal','inherited_historical')
    def test_chain(self):
        a=[org('O','regional'),ser('P',active=False,start='1990',end='2015'),ser('S',active=False,start='2000',end='2010')]
        r=[link('R','P','O',start='1995',end='2015'),link('T','S','P',start='2000',end='2010')]
        self.run_case(a,r,'regional','inherited_historical')
        self.assertEqual(a[-1]['classification']['level_origin']['relation_ids'],['R','T'])
    def test_disjoint_chain(self):
        self.run_case([org('O','regional'),ser('P',active=False),ser('S',active=False)],[link('R','P','O',end='1999'),link('T','S','P',start='2000')],None,'unresolved','historical_temporal_uncertainty')
    def test_cycle(self):
        with self.assertRaisesRegex(ValueError,'Cycle'):
            apply_level_inheritance([ser('S',active=False),ser('P',active=False)],[link('R','S','P'),link('T','P','S')],as_of=AS_OF)
    def test_partial_month(self):
        self.run_case([org('O','regional'),ser('S',active=False,start='2000-01',end='2000-02')],[link('R','S','O',start='2000-02',end='2000-02')],'regional','inherited_historical')
    def test_org_unchanged(self):
        o=org('O','regional')
        apply_level_inheritance([o,ser('S',active=False)],[link('R','S','O')],as_of=AS_OF)
        self.assertEqual(o['classification'],{'level':'regional'})
    def test_not_applicable(self):
        for typ in sorted(NOT_APPLICABLE_TYPES):
            with self.subTest(type=typ):
                a=[org('O','national'),ser('S',active=True)]
                a[-1]['classification'].update(type=typ,level_applicability='not_applicable')
                result=apply_level_inheritance(a,[link('R','S','O')],as_of=AS_OF)
                self.assertEqual(a[-1]['classification']['level_origin']['method'],'not_applicable')
                self.assertFalse(a[-1]['quality']['level_unresolved'])
                self.assertEqual(result['counts']['not_applicable'],1)
    def test_not_applicable_explicit_level_rejected(self):
        a=[ser('S','communal',active=True)]
        a[0]['classification'].update(type='service_recherche',level_applicability='not_applicable')
        with self.assertRaisesRegex(ValueError,'contradictoire'): apply_level_inheritance(a,[],as_of=AS_OF)
    def test_unqualified_research_service_unresolved(self):
        a=[ser('S',active=True)];a[0]['classification']['type']='service_recherche'
        self.assertEqual(apply_level_inheritance(a,[],as_of=AS_OF)['unresolved_service_ids'],['S'])
    def test_incompatible_not_applicable_rejected(self):
        a=[ser('S',active=True)]
        a[0]['classification'].update(type='service_municipal',level_applicability='not_applicable')
        with self.assertRaisesRegex(ValueError,'incompatible'): apply_level_inheritance(a,[],as_of=AS_OF)
    def test_territorial_service_unresolved(self):
        a=[ser('S',active=True)];a[0]['classification']['type']='service_archeologique_territorial'
        self.assertEqual(apply_level_inheritance(a,[],as_of=AS_OF)['unresolved_service_ids'],['S'])
    def test_missing_relation_parent_raises(self):
        with self.assertRaisesRegex(ValueError,'inconnue'):
            apply_level_inheritance([ser('S')],[link('R','S','O')],as_of=AS_OF)

if __name__=='__main__': unittest.main()
