"""Contrat de migration 1.47 : champs optionnels et absence d'affiliation ajoutée."""
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import export_organismes


def org():
    return {'organisme_id': 'ORG-0008', 'nom_normalise': 'Inrap',
            'type_organisme': 'etablissement_public', 'echelon_institutionnel': 'national',
            'perimetre_competence': 'national', 'secteur_institutionnel': 'public',
            'affichage_catalogue': 'oui'}


def ser():
    return {'service_id': 'SER-0168', 'nom_normalise': 'Inrap Auvergne-Rhône-Alpes',
            'type_service': 'direction_regionale_inrap', 'perimetre_competence': 'regional',
            'affichage_catalogue': 'oui'}


def sheets(o=None, s=None):
    sh = {name: [] for name in export_organismes.CORE}
    sh['Organismes'] = [o or org()]
    sh['Services'] = [s or ser()]
    sh['Relations_services'] = [{'relation_service_id': 'RSE-0221',
                                'service_source_id': 'SER-0168',
                                'organisme_cible_id': 'ORG-0008',
                                'type_relation': 'rattachement_service',
                                'statut_validation': 'valide'}]
    return sh


class MigrationContractTests(unittest.TestCase):
    def build(self, sh):
        with patch.object(export_organismes, 'parse_workbook', return_value=sh), \
             patch.object(export_organismes, 'media_for',
                          return_value={'image': None, 'logo': None}):
            return export_organismes.build(Path(__file__))

    def test_explicit_national_org_and_inherited_ser(self):
        data = self.build(sheets())
        records = {a['id']: a for a in data['authorities']}
        self.assertEqual(records['ORG-0008']['classification']['level'], 'national')
        self.assertEqual(records['ORG-0008']['classification']['level_origin']['method'], 'explicit')
        self.assertEqual(records['SER-0168']['classification']['level'], 'national')
        self.assertEqual(records['SER-0168']['classification']['level_origin']['org_ids'],
                         ['ORG-0008'])
        self.assertEqual(records['SER-0168']['classification']['territorial_competence'],
                         'regional')
        self.assertEqual(records['SER-0168']['usage']['affiliations_linked'], 0)

    def test_legacy_org_level_remains_supported(self):
        old = org()
        del old['echelon_institutionnel']
        old['echelon_territorial'] = 'regional'
        data = self.build(sheets(o=old))
        self.assertEqual(data['authorities'][0]['classification']['level'], 'regional')
        self.assertEqual(data['authorities'][0]['classification']['level_origin']['field'],
                         'Organismes.echelon_territorial')

    def test_explicit_level_overrides_legacy(self):
        o = org()
        o['echelon_territorial'] = 'regional'
        data = self.build(sheets(o=o))
        self.assertEqual(data['authorities'][0]['classification']['level'], 'national')

    def test_unknown_competence_rejected(self):
        s = ser()
        s['perimetre_competence'] = 'pluriregional'
        with self.assertRaisesRegex(ValueError, 'Périmètre de compétence inconnu'):
            self.build(sheets(s=s))

    def test_missing_new_columns_is_backward_compatible(self):
        o, s = org(), ser()
        del o['echelon_institutionnel']
        del o['perimetre_competence']
        del s['perimetre_competence']
        data = self.build(sheets(o=o, s=s))
        records = {a['id']: a for a in data['authorities']}
        self.assertIsNone(records['SER-0168']['classification']['level'])
        self.assertIsNone(records['SER-0168']['classification']['territorial_competence'])
        self.assertEqual(data['totals']['service_level_unresolved_ids'], ['SER-0168'])


if __name__ == '__main__':
    unittest.main()
