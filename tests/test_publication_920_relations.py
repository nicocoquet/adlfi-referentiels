"""Contrat de publication du maître AdlFI enrichi (20 novembre 2026).

Ce contrôle porte exclusivement sur le JSON public, jamais sur le XLSX privé.
Il complète les tests historiques et assure la recette des nouvelles filiations.
"""
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'docs/data/organismes.json'
MASTER='AdlFI_referentiel_1-61_lot01_activites_et_date_CANDIDAT.xlsx'
MASTER_SHA='fb475d0270ca74757c7d34dc97978897dccdf5b12cc10c2ec8aa3f35a65e8b98'


class OrganismesPublication920Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(PUBLIC.read_text(encoding='utf-8'))
        cls.entities={a['id']:a for a in cls.data['authorities']}
        cls.relations={r['id']:r for r in cls.data['relations']}

    def test_provenance_and_card_counts(self):
        d=self.data
        self.assertEqual(d['schema_version'],'0.3.0')
        self.assertEqual(d['provenance']['source_filename'],MASTER)
        self.assertEqual(d['provenance']['source_sha256'],MASTER_SHA)
        self.assertEqual(len(self.entities),935)
        self.assertEqual(len(self.relations),600)
        self.assertEqual(d['totals']['organismes'],735)
        self.assertEqual(d['totals']['services'],200)
        self.assertEqual(d['totals']['catalog_included'],683)
        self.assertEqual(d['totals']['catalog_excluded'],252)
        self.assertEqual(sum(a['presentation']['visible'] for a in self.entities.values()),683)
        self.assertEqual(Counter(a['kind'] for a in self.entities.values()),
                         Counter({'ORG':735,'SER':200}))

    def test_references_and_source_types(self):
        for rid, rel in self.relations.items():
            self.assertIn(rel['source'],self.entities,rid)
            self.assertIn(rel['target'],self.entities,rid)
            self.assertNotEqual(rel['source'],rel['target'],rid)
            source=self.entities[rel['source']]['kind']
            target=self.entities[rel['target']]['kind']
            if rid.startswith('REL-'):
                self.assertEqual((source,target),('ORG','ORG'),rid)
            else:
                self.assertTrue(rid.startswith('RSE-'),rid)
                self.assertEqual(source,'SER',rid)
                self.assertIn(target,('SER','ORG'),rid)
        self.assertEqual(sum(r.startswith('REL-') for r in self.relations),342)
        self.assertEqual(sum(r.startswith('RSE-') for r in self.relations),258)

    def test_traces_fusion_and_imbé(self):
        for rid,source,target,date in [
                ('REL-0314','ORG-0736','ORG-0151','2007-01-01'),
                ('REL-0315','ORG-0737','ORG-0151','2007-01-01'),
                ('REL-0318','ORG-0741','ORG-0743','2012-01-01'),
                ('REL-0319','ORG-0742','ORG-0743','2012-01-01')]:
            r=self.relations[rid]
            self.assertEqual((r['source'],r['target'],r['type'],r['start'],r['validation']),
                             (source,target,'fusion_constitutive',date,'valide'))

    def test_crp2a_not_misread_as_universal_succession(self):
        r=self.relations['RSE-0252']
        self.assertEqual(r,{
            'id':'RSE-0252','source':'SER-0196','target':'ORG-0537',
            'type':'filiation_partielle','start':'2022-01-01',
            'end':None,'validation':'valide'
        })
        self.assertEqual(self.relations['REL-0128']['type'],'succession_partielle')
        self.assertEqual(self.relations['RSE-0251']['target'],'ORG-0393')
        self.assertFalse(self.entities['SER-0196']['activity']['active'])
        self.assertTrue(self.entities['ORG-0537']['activity']['active'])

    def test_nested_departmental_service_and_museum(self):
        self.assertEqual(self.relations['RSE-0247']['target'],'ORG-0725')
        self.assertEqual(self.relations['RSE-0248']['source'],'SER-0193')
        self.assertEqual(self.relations['RSE-0248']['target'],'SER-0192')
        self.assertEqual(self.relations['RSE-0233']['target'],'ORG-0697')
        self.assertFalse(self.entities['ORG-0697']['presentation']['visible'])
        self.assertTrue(self.entities['SER-0180']['presentation']['visible'])

    def test_media_and_editorial_confidentiality(self):
        logos={f'assets/organismes/{p.name}'
               for p in (ROOT/'docs/assets/organismes').glob('*.jpg')}
        media={a['presentation']['media']['logo']
               for a in self.entities.values()
               if a['presentation']['media']['logo']}
        # Les logos encore adressables par un ancien ID doivent être couverts
        # par un alias documenté et avoir exactement les mêmes octets que le
        # fichier canonique, sans ouvrir la porte à d'autres orphelins.
        from hashlib import sha256
        legacy=logos-media
        self.assertEqual(legacy,{'assets/organismes/SER-0063.jpg'})
        aliases={x['from']:x['to'] for x in self.data['aliases']}
        for ref in legacy:
            old=Path(ref).stem
            self.assertIn(old,aliases)
            target='assets/organismes/'+aliases[old]+'.jpg'
            self.assertIn(target,media)
            self.assertEqual(sha256((ROOT/'docs'/ref).read_bytes()).digest(),
                             sha256((ROOT/'docs'/target).read_bytes()).digest())
        self.assertEqual(len(media),684)
        for a in self.entities.values():
            self.assertIsNone(a['presentation']['media']['image'])
        source=PUBLIC.read_text(encoding='utf-8')
        self.assertNotIn('"commentaire"',source)
        self.assertNotIn('"source_documentaire"',source)


if __name__=='__main__':
    unittest.main()
