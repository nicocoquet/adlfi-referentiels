"""Tester le comparateur sans nécessiter le XLSX privé."""
import unittest
from scripts.comparer_export_officiel_organismes_152 import differences


class ComparaisonJSONTests(unittest.TestCase):
    def test_identiques(self):
        self.assertEqual(differences({'a':[1,{'b':None}]}, {'a':[1,{'b':None}]}), [])
    def test_ordre_des_dictionnaires_non_significatif(self):
        self.assertEqual(differences({'b':2,'a':1}, {'a':1,'b':2}), [])
    def test_provenance_et_relations_differentes_relevees(self):
        errors=differences({'provenance': {'source_sha256':'abc'},'relations':[1,2]},
                           {'provenance': {'source_sha256':'def'},'relations':[1]})
        self.assertTrue(any('source_sha256' in e for e in errors))
        self.assertTrue(any('relations' in e for e in errors))
    def test_champ_manquant(self):
        self.assertTrue(any('absent' in e for e in differences({'a':1},{}) ))
    def test_difference_bool_et_int(self):
        self.assertTrue(differences({'a':True},{'a':1}))


if __name__ == '__main__':
    unittest.main()
