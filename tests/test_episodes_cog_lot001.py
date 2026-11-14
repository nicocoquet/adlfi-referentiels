import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from construire_episodes_cog_lot001 import construire
DATA=ROOT/'docs/lieux/recette/lot-001-preuves-cog'

class EpisodesCOG(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.out=Path(self.tmp.name)
        self.a=DATA/'transitions_code_a_verifier.csv'
        self.b=DATA/'evenements_communaux_particuliers.csv'
    def tearDown(self):self.tmp.cleanup()
    def test_real_evidence(self):
        if not self.a.is_file() or not self.b.is_file():self.skipTest('preuves externes non disponibles sur ce runner')
        r=construire(self.a,self.b,self.out)
        self.assertEqual(r['nombre_lignes_mouvements'],23)
        self.assertEqual(r['operations_distinctes'],11)
        self.assertEqual(r['operations_mod'],{'32':3,'41':8})
        j=json.loads((self.out/'graphe-episodes-cog-lot001.json').read_text())
        mougon={x['libelle'] for x in j['etats_administratifs'] if x['code']=='79185' and x['typecom']=='COM'}
        self.assertEqual(mougon,{'Mougon','Mougon-Thorigné','Aigondigné'})
        self.assertEqual(len(j['arcs_evenements']),23)
        self.assertTrue(all(not x['periode_validite_officielle_complete'] for x in j['etats_administratifs']))
    def test_reject_duplicate_proof(self):
        if not self.a.is_file() or not self.b.is_file():self.skipTest('preuves non disponibles')
        s=self.b.read_text(encoding='utf-8-sig')
        bad=self.out/'bad.csv';bad.write_text(s+s.splitlines()[-1]+'\n')
        with self.assertRaises(ValueError):construire(self.a,bad,self.out)

if __name__=='__main__':unittest.main()

