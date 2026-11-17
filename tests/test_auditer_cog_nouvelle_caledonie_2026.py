"""Nouvelle-Calédonie : 33 communes COMER, Poya non mono-provinciale."""
from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_cog_nouvelle_caledonie_2026 as a
class TestNouvelleCaledonie(unittest.TestCase):
 def fixture(self):
  # Codes fictifs, uniquement pour les garde-fous ; le COG officiel est
  # testé en CI séparément, sans invention de rattachement réel.
  c={f'988{i:02d}':f'Commune-{i}' for i in range(1,34)}
  c['98827']='Poya'
  sources={
    'v_comer_2026.csv':[{'COMER':'988','LIBELLE':'Nouvelle-Calédonie'}],
    'v_commune_comer_2026.csv':[
        {'COMER':'988','COM_COMER':code,'LIBELLE':label,'NATURE_ZONAGE':'COM'}
        for code,label in c.items()],
    'v_tom_depuis_1943.csv':[
        {'COMER':'988','LIBELLE':'Nouvelle-Calédonie','DATE_DEBUT':'1943-01-01','DATE_FIN':'','NATURE_ZONAGE':''}],
    'v_commune_outremer_depuis_1943.csv':[
        {'COM_COMER':code,'LIBELLE':label,'DATE_DEBUT':'1985-01-01',
         'DATE_FIN':'','NATURE_ZONAGE':'COM'} for code,label in c.items()],
    'v_commune_2026.csv':[{'COM':'97101'}],
    'v_commune_depuis_1943.csv':[{'COM':'97101'}]
  }
  base={'schema':'adlfi.lieux.recherche.outremer.public.v1',
        'communes':{'988':'\n'.join(f'{code}|{label}' for code,label in c.items())},
        'pactols_valides':{f'987{i}':f'26678/pcrtx{i}' for i in range(11,187)},
        'pactols_collectivites_valides':{str(i):f'26678/pcrt{i}' for i in range(4)}}
  return sources,base
 def audit(self,sources,base):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'index.json').write_text(json.dumps(base),encoding='utf-8')
   with (patch.object(a,'sha',side_effect=lambda path:a.SHAS[path.name]),
         patch.object(a,'read',side_effect=lambda path:sources[path.name])):
    return a.analyser(p,p/'index.json')
 def test_separation_provinces_coutume(self):
  d=self.audit(*self.fixture())
  self.assertEqual(d['bilan']['communes_2026'],33)
  self.assertEqual(d['bilan']['communes_Poya_a_double_province'],1)
  self.assertEqual(d['Poya']['provinces_juridiques'],['Nord','Sud'])
  self.assertIsNone(d['Poya']['code_COG_province_unique'])
  self.assertEqual(d['aires_coutumieres']['nombre'],8)
  self.assertEqual(d['provinces']['nombre'],3)
  self.assertEqual(d['bilan']['nouveaux_ARK'],0)
  self.assertEqual(d['bilan']['nouveaux_contours'],0)
 def test_refuser_poya_absente(self):
  t,b=self.fixture()
  t['v_commune_comer_2026.csv'][26]['LIBELLE']='Inconnue'
  with self.assertRaisesRegex(ValueError,'divergent'):self.audit(t,b)
 def test_refuser_commune_drom_988(self):
  t,b=self.fixture();t['v_commune_2026.csv'].append({'COM':'98801'})
  with self.assertRaisesRegex(ValueError,'DROM'):self.audit(t,b)
 def test_refuser_fausse_commune_nc(self):
  t,b=self.fixture();t['v_commune_comer_2026.csv'][0]['NATURE_ZONAGE']='CIR'
  with self.assertRaisesRegex(ValueError,'Communes NC'):self.audit(t,b)
if __name__=="__main__":unittest.main()
