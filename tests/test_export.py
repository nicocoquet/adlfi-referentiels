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

    def test_published_sector_resolution_1_47(self):
        # 172 SER ont un secteur explicite dans le maître 1.47 ; 2 cas historiques héritent.
        self.assertEqual(
            self.d['provenance']['source_filename'],
            'AdlFI_referentiel_1-47_20261111_echelons_competences_Inrap.xlsx')
        self.assertEqual(
            self.d['provenance']['source_sha256'],
            '1138c330f59c91c301d0cb6a5136c1e1347fbf491a75a9bddfe7d9b9fa83df51')
        services = [a for a in self.authorities.values() if a['kind'] == 'SER']
        self.assertEqual(len(services), 174)
        inherited = [a for a in services if a['classification']['sector_origin']['method'] == 'inherited']
        explicit = [a for a in services if a['classification']['sector_origin']['method'] == 'explicit']
        self.assertEqual(len(inherited), 2)
        self.assertEqual(len(explicit), 172)
        self.assertEqual(
            {a['id'] for a in inherited}, {'SER-0116', 'SER-0149'})
        for a in inherited:
            self.assertIn(a['classification']['sector'], ('public', 'prive'))
            self.assertTrue(a['classification']['sector_origin']['org_ids'])
            self.assertFalse(a['quality']['sector_unresolved'])
        for a in explicit:
            self.assertIn(a['classification']['sector'], ('public', 'prive'))
            self.assertEqual(a['classification']['sector_origin']['field'], 'Services.secteur_institutionnel')
            self.assertFalse(a['quality']['sector_unresolved'])
        self.assertEqual(self.d['totals']['service_sector_unresolved_ids'], [])
        self.assertEqual(self.d['totals']['service_sector_resolution'], {'prive': 2, 'public': 172})
        visible = [a for a in self.authorities.values() if a['presentation']['visible']]
        self.assertEqual(sum(a['classification']['sector'] == 'public' for a in visible), 396)
        self.assertEqual(sum(a['classification']['sector'] == 'prive' for a in visible), 195)
        self.assertEqual(sum(a['classification']['sector'] is None for a in visible), 0)
        scp = self.authorities['ORG-0292']
        self.assertEqual(scp['classification']['bsr'], 'PRIV')
        self.assertEqual(scp['classification']['sector'], 'public')

    def test_archeologie_alsace_legal_succession_1_41(self):
        old = self.authorities['ORG-0093']
        new = self.authorities['ORG-0675']
        self.assertEqual(old['names']['preferred'], 'Archéologie Alsace')
        self.assertEqual(new['names']['preferred'], 'Archéologie Alsace')
        self.assertEqual(old['classification']['type'], 'etablissement_public')
        self.assertEqual(new['classification']['type'], 'syndicat_mixte')
        self.assertEqual(old['classification']['sector'], 'public')
        self.assertEqual(new['classification']['sector'], 'public')
        self.assertIsNone(old['classification']['level'])
        self.assertIsNone(new['classification']['level'])
        self.assertFalse(old['activity']['active'])
        self.assertEqual(old['activity']['end'], '2020-12-11')
        self.assertTrue(new['activity']['active'])
        self.assertEqual(new['activity']['start'], '2020-12-11')
        self.assertEqual(old['usage']['source_occurrences_linked'], 181)
        self.assertEqual(old['usage']['affiliations_linked'], 2)
        self.assertEqual(old['usage']['affiliations_validated'], 2)
        self.assertEqual(new['usage']['source_occurrences_linked'], 0)
        self.assertEqual(new['usage']['affiliations_linked'], 0)
        self.assertEqual(old['names']['history'][0]['end'], '2016-10-14')
        self.assertEqual(old['names']['legal_status_history'][0]['legal_form'],
                         'institution_interdepartementale')
        self.assertEqual(new['names']['legal_status_history'][0]['legal_form'],
                         'syndicat_mixte_ouvert')
        self.assertIsNone(old['presentation']['media']['logo'])
        self.assertEqual(new['presentation']['media']['logo'],
                         'assets/organismes/ORG-0675-logo.webp')
        self.assertIsNone(old['website'])
        self.assertEqual(new['website'], 'https://www.archeologie.alsace/')
        rels = {r['id']: r for r in self.d['relations']}
        self.assertEqual(
            (rels['REL-0305']['source'], rels['REL-0305']['target'],
             rels['REL-0305']['type'], rels['REL-0305']['start'],
             rels['REL-0305']['validation']),
            ('ORG-0093', 'ORG-0675', 'succession_institutionnelle',
             '2020-12-11', 'valide'))
        self.assertEqual(rels['REL-0054']['validation'], 'a_verifier')
        # Une relation non validée ne constitue pas une tutelle établie.

    def test_published_institutional_levels_lot01(self):
        self.assertEqual(self.authorities['ORG-0249']['classification']['type'],
                         'epci')
        self.assertEqual(self.authorities['ORG-0249']['classification']['level'],
                         'intercommunal')
        self.assertEqual(self.authorities['ORG-0249']['names']['legal_status_history'][0]['legal_form'],
                         'communaute_agglomeration')
        self.assertEqual(self.authorities['ORG-0429']['classification']['level'],
                         'communal')
        lyon = self.authorities['ORG-0650']
        self.assertEqual(lyon['classification']['type'], 'collectivite_territoriale')
        self.assertEqual(lyon['classification']['level'], 'metropolitain')
        self.assertEqual(lyon['names']['legal_status_history'][0]['legal_form'],
                         'collectivite_statut_particulier')

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
        # Une identité visuelle unique par autorité, réutilisable comme tutelle.
        import re
        folder = ROOT / 'docs/assets/organismes'
        files = {'assets/organismes/' + p.name for p in folder.iterdir()
                 if p.is_file() and re.fullmatch(
                     r'(?:ORG|SER)-[0-9]{4}-logo\.(?:webp|svg|png|jpg|jpeg)',
                     p.name)}
        logos = {}
        for record in self.d['authorities']:
            ref = record['presentation']['media']['logo']
            if ref:
                self.assertRegex(ref, r'^assets/organismes/(?:ORG|SER)-[0-9]{4}-logo\.(?:webp|svg|png|jpg|jpeg)$')
                self.assertEqual(ref.split('/')[-1][:8], record['id'])
                self.assertNotIn(ref, logos)
                logos[ref] = record['id']
        self.assertEqual(set(logos), files)
        self.assertGreaterEqual(len(logos), 150)
        self.assertGreaterEqual(len([i for i in logos.values() if i.startswith('ORG-')]), 139)
        self.assertGreaterEqual(len([i for i in logos.values() if i.startswith('SER-')]), 11)
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
        # Jalons historiques conservés après migration du maître 1.41.
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
        self.assertEqual(self.d['totals']['organismes'], 655)
        self.assertEqual(self.d['totals']['services'], 174)
        self.assertEqual(len(self.d['relations']), 531)
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


    def test_2026_preventive_archaeology_operators(self):
        # Les nouvelles autorités des listes ministérielles sont distinctes de leurs tutelles.
        expected = {
            'SER-0157': 'ORG-0653',
            'SER-0158': 'ORG-0654',
            'SER-0159': 'ORG-0240',
            'SER-0160': 'ORG-0145',
            'SER-0161': 'ORG-0096',
            'SER-0162': 'ORG-0102',
            'SER-0163': 'ORG-0655',
            'SER-0164': 'ORG-0339',
            'SER-0165': 'ORG-0294',
            'SER-0166': 'ORG-0189',
        }
        relations = {(r['source'], r['target'], r['type'], r['validation'])
                     for r in self.d['relations']}
        self.assertEqual(self.d['totals']['authorities'], 829)
        for service, tutelle in expected.items():
            self.assertIn(service, self.authorities)
            self.assertIn(tutelle, self.authorities)
            self.assertIn((service, tutelle, 'rattachement_service', 'valide'), relations)

    def test_site_files_exist(self):
        self.assertTrue((ROOT/'docs/index.html').exists())
        for p in ['lieux','personnes','autorites','organismes','natures-operations']:
            self.assertTrue((ROOT/f'docs/{p}/index.html').exists())
        self.assertTrue((ROOT/'docs/.nojekyll').exists())


if __name__=='__main__': unittest.main()
