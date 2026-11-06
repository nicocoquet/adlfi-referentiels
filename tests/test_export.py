#!/usr/bin/env python3
"""Vérifications du JSON de publication, sans dépendances externes."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from scripts import export_organismes

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/data/organismes.json'


class TestReferentielOrganismes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(DATA.read_text(encoding='utf-8'))
        cls.authorities = {x['id']: x for x in cls.d['authorities']}

    def test_identifiers_and_counts(self):
        self.assertEqual(len(self.authorities), len(self.d['authorities']))
        self.assertEqual(self.d['totals']['authorities'], len(self.authorities))
        self.assertEqual(self.d['totals']['catalog_included'],
                         sum(x['presentation']['visible'] for x in self.authorities.values()))
        self.assertEqual(self.d['totals']['catalog_excluded'],
                         sum(not x['presentation']['visible'] for x in self.authorities.values()))

    def test_identity_hierarchy(self):
        musee=self.authorities['ORG-0013']
        ville=self.authorities['ORG-0027']
        self.assertTrue(musee['presentation']['visible'])
        self.assertFalse(ville['presentation']['visible'])
        self.assertTrue(any(r['source']=='ORG-0013' and r['target']=='ORG-0027'
                            and r['validation']=='valide' for r in self.d['relations']))

    def test_relations_refer_to_existing_authorities(self):
        for r in self.d['relations']:
            self.assertIn(r['source'], self.authorities)
            self.assertIn(r['target'], self.authorities)
        self.assertTrue(any(r['id']=='REL-0287' and r['target']=='ORG-0632'
                            for r in self.d['relations']))

    def test_laboratory_designation_is_not_duplicated(self):
        self.assertEqual(self.authorities['ORG-0001']['identifiers']['lab'], 'UMR 7299')
        for record in self.authorities.values():
            self.assertNotIn('umr',record['identifiers'])

    def test_atemporelle_continuity_and_provisional_history(self):
        r=self.authorities['ORG-0237']
        h=r['names']['legal_status_history']
        self.assertEqual(len(h),2)
        self.assertEqual([(x['start'],x['type']) for x in h],
                         [('1998','association'),('2011','entreprise')])
        self.assertTrue(all(x['validation']=='a_verifier' for x in h))

    def test_no_editorial_comments(self):
        text=DATA.read_text(encoding='utf-8')
        self.assertNotIn('"commentaire"',text)
        self.assertNotIn('"source_documentaire"',text)
        self.assertNotIn('"editorial"',text)

    def test_shared_authority_media_and_unique_roles(self):
        self.assertEqual(export_organismes.SITE_ROOT, ROOT / 'docs')
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'assets/organismes'
            folder.mkdir(parents=True)
            # Un même logo est utilisé pour l'ORG elle-même et comme tutelle.
            (folder / 'ORG-0004-logo.svg').write_text('<svg/>', encoding='utf-8')
            (folder / 'ORG-0001-illustration.webp').write_bytes(b'image')
            (folder / 'ORG-0001-logo.png').write_bytes(b'logo')
            with patch.object(export_organismes,'SITE_ROOT',root):
                self.assertEqual(export_organismes.media_for('ORG-0004'), {
                    'image': None,
                    'logo': 'assets/organismes/ORG-0004-logo.svg'})
                self.assertEqual(export_organismes.media_for('ORG-0001'), {
                    'image': 'assets/organismes/ORG-0001-illustration.webp',
                    'logo': 'assets/organismes/ORG-0001-logo.png'})
                self.assertEqual(export_organismes.media_for('ORG-NONVALIDE'),
                                 {'image':None,'logo':None})
                # Deux extensions pour le même rôle ne sont pas permises.
                (folder / 'ORG-0001-logo.svg').write_text('<svg/>',encoding='utf-8')
                with self.assertRaises(ValueError):
                    export_organismes.media_for('ORG-0001')

    def test_laboratory_cards_keep_the_standard_grid(self):
        # Les laboratoires ne doivent pas occuper les deux colonnes :
        # le résultat filtré doit conserver la même largeur de cartouche.
        import re
        css = (ROOT / 'docs/assets/site.css').read_text(encoding='utf-8')
        grid = re.search(r'\\.cards\\s*\\{([^}]*)\\}', css)
        self.assertIsNotNone(grid)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',
                      grid.group(1))
        lab = re.search(r'\\.cards\\s+\\.laboratory-card\\s*\\{([^}]*)\\}', css)
        self.assertIsNotNone(lab)
        self.assertNotIn('grid-column', lab.group(1))
        self.assertIn('.cards.list-mode{grid-template-columns:1fr}', css)

    def test_site_files_exist(self):
        self.assertTrue((ROOT/'docs/index.html').exists())
        for p in ['lieux','autorites','organismes','natures-operations']:
            self.assertTrue((ROOT/f'docs/{p}/index.html').exists())
        self.assertTrue((ROOT/'docs/.nojekyll').exists())


if __name__=='__main__': unittest.main()
