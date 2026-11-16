"""Contrats de l'audit des contours intermédiaires, sans publication ni alignements."""
from __future__ import annotations

import gzip
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import auditer_contours_region_departement_2018_2025 as audit


def fc(elements):
    return {"type": "FeatureCollection", "features": elements}


def polygon(code, coords=None):
    if coords is None:
        coords = [[[2, 47], [3, 47], [3, 48], [2, 48], [2, 47]]]
    return {"type": "Feature",
            "properties": {"code": code},
            "geometry": {"type": "Polygon", "coordinates": coords}}


class Archives(unittest.TestCase):
    def test_annees_explicitement_millesimees(self):
        self.assertEqual(audit.ANNEES, (2018, 2019, 2021, 2022, 2023, 2024, 2025))
        self.assertEqual(audit.NIVEAUX, ("regions", "departements"))
        self.assertNotIn(2017, audit.ANNEES)
        self.assertNotIn(2020, audit.ANNEES)
        self.assertEqual(len(audit.METRO_REGIONS), 13)
        self.assertEqual(len(audit.DROM_REGIONS), 5)

    def test_controle_geojson_compresse_et_empreinte(self):
        with tempfile.TemporaryDirectory() as temp:
            chemin = Path(temp) / "regions-2018.geojson.gz"
            data = json.dumps(fc([polygon("11")])).encode()
            chemin.write_bytes(gzip.compress(data,mtime=0))
            doc, empreinte = audit.lire_geojson(chemin, originaire=True)
            self.assertEqual(len(doc["features"]), 1)
            self.assertEqual(empreinte, audit.sha256(chemin.read_bytes()))
            chemin.write_bytes(gzip.compress(json.dumps({"type": "Feature"}).encode(),mtime=0))
            with self.assertRaisesRegex(ValueError,"GeoJSON"):
                audit.lire_geojson(chemin, originaire=True)

    def test_codes_doublons_et_territoires_non_regionaux(self):
        d,ex = audit.indexer(fc([polygon("11"),polygon("975")]), "2018")
        self.assertEqual(sorted(d), ["11","975"])
        self.assertEqual(ex, ["975"])
        with self.assertRaisesRegex(ValueError, "dupliqués"):
            audit.indexer(fc([polygon("11"),polygon("11")]), "2018")

    @unittest.skipUnless(importlib.util.find_spec("shapely") and
                         importlib.util.find_spec("pyproj"), "Géométrie optionnelle en CI générale")
    def test_comparaison_geometries_distinctes(self):
        a, b = polygon("11"),polygon("11",[[[2.01,47],[3.01,47],[3.01,48],[2.01,48],[2.01,47]]])
        result = audit.mesurer(a,b)
        self.assertLess(result["intersection_union_pct"],100)
        self.assertGreater(result["intersection_union_pct"],90)
        self.assertGreater(result["difference_symetrique_km2"],0)


if __name__=="__main__":
    unittest.main()
