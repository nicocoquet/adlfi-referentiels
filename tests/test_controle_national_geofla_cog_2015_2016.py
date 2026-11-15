"""Tests de la concordance nationale des rattachements IGN–COG sans réseau."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from controle_national_geofla_cog_2015_2016 import exporter,FUSIONS_2016

class RattachementsNationauxTests(unittest.TestCase):
    def test_sept_fusions_et_seize_predecesseurs(self):
        self.assertEqual(len(FUSIONS_2016),7)
        all_old=[r for values in FUSIONS_2016.values() for r in values]
        self.assertEqual(len(all_old),16)
        self.assertEqual(len(set(all_old)),16)
        self.assertEqual(FUSIONS_2016["27"],("26","43"))
    def test_veto_publication_prematuree(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"docs"):
                exporter([],{},Path(d)/"docs"/"lieux")
    def test_exports_96_lignes_sans_validation(self):
        with tempfile.TemporaryDirectory() as d:
            rows=[{
                "code_departement":f"{i:03d}",
                "code_region_COG2015":"26",
                "code_region_COG2016":"27",
                "nature_succession":"fusion_regionale_2016",
            } for i in range(96)]
            report={"nouvelles_geometries_historiques_generees":0,
                    "nouveaux_alignements_Pactols":0}
            exporter(rows,report,Path(d)/"recette")
            f=Path(d)/"recette"/"rattachements-IGN-COG-2015-2016.csv"
            self.assertEqual(len(f.read_text(encoding="utf-8-sig").splitlines()),97)
if __name__=="__main__":
    unittest.main()
