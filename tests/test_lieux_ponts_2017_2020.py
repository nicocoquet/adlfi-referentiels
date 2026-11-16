"""Recette publique des deux éditions historiques IGN ADMIN EXPRESS COG."""
from __future__ import annotations
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"docs/data/lieux-historique"
YEARS=(2017,2020)
SHA={
  2017:"222c420c4edbbf6fac76a7426ff74f075feed337103794b5048ede92abcb0133",
  2020:"ff7a732872a069cbc31f426b613a751cf990e80f4a98e984ecd81d9adbf0fd08",
}
EDITIONS={2017:"2017-06-19",2020:"2020-11-20"}

class PontsHistoriques(unittest.TestCase):
    def test_interface_sans_contours_inferes(self):
        js=(ROOT/"docs/assets/lieux-multiechelon.js").read_text(encoding="utf8")
        self.assertIn("ANNEES_PONTS=[2017,2020]",js)
        self.assertIn("validateAdminPonts",js)
        self.assertIn("index-ponts.json",js)
        self.assertIn("IGN ADMIN EXPRESS COG",js)

    @unittest.skipUnless((DATA/"index-ponts.json").exists(),
                         "Couches IGN qualifiées encore en recette")
    def test_millesimes_insee_et_sources_ign(self):
        index=json.loads((DATA/"index-ponts.json").read_text(encoding="utf8"))
        self.assertEqual(index["schema"],"adlfi.lieux.admin.index_ponts.v1")
        self.assertEqual(index["annees"],[2017,2020])
        self.assertEqual(index["nouvelles_correspondances_pactols"],0)
        self.assertEqual(len(index["entries"]),238)
        keys={(e["year"],e["level"],e["code"]) for e in index["entries"]}
        self.assertEqual(len(keys),238)
        for year in YEARS:
            for level,count in (("regions",18),("departements",101)):
                path=DATA/f"{level}-{year}.geojson"
                self.assertTrue(path.is_file(),path.name)
                fc=json.loads(path.read_text(encoding="utf8"))
                prov=fc["provenance"]
                self.assertEqual(fc["type"],"FeatureCollection")
                self.assertEqual(prov["schema"],"adlfi.lieux.contours.annuels.v1")
                self.assertEqual(prov["cog_au_premier_janvier"],str(year))
                self.assertEqual(prov["annee_geometrie"],year)
                self.assertEqual(prov["edition_IGN"],EDITIONS[year])
                self.assertEqual(prov["generalisation_m"],100)
                self.assertEqual(prov["source_geometrie"],"IGN ADMIN EXPRESS COG")
                self.assertFalse(prov["pactols_valide"])
                self.assertEqual(prov["source_archives_sha256"][
                    f"ADMIN-EXPRESS-COG_{'1-0' if year==2017 else '2-1'}__SHP__FRA_{EDITIONS[year]}.7z"], SHA[year])
                self.assertEqual(len(fc["features"]),count)
                codes=set()
                for f in fc["features"]:
                    p=f["properties"]
                    self.assertEqual(p["annee"],year)
                    self.assertEqual(p["date_reference_COG"],f"{year}-01-01")
                    self.assertEqual(p["annee_geometrie"],year)
                    self.assertEqual(p["niveau"],"region" if level=="regions" else "departement")
                    self.assertFalse(p["pactols_valide"])
                    self.assertNotIn("ark_pactols",p)
                    self.assertIn(f["geometry"]["type"],("Polygon","MultiPolygon"))
                    codes.add(p["code"])
                self.assertEqual(len(codes),count)
        reg17=json.loads((DATA/"regions-2017.geojson").read_text())
        dep17=json.loads((DATA/"departements-2017.geojson").read_text())
        self.assertIn("06",{f["properties"]["code"] for f in reg17["features"]})
        dep976=next(x for x in dep17["features"] if x["properties"]["code"]=="976")
        self.assertEqual(dep976["properties"]["code_region_parent"],"06")
        r17=json.loads((DATA/"rapport-2017.json").read_text())
        self.assertEqual({(x["niveau"],x["code"]) for x in r17["reparations"]},
                         {("region","06"),("departement","976")})
        self.assertEqual(r17["divergences_noms"],[])
        for year in YEARS:
            rep=json.loads((DATA/f"rapport-{year}.json").read_text())
            self.assertEqual(rep["source_IGN_SHA256"],SHA[year])
            self.assertEqual(rep["divergences_noms"],[])
            self.assertEqual(rep["nouvelles_autorites_Pactols"],0)
            self.assertTrue(all(x["difference_relative_aire_pct"]<=0.001
                for x in rep["reparations"]))

    @unittest.skipUnless(importlib.util.find_spec("shapely") and
                         (DATA/"index-ponts.json").exists(),
                         "Recette topologique complète en CI SIG")
    def test_geometries_ponts_valides(self):
        from shapely.geometry import shape
        for y in YEARS:
            for level in ("regions","departements"):
                fc=json.loads((DATA/f"{level}-{y}.geojson").read_text(encoding="utf8"))
                for f in fc["features"]:
                    geom=shape(f["geometry"])
                    self.assertTrue(geom.is_valid,(y,level,f["properties"]["code"]))
                    self.assertFalse(geom.is_empty)

if __name__=="__main__":
    unittest.main()
