"""Non-régression du lot 03 publié : 72 PER, 1 276 contributions, 1 222 notices.

Sources : visa éditorial lot 03 AdlFI 2026-11-25, rapprochement Heurist et audit TEI.
Ce fichier ne contient pas de journaux internes ni de références aux fichiers XML privés.
"""
import json
import unittest
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PUB = BASE / 'docs/data/personnes.json'
MANIFEST = BASE / 'docs/data/manifest.json'

EXPECTED_LOT03 = [
    ('Florence Mocci', '112126618', 12),
    ('Katherine Gruel', '026904918', 11),
    ('Romain Pigeaud', '067353754', 11),
    ('Michiel Gazenbeek', '048653462', 10),
    ('Nathalie Bonvalot', '092110215', 10),
    ('Elsa Sagetat-Basseuil', '159763762', 10),
    ('Vincent Ard', '161182097', 10),
    ('Vincent Delvigne', '19350345X', 10),
    ('Vanessa Elizagoyen', '269619909', 10),
    ('Michèle Julien', '026942844', 9),
    ('Philippe Barral', '029141923', 9),
    ('Joseph Cesari', '029373832', 9),
    ('Martial Monteil', '031790135', 9),
    ('Béatrice Cauuet', '033900515', 9),
    ('Yves Lanchon', '056544561', 9),
    ('Yves Manniez', '056905483', 9),
    ('Jean-Pierre Coutard', '057314616', 9),
    ('Gérald Barbet', '057572771', 9),
    ('Boris Valentin', '05777059X', 9),
    ('Thierry Argant', '060944560', 9),
    ('Vincent Goustard', '184668344', 18),
    ('Dominique Pitte', '030111102', 13),
    ('Pierre Bodu', '057770603', 13),
    ('Yoann Rabasté', '16109743X', 13),
    ('Sandrine Bertaudière', '243730233', 13),
    ('Sébastien Jeandemange', '249886383', 13),
    ('Jean-Philippe Baigl', '136224830', 12),
    ('Stéphane Dubois', '170483290', 11),
    ('Jonathan Letuppe', '281432848', 11),
    ('Jean-Pierre Urlacher', '028814355', 10),
]

class TestPersonnesLot03(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pub=json.loads(PUB.read_text(encoding='utf-8'))
        cls.manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))

    def test_autorites_identifiants_stables(self):
        people=self.pub['authorities']
        self.assertGreaterEqual(len(people), 72)
        self.assertEqual([x['id'] for x in people[:72]], [f'PER-{i:06d}' for i in range(1,73)])
        self.assertEqual(len({x['identifiers']['idref'] for x in people[:72]}),72)
        for pos, (name,ppn,count) in enumerate(EXPECTED_LOT03,start=42):
            a=people[pos]
            self.assertEqual((a['name'],a['identifiers']['idref'],a['contributions_count']),(name,ppn,count))
            self.assertTrue(a['family_name'])
            self.assertEqual(a['name_variants'], [])

    def test_contributions_et_notices(self):
        docs=self.pub['contributions'][:1276]
        self.assertGreaterEqual(self.pub['totals']['authorities'], 72)
        self.assertGreaterEqual(self.pub['totals']['contributions'], 1276)
        self.assertGreaterEqual(self.pub['totals']['notices'], 1222)
        self.assertEqual(len(docs),1276)
        self.assertEqual(len({x['notice']['url'] for x in docs}),1222)
        self.assertEqual(len({(x['person_id'],x['notice']['url']) for x in docs}),1276)
        self.assertEqual(Counter(' '.join(x['roles']) for x in docs),Counter({'aut fld':1067,'aut':199,'fld':10}))
        self.assertEqual(len(docs[956:]),320)
        self.assertEqual(len({x['notice']['url'] for x in docs[956:]}),309)
        self.assertEqual(len({x['notice']['url'] for x in docs[:956]} & {x['notice']['url'] for x in docs[956:]}),17)
        self.assertTrue(all(x['notice']['title'].strip() for x in docs))
        self.assertFalse(any('entités actuelles' in x['notice']['title'] for x in docs))

    def test_manifeste(self):
        module=self.manifest['modules']['personnes']
        self.assertEqual((module['autorites_validees'],module['contributions_adlfi'],module['notices_adlfi']), (self.pub['totals']['authorities'],self.pub['totals']['contributions'],self.pub['totals']['notices']))
        self.assertEqual(module['data_schema'],'0.4.0')
        self.assertEqual(module['status'],'pilote')

    def test_aucune_donnee_de_visa_publique(self):
        forbidden={'reference_visa','h_id_heurist','source_xml','sha256_xml_source','publication_nouvelle_autorisee','responsable_visa'}
        def walk(obj):
            if isinstance(obj,dict):
                for key,value in obj.items():
                    yield key
                    yield from walk(value)
            if isinstance(obj,list):
                for value in obj:yield from walk(value)
        self.assertFalse(forbidden & set(walk(self.pub)))

if __name__=='__main__':
    unittest.main()
