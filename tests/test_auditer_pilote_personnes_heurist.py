"""Tests synthétiques du pilote Heurist, sans aucun fichier de source privée."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/auditer_pilote_personnes_heurist.py'
spec=importlib.util.spec_from_file_location('auditer_heurist', SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    source='a'*64
    authority={
      'heurist_person_id':'301', 'strate_technique':'mixte',
      'statut':'CANDIDAT_NON_VALIDE', 'per_propose':None,
      'autorite_candidat':{
        'name':'Prénom Exemple','family_name':'Exemple','name_idref':'',
        'identifiers':{'idref':'123456789','persee':'123456'},
        'contributions_count':0,
        'name_variants':[{'value':'Autre Prénom Exemple', 'kind':'autre_forme_attestee','source':'Heurist'}]
      },
      'relations_par_revue_role':{
        'gallia':{'auteur':1,'collaborateur':0},
        'gallia_prehistoire':{'auteur':0,'collaborateur':1}}
    }
    people={'status':'CANDIDAT_NON_VALIDE','source_sha256':source,'authority_count':1,'authorities':[authority]}
    new_article={'id':'heurist:1519:73:702', 'journal':'gallia','title':'Nouvel article',
          'year':2020,'volume':'Gallia, 77','first_page':'15','last_page':'21',
          'url':'https://journals.openedition.org/gallia/702', 'doi':'10.4000/gallia.702'}
    articles={'status':'CANDIDAT_NON_VALIDE','source_sha256':source,
              'new_articles':[new_article], 'existing_articles_reused':['heurist:1519:73:701']}
    relations={'status':'CANDIDAT_NON_VALIDE','source_sha256':source,
     'relations':[
       {'heurist_article_id':'702','heurist_person_id':'301','journal':'gallia','role':'auteur','position_in_role':2},
       {'heurist_article_id':'701','heurist_person_id':'301','journal':'gallia_prehistoire','role':'collaborateur','position_in_role':1},
     ]}
    base_people={'publication_status':'PUBLIC_PILOT','authorities':[
      {'id':'PER-000001','identifiers':{'idref':'028293290', 'wikidata':'Q9999999'}}]}
    base_articles={'publication_status':'PUBLIC_PILOT','source_sha256':source,'articles':[
       {'id':'heurist:1519:73:701','journal':'gallia_prehistoire','title':'Article existant',
        'year':2019,'volume':'Gallia Préhistoire, 60','first_page':'1','last_page':'7',
        'url':'https://www.persee.fr/doc/abc','doi':'10.3406/galliap.701'}]}
    return [people,articles,relations,base_people,base_articles]

class TestAuditPiloteHeurist(unittest.TestCase):
    def test_pilote_pre_visa_valide(self):
        result=module.validate(*fixture())
        self.assertEqual(result['personnes'],1)
        self.assertEqual(result['relations'],2)
        self.assertEqual((result['auteurs'],result['collaborateurs']), (1,1))
        self.assertEqual((result['nouveaux_articles'],result['articles_deja_publies_reutilises']),(1,1))
        self.assertEqual(result['per_attribues'],0)

    def test_rejette_une_relation_hors_roles_publics(self):
        case=fixture();case[2]['relations'][0]['role']='expert'
        with self.assertRaisesRegex(ValueError,'Rôle ou revue'):module.validate(*case)

    def test_rejette_un_champ_prive_article(self):
        case=fixture();case[1]['new_articles'][0]['private_metadata']='champ hors diffusion'
        with self.assertRaisesRegex(ValueError,'bibliographique hors'):module.validate(*case)

    def test_rejette_un_champ_prive_personne(self):
        case=fixture();case[0]['authorities'][0]['autorite_candidat']['email']='secret'
        with self.assertRaisesRegex(ValueError,'profil non public'):module.validate(*case)

    def test_refuse_allocation_per_sans_visa(self):
        case=fixture();case[0]['authorities'][0]['per_propose']='PER-000203'
        with self.assertRaisesRegex(ValueError,'PER alloué'):module.validate(*case)

    def test_compteur_adlfi_zero_obligatoire(self):
        case=fixture();case[0]['authorities'][0]['autorite_candidat']['contributions_count']=2
        with self.assertRaisesRegex(ValueError,'AdlFI fictive'):module.validate(*case)

    def test_refuse_collision_idref_avec_existant(self):
        case=fixture();case[0]['authorities'][0]['autorite_candidat']['identifiers']['idref']='028293290'
        with self.assertRaisesRegex(ValueError,'Collision'):module.validate(*case)

    def test_refuse_collision_secondaire_inter_candidats(self):
        case=fixture();row=copy.deepcopy(case[0]['authorities'][0]);row['heurist_person_id']='302'
        row['autorite_candidat']['identifiers']['idref']='12345678X'
        case[0]['authorities'].append(row);case[0]['authority_count']=2
        with self.assertRaisesRegex(ValueError,'Collision'):module.validate(*case)

    def test_refuse_duplication_doi(self):
        case=fixture();case[1]['new_articles'][0]['doi']='10.3406/galliap.701'
        with self.assertRaisesRegex(ValueError,'Doublon de doi'):module.validate(*case)

    def test_refuse_duplication_url(self):
        case=fixture();case[1]['new_articles'][0]['url']='https://www.persee.fr/doc/abc'
        with self.assertRaisesRegex(ValueError,'Doublon de url'):module.validate(*case)

    def test_refuse_article_sans_relation(self):
        case=fixture();case[2]['relations'].pop(1)
        case[0]['authorities'][0]['relations_par_revue_role']['gallia_prehistoire']['collaborateur']=0
        with self.assertRaisesRegex(ValueError,'Article non rattaché'):module.validate(*case)

    def test_refuse_bilan_par_role_inexact(self):
        case=fixture();case[0]['authorities'][0]['relations_par_revue_role']['gallia']['auteur']=2
        with self.assertRaisesRegex(ValueError,'Compteur de contribution'):module.validate(*case)

    def test_refuse_provenance_incoherente(self):
        case=fixture();case[1]['source_sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'Provenances Heurist'):module.validate(*case)

    def test_refuse_identifiant_fantaisiste(self):
        case=fixture();case[0]['authorities'][0]['autorite_candidat']['identifiers']['wikidata']='####'
        with self.assertRaisesRegex(ValueError,'Identifiant invalide'):module.validate(*case)

if __name__=='__main__':unittest.main()
