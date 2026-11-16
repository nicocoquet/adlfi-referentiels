"""Tests sans réseau de la carte de recette multi-échelon et de sa provenance."""
from __future__ import annotations
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from construire_vue_lieux_multiechelon import construire, verifier_regions, MARQUEUR

SHAPELY = importlib.util.find_spec('shapely') is not None
TEMPLATE = ROOT / 'recette' / 'lieux' / 'vue-lieux-multiechelon-modele.html'


def fixture():
    layers = {}
    for year, region_count in ((2015, 22), (2016, 13)):
        reg = [{'properties': {'code': f'{i:02}', 'nom': f'Région {i}',
                               'niveau': 'region', 'annee': year}}
               for i in range(region_count)]
        dep = [{'properties': {'code': f'{i:02}', 'nom': f'Département {i}',
                               'niveau': 'departement', 'annee': year}}
               for i in range(96)]
        layers[str(year)] = {'region': reg, 'departement': dep}
    return {'layers': layers, 'alignements_Pactols_generes': 0,
            'aucune_geometrie_2026_retroprojetee': True}


class InterfaceLieuxRecetteTests(unittest.TestCase):
    def test_modele_controles_et_recherche(self):
        html = TEMPLATE.read_text(encoding='utf8')
        for control in ('zoom','level','year','search','results','map','detail'):
            self.assertIn('id="'+control+'"', html)
        self.assertEqual(html.count(MARQUEUR), 1)
        self.assertIn('value="arrondissement"', html)
        self.assertIn('value="territoire"', html)
        self.assertIn('value="2026"', html)
        self.assertIn('code_region_parent', html)
        self.assertIn('Le Fresne-sur-Loire', html)
        self.assertNotIn('<script src=', html)
        self.assertNotIn('geometries_2026_utilisees": true', html)

    def test_reproduction_octet_et_pas_de_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            d = fixture()
            with self.assertRaisesRegex(ValueError, 'docs'):
                construire(TEMPLATE, base/'docs'/'index.html', d)
            a = construire(TEMPLATE, base/'a'/'carte.html', d)
            b = construire(TEMPLATE, base/'b'/'carte.html', d)
            self.assertEqual(a['sha256'], b['sha256'])
            self.assertEqual((base/'a'/'carte.html').read_bytes(),
                             (base/'b'/'carte.html').read_bytes())
            self.assertEqual(a['departements_2016'], 96)
            self.assertEqual(a['regions_2015'], 22)
            self.assertFalse(a['publication_docs'])

    def test_controles_de_non_inference_et_cardinalite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'carte.html'
            data = fixture()
            data['layers']['2015']['region'].pop()
            with self.assertRaisesRegex(ValueError, 'contours'):
                construire(TEMPLATE,out,data)
            data=fixture();data['alignements_Pactols_generes']=1
            with self.assertRaisesRegex(ValueError,'Pactols'):
                construire(TEMPLATE,out,data)
            data=fixture();data['aucune_geometrie_2026_retroprojetee']=False
            with self.assertRaisesRegex(ValueError,'rétroprojection'):
                construire(TEMPLATE,out,data)

    def test_donnees_embarquees_ne_sortent_pas_du_script_json(self):
        data=fixture()
        data['texte_injecte'] = '</script><script>alert("x")</script>'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'carte.html'
            construire(TEMPLATE,out,data)
            html=out.read_text(encoding='utf8')
            self.assertNotIn('</script><script>alert',html)
            marker='type="application/json">'
            payload=html.split(marker,1)[1].split('</script>',1)[0]
            self.assertEqual(json.loads(payload)['texte_injecte'],data['texte_injecte'])


@unittest.skipUnless(SHAPELY, 'Shapely requis uniquement en CI géographique')
class QualificationGeomTests(unittest.TestCase):
    def test_valider_annee_source_et_non_alignement(self):
        from shapely.geometry import mapping, box
        codes=[f'{i:02}' for i in range(22)]
        geo={'type':'FeatureCollection',
             'provenance':{'edition':'GEOFLA_2015','producteur':'IGN',
                           'geometries_2026_utilisees':False},
             'features':[{'type':'Feature',
                          'properties':{'code_region':code,'nom_COG':'R'+code,
                                        'millesime_COG':2015,'date_edition_IGN':'2015-03-04',
                                        'contour_regional_natif':False,'alignement_Pactols_valide':False,
                                        'code_departement_sources':[code]},
                          'geometry':mapping(box(1+i,43,1.5+i,44))}
                         for i,code in enumerate(codes)]}
        names={code:'R'+code for code in codes}
        results=verifier_regions(geo,2015,names)
        self.assertEqual(len(results),22)
        self.assertTrue(all(not r['properties']['pactols_valide'] for r in results))
        geo['provenance']['geometries_2026_utilisees']=True
        with self.assertRaisesRegex(ValueError,'Provenance'):
            verifier_regions(geo,2015,names)


if __name__=='__main__':unittest.main()