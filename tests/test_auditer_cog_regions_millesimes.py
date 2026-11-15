"""Tests hors réseau de l'instruction des millésimes COG régionaux 2015–2026."""
import csv
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_cog_regions_millesimes import FUSIONS_2016,FILES,NOMS_DEFINITIFS_2016,NOM_CENTRE_2015,csv_lire,ecrire


class Reg2015Reg2016Tests(unittest.TestCase):
    def test_sept_fusions_2016_dont_bfc(self):
        self.assertEqual(len(FUSIONS_2016),7)
        self.assertEqual(FUSIONS_2016["27"],("26","43"))
        self.assertEqual(FUSIONS_2016["44"],("21","41","42"))
        self.assertEqual(FUSIONS_2016["28"],("23","25"))
        anciens=[r for rs in FUSIONS_2016.values() for r in rs]
        self.assertEqual(len(anciens),16)
        self.assertEqual(len(set(anciens)),16)

    def test_cinq_changements_de_noms_dates_par_les_textes(self):
        self.assertEqual(set(NOMS_DEFINITIFS_2016),{"32","44","75","76"})
        self.assertTrue(all(d=="2016-09-30" and ref.startswith("https://www.legifrance.gouv.fr/")
                            for d,ref in NOMS_DEFINITIFS_2016.values()))
        self.assertEqual(NOM_CENTRE_2015[:4],
                         ("24","2015-01-17","Centre","Centre-Val de Loire"))

    def test_anciens_exports_latin1_et_tabs_sans_perdre_codes(self):
        with tempfile.TemporaryDirectory() as d:
            for y in (2015,2016):
                path=Path(d)/f"reg{y}.zip"
                data="REGION\tCHEFLIEU\tTNCC\tNCC\tNCCENR\n01\t97105\t3\tGUADELOUPE\tGuadeloupe\n43\t25056\t0\tFRANCHE-COMTE\tFranche-Comté\n".encode("latin-1")
                with zipfile.ZipFile(path,"w") as z:
                    z.writestr(FILES[f"reg{y}"],data)
                rows=csv_lire(path,"reg",y)
                self.assertEqual(rows[0]["REGION"],"01")
                self.assertEqual(rows[1]["REGION"],"43")
                self.assertEqual(rows[1]["NCCENR"],"Franche-Comté")

    def test_export_2026_utf8_premier_zero_preserve(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"2026.csv"
            p.write_text("REG,CHEFLIEU,TNCC,NCC,NCCENR,LIBELLE\n"
                         "01,97105,3,GUADELOUPE,Guadeloupe,Guadeloupe\n"
                         "27,21231,0,BOURGOGNE FRANCHE COMTE,Bourgogne-Franche-Comté,Bourgogne-Franche-Comté\n",
                         encoding="utf-8-sig")
            rows=csv_lire(p,"reg",2026)
            self.assertEqual(rows[0]["REG"],"01")
            self.assertEqual(rows[1]["NCCENR"],"Bourgogne-Franche-Comté")

    def test_interdiction_ecriture_publique_docs(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"docs"/"region"
            with self.assertRaisesRegex(ValueError,"docs"):
                ecrire({},target)

if __name__=="__main__":
    unittest.main()
