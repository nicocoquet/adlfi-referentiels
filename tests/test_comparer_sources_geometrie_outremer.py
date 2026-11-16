"""Contrôles de comparaison non validante de sources ultramarines."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from comparer_sources_geometrie_outremer import (GEOMETRIES_DISPONIBLES, comparer, normalized, stats_comparaison)

def polygon(x=0.0):
    return {"type":"Polygon","coordinates":[[
        [x,0],[x+1,0],[x+1,1],[x,1],[x,0]
    ]]}

def fixture():
    national={"type":"FeatureCollection","features":[]}
    sources={"schema":"adlfi.lieux.sources.territoriales.v1","sources":{}}
    for code,name in (("98745","Tahaa"),("98805","Dumbéa")):
        national["features"].append({"type":"Feature","properties":{"code":code},
                                     "geometry":polygon(1)})
        sources["sources"][code]={
            "proprietes":{"nom":name}, "code_source":code,
            "endpoint":"https://example.org/FeatureServer/0",
            "geometrie_sha256":"d"*64,
            "geojson":{"type":"Feature","geometry":polygon(1)},
        }
    return national,sources

class Normalisations(unittest.TestCase):
    def test_identites_toponymiques(self):
        self.assertEqual(normalized("Taha'a"), normalized("TAHAA"))
        self.assertEqual(normalized("Dumbéa"), normalized("DUMBEA"))


@unittest.skipUnless(GEOMETRIES_DISPONIBLES, "Shapely et pyproj requis pour l'audit géométrique")
class Comparaisons(unittest.TestCase):
    def test_normalisation_ne_cree_pas_de_faux_code(self):
        self.assertEqual(normalized("Taha'a"),normalized("Tahaa"))
        self.assertEqual(normalized("Dumbéa"),normalized("DUMBEA"))
        self.assertNotEqual(normalized("Dumbéa"),normalized("Dumbarton"))

    def test_comparaison_identite_sans_equivalence_pactols(self):
        national,src=fixture()
        audit=comparer(national,src)
        self.assertEqual(set(audit["comparaisons"]),{"98745","98805"})
        self.assertEqual(audit["statut"],"RECETTE_NON_VALIDANTE_NON_PUBLIEE")
        self.assertEqual(audit["alignements_pactols_crees"],0)
        self.assertEqual(audit["geometries_publiees"],0)
        for row in audit["comparaisons"].values():
            self.assertEqual(row["verification_identite_source"],"A_INSTRUIRE")
            self.assertTrue(row["donnees_geometriques"]["validite_source"])
            self.assertAlmostEqual(
                row["donnees_geometriques"]["difference_symetrique_km2"],0)

    def test_rejet_couche_nationale_absente(self):
        national,src=fixture()
        national["features"].pop()
        with self.assertRaisesRegex(ValueError,"manquante"):
            comparer(national,src)

    def test_rejet_code_national_duplique(self):
        national,src=fixture()
        national["features"].append(national["features"][0])
        with self.assertRaisesRegex(ValueError,"manquante"):
            comparer(national,src)

    def test_comparer_geometry_deplacee(self):
        r=stats_comparaison(polygon(1),polygon(3))
        self.assertTrue(r["validite_source"])
        self.assertTrue(r["validite_nationale"])
        self.assertGreater(r["difference_symetrique_km2"],0)
        self.assertEqual(r["recouvrement_pct_surface_source"],0)

    def test_autointersection_diagnostique_sur_copie(self):
        poly={"type":"Polygon","coordinates":[[
            [1,0],[2,1],[1,1],[2,0],[1,0]
        ]]}
        r=stats_comparaison(poly,polygon(1))
        self.assertFalse(r["validite_source"])
        self.assertIn("Self-intersection", r["motif_source"])
        self.assertTrue(r["reparation_diagnostic_source"])
        self.assertTrue(r["diagnostic_sur_copie_uniquement"])
        self.assertGreater(r["source_surface_km2"],0)

if __name__ == "__main__":
    unittest.main()
