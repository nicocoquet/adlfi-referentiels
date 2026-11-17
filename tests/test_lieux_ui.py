"""Tests statiques du contrat d'interface Lieux et de son activation par le manifeste."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = {}
        self.tags = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError("ID HTML dupliqué : " + attrs["id"])
            self.ids[attrs["id"]] = (tag, attrs)


class LieuxUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "docs/lieux/index.html").read_text(encoding="utf-8")
        cls.home = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        cls.page = Elements()
        cls.page.feed(cls.html)
        cls.manifest = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))

    def test_controls_are_unique_and_accessible(self):
        for element_id in (
            "zoom", "level", "year", "search", "results",
            "reset", "map", "map-status", "detail", "reference",
        ):
            self.assertIn(element_id, self.page.ids)
        query = self.page.ids["search"][1]
        self.assertEqual(query["role"], "combobox")
        self.assertEqual(query["aria-controls"], "results")
        self.assertEqual(query["aria-autocomplete"], "list")
        self.assertEqual(self.page.ids["results"][1]["role"], "listbox")
        self.assertEqual(self.page.ids["map-status"][1]["role"], "status")
        self.assertEqual(self.page.ids["map"][1]["role"], "region")


    def test_trois_echelons_territoriaux_visibles(self):
        """Les arrondissements et collectivités atypiques restent hors sélecteur."""
        selecteur = self.html.split('<select id="level">', 1)[1].split('</select>', 1)[0]
        self.assertEqual(
            [fragment.split('"', 1)[0] for fragment in selecteur.split('<option value="')[1:]],
            ['region', 'departement', 'commune'],
        )
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf8")
        self.assertIn("const label={region:'Région',departement:'Département',commune:'Commune'};", js)

    def test_frise_historique_remplace_le_selecteur_annee(self):
        year_tag, year_attrs = self.page.ids["year"]
        self.assertEqual(year_tag, "input")
        self.assertEqual(year_attrs.get("type"), "range")
        self.assertEqual(year_attrs.get("min"), "1943")
        self.assertEqual(year_attrs.get("max"), "2026")
        self.assertEqual(year_attrs.get("step"), "1")
        self.assertEqual(year_attrs.get("value"), "2026")
        self.assertEqual(year_attrs.get("aria-describedby"), "year-description")
        self.assertEqual(self.page.ids["year-label"][0], "output")
        self.assertEqual(self.page.ids["year-label"][1].get("for"), "year")
        for removed in ("year-prev", "year-next", "year-now"):
            self.assertNotIn(removed, self.page.ids)
        self.assertIn("year-description", self.page.ids)
        self.assertEqual(self.page.ids["year-description"][1].get("class"),
                         "visually-hidden")
        self.assertIn('class="lieux-timeline"', self.html)
        self.assertNotIn('<select id="year"', self.html)
        self.assertIn("historique", self.html)
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf8")
        self.assertIn("function refreshTimeline()", js)
        self.assertIn("function commitTimeline()", js)
        self.assertIn("'year').addEventListener('input'", js)
        self.assertNotIn("'year-prev'", js)
        self.assertNotIn("'year-next'", js)
        self.assertNotIn("'year-now'", js)
        self.assertIn("state.selected?.kind==='admin'&&state.selected.year!==year()", js)

    def test_presentation_compacte_sans_aides_visibles(self):
        self.assertNotIn('class="notice-intro"', self.html)
        self.assertNotIn('class="hint"', self.html)
        self.assertNotIn('class="lieux-timeline-actions"', self.html)
        self.assertEqual(self.html.count('class="control"'), 3)
        self.assertIn('class="visually-hidden"', self.html)
        for expected in ("Zoom sur", "Échelon territorial",
                         "Rechercher un nom, un code INSEE ou un ARK Pactols"):
            self.assertIn(expected, self.html)

    def test_index_cog_outremer_complementaire_et_non_geometrique(self):
        dataset = json.loads(
            (ROOT / "docs/data/lieux-outremer/recherche-2026.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(dataset["schema"], "adlfi.lieux.recherche.outremer.public.v1")
        self.assertEqual(dataset["cog_ref"], "2026-01-01")
        self.assertEqual(set(dataset["communes"]), {
            "971", "972", "973", "974", "975", "976", "987", "988"
        })
        counts = {key: len(value.splitlines()) for key, value
                  in dataset["communes"].items()}
        self.assertEqual(counts, {"971": 32, "972": 34, "973": 22,
                                  "974": 24, "975": 2, "976": 17,
                                  "987": 48, "988": 33})
        self.assertEqual(sum(counts.values()), 212)
        self.assertEqual(len(dataset["autres"]), 21)
        self.assertEqual(len(dataset["pactols_valides"]), 128)
        self.assertEqual(len([k for k in dataset["pactols_valides"] if k.startswith("971")]), 32)
        self.assertNotIn("97123", dataset["pactols_valides"])
        self.assertNotIn("97127", dataset["pactols_valides"])
        self.assertEqual(len([k for k in dataset["pactols_valides"] if k.startswith("972")]), 34)
        self.assertEqual(len([k for k in dataset["pactols_valides"] if k.startswith("973")]), 22)
        self.assertEqual(dataset["ark_confirmes_non_valides"], {
            "97407": "26678/pcrtIKvRT9vwUl",
            "97607": "26678/crtZcuFSJVYZU",
        })
        self.assertEqual(dataset["contours_invalides"], ["98745", "98805"])
        self.assertNotIn("geometry", str(dataset))
        self.assertIn("ref_cog", (ROOT / "docs/assets/lieux-multiechelon.js")
                      .read_text(encoding="utf-8"))


    def test_guyane_historique_41_etats_sans_geometrie(self):
        p = ROOT / "docs/data/lieux-guyane/chronologie-cog-2026.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "adlfi.lieux.guyane.etats_cog_public.v1")
        self.assertEqual(data["start_year"], 1943)
        self.assertEqual(data["end_year"], 2026)
        self.assertEqual(len(data["episodes"].splitlines()), 41)
        self.assertEqual(len(data["anciennes"]), 4)
        self.assertEqual(data["contours_historiques_publies"], 0)
        self.assertEqual(data["nouvelles_relations_pactols_validees"], 0)
        self.assertEqual({a["code"] for a in data["anciennes"]},
                         {"97351", "97354", "97355", "97359"})
        self.assertFalse(any("geometry" in x.lower() for x in data))

    def test_martinique_historique_34_etats_sans_geometrie(self):
        p = ROOT / "docs/data/lieux-martinique/chronologie-cog-2026.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "adlfi.lieux.martinique.etats_cog_public.v1")
        self.assertEqual(data["start_year"], 1943)
        self.assertEqual(data["end_year"], 2026)
        self.assertEqual(len(data["episodes"].splitlines()), 34)
        self.assertEqual(data["codes_historiques_non_courants"], [])
        self.assertEqual(data["nouveaux_alignements_pactols"], 0)
        self.assertEqual(data["contours_historiques_publies"], 0)
        self.assertEqual(data["nouvelles_succession_inferrees"], 0)
        self.assertEqual(data["correspondances_pactols_validees_pour_2026"], 34)
        self.assertFalse(any("geometry" in x.lower() for x in data))

    def test_guadeloupe_historique_35_etats_sans_geometrie(self):
        p = ROOT / "docs/data/lieux-guadeloupe/chronologie-cog-2026.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "adlfi.lieux.guadeloupe.etats_cog_public.v1")
        self.assertEqual(data["start_year"], 1943)
        self.assertEqual(data["end_year"], 2026)
        self.assertEqual(len(data["episodes"].splitlines()), 35)
        self.assertEqual({x["code"] for x in data["anciens_codes"]},
                         {"97123", "97127"})
        self.assertEqual(data["correspondances_pactols_COG_2026_conservees"], 32)
        self.assertEqual(data["nouveaux_alignements_pactols"], 0)
        self.assertEqual(data["contours_historiques_publies"], 0)
        self.assertEqual(data["nouvelles_relations_successions_inferrees"], 0)
        self.assertTrue(all(x["destination_com_ap"] is None for x in data["anciens_codes"]))
        self.assertTrue(all(x["ark_pactols_uri_insee_atteste"] is None
                            for x in data["anciens_codes"]))
        self.assertFalse(any("geometry" in x.lower() for x in data))

    def test_external_leaflet_pinned_and_local_assets_ordered(self):
        scripts = [attrs["src"] for tag, attrs in self.page.tags
                   if tag == "script" and "src" in attrs]
        self.assertEqual(
            scripts,
            [
                "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js",
                "../assets/lieux-chronologie-core.js",
                "../assets/lieux-search.js",
                "../assets/lieux-outremer-search.js",
                "../assets/lieux-guyane-historique.js",
                "../assets/lieux-martinique-historique.js",
                "../assets/lieux-guadeloupe-historique.js",
                "../assets/lieux-multiechelon.js",
            ],
        )
        for path in (
            "docs/assets/lieux-chronologie-core.js", "docs/assets/lieux-search.js",
            "docs/assets/lieux-multiechelon.js", "docs/assets/lieux-outremer-search.js",
            "docs/assets/lieux-guyane-historique.js",
            "docs/assets/lieux-martinique-historique.js",
            "docs/assets/lieux-guadeloupe-historique.js",
            "docs/assets/lieux-multiechelon.css",
            "docs/assets/lieux.css",
        ):
            self.assertTrue((ROOT / path).is_file(), path)
        for stylesheet in (
            "../assets/site.css", "../assets/lieux.css",
            "../assets/lieux-multiechelon.css",
            "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css",
        ):
            self.assertTrue(
                any(tag == "link" and attrs.get("href") == stylesheet
                    for tag, attrs in self.page.tags),
                stylesheet,
            )

    def test_module_manifest_and_homepage(self):
        lieu = self.manifest["modules"]["lieux"]
        self.assertEqual(lieu["status"], "prototype")
        self.assertEqual(lieu["data"], "data/lieux.json")
        self.assertEqual(lieu["geometries"], "data/lieux-communes.geojson")
        self.assertEqual(lieu["data_schema"], "0.1.0")
        self.assertEqual(lieu["autorites_validees"], 103)
        outremer = lieu["recherche_cog_outremer_2026"]
        self.assertEqual(outremer["communes"], 212)
        self.assertEqual(outremer["autres_entites"], 21)
        self.assertEqual(outremer["relations_pactols_cog_validees_2026"], 128)
        self.assertEqual(outremer["relations_pactols_cog_validees_guadeloupe_2026"], 32)
        self.assertEqual(outremer["relations_pactols_cog_validees_reunion_2026"], 24)
        self.assertEqual(outremer["relations_pactols_cog_validees_martinique_2026"], 34)
        self.assertEqual(outremer["relations_pactols_cog_validees_guyane_2026"], 22)
        self.assertEqual(outremer["ark_confirmes_lien_non_valide"], 1)
        self.assertEqual(outremer["geometries_publiees"], 0)
        self.assertEqual(outremer["identites_historiques_retroprojetees"], 0)

        self.assertIn('href="lieux/"', self.home)
        self.assertNotIn('<p class="eyebrow">À venir</p><h2>Lieux</h2>', self.home)

    def test_limitations_and_attribution_visible(self):
        for excerpt in (
            "103 correspondances", "contours", "Les régions et départements des cinq DROM",
            "https://www.data.gouv.fr/datasets/contours-administratifs",
            "OpenStreetMap", "Zoom sur", "Échelon territorial",
            "Situation administrative au 1er janvier",
        ):
            self.assertIn(excerpt, self.html)



if __name__ == "__main__":
    unittest.main()
