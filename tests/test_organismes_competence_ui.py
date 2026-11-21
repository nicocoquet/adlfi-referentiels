"""Rendre la compétence territoriale documentée sans la confondre avec l'échelon."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class OrganismesCompetenceUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/'docs/data/organismes.json').read_text(encoding='utf-8'))
        cls.org={r['id']:r for r in cls.d['authorities']}
        cls.js=(ROOT/'docs/assets/organismes.js').read_text(encoding='utf-8')
        cls.readme=(ROOT/'README.md').read_text(encoding='utf-8')

    def test_provenance_et_effectifs_maitre_149(self):
        self.assertEqual(self.d['provenance']['source_filename'],
            'AdlFI_referentiel_1-52_A02_A03_QUALIFIE_CANDIDAT.xlsx')
        self.assertEqual(self.d['totals']['authorities'],934)
        self.assertEqual(self.d['totals']['organismes'],734)
        self.assertEqual(self.d['totals']['services'],200)
        self.assertEqual(self.d['totals']['catalog_included'],682)
        self.assertIn('934 autorités',self.readme)
        self.assertIn('maître 1.50',self.readme)

    def test_treize_perimetres_explicitement_renseignes(self):
        explicit={r['id']:r for r in self.d['authorities']
                  if r['classification'].get('territorial_competence')}
        self.assertEqual(set(explicit),{'ORG-0008','SER-0176','SER-0192','SER-0193','SER-0194'}|
                         {f'SER-{i:04d}' for i in range(168,176)})
        self.assertEqual(explicit['ORG-0008']['classification']['level'],'national')
        self.assertEqual(explicit['ORG-0008']['classification']['territorial_competence'],'national')
        for i in range(168,176):
            r=explicit[f'SER-{i:04d}']
            self.assertEqual(r['classification']['level'],'national')
            self.assertIn(r['classification']['territorial_competence'],
                          ('regional','interregional'))
        self.assertEqual(sum(x['classification'].get('territorial_competence') is None
                             for x in self.d['authorities']),921)

    def test_fiche_et_csv_distincts_sans_fausse_facette(self):
        self.assertIn("row('Échelon institutionnel'",self.js)
        self.assertIn("row('Périmètre de compétence'",self.js)
        self.assertIn("r.classification.territorial_competence?row",self.js)
        self.assertIn("'Échelon institutionnel','Périmètre de compétence','Actif'",self.js)
        self.assertIn("x.classification.level_origin?.method==='not_applicable'",self.js)
        self.assertIn("x.classification.territorial_competence,flagLabel(x.activity.active)",self.js)
        self.assertIn("interregional:'Interrégional'",self.js)
        self.assertNotIn("key:'competence'",self.js)
        self.assertIn("facette Échelon institutionnel",self.readme)

    def test_secteur_et_categorie_reste_distincts(self):
        services=[a for a in self.d['authorities'] if a['kind']=='SER']
        self.assertEqual(len(services),200)
        self.assertEqual({key:sum(x['classification']['sector']==key for x in services)
                          for key in ('public','prive')},{'public':197,'prive':3})
        self.assertEqual(self.org['ORG-0292']['classification']['sector'],'public')
        self.assertEqual(self.org['ORG-0292']['classification']['bsr'],'PRIV')


if __name__=='__main__':
    unittest.main()
