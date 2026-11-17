"""Tests unitaires du générateur de contours SPM 2026."""
from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_contours_spm_2026 import construire, verifier_index


def carre(code, lon, lat):
    return {"type":"Feature","properties":{"code":code},"geometry":{
        "type":"Polygon","coordinates":[[
            [lon,lat],[lon+.01,lat],[lon+.01,lat+.01],[lon,lat+.01],[lon,lat]
        ]]}}


class TestIndexSPM(unittest.TestCase):
    def test_index_conserve_codes_et_ark(self):
        import json
        doc=json.loads((ROOT/"docs/data/lieux-outremer/recherche-2026.json").read_text())
        verifier_index(doc)
        bad={**doc,"communes":{**doc["communes"],"975":"97502|Saint-Pierre\n97501|Miquelon-Langlade"}}
        with self.assertRaisesRegex(ValueError,"COG/COMER"):
            verifier_index(bad)


@unittest.skipUnless(importlib.util.find_spec("shapely"),"Shapely réservé à la CI géospatiale")
class TestGeoSPM(unittest.TestCase):
    def test_deux_polygones_sans_publication_historique(self):
        a=construire({"type":"FeatureCollection","features":[
            carre("97501",-56.4,47.0),carre("97502",-56.1,46.8)
        ]})
        self.assertEqual([x["properties"]["code"] for x in a["features"]],["97501","97502"])
        self.assertEqual(a["provenance"]["restitutions_historiques"],0)
        self.assertFalse(a["provenance"]["limites_juridiques_homologuees"])
        self.assertTrue(all(x["properties"]["ark_pactols"] is None for x in a["features"]))
    def test_doublons_et_omissions_rejetes(self):
        with self.assertRaisesRegex(ValueError,"dupliquée"):
            construire({"type":"FeatureCollection","features":[carre("97501",-56.4,47.0)]*2})
        with self.assertRaisesRegex(ValueError,"incomplète"):
            construire({"type":"FeatureCollection","features":[carre("97501",-56.4,47.0)]})
    def test_chevauchement_rejete(self):
        with self.assertRaisesRegex(ValueError,"Chevauchement"):
            construire({"type":"FeatureCollection","features":[
                carre("97501",-56.4,47.0),carre("97502",-56.399,47.001)
            ]})


if __name__=="__main__":unittest.main()
