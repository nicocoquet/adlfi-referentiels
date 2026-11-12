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
            "lieux-query", "lieux-suggestions", "lieux-reset",
            "lieux-counter", "lieux-map", "lieux-map-status", "lieux-detail-body",
        ):
            self.assertIn(element_id, self.page.ids)
        query = self.page.ids["lieux-query"][1]
        self.assertEqual(query["role"], "combobox")
        self.assertEqual(query["aria-controls"], "lieux-suggestions")
        self.assertEqual(query["aria-autocomplete"], "list")
        self.assertEqual(self.page.ids["lieux-suggestions"][1]["role"], "listbox")
        self.assertEqual(self.page.ids["lieux-map-status"][1]["role"], "status")
        self.assertEqual(self.page.ids["lieux-map"][1]["role"], "region")

    def test_external_leaflet_pinned_and_local_assets_ordered(self):
        scripts = [attrs["src"] for tag, attrs in self.page.tags
                   if tag == "script" and "src" in attrs]
        self.assertEqual(
            scripts,
            [
                "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js",
                "../assets/lieux-search.js",
                "../assets/lieux.js",
            ],
        )
        for path in ("docs/assets/lieux-search.js", "docs/assets/lieux.js",
                     "docs/assets/lieux.css"):
            self.assertTrue((ROOT / path).is_file(), path)
        for stylesheet in (
            "../assets/site.css", "../assets/lieux.css",
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
        self.assertIn('href="lieux/"', self.home)
        self.assertNotIn('<p class="eyebrow">À venir</p><h2>Lieux</h2>', self.home)

    def test_limitations_and_attribution_visible(self):
        for excerpt in (
            "103 correspondances éditoriales validées",
            "non leurs", "limites historiques",
            "https://www.data.gouv.fr/datasets/contours-administratifs",
            "licence ODbL",
        ):
            self.assertIn(excerpt, self.html)


if __name__ == "__main__":
    unittest.main()
