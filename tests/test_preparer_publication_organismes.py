"""Préflight du JSON maître : intégrité et refus de publication involontaire."""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.preparer_publication_organismes import (
    REQUIRED_RELATION, PUBLIC, audit, safe_destination
)


def authority(ident: str, kind: str):
    return {'id': ident, 'kind': kind, 'names': {'preferred': ident}}


def dataset(authorities, relations):
    return {
        'schema_version': '0.3.0',
        'authorities': authorities, 'relations': relations,
        'provenance': {'source_filename': 'maitre.xlsx', 'source_sha256': 'abc'}
    }


class PreflightPublication(unittest.TestCase):
    def setUp(self):
        self.org = authority('ORG-0537', 'ORG')
        self.ser = authority('SER-0196', 'SER')
        self.parent = authority('ORG-0393', 'ORG')
        self.original_relation = {
            'id': 'RSE-0251', 'source': 'SER-0196', 'target': 'ORG-0393',
            'type': 'rattachement_service', 'start': '1999', 'end': '2021-12-31',
            'validation': 'valide'
        }
        self.old = dataset([self.org, self.ser, self.parent], [self.original_relation])
        self.new = dataset([self.org, self.ser, self.parent],
                           [self.original_relation, dict(REQUIRED_RELATION)])

    def test_append_only_and_rse(self):
        result = audit(self.old, self.new, expected={
            'authorities': 3, 'org': 2, 'ser': 1, 'relations': 2
        }, require_rse_0252=True)
        self.assertEqual(result['status'], 'CANDIDAT_NON_PUBLIE')
        self.assertEqual(result['new_relation_ids'], ['RSE-0252'])
        self.assertEqual(result['unchanged_prior_relations'], 1)
        self.assertTrue(result['relation_rse_0252'])

    def test_protection_against_replacement(self):
        with self.assertRaisesRegex(ValueError, 'Identifiants supprimés'):
            audit(self.old, dataset([self.org, self.ser], []))
        broken = dataset([self.org, self.ser, self.parent],
                         [dict(self.original_relation, target='ORG-0537')])
        with self.assertRaisesRegex(ValueError, 'modifiées'):
            audit(self.old, broken)

    def test_orphan_and_cycle(self):
        orphan = dict(REQUIRED_RELATION, target='ORG-9999')
        with self.assertRaisesRegex(ValueError, 'absente'):
            audit(self.old, dataset([self.org, self.ser, self.parent],
                                    [self.original_relation, orphan]))
        first = {'id': 'REL-0001', 'source': 'ORG-0393', 'target': 'ORG-0537',
                 'type': 'succession_partielle', 'validation': 'valide'}
        last = {'id': 'REL-0002', 'source': 'ORG-0537', 'target': 'ORG-0393',
                'type': 'fusion_constitutive', 'validation': 'valide'}
        base = dataset([self.org, self.ser, self.parent], [])
        with self.assertRaisesRegex(ValueError, 'Cycle historique'):
            audit(base, dataset([self.org, self.ser, self.parent], [first, last]))

    def test_schema_and_counts(self):
        with self.assertRaisesRegex(ValueError, 'Effectif'):
            audit(self.old, self.new, expected={'relations': 586})
        with self.assertRaisesRegex(ValueError, 'Version de schéma'):
            audit(self.old, dict(self.new, schema_version='0.4.0'))

    def test_no_overwrite_public_json(self):
        with self.assertRaisesRegex(ValueError, 'Refus'):
            safe_destination(PUBLIC, Path('/tmp/master.xlsx'))
        with self.assertRaisesRegex(ValueError, 'docs/data'):
            safe_destination(PUBLIC.parent / 'candidate.json', Path('/tmp/master.xlsx'))
        self.assertEqual(safe_destination(Path('/tmp/adlfi-recette.json'),
                                          Path('/tmp/master.xlsx')).suffix, '.json')


if __name__ == '__main__':
    unittest.main()
