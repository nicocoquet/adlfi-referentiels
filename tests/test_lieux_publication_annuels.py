"""Contrat de publication des couches annuelles, avec contrôle des six corrections."""
from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/"docs/data/lieux-historique"
ANNEES=(2018,2019,2021,2022,2023,2024,2025)
ANOMALIES={(2019,"region","53"),(2019,"departement","22"),
           (2019,"departement","39"),(2019,"departement","71"),
           (2025,"region","53"),(2025,"departement","22")}

class PublicationAnnuelle(unittest.TestCase):
    def test_implementation_des_millesimes_sans_interpolation(self):
        js=(ROOT/"docs/assets/lieux-multiechelon.js").read_text(encoding="utf8")
        self.assertIn("ANNEES_QUALIFIEES=[2018,2019,2021,2022,2023,2024,2025]",js)
        self.assertIn("validateAdminAnnuels",js)
        self.assertIn("index-annuels.json",js)
        self.assertIn("ANNEES_DISPONIBLES.has(y)",js)
        self.assertIn("geo.source_COG[String(y)]=fc.provenance.source_cog_url",js)
        self.assertIn("const refYear=y<2015?2015:",js)
        self.assertNotIn("2017,2020",js)

    @unittest.skipUnless((DOCS/"index-annuels.json").exists(),
                         "Couches de recette non encore publiées dans la branche")
    def test_couches_datation_codes_reparations_et_pactols(self):
        index=json.loads((DOCS/"index-annuels.json").read_text(encoding="utf8"))
        self.assertEqual(index["schema"],"adlfi.lieux.admin.index_annuels.v1")
        self.assertEqual(index["annees"],list(ANNEES))
        self.assertEqual(index["nouvelles_correspondances_pactols"],0)
        self.assertEqual(len(index["entries"]),833)
        clefs={(e["year"],e["level"],e["code"]) for e in index["entries"]}
        self.assertEqual(len(clefs),833)
        for year in ANNEES:
            for level,count in (("regions",18),("departements",101)):
                path=DOCS/f"{level}-{year}.geojson"
                self.assertTrue(path.is_file(),str(path))
                data=json.loads(path.read_text(encoding="utf8"))
                prov=data["provenance"]
                self.assertEqual(data["type"],"FeatureCollection")
                self.assertEqual(prov["schema"],"adlfi.lieux.contours.annuels.v1")
                self.assertEqual(prov["cog_au_premier_janvier"],str(year))
                self.assertEqual(prov["annee_geometrie"],year)
                self.assertEqual(prov["generalisation_m"],100)
                self.assertFalse(prov["pactols_valide"])
                self.assertEqual(len(data["features"]),count)
                codes=set()
                for f in data["features"]:
                    p=f["properties"]
                    self.assertEqual(p["annee"],year)
                    self.assertEqual(p["annee_geometrie"],year)
                    self.assertEqual(p["date_reference_COG"],f"{year}-01-01")
                    self.assertFalse(p["pactols_valide"])
                    self.assertNotIn("ark_pactols",p)
                    self.assertEqual(p["niveau"],"region" if level=="regions" else "departement")
                    self.assertIn(f["geometry"]["type"],("Polygon","MultiPolygon"))
                    codes.add(p["code"])
                self.assertEqual(len(codes),count)
        report=json.loads((DOCS/"rapport-annuels.json").read_text(encoding="utf8"))
        self.assertEqual(len(report["couches"]),14)
        self.assertEqual(report["nouvelles_correspondances_pactols"],0)
        self.assertFalse(report["restitution_historique_depuis_2026"])
        fixed={(r["annee"],r["niveau"],r["code"])
               for r in report["reparations_geometriques"]}
        self.assertEqual(fixed,ANOMALIES)
        self.assertTrue(all(r["difference_relative_aire_pct"]<0.00001
                            for r in report["reparations_geometriques"]))
        for year in (2017,2020):
            self.assertFalse((DOCS/f"regions-{year}.geojson").exists())
            self.assertFalse((DOCS/f"departements-{year}.geojson").exists())

    def test_generation_ne_peut_ecrire_dans_docs(self):
        try:
            from scripts.construire_couches_lieux_2018_2025 import verifier_dossier_sortie
        except ImportError:
            self.skipTest("Shapely absent des tests généraux, présent dans la CI SIG")
        with self.assertRaisesRegex(ValueError,"docs"):
            verifier_dossier_sortie(ROOT/"docs/test")

if __name__=="__main__":
    unittest.main()
