import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.auditer_lieux_pays_loire_cog import produire

class PaysLoire(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.d=Path(t.name)
    def csv(self,name,fields,items):
        p=self.d/name
        with p.open('w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,fieldnames=fields,delimiter=';');w.writeheader();w.writerows(items)
        return p
    def sources(self):
        inv=self.csv('in.csv',['region','ark_pactols','pref_fr_pactols','departement_hierarchie','codes_insee_skos','types_liens_insee_skos','autres_uris_insee'],[
          {'region':'Pays de la Loire','ark_pactols':'26678/test1','pref_fr_pactols':'Thouarsais-Bouildroux','departement_hierarchie':'85','codes_insee_skos':'["85292"]','types_liens_insee_skos':'["communeDeleguee"]','autres_uris_insee':'[]'},
          {'region':'Pays de la Loire','ark_pactols':'26678/test2','pref_fr_pactols':'Le Puy-Saint-Bonnet','departement_hierarchie':'49','codes_insee_skos':'["79224"]','types_liens_insee_skos':'["commune"]','autres_uris_insee':'[]'}])
        cur=self.csv('cur.csv',['COM','TYPECOM','REG','DEP','LIBELLE','COMPARENT'],[
          {'COM':'85292','TYPECOM':'COM','REG':'52','DEP':'85','LIBELLE':'Rives-du-Fougerais','COMPARENT':''},
          {'COM':'85292','TYPECOM':'COMD','REG':'52','DEP':'85','LIBELLE':'Thouarsais-Bouildroux','COMPARENT':'85292'},
          {'COM':'79224','TYPECOM':'COMA','REG':'52','DEP':'49','LIBELLE':'Le Puy-Saint-Bonnet','COMPARENT':'49099'}])
        hist=self.csv('hist.csv',['COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN'],[{'COM':'85292','TYPECOM':'COM','LIBELLE':'Thouarsais-Bouildroux','DATE_DEBUT':'1943-01-01','DATE_FIN':'2024-01-01'}])
        evt=self.csv('evt.csv',['MOD','DATE_EFF','COM_AV','TYPECOM_AV','COM_AP','TYPECOM_AP'],[{'MOD':'32','DATE_EFF':'2024-01-01','COM_AV':'85292','TYPECOM_AV':'COM','COM_AP':'85292','TYPECOM_AP':'COMD'}])
        return inv,cur,hist,evt
    def test_code_partage_et_ancien_departement(self):
        report=produire(*self.sources(),self.d/'out',2)
        self.assertEqual(report['validations_nouvelles'],0)
        self.assertEqual(report['repartition']['code_partage_types_a_instruire'],1)
        self.assertEqual(report['repartition']['commune_associee_deleguee_a_instruire'],1)
        with (self.d/'out/candidatures.csv').open(encoding='utf-8-sig') as f:
            rows=list(csv.DictReader(f,delimiter=';'))
        self.assertEqual(rows[1]['code_skos'],'79224')
        self.assertIn('COMD',rows[0]['candidats_cog_2026'])
    def test_cardinalite(self):
        with self.assertRaises(ValueError):produire(*self.sources(),self.d/'out',806)
    def test_protection_ecrasement(self):
        src=list(self.sources());src[0].rename(self.d/'candidatures.csv');src[0]=self.d/'candidatures.csv'
        with self.assertRaises(ValueError):produire(*src,self.d,2)

if __name__=='__main__':unittest.main()
