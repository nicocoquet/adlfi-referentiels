import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from qualifier_exceptions_skos_lieux import traiter, construire


def rec(ark,label,pref,alt,status,deprecated='non'):
    return dict(ark_pactols='26678/'+ark,libelle_xml=label,
      pref_fr_pactols=json.dumps([pref]),alt_fr_pactols=json.dumps(alt),
      statut_comparaison=status,concept_deprecie_export=deprecated)

class Tests(unittest.TestCase):
    def test_categorisation_et_non_validation(self):
        rows=[rec('pcrt4WmiOPzg1T','Loire R','Loire (fleuve)',[],'libelle_xml_non_retrouve'),
              rec('pcrt4Y17GtzJWk','Exideuil','Exideuil-sur-Vienne',['Exideuil'],'libelle_alt_fr_concordant'),
              rec('pcrtlhwJPMkYwg','Bazeilles','Bazeilles (commune déléguée)',['08140'],'libelle_xml_non_retrouve'),
              rec('pcrtYl5BQ48ldd','Oisans Massif','Oisans Massif',[],'concept_deprecie_a_instruire','oui')]
        r=traiter(rows)
        self.assertEqual({x['categorie_revue'] for x in r},{'abreviation_documentaire_physique','variante_skos_attestee','distinction_historique_ou_typologique','concept_skos_deprecie'})
        self.assertEqual(next(x['alerte_altlabel_numerique'] for x in r if x['libelle_xml']=='Bazeilles'),'08140')
        self.assertTrue(all(x['alignement_pactols_cog']=='non_valide' for x in r))
        self.assertTrue(all(x['geometrie_historique_validee']=='non' for x in r))
    def test_pas_de_pref_concordant_parmi_exceptions(self):
        self.assertEqual(traiter([rec('pcrtTEST','Ambronay','Ambronay',[],'libelle_pref_fr_concordant')]),[])
    def test_imprevu_classe_a_examiner(self):
        x=traiter([rec('pcrtTEST','Objet inconnu','Objet sans nom',[],'libelle_xml_non_retrouve')])[0]
        self.assertEqual(x['categorie_revue'],'exception_non_classee')
    def test_source_absente(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):construire(Path(d)/'absent.csv',Path(d)/'out')

if __name__=='__main__':unittest.main()
