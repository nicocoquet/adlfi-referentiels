"""Lot national des arrondissements municipaux, sans inférence d'ARK propres."""
import json
import unittest
from pathlib import Path
from scripts.valider_lieux_arrondissements import verifier, DATA, GEO

class ArrondissementsMunicipauxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(DATA.read_text(encoding='utf-8'))
        cls.geo=json.loads(GEO.read_text(encoding='utf-8'))

    def test_45_arm_et_geometries(self):
        self.assertEqual(verifier(self.data,self.geo),{
            'autorites':45,'geometries':45,'attestees_adlfi':32,'non_attestees':13,
        })

    def test_parent_pactols_sans_ark_arrondissement(self):
        for a in self.data['autorites']:
            self.assertNotIn('ark_pactols_arrondissement',a)
            self.assertTrue(a['commune_parente']['ark_pactols'].startswith('26678/'))
            self.assertEqual(a['typecom'],'ARM')

    def test_interdiction_doublon_code(self):
        clone=json.loads(json.dumps(self.data,ensure_ascii=False))
        clone['autorites'][0]['code_insee']=clone['autorites'][1]['code_insee']
        with self.assertRaises(ValueError):verifier(clone,self.geo)

    def test_interdiction_mauvaise_commune_parente(self):
        clone=json.loads(json.dumps(self.data,ensure_ascii=False))
        clone['autorites'][0]['commune_parente']['code_insee']='13055'
        with self.assertRaises(ValueError):verifier(clone,self.geo)

    def test_interdiction_geometrie_sans_provenance(self):
        clone=json.loads(json.dumps(self.geo,ensure_ascii=False))
        clone['metadata'].pop('sha256_source')
        with self.assertRaises(ValueError):verifier(self.data,clone)

    def test_interdiction_geojson_autre_zone(self):
        clone=json.loads(json.dumps(self.geo,ensure_ascii=False))
        clone['features'][0]['geometry']['coordinates'][0][0][0]=0
        with self.assertRaises(ValueError):verifier(self.data,clone)

if __name__=='__main__':unittest.main()
