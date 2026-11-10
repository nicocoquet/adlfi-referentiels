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
