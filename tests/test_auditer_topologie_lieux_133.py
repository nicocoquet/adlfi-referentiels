import copy
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from auditer_topologie_lieux_133 import mesurer, geometries


def polygon(x):
    return {'type':'Polygon','coordinates':[[[x,43],[x+.001,43],[x+.001,43.001],[x,43.001],[x,43]]]}

def feature(n):
    return {'type':'Feature','properties':{'code':f'{n:05d}','nom':f'Commune {n}',
             'statut_lien_pactols_cog':'valide_pilote_paca_2026' if n<=103 else 'candidat_non_valide'},
             'geometry':polygon(2+(n-1)*.001)}

class TestTopology(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
        self.features=[feature(n) for n in range(1,135)]
        self.full=self.d/'communes-100m.geojson.gz'
        self.sample=self.d/'carte.geojson'
        self.pilot=self.d/'pilot.geojson'
        self.old={'type':'FeatureCollection','features':self.features[:103]}
        self.current={'type':'FeatureCollection','metadata':{
            'etat':'recette_non_publiee','millesime':2026,'generalisation':'100m'},
            'features':copy.deepcopy(self.features[:133])}
        self.write()
    def tearDown(self):self.tmp.cleanup()
    def write(self):
        with gzip.open(self.full,'wt',encoding='utf8') as f:json.dump({'type':'FeatureCollection','features':self.features},f)
        self.current['metadata']['source_sha256']=__import__('hashlib').sha256(self.full.read_bytes()).hexdigest()
        self.sample.write_text(json.dumps(self.current));self.pilot.write_text(json.dumps(self.old))
    def test_133_against_full_and_pilot(self):
        r=mesurer(self.sample,self.full,self.pilot,self.d/'out',sha_attendu='')
        self.assertEqual(r['nombre_contours_2026'],133)
        self.assertEqual(r['nombre_contours_pilote_1000m'],103)
        self.assertEqual(r['nombre_contours_non_identiques_source'],0)
        self.assertEqual(r['nombre_geometries_invalides'],0)
        self.assertGreaterEqual(r['nombre_paires_contigues_dans_133'],100)
        self.assertEqual(r['nombre_contours_pilote_comparables'],103)
    def test_bad_metadata_fails(self):
        self.current['metadata']['generalisation']='1000m';self.write()
        with self.assertRaises(ValueError):mesurer(self.sample,self.full,self.pilot,self.d/'out',sha_attendu='')
    def test_missing_code_fails(self):
        self.current['features'][-1]['properties']['code']='99999';self.write()
        with self.assertRaises(ValueError):mesurer(self.sample,self.full,self.pilot,self.d/'out',sha_attendu='')
    def test_duplicate_code_fails(self):
        self.current['features'][-1]['properties']['code']='00001';self.write()
        with self.assertRaises(ValueError):mesurer(self.sample,self.full,self.pilot,self.d/'out',sha_attendu='')
    def test_reject_non_polygon(self):
        self.current['features'][4]['geometry']={'type':'Point','coordinates':[2,43]};self.write()
        with self.assertRaises(ValueError):mesurer(self.sample,self.full,self.pilot,self.d/'out',sha_attendu='')

if __name__=='__main__':unittest.main()

