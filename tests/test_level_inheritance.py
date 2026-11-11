"""Tests sans données privées de l'héritage de l'échelon institutionnel."""
import unittest
from datetime import date
from scripts.level_inheritance import apply_level_inheritance


def org(ident, level):
    return {'id': ident, 'kind': 'ORG', 'classification': {'level': level}, 'quality': {}}


def ser(ident, level=None):
    return {'id': ident, 'kind': 'SER', 'classification': {'level': level}, 'quality': {}}


def link(ident, source, target, **overrides):
    return {'id': ident, 'source': source, 'target': target,
            'type': 'rattachement_service', 'validation': 'valide', **overrides}


class LevelInheritanceTests(unittest.TestCase):
    def test_direct_inheritance_and_provenance(self):
        entities = [org('ORG-0008', 'national'), ser('SER-0168')]
        result = apply_level_inheritance(entities, [
            link('RSE-0221', 'SER-0168', 'ORG-0008')], as_of=date(2026, 11, 11))
        self.assertEqual(entities[1]['classification']['level'], 'national')
        self.assertEqual(entities[1]['classification']['level_origin']['org_ids'], ['ORG-0008'])
        self.assertEqual(result['unresolved_service_ids'], [])

    def test_chained_service(self):
        entities = [org('ORG-0001', 'regional'), ser('SER-0001'), ser('SER-0002')]
        apply_level_inheritance(entities, [
            link('RSE-1', 'SER-0001', 'ORG-0001'),
            link('RSE-2', 'SER-0002', 'SER-0001')])
        self.assertEqual(entities[2]['classification']['level'], 'regional')
        self.assertEqual(entities[2]['classification']['level_origin']['relation_ids'],
                         ['RSE-1', 'RSE-2'])

    def test_parent_level_absent_is_not_inferred(self):
        entities = [org('ORG-0008', None), ser('SER-0168')]
        result = apply_level_inheritance(entities, [
            link('RSE-0221', 'SER-0168', 'ORG-0008')])
        self.assertIsNone(entities[1]['classification']['level'])
        self.assertEqual(entities[1]['classification']['level_origin']['reason'],
                         'missing_parent_level')
        self.assertEqual(result['unresolved_service_ids'], ['SER-0168'])

    def test_explicit_service_overrides_parent(self):
        entities = [org('ORG-0001', 'national'), ser('SER-0001', 'regional')]
        apply_level_inheritance(entities, [link('RSE-1', 'SER-0001', 'ORG-0001')])
        self.assertEqual(entities[1]['classification']['level'], 'regional')
        self.assertEqual(entities[1]['classification']['level_origin']['method'], 'explicit')

    def test_conflicting_parent_levels_are_unresolved(self):
        entities = [org('ORG-0001', 'national'), org('ORG-0002', 'regional'),
                    ser('SER-0001')]
        apply_level_inheritance(entities, [
            link('RSE-1', 'SER-0001', 'ORG-0001'),
            link('RSE-2', 'SER-0001', 'ORG-0002')])
        self.assertEqual(entities[2]['classification']['level_origin']['reason'],
                         'conflicting_parent_levels')

    def test_historical_future_unvalidated_and_succession_excluded(self):
        entities = [org('ORG-0001', 'national'), ser('SER-0001')]
        links = [link('RSE-1', 'SER-0001', 'ORG-0001', end='2020-12-31'),
                 link('RSE-2', 'SER-0001', 'ORG-0001', start='2030-01-01'),
                 link('RSE-3', 'SER-0001', 'ORG-0001', validation='a_verifier'),
                 link('RSE-4', 'SER-0001', 'ORG-0001', type='succession_service')]
        apply_level_inheritance(entities, links, as_of=date(2026, 11, 11))
        self.assertEqual(entities[1]['classification']['level_origin']['reason'],
                         'no_validated_current_attachment')

    def test_cycle_blocks_export(self):
        entities = [ser('SER-0001'), ser('SER-0002')]
        with self.assertRaisesRegex(ValueError, 'Cycle de rattachements SER'):
            apply_level_inheritance(entities, [
                link('RSE-1', 'SER-0001', 'SER-0002'),
                link('RSE-2', 'SER-0002', 'SER-0001')])

    def test_org_is_not_modified(self):
        entities = [org('ORG-0001', 'national'), ser('SER-0001')]
        apply_level_inheritance(entities, [link('RSE-1', 'SER-0001', 'ORG-0001')])
        self.assertEqual(entities[0]['classification'], {'level': 'national'})


if __name__ == '__main__':
    unittest.main()
