import csv
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from reconstituer_lieux_pays_loire_806 import comparer_pilote,verifier_sources,ID_FIELDS

class ReconstructionPaysLoire(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.d=Path(t.name)
    def csv(self,name,rows):
        p=self.d/name
        with p.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=ID_FIELDS,delimiter=';');w.writeheader();w.writerows(rows)
        return p
    def test_806_25_stables(self):
        rows=[dict.fromkeys(ID_FIELDS,'')|{'ark_pactols':f'26678/test{i}'} for i in range(806)]
        a=self.csv('complet.csv',rows);p=self.csv('pilote.csv',rows[:25])
        self.assertEqual(comparer_pilote(a,p),25)
        rows[0]['codes_insee_skos']='["49099"]'
        a=self.csv('complet.csv',rows)
        with self.assertRaisesRegex(ValueError,'Divergence pilote'):comparer_pilote(a,p)
    def test_sha_source_bloquant(self):
        p=self.d/'source.csv';p.write_text('test',encoding='utf8')
        with self.assertRaisesRegex(ValueError,'Empreinte non conforme'):
            verifier_sources({'source':p},{'source':'0'*64})
    def test_absence_source(self):
        with self.assertRaises(FileNotFoundError):
            verifier_sources({'source':self.d/'absent'},{'source':'0'*64})

if __name__=='__main__':unittest.main()
