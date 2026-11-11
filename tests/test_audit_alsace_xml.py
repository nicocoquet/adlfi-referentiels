"""Contrôle TEI reproductible de la réconciliation Pair / Archéologie Alsace."""
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.audit_alsace_xml import audit_xml_documents


def xml(labels, year='2016'):
    notices = ''.join(
        f'<div subtype="notice"><head style="T_2"><index><term type="orig">Altorf</term></index> – Place</head>'
        f'<p style="txt_archeo_autorites"><name role="aut fld">Auteur</name>'
        f'<affiliation xml:id="aff{i}">{label}</affiliation></p>'
        f'<ab type="meta-archeo">Année de l’opération : <date>{year}</date></ab></div>'
        for i,label in enumerate(labels,1)
    )
    return ('<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>'
            + notices + '</body></text></TEI>').encode()


class AuditAlsaceXMLTests(unittest.TestCase):
    def test_complete_matching_with_zip_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            a = d/'2015.xml'; b = d/'2016.xml'; archive = d/'2016.zip'
            a.write_bytes(xml(['Pair'], '2015'))
            b.write_bytes(xml(['Archéologie Alsace','Archéologie Alsace']))
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('2016.xml',b.read_bytes())
                z.writestr('__MACOSX/._2016.xml',b'duplicate')
            report = audit_xml_documents(
                [a,b,archive], expected={'Pair':1,'Archéologie Alsace':2})
            self.assertEqual(report['status'],'reconciliation_complete')
            self.assertEqual(report['total'],3)
            self.assertEqual(len(report['sources']),2)
            self.assertEqual(report['occurrences'][1]['titre_notice'], '– Place')
            self.assertEqual(report['occurrences'][1]['annees_operation'], '2016')
            self.assertEqual(report['occurrences'][1]['org_historique'], 'ORG-0093')

    def test_count_discrepancy_refuses_resolution(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'2016.xml'
            p.write_bytes(xml(['Archéologie Alsace']))
            with self.assertRaisesRegex(ValueError, 'Écart au maître'):
                audit_xml_documents([p], expected={'Pair':1,'Archéologie Alsace':1})

    def test_post_2020_operation_refuses_historical_assignment(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'2021.xml'
            p.write_bytes(xml(['Archéologie Alsace'], '2021'))
            with self.assertRaisesRegex(ValueError, 'année incompatible'):
                audit_xml_documents([p], expected={'Archéologie Alsace':1})

    def test_missing_operation_year_refuses_assignment(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'sans-date.xml'
            p.write_bytes(xml(['Pair']).replace(b'<date>2016</date>',b''))
            with self.assertRaisesRegex(ValueError, 'année incompatible'):
                audit_xml_documents([p], expected={'Pair':1})


if __name__ == '__main__':
    unittest.main()
