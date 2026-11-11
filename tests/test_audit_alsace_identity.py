"""Tests du dossier de scission (aucune migration automatique)."""
import copy
import unittest

from scripts.audit_alsace_identity import build_dossier


def sheets():
    return {
        'Organismes': [
            {'organisme_id': 'ORG-0093', 'nom_normalise': 'Archéologie Alsace',
             'date_debut': '2006', 'type_organisme': 'collectivite_territoriale'},
            {'organisme_id': 'ORG-0674', 'nom_normalise': 'Dernière autorité'},
        ],
        'Affiliations_sources': [
            {'affiliation_source_id': 'AFF-0047', 'libelle_source': 'Pair',
             'occurrences': '57', 'organisme_id': 'ORG-0093'},
            {'affiliation_source_id': 'AFF-0048', 'libelle_source': 'Archéologie Alsace',
             'occurrences': '124', 'organisme_id': 'ORG-0093'},
        ],
        'Correspondances_affiliations': [
            {'correspondance_id': 'COR-0054', 'affiliation_source_id': 'AFF-0047',
             'organisme_id': 'ORG-0093'},
            {'correspondance_id': 'COR-0055', 'affiliation_source_id': 'AFF-0048',
             'organisme_id': 'ORG-0093'},
        ],
        'Historique': [{'historique_id': 'HIS-0003', 'organisme_id': 'ORG-0093',
                        'date_debut': '2006', 'date_fin': '2015'}],
        'Relations': [
            {'relation_id': 'REL-0054', 'organisme_source_id': 'ORG-0093',
             'organisme_cible_id': 'ORG-0092', 'statut_validation': 'a_verifier'},
            {'relation_id': 'REL-0304', 'organisme_source_id': 'ORG-0001',
             'organisme_cible_id': 'ORG-0002'},
        ],
    }


class AlsaceIdentityAuditTests(unittest.TestCase):
    def test_candidate_and_ambiguity(self):
        input_sheets = sheets()
        before = copy.deepcopy(input_sheets)
        data = build_dossier(input_sheets)
        self.assertEqual(before, input_sheets)
        self.assertEqual(data['status'], 'proposition_non_appliquee')
        self.assertEqual(data['proposed_new_authority'], 'ORG-0675')
        self.assertEqual(data['proposed_succession_relation'], 'REL-0305')
        self.assertEqual(data['identity']['historical']['siren'], '200006336')
        self.assertEqual(data['identity']['successor']['siren'], '200094746')
        self.assertEqual(data['history_correction']['end_inclusive'], '2016-10-14')
        self.assertEqual(data['total_source_occurrences'], 181)
        self.assertEqual(
            [a['occurrences'] for a in data['affiliations'] if a['context_required']], [124])
        self.assertEqual(data['existing_relation_to_review']['status'], 'a_verifier')

    def test_fully_reconciled_xml_unlocks_affiliation_context(self):
        report = {
            'status':'reconciliation_complete',
            'total':181,
            'actual':{'Pair':57,'Archéologie Alsace':124},
            'sources':[{'sha256':'2015'},{'sha256':'2016'},{'sha256':'2017'}],
        }
        dossier = build_dossier(sheets(), corpus_report=report)
        self.assertTrue(dossier['xml_corpus_reconciled'])
        self.assertFalse(any(x['context_required'] for x in dossier['affiliations']))
        self.assertEqual(dossier['affiliations'][0]['current_authority'],'ORG-0093')
        self.assertIn('48 opérations 2016', dossier['affiliations'][1]['proposed_handling'])
        self.assertFalse(any('124 occurrences' in x for x in dossier['blocked']))
        self.assertEqual(dossier['xml_corpus_sha256'], ['2015','2016','2017'])

    def test_incomplete_xml_reconciliation_refuses_clearance(self):
        report = {'status':'reconciliation_complete', 'total':133,
                  'actual':{'Pair':57,'Archéologie Alsace':76},'sources':[]}
        with self.assertRaisesRegex(ValueError, 'Corpus XML non réconcilié'):
            build_dossier(sheets(), corpus_report=report)

    def test_counterpart_mismatch_is_error(self):
        data = sheets()
        data['Correspondances_affiliations'][0]['organisme_id'] = 'ORG-0042'
        with self.assertRaisesRegex(ValueError, 'correspondance source modifiée'):
            build_dossier(data)

    def test_source_count_mismatch_is_error(self):
        data = sheets()
        data['Affiliations_sources'][1]['occurrences'] = '123'
        with self.assertRaisesRegex(ValueError, 'décompte inattendu'):
            build_dossier(data)

    def test_multiple_canonical_identifiers_block(self):
        data = sheets()
        data['Organismes'].append(copy.deepcopy(data['Organismes'][0]))
        with self.assertRaisesRegex(ValueError, '2 lignes'):
            build_dossier(data)

    def test_existing_source_classification_changed_blocks(self):
        data = sheets()
        data['Organismes'][0]['type_organisme'] = 'etablissement_public'
        with self.assertRaisesRegex(ValueError, 'type déjà modifié'):
            build_dossier(data)


if __name__ == '__main__':
    unittest.main()
