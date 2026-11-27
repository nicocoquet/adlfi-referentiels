"""Non-régression du lot 07 — référentiel Personnes AdlFI.

À déposer sous tests/ dans le dépôt. Exécution sans réseau :
python3 -m unittest tests/test_personnes_lot07_publication.py
"""

import collections
import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/data/personnes.json'
MANIFEST = ROOT / 'docs/data/manifest.json'
PROVENANCE = ROOT / 'recette/personnes/lot07_contributions_provenance.csv'
IDENTITES = ROOT / 'recette/personnes/lot07_correspondances_per_proposes.csv'
PER_LOT07 = {f'PER-{i:06d}' for i in range(163, 193)}


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream, delimiter=';'))


class TestPublicationPersonnesLot07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pub = json.loads(DATA.read_text(encoding='utf-8'))
        cls.manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        cls.provenance = rows(PROVENANCE)
        cls.identites = rows(IDENTITES)
        cls.auth = {a['id']: a for a in cls.pub['authorities']}
        cls.relations = {(c['person_id'], c['handle']): c for c in cls.pub['contributions']}

    def test_comptage_et_manifest(self):
        pub = self.pub
        self.assertGreaterEqual(len(pub['authorities']), 192)
        self.assertGreaterEqual(len(pub['contributions']), 1953)
        handles = {c['handle'] for c in pub['contributions']}
        self.assertGreaterEqual(len(handles), 1759)
        self.assertEqual(pub['totals'], {
            'authorities': len(pub['authorities']),
            'contributions': len(pub['contributions']),
            'notices': len(handles),
        })
        m = self.manifest['modules']['personnes']
        self.assertEqual((m['autorites_validees'], m['contributions_adlfi'], m['notices_adlfi']),
                         (len(pub['authorities']), len(pub['contributions']), len(handles)))
        self.assertEqual(pub['schema_version'], m['data_schema'])
        self.assertEqual(pub['publication_status'], 'PUBLIC_PILOT')

    def test_identites_et_ppn(self):
        self.assertEqual(len(self.identites), 30)
        self.assertTrue(PER_LOT07.issubset(self.auth))
        self.assertEqual(len({a['identifiers']['idref'] for a in self.pub['authorities']}),
                         len(self.pub['authorities']))
        for p in self.identites:
            with self.subTest(p=p['per_propose']):
                self.assertIn(p['per_propose'], PER_LOT07)
                authority = self.auth[p['per_propose']]
                self.assertEqual(authority['name'], p['nom'])
                self.assertEqual(authority['identifiers']['idref'], p['ppn_idref'])
                self.assertGreaterEqual(authority['contributions_count'], int(p['mentions']))

    def test_relations_tei_et_roles(self):
        self.assertEqual(len(self.provenance), 111)
        self.assertEqual(len({p['id_mention_xml'] for p in self.provenance}), 111)
        self.assertEqual(len({p['handle'] for p in self.provenance}), 110)
        self.assertEqual(collections.Counter(p['roles'] for p in self.provenance),
                         {'aut fld': 62, 'aut': 48, 'fld': 1})
        for p in self.provenance:
            with self.subTest(person=p['per_propose'], handle=p['handle']):
                c = self.relations[(p['per_propose'], p['handle'])]
                self.assertEqual(c['notice']['title'], p['titre_tei'])
                self.assertEqual(c['notice']['url'], p['url'])
                self.assertEqual(' '.join(c['roles']), p['roles'])
                expected = (['responsable_operation'] if 'fld' in c['roles'] else []) + (
                    ['auteur'] if 'aut' in c['roles'] else [])
                self.assertEqual(c['normalized_roles'], expected)
                self.assertEqual(c['journal'], 'adlfi')

    def test_provenance_non_publiee(self):
        forbidden = {'id_mention_xml', 'source_xml', 'sha256_fragment_tei',
                     'sha256_xml_source', 'reference_visa', 'publication_autorisee',
                     'per_propose', 'statut_contribution'}

        def keys(obj):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    yield key
                    yield from keys(val)
            elif isinstance(obj, list):
                for val in obj:
                    yield from keys(val)

        self.assertFalse(forbidden & set(keys(self.pub)))


if __name__ == '__main__':
    unittest.main()
