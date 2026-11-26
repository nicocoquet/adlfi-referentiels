"""Non-régression de la publication du lot 04, sans dépendances externes."""
import json,unittest,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'docs/data/personnes.json'
class TestPublicationPersonnesLot04(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=json.loads(P.read_text(encoding='utf-8'))
 def test_effectifs(self):
  d=self.data
  self.assertEqual(d['totals'],{'authorities':102,'contributions':1517,'notices':1432})
  self.assertEqual((len(d['authorities']),len(d['contributions'])),(102,1517))
 def test_identifiants(self):
  d=self.data
  self.assertEqual([a['id'] for a in d['authorities']],[f'PER-{i:06d}' for i in range(1,103)])
  self.assertEqual(len({a['identifiers']['idref'] for a in d['authorities']}),102)
 def test_contributions(self):
  d=self.data;cs=d['contributions']
  self.assertEqual(len({(x['person_id'],x['handle']) for x in cs}),1517)
  self.assertEqual(len({x['handle'] for x in cs}),1432)
  self.assertEqual(len(set(x['handle'] for x in cs[:1276])&set(x['handle'] for x in cs[1276:])),23)
  self.assertEqual(collections.Counter(' '.join(x['roles']) for x in cs),{'aut fld':1252,'aut':253,'fld':12})
  cnt=collections.Counter(x['person_id'] for x in cs)
  self.assertTrue(all(x['contributions_count']==cnt[x['id']] for x in d['authorities']))
 def test_variante(self):
  a=next(a for a in self.data['authorities'] if a['id']=='PER-000085')
  self.assertEqual(a['name_variants'][0]['value'],'Martine Corsi-Sciallano')
  self.assertEqual(a['name_variants'][0]['kind'],'autre_forme_attestee')
 def test_projection_public_only(self):
  s=json.dumps(self.data,ensure_ascii=False)
  self.assertNotIn('reference_visa',s)
  self.assertNotIn('sha256_xml_source',s)
  self.assertNotIn('source_xml',s)
if __name__=='__main__':unittest.main()
