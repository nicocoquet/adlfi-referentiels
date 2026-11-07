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

    def test_all_published_logos_are_present_and_unique(self):
        # Les logos des autorités peuvent être réutilisés dans les bandeaux
        # de tutelle : une seule image par identifiant, sans fichier orphelin.
        import re
        folder=ROOT/'docs/assets/organismes'
        files={'assets/organismes/'+p.name for p in folder.iterdir()
               if p.is_file() and re.fullmatch(
                   r'(?:ORG|SER)-[0-9]{4}-logo\\.(?:webp|svg|png|jpg|jpeg)',
                   p.name)}
        logos={}
        for record in self.d['authorities']:
            ref=record['presentation']['media']['logo']
            if ref:
                self.assertRegex(ref,r'^assets/organismes/(?:ORG|SER)-[0-9]{4}-logo\\.(?:webp|svg|png|jpg|jpeg)
        # Les laboratoires ne doivent pas occuper les deux colonnes :
        # le résultat filtré doit conserver la même largeur de cartouche.
        import re
        css = (ROOT / 'docs/assets/site.css').read_text(encoding='utf-8')
        grid = re.search(r'\.cards\s*\{([^}]*)\}', css)
        self.assertIsNotNone(grid)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',
                      grid.group(1))
        lab = re.search(r'\.cards\s+\.laboratory-card\s*\{([^}]*)\}', css)
        self.assertIsNotNone(lab)
        self.assertNotIn('grid-column', lab.group(1))
        self.assertIn('.cards.list-mode{grid-template-columns:1fr}', css)
        band = re.search(r'\.lab-logo-band\s*\{([^}]*)\}', css)
        self.assertIsNotNone(band)
        self.assertIn('justify-content:center', band.group(1))

    def test_culture_master_consolidation(self):
        # Dates et autorités issues du maître consolidé du 7 novembre 2026.
        expected = {
            'ORG-0023': '1959',
            'ORG-0035': '1969', 'ORG-0055': '1980',
            'ORG-0057': '1969', 'ORG-0067': '1969',
            'ORG-0041': '1981-12-20', 'ORG-0042': '1992',
            'ORG-0043': '1984-07', 'ORG-0044': '1989',
            'ORG-0051': '2016', 'ORG-0478': '1990',
            'ORG-0314': '1882', 'ORG-0083': '2013-03-01',
            'SER-0083': '1996', 'SER-0111': '1999-01-01',
            'SER-0118': '1975',
            'SER-0151': '1966-09-30', 'SER-0152': '1980',
        }
        for key, start in expected.items():
            self.assertEqual(self.authorities[key]['activity']['start'], start,
                             key)
        self.assertFalse(self.authorities['ORG-0042']['activity']['active'])
        self.assertEqual(self.authorities['ORG-0042']['activity']['end'],
                         '2019-12-31')
        self.assertEqual(self.authorities['ORG-0478']['names']['history'][0]['label'],
                         'École nationale du patrimoine')
        self.assertEqual(len(self.authorities['ORG-0041']['names']['history']), 2)
        self.assertEqual(self.authorities['SER-0151']['names']['history'][0]['start'],
                         '1991')
        self.assertEqual(self.authorities['SER-0083']['names']['history'], [])
        self.assertEqual(self.d['totals']['organismes'], 611)
        self.assertEqual(self.d['totals']['services'], 152)
        self.assertEqual(len(self.d['relations']), 419)
        rels = {rel['id']: rel for rel in self.d['relations']}
        for key, src, dst, role in [
            ('REL-0288','ORG-0478','ORG-0023','tutelle'),
            ('RSE-0130','SER-0151','SER-0083','fusion_constitutive'),
            ('RSE-0131','SER-0152','SER-0083','fusion_constitutive'),
            ('RSE-0132','SER-0111','ORG-0023','rattachement_service'),
            ('RSE-0133','SER-0118','SER-0037','rattachement_service')]:
            self.assertEqual((rels[key]['source'], rels[key]['target'],
                              rels[key]['type'], rels[key]['validation']),
                             (src, dst, role, 'valide'))

    def test_site_files_exist(self):
        self.assertTrue((ROOT/'docs/index.html').exists())
        for p in ['lieux','autorites','organismes','natures-operations']:
            self.assertTrue((ROOT/f'docs/{p}/index.html').exists())
        self.assertTrue((ROOT/'docs/.nojekyll').exists())


