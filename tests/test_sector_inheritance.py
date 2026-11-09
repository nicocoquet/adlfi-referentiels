"""Unit tests for derived public/private classification of SER entities."""
import copy
import unittest

from scripts.sector_inheritance import apply_sector_inheritance


def org(id, sector='public'):
    return {'id': id, 'kind': 'ORG', 'classification': {'sector': sector}, 'quality': {}}


def ser(id):
    return {'id': id, 'kind': 'SER', 'classification': {'sector': None}, 'quality': {}}


def link(id, source, target, *, type='rattachement_service', validation='valide'):
    return {'id': id, 'source': source, 'target': target, 'type': type, 'validation': validation}


class SectorInheritanceTests(unittest.TestCase):
    def test_direct_public_and_private(self):
        entities = [org('ORG-0001'), org('ORG-0002', 'prive'), ser('SER-0001'), ser('SER-0002')]
        result = apply_sector_inheritance(entities, [link('RSE-1', 'SER-0001', 'ORG-0001'),
                                                     link('RSE-2', 'SER-0002', 'ORG-0002')])
        self.assertEqual(result['counts'], {'prive': 1, 'public': 1})
        self.assertEqual(entities[2]['classification']['sector'], 'public')
        self.assertEqual(entities[3]['classification']['sector'], 'prive')
        self.assertEqual(entities[2]['classification']['sector_origin']['relation_ids'], ['RSE-1'])

    def test_chained_ser_and_provenance(self):
        entities = [org('ORG-0001'), ser('SER-0001'), ser('SER-0002')]
        apply_sector_inheritance(entities, [link('RSE-2', 'SER-0002', 'SER-0001'),
                                            link('RSE-1', 'SER-0001', 'ORG-0001')])
        self.assertEqual(entities[2]['classification']['sector'], 'public')
        self.assertEqual(entities[2]['classification']['sector_origin']['relation_ids'], ['RSE-1', 'RSE-2'])
        self.assertEqual(entities[2]['classification']['sector_origin']['org_ids'], ['ORG-0001'])

    def test_historical_multiple_same_sector(self):
        entities = [org('ORG-0001'), org('ORG-0002'), ser('SER-0001')]
        apply_sector_inheritance(entities, [link('RSE-1', 'SER-0001', 'ORG-0001'),
                                            link('RSE-2', 'SER-0001', 'ORG-0002')])
        self.assertEqual(entities[2]['classification']['sector'], 'public')
        self.assertEqual(entities[2]['classification']['sector_origin']['org_ids'], ['ORG-0001', 'ORG-0002'])

    def test_other_and_rejected_relations_excluded(self):
        entities = [org('ORG-0001'), ser('SER-0001'), ser('SER-0002')]
        result = apply_sector_inheritance(entities, [
            link('RSE-1', 'SER-0001', 'ORG-0001', type='fusion_constitutive'),
            link('RSE-2', 'SER-0002', 'ORG-0001', validation='rejete')])
        self.assertEqual(result['unresolved_service_ids'], ['SER-0001', 'SER-0002'])
        self.assertTrue(all(x['quality']['sector_unresolved'] for x in entities[1:]))

    def test_sector_conflict_blocks_export(self):
        entities = [org('ORG-0001'), org('ORG-0002', 'prive'), ser('SER-0001')]
        with self.assertRaisesRegex(ValueError, 'Secteurs contradictoires pour SER-0001'):
            apply_sector_inheritance(entities, [link('RSE-1', 'SER-0001', 'ORG-0001'),
                                                link('RSE-2', 'SER-0001', 'ORG-0002')])

    def test_cycle_blocks_export(self):
        entities = [ser('SER-0001'), ser('SER-0002')]
        with self.assertRaisesRegex(ValueError, 'Cycle de rattachements SER'):
            apply_sector_inheritance(entities, [link('RSE-1', 'SER-0001', 'SER-0002'),
                                                link('RSE-2', 'SER-0002', 'SER-0001')])

    def test_missing_org_sector_blocks_export(self):
        entities = [org('ORG-0001', None), ser('SER-0001')]
        with self.assertRaisesRegex(ValueError, 'Secteur inconnu'):
            apply_sector_inheritance(entities, [link('RSE-1', 'SER-0001', 'ORG-0001')])

    def test_no_changes_to_org_classifications(self):
        entities = [org('ORG-0001'), ser('SER-0001')]
        original = copy.deepcopy(entities[0])
        apply_sector_inheritance(entities, [link('RSE-1', 'SER-0001', 'ORG-0001')])
        self.assertEqual(entities[0], original)


if __name__ == '__main__':
    unittest.main()
