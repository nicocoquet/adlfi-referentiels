"""Contrat et tests des invariants de la scission Archéologie Alsace."""
import copy
import unittest

from scripts.controle_maitre_1_41 import check


def fixture():
    return {
        'Organismes':[
            {'organisme_id':'ORG-0093','nom_normalise':'Archéologie Alsace',
             'type_organisme':'etablissement_public','secteur_institutionnel':'public',
             'date_debut':'2006-09-01','date_fin':'2020-12-11','actif':'non',
             'affichage_catalogue':'oui'},
            {'organisme_id':'ORG-0675','nom_normalise':'Archéologie Alsace',
             'type_organisme':'syndicat_mixte','secteur_institutionnel':'public',
             'date_debut':'2020-12-11','actif':'oui','affichage_catalogue':'oui',
             'url_site_officiel':'https://www.archeologie.alsace/'},
            {'organisme_id':'ORG-0249','type_organisme':'epci',
             'echelon_territorial':'intercommunal'},
            {'organisme_id':'ORG-0429','echelon_territorial':'communal'},
            {'organisme_id':'ORG-0650','type_organisme':'collectivite_territoriale',
             'echelon_territorial':'metropolitain'},
        ],
        'Services':[],
        'Affiliations_sources':[
            {'affiliation_source_id':'AFF-0047','organisme_id':'ORG-0093',
             'libelle_source':'Pair','occurrences':'57'},
            {'affiliation_source_id':'AFF-0048','organisme_id':'ORG-0093',
             'libelle_source':'Archéologie Alsace','occurrences':'124'},
        ],
        'Correspondances_affiliations':[
            {'correspondance_id':'COR-0054','organisme_id':'ORG-0093',
             'affiliation_source_id':'AFF-0047','statut_validation':'validee'},
            {'correspondance_id':'COR-0055','organisme_id':'ORG-0093',
             'affiliation_source_id':'AFF-0048','statut_validation':'validee'},
        ],
        'Relations':[
            {'relation_id':'REL-0054','organisme_source_id':'ORG-0093',
             'organisme_cible_id':'ORG-0249','statut_validation':'a_verifier'},
            {'relation_id':'REL-0305','organisme_source_id':'ORG-0093',
             'organisme_cible_id':'ORG-0675','type_relation':'succession_institutionnelle',
             'date_debut':'2020-12-11','statut_validation':'valide'},
        ],
        'Historique':[
            {'historique_id':'HIS-0003','organisme_id':'ORG-0093',
             'date_debut':'2006-09-01','date_fin':'2016-10-14'}
        ],
        'Statuts_historiques':[
            {'statut_historique_id':ident,'organisme_id':org,'forme_juridique':form,
             'statut_validation':'valide','source_url':'https://source.example/reference'}
            for ident,org,form in [
                ('STH-0003','ORG-0093','institution_interdepartementale'),
                ('STH-0004','ORG-0675','syndicat_mixte_ouvert'),
                ('STH-0005','ORG-0249','communaute_agglomeration'),
                ('STH-0006','ORG-0650','collectivite_statut_particulier')]]
    }


class ControleMaitre141Tests(unittest.TestCase):
    def test_migration_consistent_and_traced(self):
        s=fixture()
        before=copy.deepcopy(s)
        report=check(s,check_totals=False)
        self.assertEqual(s,before)
        self.assertEqual(report['status'],'ok')
        self.assertEqual(report['historical']['total_occurrences'],181)
        self.assertEqual(report['successor']['affiliations_linked'],0)

    def test_no_affiliation_transfer_to_successor(self):
        s=fixture()
        s['Correspondances_affiliations'][1]['organisme_id']='ORG-0675'
        with self.assertRaisesRegex(ValueError, 'transfert vers successeur'):
            check(s,check_totals=False)

    def test_no_retroprojection_of_anachronistic_relation(self):
        s=fixture()
        s['Relations'][0]['statut_validation']='valide'
        with self.assertRaisesRegex(ValueError,'promue sans vérification'):
            check(s,check_totals=False)

    def test_status_must_match_legal_identity(self):
        s=fixture()
        s['Statuts_historiques'][1]['forme_juridique']='etablissement_public'
        with self.assertRaisesRegex(ValueError,'statut historique'):
            check(s,check_totals=False)

    def test_wrong_succession_date_blocks(self):
        s=fixture()
        s['Relations'][1]['date_debut']='2021-01-01'
        with self.assertRaisesRegex(ValueError,'REL-0305.date_debut'):
            check(s,check_totals=False)

    def test_unchanged_affiliation_counts_required(self):
        s=fixture()
        s['Affiliations_sources'][1]['occurrences']='123'
        with self.assertRaisesRegex(ValueError,'occurrences modifiées'):
            check(s,check_totals=False)


if __name__=='__main__':
    unittest.main()
