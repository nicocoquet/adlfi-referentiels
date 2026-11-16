"""Tests sans réseau des écarts géométriques et du transfert Loire-Atlantique→Maine-et-Loire."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from shapely.geometry import box
except ImportError:
    box = None

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from auditer_ecarts_departementaux_geofla_2015_2016 import (
    calculer_transfert, comparer, exporter
)


def corpus():
    ancien = {}
    nouveau = {}
    for i in range(94):
        code = f"D{i:03d}"
        geometry = box(100 + i, 0, 101 + i, 1)
        ancien[code] = ("11", geometry)
        nouveau[code] = ("11", geometry)
    ancien["44"] = ("52", box(0, 0, 10, 1))
    nouveau["44"] = ("52", box(0, 0, 3.8, 1))
    ancien["49"] = ("52", box(10, 0, 20, 1))
    nouveau["49"] = ("52", box(3.8, 0, 20, 1))
    return ancien, nouveau


@unittest.skipUnless(box is not None, "Shapely disponible seulement dans les workflows SIG")
class DepartementsGeoFLATests(unittest.TestCase):
    def test_transfert_geometrique(self):
        a, b = corpus()
        area = calculer_transfert(a["44"][1], b["44"][1], a["49"][1], b["49"][1])
        self.assertAlmostEqual(area, 6.2)

    def test_96_departements_et_transfert_non_regional(self):
        ancien, nouveau = corpus()
        rows, rapport = comparer(ancien, nouveau)
        self.assertEqual(len(rows), 96)
        self.assertEqual(rapport["transfert_interdepartemental_documente"]["date_effet_juridique"], "2015-12-31")
        self.assertEqual(rapport["transfert_interdepartemental_documente"]["surface_geometrique_perdue_et_gagnee_km2"], 0.0)
        self.assertEqual(next(r for r in rows if r["code_departement"] == "44")["code_region_2016"], "52")
        self.assertEqual(rapport["nouveaux_alignements_Pactols"], 0)

    def test_veto_de_publication_et_reproductibilite(self):
        ancien, nouveau = corpus()
        rows, rapport = comparer(ancien, nouveau)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "docs"):
                exporter(rows, rapport, Path(d) / "docs")
            exporter(rows, rapport, Path(d) / "a")
            exporter(rows, rapport, Path(d) / "b")
            for f in (Path(d) / "a").iterdir():
                self.assertEqual(f.read_bytes(), (Path(d) / "b" / f.name).read_bytes())

    def test_blocage_si_transfert_absent(self):
        ancien, nouveau = corpus()
        nouveau["49"] = ancien["49"]
        with self.assertRaisesRegex(ValueError, "hors référence"):
            comparer(ancien, nouveau)


if __name__ == "__main__":
    unittest.main()