if __name__=='__main__': unittest.main()
)
                self.assertEqual(ref.split('/')[-1][:8],record['id'])
                self.assertNotIn(ref,logos)
                logos[ref]=record['id']
        self.assertEqual(set(logos),files)
        self.assertEqual(len(logos),147)
        self.assertEqual(len([x for x in logos.values() if x.startswith('ORG-')]),136)
        self.assertEqual(len([x for x in logos.values() if x.startswith('SER-')]),11)
        self.assertEqual(self.authorities['ORG-0079']['presentation']['media']['logo'],
                         'assets/organismes/ORG-0079-logo.webp')
        self.assertEqual(self.authorities['SER-0083']['presentation']['media']['logo'],
                         'assets/organismes/SER-0083-logo.webp')

    def test_laboratory_cards_keep_the_standard_grid(self):
        # Les laboratoires ne doivent pas occuper les deux colonnes :
        # le résultat filtré doit conserver la même largeur de cartouche.
        import re
        css = (ROOT / 'docs/assets/site.css').read_text(encoding='utf-8')
        grid = re.search(r'\.cards\s*\{([^}]*)\}', css)
        self.assertIsNotNone(grid)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',
                      grid.group(1))
        lab = re.search(r'\.cards\s+\.laboratory-card\s*\{([^}]*)\}', css)
        self.assertIsNotNone(lab)
        self.assertNotIn('grid-column', lab.group(1))
        self.assertIn('.cards.list-mode{grid-template-columns:1fr}', css)
        band = re.search(r'\.lab-logo-band\s*\{([^}]*)\}', css)
        self.assertIsNotNone(band)
        self.assertIn('justify-content:center', band.group(1))

    def test_culture_master_consolidation(self):
        # Dates et autorités issues du maître consolidé du 7 novembre 2026.
        expected = {
            'ORG-0023': '1959',
            'ORG-0035': '1969', 'ORG-0055': '1980',
            'ORG-0057': '1969', 'ORG-0067': '1969',
            'ORG-0041': '1981-12-20', 'ORG-0042': '1992',
            'ORG-0043': '1984-07', 'ORG-0044': '1989',
            'ORG-0051': '2016', 'ORG-0478': '1990',
            'ORG-0314': '1882', 'ORG-0083': '2013-03-01',
            'SER-0083': '1996', 'SER-0111': '1999-01-01',
            'SER-0118': '1975',
            'SER-0151': '1966-09-30', 'SER-0152': '1980',
        }
        for key, start in expected.items():
            self.assertEqual(self.authorities[key]['activity']['start'], start,
                             key)
        self.assertFalse(self.authorities['ORG-0042']['activity']['active'])
        self.assertEqual(self.authorities['ORG-0042']['activity']['end'],
                         '2019-12-31')
        self.assertEqual(self.authorities['ORG-0478']['names']['history'][0]['label'],
                         'École nationale du patrimoine')
        self.assertEqual(len(self.authorities['ORG-0041']['names']['history']), 2)
        self.assertEqual(self.authorities['SER-0151']['names']['history'][0]['start'],
                         '1991')
        self.assertEqual(self.authorities['SER-0083']['names']['history'], [])
        self.assertEqual(self.d['totals']['organismes'], 611)
        self.assertEqual(self.d['totals']['services'], 152)
        self.assertEqual(len(self.d['relations']), 419)
        rels = {rel['id']: rel for rel in self.d['relations']}
        for key, src, dst, role in [
            ('REL-0288','ORG-0478','ORG-0023','tutelle'),
            ('RSE-0130','SER-0151','SER-0083','fusion_constitutive'),
            ('RSE-0131','SER-0152','SER-0083','fusion_constitutive'),
            ('RSE-0132','SER-0111','ORG-0023','rattachement_service'),
            ('RSE-0133','SER-0118','SER-0037','rattachement_service')]:
            self.assertEqual((rels[key]['source'], rels[key]['target'],
                              rels[key]['type'], rels[key]['validation']),
                             (src, dst, role, 'valide'))

    def test_site_files_exist(self):
        self.assertTrue((ROOT/'docs/index.html').exists())
        for p in ['lieux','autorites','organismes','natures-operations']:
            self.assertTrue((ROOT/f'docs/{p}/index.html').exists())
        self.assertTrue((ROOT/'docs/.nojekyll').exists())


if __name__=='__main__': unittest.main()
