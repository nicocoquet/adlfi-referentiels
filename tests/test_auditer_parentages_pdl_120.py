"""Tests de sécurité : les codes COG ne créent pas de validation Pactols."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from auditer_parentages_pdl_120 import extraire_codes_parent,qualifier,MODALITES

class ParentagesPdlTests(unittest.TestCase):
    def test_ne_pas_assimiler_uri_deleguee_et_commune(self):
        links={'liens_exact_match_pactols':'["http://id.insee.fr/geo/commune/49065","http://id.insee.fr/geo/communeDeleguee/49065","http://id.insee.fr/geo/commune/uuid"]'}
        self.assertEqual(extraire_codes_parent(links),['49065'])
    def test_classes_non_validantes(self):
        self.assertEqual(qualifier({},['49069'],{'parents_2026':'49126'},['49126']),'ecart_code_parent_historique')
        self.assertEqual(qualifier({},[],{'parents_2026':'49080'},['49080']),'parent_hors_corpus_terminal')
        self.assertEqual(qualifier({},['49080'],{'parents_2026':'49080'},['49080']),'accord_code_parent_2026')
        self.assertEqual(qualifier({},['49080'],{'parents_2026':''},[]),'sans_compa_2026')
        self.assertEqual(qualifier({},['49080'],None,[]),'code_partage_ark_22')
    def test_modalites_insee_distinctes(self):
        self.assertEqual(MODALITES['34'],'transformation_fusion_association_en_fusion_simple')
        self.assertEqual(MODALITES['35'],'suppression_commune_deleguee')
        self.assertNotEqual(MODALITES['35'],MODALITES['21'])

if __name__=='__main__':unittest.main()
