"""Non-régression : un contour IGN dérivé n'est pas un contour original régional."""
import tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from qualifier_source_geofla_originale_bfc import DEP,SHA_ARCHIVE,URL_IGN,exporter

class QualifierGeoFLA(unittest.TestCase):
    def test_huit_departements_et_deux_anciennes_regions(self):
        self.assertEqual(set(DEP),{"26","43"})
        all_deps=[x for _,codes in DEP.values() for x in codes]
        self.assertEqual(len(all_deps),8)
        self.assertEqual(len(set(all_deps)),8)
        self.assertEqual(set(all_deps),{"21","25","39","58","70","71","89","90"})
    def test_archive_edition_2015_03_pas_2026(self):
        self.assertIn("2015-03-04",URL_IGN)
        self.assertIn("DEPARTEMENT",URL_IGN)
        self.assertEqual(len(SHA_ARCHIVE),64)
    def test_interdiction_export_public_direct(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"docs"):
                exporter({}, {}, Path(d)/"docs"/"lieux")

if __name__=="__main__":unittest.main()
