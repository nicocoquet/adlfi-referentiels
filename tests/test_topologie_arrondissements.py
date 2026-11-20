"""Contrat statique de l'audit de bordure sans dépendance géospatiale en CI."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/data/lieux-communes-plm-reconstituees.geojson'
AUDIT = ROOT / 'docs/data/lieux-arrondissements-topologie-2026.json'
HTML = ROOT / 'docs/lieux/arrondissements-recette.html'
JS = ROOT / 'docs/assets/lieux-arrondissements-recette.js'


class TopologieArrondissements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))
        cls.audit = json.loads(AUDIT.read_text(encoding='utf-8'))

    def test_trois_communes_derivees_et_qualifiees(self):
        self.assertEqual(self.data['type'], 'FeatureCollection')
        self.assertEqual(self.data['metadata']['nature'], 'geometrie_derivee')
        self.assertEqual(self.data['metadata']['validation_independante'], 'non_effectuee')
        self.assertEqual({x['properties']['code_commune'] for x in self.data['features']},
                         {'75056','69123','13055'})
        for feature in self.data['features']:
            self.assertTrue(feature['geometry']['coordinates'])
            self.assertEqual(feature['properties']['validation_limite_communale_independante'],
                             'non_verifiee')

    def test_topologie_interne_documentee(self):
        effectifs = {'Paris': 20, 'Lyon': 9, 'Marseille': 16}
        for ville, n in effectifs.items():
            s = self.audit['communes'][ville]
            self.assertEqual(s['nombre_arrondissements'], n)
            self.assertTrue(s['geometrie_union_valide'])
            self.assertEqual(s['chevauchements_surface_significatifs'], 0)
            self.assertEqual(s['trous_internes'], 0)
            self.assertLess(abs(s['ecart_additivite_bordures_m']), .001)
            self.assertEqual(s['reference_communale_independante']['statut'], 'non_fournie')
        self.assertEqual(self.audit['communes']['Marseille']['composantes_spatiales'], 7)

    def test_presentation_n_annonce_pas_une_validation_externe(self):
        html = HTML.read_text(encoding='utf-8')
        js = JS.read_text(encoding='utf-8')
        self.assertIn('ne constitue pas une comparaison indépendante', html)
        self.assertIn('lieux-communes-plm-reconstituees.geojson', js)
        self.assertIn('parentBorders.addTo(map)', js)


if __name__ == '__main__':
    unittest.main()
