"""Contrôles des instantanés publiés 1.47 et 1.49 : provenance, Inrap et historique."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/data/organismes.json'
SOURCES = {
    'AdlFI_referentiel_1-47_20261111_echelons_competences_Inrap.xlsx':
        '1138c330f59c91c301d0cb6a5136c1e1347fbf491a75a9bddfe7d9b9fa83df51',
    'AdlFI_referentiel_1-49_20261111_Historique_consolide.xlsx':
        '41c39072771435c4b5d18eccfee7483aa82af5f3f43c8f06d4d4c8cd13261642',
}

class PublicationSnapshotsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))
        cls.by_id = {x['id']: x for x in cls.data['authorities']}
        cls.relations = {x['id']: x for x in cls.data['relations']}

    def test_provenance_and_counts(self):
        d = self.data
        source = d['provenance']['source_filename']
        self.assertIn(source, SOURCES)
        self.assertEqual(d['provenance']['source_sha256'], SOURCES[source])
        self.assertEqual(len(self.by_id), 829)
        self.assertEqual(len(self.relations), 531)
        self.assertEqual(d['totals']['organismes'], 655)
        self.assertEqual(d['totals']['services'], 174)
        self.assertEqual(d['totals']['catalog_included'], 591)

    def test_historical_publication_and_adera_correction(self):
        is_149 = self.data['provenance']['source_filename'].startswith(
            'AdlFI_referentiel_1-49_')
        histories = [
            (a['id'], h)
            for a in self.data['authorities'] if a['kind'] == 'ORG'
            for h in a['names']['history']
        ]
        service_histories = [
            h for a in self.data['authorities'] if a['kind'] == 'SER'
            for h in a['names']['history']
        ]
        self.assertEqual(len(service_histories), 72)
        if is_149:
            self.assertEqual(len(histories), 124)
            added = [(authority, h) for authority, h in histories
                     if h.get('id') in {
                         f'HIS-{n:04d}' for n in range(67, 125)}]
            self.assertEqual(len(added), 58)
            self.assertEqual(
                {h['id'] for _, h in added},
                {f'HIS-{n:04d}' for n in range(67, 125)})
            self.assertEqual(len({authority for authority, _ in added}), 57)
            self.assertEqual(
                sum(h['type'] == 'designation_historique_organe'
                    for _, h in added), 48)
            self.assertEqual(
                {authority for authority, h in added if h['validation'] == 'a_verifier'},
                {'ORG-0409', 'ORG-0590', 'ORG-0670'})
            self.assertTrue(all(h.get('source') for _, h in added))
            self.assertEqual(self.by_id['ORG-0662']['names']['acronym'], 'ADERA')
        else:
            self.assertEqual(len(histories), 66)
            self.assertIsNone(self.by_id['ORG-0662']['names']['acronym'])

    def test_eight_inrap_directions(self):
        levels = {'SER-0168': 'regional', 'SER-0169': 'regional',
                  'SER-0170': 'interregional', 'SER-0171': 'regional',
                  'SER-0172': 'interregional', 'SER-0173': 'regional',
                  'SER-0174': 'interregional', 'SER-0175': 'interregional'}
        for i, (sid, competence) in enumerate(levels.items(), 221):
            rec = self.by_id[sid]
            self.assertTrue(rec['names']['preferred'].startswith('Inrap '))
            self.assertEqual(rec['kind'], 'SER')
            self.assertEqual(rec['classification']['level'], 'national')
            self.assertEqual(rec['classification']['level_origin']['org_ids'], ['ORG-0008'])
            self.assertEqual(rec['classification']['territorial_competence'], competence)
            self.assertEqual(rec['usage']['affiliations_linked'], 0)
            self.assertEqual(rec['usage']['source_occurrences_linked'], 0)
            rel = self.relations[f'RSE-{i:04d}']
            self.assertEqual((rel['source'], rel['target'], rel['type']),
                             (sid, 'ORG-0008', 'rattachement_service'))

    def test_thau_historical_succession(self):
        old = self.by_id['ORG-0676']
        self.assertFalse(old['activity']['active'])
        self.assertFalse(old['presentation']['visible'])
        self.assertEqual(old['usage']['affiliations_linked'], 0)
        self.assertEqual(self.relations['REL-0306']['target'], 'ORG-0214')
        self.assertEqual(self.by_id['ORG-0214']['activity']['start'], '2017-01-01')
        self.assertEqual(self.by_id['ORG-0659']['classification']['level'], None)

    def test_source_affiliations_not_propagated(self):
        self.assertEqual(
            self.by_id['ORG-0008']['usage']['affiliations_linked'], 46)
        self.assertEqual(
            self.by_id['ORG-0008']['usage']['source_occurrences_linked'], 270)

if __name__ == '__main__':
    unittest.main()
