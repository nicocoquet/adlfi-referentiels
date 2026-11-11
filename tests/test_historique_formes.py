"""Contrat des formes historiques : conserver la source et distinguer les organes."""
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import export_organismes

ROOT=Path(__file__).resolve().parents[1]

class HistoriqueFormesTests(unittest.TestCase):
    def test_types_and_provenance_are_preserved_by_exporter(self):
        sh={k:[] for k in export_organismes.CORE}
        sh['Organismes']=[{
            'organisme_id':'ORG-0001','nom_normalise':'Département témoin',
            'type_organisme':'collectivite_territoriale',
            'secteur_institutionnel':'public','affichage_catalogue':'oui'}]
        sh['Historique']=[
            {'historique_id':'HIS-0114','organisme_id':'ORG-0001',
             'denomination':'Conseil général témoin',
             'type_denomination':'designation_historique_organe',
             'date_fin':'2015-03-21','statut_validation':'valide',
             'source_documentaire':'https://www.legifrance.gouv.fr/'},
            {'historique_id':'HIS-0115','organisme_id':'ORG-0001',
             'denomination':'Nom encore utilisé',
             'type_denomination':'variante_denomination',
             'statut_validation':'valide'}]
        with patch.object(export_organismes,'parse_workbook',return_value=sh), \\
             patch.object(export_organismes,'media_for',
                          return_value={'image':None,'logo':None}):
            d=export_organismes.build(Path(__file__))
        hist=d['authorities'][0]['names']['history']
        self.assertEqual([x['id'] for x in hist],['HIS-0114','HIS-0115'])
        self.assertEqual([x['type'] for x in hist],
                         ['designation_historique_organe','variante_denomination'])
        self.assertEqual(hist[0]['source'],'https://www.legifrance.gouv.fr/')
        self.assertEqual(hist[0]['end'],'2015-03-21')
        self.assertIsNone(hist[0]['start'])

    def test_ui_has_distinct_sections_without_legal_identity_confusion(self):
        js=(ROOT/'docs/assets/organismes.js').read_text(encoding='utf-8')
        self.assertIn("item.type==='designation_historique_organe'",js)
        self.assertIn("item.type==='variante_denomination'",js)
        self.assertIn('Désignations historiques d’organes',js)
        self.assertIn('Variantes de dénomination en usage',js)
        self.assertIn('et non un changement d’identité juridique',js)
        self.assertIn("VALID_STATES.has(item.validation||'')",js)

if __name__=='__main__':
    unittest.main()
