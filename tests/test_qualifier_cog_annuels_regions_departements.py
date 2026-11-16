"""Tests des COG annuels et de leurs relations département–région."""
import csv
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import qualifier_cog_annuels_regions_departements as q


def archive(path, member, headers, rows, enc='utf-8', delimiter=','):
    s=io.StringIO()
    w=csv.DictWriter(s,fieldnames=headers,delimiter=delimiter)
    w.writeheader()
    w.writerows(rows)
    with zipfile.ZipFile(path,'w') as z:
        z.writestr(member,s.getvalue().encode(enc))


class CogAnnuel(unittest.TestCase):
    def test_normaliser_noms_et_cardinalites(self):
        self.assertEqual(q.normaliser("Centre-Val de Loire"),"centre val de loire")
        self.assertEqual(q.normaliser("Île-de-France"),"ile de france")
        self.assertEqual(len(q.SOURCE_PAGES),7)
        self.assertEqual(q.ANNEES,(2018,2019,2021,2022,2023,2024,2025))

    def test_detecter_zip_membres(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cog_ensemble_2025_csv.zip'
            archive(p,'dossier/v_region_2025.csv',['REG','NCCENR','LIBELLE'],
                    [{'REG':'11','NCCENR':'Île-de-France','LIBELLE':'Île-de-France'}])
            with zipfile.ZipFile(p) as z:
                self.assertEqual(q.membre_cog(z,2025,'regions'),'dossier/v_region_2025.csv')
                with self.assertRaisesRegex(ValueError,'ambigu/absent'):
                    q.membre_cog(z,2025,'departements')

    def test_rejeter_zip_doublon_ou_cardinalite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cog_ensemble_2024_csv.zip'
            archive(p,'v_region_2024.csv',['REG','NCCENR','LIBELLE'],
                    [{'REG':'11','NCCENR':'Île-de-France','LIBELLE':'Île-de-France'},
                     {'REG':'11','NCCENR':'Île-de-France','LIBELLE':'Île-de-France'}])
            with patch.dict(q.ARCHIVES_SHA256, {}, clear=True):
                with self.assertRaisesRegex(ValueError,'dupliqué'):
                    q.lire_cog(p,2024,'regions')
            archive(p,'v_region_2024.csv',['REG','NCCENR','LIBELLE'],
                    [{'REG':'11','NCCENR':'Île-de-France','LIBELLE':'Île-de-France'}])
            with patch.dict(q.ARCHIVES_SHA256, {}, clear=True):
                with self.assertRaisesRegex(ValueError,'Cardinalité'):
                    q.lire_cog(p,2024,'regions')
            with self.assertRaisesRegex(ValueError,'Empreinte'):
                q.lire_cog(p,2024,'regions')

    def test_parseur_2018_tabulation_latin1(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'regions-2018-txt.zip'
            archive(p,'reg2018.txt',['REGION','NCCENR'],
                    [{'REGION':'53','NCCENR':'Bretagne'}],
                    enc='latin-1',delimiter='\t')
            with patch.dict(q.ARCHIVES_SHA256, {}, clear=True):
                with self.assertRaisesRegex(ValueError,'Cardinalité'):
                    q.lire_cog(p,2018,'regions')

    def test_refus_ecriture_docs(self):
        with self.assertRaisesRegex(ValueError,'publique interdite'):
            q.qualifier(Path('/tmp/nonexistent'),Path('/tmp/nonexistent'),
                        ROOT/'docs/data/rapport-coordination.json')


if __name__=="__main__":
    unittest.main()
