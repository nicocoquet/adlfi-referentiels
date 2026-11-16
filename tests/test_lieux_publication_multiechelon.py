"""Tests de publication du module Lieux unifié, sans géométrie anachronique."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data/lieux-historique"


class PublicationLieuxMultiechelon(unittest.TestCase):
    def test_couches_regionales_departementales_et_sources(self):
        attendu = {(2015, "regions"): 22, (2015, "departements"): 96,
                   (2016, "regions"): 13, (2016, "departements"): 96}
        parents = {}
        for (year, niveau), nombre in attendu.items():
            path = DATA / f"{niveau}-{year}.geojson"
            self.assertLess(path.stat().st_size, 1_050_000, path.name)
            geo = json.loads(path.read_text(encoding="utf8"))
            self.assertEqual(geo["type"], "FeatureCollection")
            source = geo["provenance"]
            self.assertEqual(source["schema"], "adlfi.lieux.contours.historiques.v1")
            self.assertEqual(source["cog_au_premier_janvier"], str(year))
            self.assertEqual(source["source_geometrie"], "IGN GEOFLA DEPARTEMENT")
            self.assertEqual(source["edition_IGN"], "2015-03-04" if year == 2015 else "2016-06-28")
            self.assertIs(source["pactols_valide"], False)
            self.assertEqual(len(geo["features"]), nombre)
            codes = []
            for feature in geo["features"]:
                props = feature["properties"]
                self.assertEqual(props["annee"], year)
                self.assertEqual(props["niveau"], "region" if niveau == "regions" else "departement")
                self.assertIs(props["pactols_valide"], False)
                self.assertNotIn("ark_pactols", props)
                self.assertIn(feature["geometry"]["type"], ("Polygon", "MultiPolygon"))
                self.assertTrue(feature["geometry"]["coordinates"])
                codes.append(props["code"])
                if niveau == "departements":
                    parents.setdefault(year, []).append(props["code_region_parent"])
            self.assertEqual(len(codes), len(set(codes)))
            if niveau == "regions":
                parents[(year, "regions")] = set(codes)
        for year in (2015, 2016):
            self.assertTrue(set(parents[year]).issubset(parents[(year, "regions")]))

    def test_couches_2026_regions_departements_drom_et_provenance(self):
        sources = {
            'regions': (18, '52ec7200994624753908c9cc1f7dd88d090abddb348c7e757d1eb60190f3bc74'),
            'departements': (101, 'c330276ba97a2c273c7b0508db9e47f3025d90b1734faf454fd089b87d9e96ea'),
        }
        for niveau,(nombre,sha) in sources.items():
            fc = json.loads((DATA / f'{niveau}-2026.geojson').read_text(encoding='utf8'))
            self.assertEqual(fc['type'],'FeatureCollection')
            self.assertEqual(len(fc['features']),nombre)
            meta = fc['provenance']
            self.assertEqual(meta['schema'],'adlfi.lieux.contours.administratifs_2026.v1')
            self.assertEqual(meta['cog_au_premier_janvier'],'2026')
            self.assertEqual(meta['edition_contours'],'2026-05-04')
            self.assertEqual(meta['source_archives_sha256'][f'{niveau}-100m.geojson.gz'],sha)
            self.assertFalse(meta['pactols_valide'])
            codes = {f['properties']['code'] for f in fc['features']}
            self.assertEqual(len(codes),nombre)
            for f in fc['features']:
                p = f['properties']
                self.assertEqual(p['annee'],2026)
                self.assertFalse(p['pactols_valide'])
                self.assertNotIn('ark_pactols',p)
                self.assertIn(f['geometry']['type'],('Polygon','MultiPolygon'))
            self.assertTrue(set(['971','972','973','974','976']).isdisjoint(codes) if niveau=='regions'
                            else set(['971','972','973','974','976']).issubset(codes))
            self.assertTrue(set(['975','977','978','984','986','987','988','989']).isdisjoint(codes))
        region = json.loads((DATA / 'regions-2026.geojson').read_text())
        dep = json.loads((DATA / 'departements-2026.geojson').read_text())
        reg06 = next(f for f in region['features'] if f['properties']['code']=='06')
        dep976 = next(f for f in dep['features'] if f['properties']['code']=='976')
        self.assertEqual(reg06['properties']['departements'],['976'])
        self.assertEqual(dep976['properties']['code_region_parent'],'06')
        report = json.loads((DATA / 'rapport-2026.json').read_text())
        self.assertEqual(report['nombre_reparations'],2)
        self.assertEqual({(e['niveau'],e['code']) for e in report['reparations_geometriques']},
                         {('region','53'),('departement','22')})
        for e in report['reparations_geometriques']:
            self.assertLess(e['difference_relative_aire_pct'],0.00001)
        self.assertEqual(report['alignements_Pactols_crees'],0)
        index = json.loads((DATA / 'index-2026.json').read_text())
        self.assertEqual(index['schema'],'adlfi.lieux.admin.index_2026.v1')
        self.assertEqual(len(index['entries']),119)
        self.assertEqual(len({(e['level'],e['code']) for e in index['entries']}),119)
        self.assertEqual(index['nouvelles_correspondances_pactols'],0)

    def test_index_distingue_les_dates_et_echelons(self):
        index = json.loads((DATA / "index.json").read_text(encoding="utf8"))
        self.assertEqual(index["schema"], "adlfi.lieux.admin.index.v1")
        self.assertEqual(index["nouvelles_correspondances_pactols"], 0)
        entries = index["entries"]
        self.assertEqual(len(entries), 227)
        keys = [(e["year"], e["level"], e["code"]) for e in entries]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(sum(e["year"] == 2015 and e["level"] == "region" for e in entries), 22)
        self.assertEqual(sum(e["year"] == 2016 and e["level"] == "region" for e in entries), 13)
        ancienne = [e for e in entries if e["year"] == 2015 and e["code"] == "26" and e["level"] == "region"]
        self.assertEqual(ancienne[0]["label"], "Bourgogne")

    def test_conservation_de_la_source_communale_et_de_pactols(self):
        pactols = json.loads((ROOT / "docs/data/lieux.json").read_text(encoding="utf8"))
        self.assertEqual(pactols["totaux"]["autorites_pactols"], 103)
        self.assertEqual(len(pactols["autorites"]), 103)
        for region in ("paca", "corse", "pdl", "bfc"):
            data = json.loads((ROOT / "docs/data/lieux-chronologie" /
                               f"cog-{region}.json").read_text(encoding="utf8"))
            self.assertEqual(data["region"], region)
            self.assertEqual(data["geometries_historiques"], [])
            if region != "paca":
                self.assertFalse(data["alignements_Pactols_COG_valides_2026"])
        self.assertEqual(
            len(json.loads((ROOT / "docs/data/lieux-chronologie/cog-paca.json").read_text())
                ["alignements_Pactols_COG_valides_2026"]), 103,
        )

    def test_moteur_leaflet_unique_et_fichiers_charges_a_la_demande(self):
        html = (ROOT / "docs/lieux/index.html").read_text(encoding="utf8")
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf8")
        for value in ('id="zoom"', 'id="level"', 'id="year"', 'id="search"',
                      'id="reference"', 'id="map"', 'id="detail"'):
            self.assertIn(value, html)
        self.assertIn("tile.openstreetmap.org/{z}/{x}/{y}.png", js)
        self.assertIn("©", js)
        self.assertIn("function layerFor(y,l)", js)
        self.assertIn("charg", js)
        self.assertIn("source_geometrie", js)
        self.assertNotIn("geographie-historique", html)
        self.assertNotIn("referentiel-communal", html)
        self.assertNotIn("NON PUBLIÉ", html)
        self.assertNotIn("Aucune géométrie historique n’est attribuée", html)

    def test_ancien_lien_chronologie_preserve_les_parametres(self):
        old = (ROOT / "docs/lieux/chronologie/index.html").read_text(encoding="utf8")
        self.assertIn("location.search", old)
        self.assertIn("location.hash", old)
        self.assertIn("location.replace", old)
        self.assertIn("new URL('../',location.href)", old)


if __name__ == "__main__":
    unittest.main()
