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
        self.assertEqual(self.html.count('class="control"'), 2)  # échelon et recherche ; zoom/année ont leurs panneaux dédiés
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
        self.assertEqual(len(dataset["pactols_valides"]), 212)
        self.assertEqual(dataset["pactols_collectivites_valides"], {
            "977":"26678/pcrtrGdtY56gmH",
            "978":"26678/pcrty5LooX8FgU",
            "986":"26678/pcrtwFq5jKHO3k",
            "987":"26678/pcrt4K8nLVxWOP"
        })
        self.assertFalse(set(dataset["pactols_collectivites_valides"].values()) &
                         set(dataset["pactols_valides"].values()))
        self.assertTrue(all("COMER:TERRITOIRE:"+code in
            {row[0] for row in dataset["autres"]}
            for code in dataset["pactols_collectivites_valides"]))
        self.assertFalse(set(dataset["pactols_valides"]) &
            {"977","978","986","987","97123","97127","97701","97801","98611","98612","98613"})
        self.assertEqual(len([k for k in dataset["pactols_valides"] if k.startswith("971")]), 32)
        self.assertNotIn("97123", dataset["pactols_valides"])
        self.assertNotIn("97127", dataset["pactols_valides"])
        self.assertEqual(len([k for k in dataset["pactols_valides"] if k.startswith("972")]), 34)
        self.assertEqual(len([k for k in dataset["pactols_valides"] if k.startswith("973")]), 22)
        self.assertEqual(len([k for k in dataset["pactols_valides"] if k.startswith("974")]), 24)
        self.assertEqual(len([k for k in dataset["pactols_valides"] if k.startswith("987")]), 48)
        self.assertEqual(dataset["pactols_valides"]["98711"],"26678/pcrtwSlYRcWVFw")
        self.assertEqual(dataset["pactols_valides"]["98735"],"26678/pcrtr90gKcAXiG")
        self.assertEqual(dataset["pactols_valides"]["98745"],"26678/pcrteZcqWgVUaT")
        self.assertEqual(dataset["pactols_valides"]["98758"],"26678/pcrtRw9F7i5M8l")
        self.assertEqual(dataset["pactols_valides"]["97407"], "26678/pcrtIKvRT9vwUl")
        self.assertEqual(dataset["ark_confirmes_non_valides"], {})
        self.assertEqual(dataset["pactols_valides"]["97607"], "26678/crtZcuFSJVYZU")
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

    def test_limites_communales_et_survol_distinct_des_reperes(self):
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf-8")
        self.assertIn("const communeWeight=z<=6?.4:z<=8?.9:z<=10?1.35:1.8", js)
        self.assertIn("const communeFill=z<=6?.04:z<=8?.09:.14", js)
        self.assertIn("state.map.on('zoomend'", js)
        self.assertIn("state.layer.setStyle(f=>displayStyle(f,false))", js)
        self.assertIn("layer.on('mouseover'", js)
        self.assertNotIn("if(p.niveau==='commune'){", js)
        self.assertIn("interactive:!reference", js)
        self.assertIn("départements, régions et futurs arrondissements municipaux", js)
        self.assertIn("fillOpacity:.42", js)
        self.assertIn("layer.on('mouseout',()=>state.layer?.resetStyle(layer))", js)
        self.assertIn("dashArray:reference?(communeRepere?'2,5':'5,5'):null", js)

    def test_chargement_regional_progressif_des_contours_2026(self):
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf-8")
        module = (ROOT / "docs/assets/lieux-communes-vue.js").read_text(encoding="utf-8")
        self.assertIn("AdlfiLieuxCommunesVue", module)
        self.assertIn("const ZOOM_REDUCTION=7", module)
        self.assertIn("zonesCommunesVisibles()", js)
        self.assertIn("zones.map(chargerRegionCommune)", js)
        self.assertIn("communeDataPromises=new Map()", js)
        self.assertIn("state.map.on('moveend'", js)
        self.assertIn("lastCommunesViewKey", js)
        self.assertIn("references=await chargerCommunes2026(zones)", js)
        self.assertIn("chargerOutremerCommunes()", js)
        self.assertIn('lieux-communes-vue.js', self.html)
        self.assertLess(self.html.index('lieux-communes-vue.js'),
                        self.html.index('lieux-multiechelon.js'))
        self.assertIn("2026", js)
        self.assertIn("ne sont pas", module if "ne sont pas" in module else
                      "les emprises ne sont pas des géométries")

    def test_chevrons_menus_et_groupes_geographiques(self):
        css = (ROOT / "docs/assets/lieux-multiechelon.css").read_text(encoding="utf-8")
        self.assertIn('content:"⏵"', css)
        self.assertIn('content:"⏷"', css)
        self.assertIn('.map-tool[open] > summary::after{content:"⏷"}', css)
        self.assertIn('.zone-group[open]>summary::before{content:"⏷"}', css)
        self.assertIn('display:flex;align-items:center;justify-content:flex-start;gap:8px', css)
        self.assertIn('.zone-count{margin-left:auto;', css)

    def test_cadrages_saint_martin_et_saint_barthelemy(self):
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf-8")
        self.assertIn("'saint-martin':[[18.04,-63.17],[18.15,-62.96]]", js)
        self.assertIn("'saint-barthelemy':[[17.86,-62.92],[17.98,-62.77]]", js)
        self.assertIn("'saint-martin':'saint-martin','saint-barthelemy':'saint-barthelemy'", js)
        self.assertIn('<option value="saint-martin">Saint-Martin</option>', self.html)
        self.assertIn('<option value="saint-barthelemy">Saint-Barthélemy</option>', self.html)

    def test_fond_nautique_echelle_et_molette(self):
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf-8")
        self.assertIn("scrollWheelZoom:true", js)
        self.assertIn("https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png", js)
        self.assertIn("L.control.layers(null", js)
        self.assertIn("Afficher OpenSeaMap (informations nautiques)", js)
        self.assertIn("L.control.scale({position:'bottomleft',imperial:false,metric:true", js)
        self.assertIn("const seaMode=L.layerGroup([seaMarks])", js)
        self.assertIn("osmTiles.addTo(state.map)", js)

    def test_chronologie_dans_menu_annee_et_recherche_renommee(self):
        html = (ROOT / "docs/lieux/index.html").read_text(encoding="utf-8")
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf-8")
        self.assertIn('id="year-tool" name="lieux-navigation"', html)
        self.assertIn('id="year-current"', html)
        self.assertIn('<span class="map-tool-title">Année</span>', html)
        self.assertIn('<span class="map-tool-title">Rechercher</span>', html)
        self.assertIn('placeholder="Recherche un nom de lieu, un code INSEE, un ARK Pactols..."', html)
        self.assertEqual(html.count('id="year"'), 1)
        self.assertIn("if($('year-current'))$('year-current').textContent=String(y)", js)

    def test_arborescence_zoom_et_vignettes_svg_sans_geometrie_inventee(self):
        html = (ROOT / "docs/lieux/index.html").read_text(encoding="utf-8")
        js = (ROOT / "docs/assets/lieux-multiechelon.js").read_text(encoding="utf-8")
        self.assertEqual(html.count('class="zone-group"'), 5)
        self.assertEqual(html.count('class="zone-choice"'), 26)
        for key in ("auvergne-rhone-alpes", "pdl", "guadeloupe",
                    "saint-martin", "taaf", "clipperton"):
            self.assertIn('data-zone="' + key + '"', html)
        self.assertIn("zonesSvg(geometry)", js)
        self.assertIn("await layerFor(2026,'region')", js)
        self.assertIn("btn.disabled=true", js)
        self.assertNotIn("M10 12 L27 7 L39 19", html)

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
                "../assets/lieux-reunion-historique.js",
                "../assets/lieux-mayotte-historique.js",
                "../assets/lieux-saint-pierre-miquelon-historique.js",
                "../assets/lieux-antilles-collectivites-2007.js",
                "../assets/lieux-wallis-futuna-historique.js",
                "../assets/lieux-polynesie-historique.js",
                "../assets/lieux-polynesie-associees.js",
                "../assets/lieux-corse-pactols.js",
                "../assets/lieux-bfc-pactols.js",
                "../assets/lieux-pdl-pactols.js",
                "../assets/lieux-pdl-uuid-resolus.js",
                "../assets/lieux-pdl-communes-nouvelles-lot01.js",
                "../assets/lieux-pdl-chemille-2026.js",
                "../assets/lieux-pdl-communes-nouvelles-lot02.js",
                "../assets/lieux-pdl-oree-mod50.js",
                "../assets/lieux-pdl-wikidata-p374.js",
                "../assets/lieux-pdl-trois-collisions.js",
                "../assets/lieux-pdl-deux-2024.js",
                "../assets/lieux-paca-pactols.js",
                "../assets/lieux-paca-renommages.js?v=20261118-paca938",
                "../assets/lieux-paca-communes-nouvelles.js",
                "../assets/lieux-paca-abries-ristolas.js",
                "../assets/lieux-drom-contours.js",
                "../assets/lieux-spm-contours.js",
                "../assets/lieux-nc-contours.js",
                "../assets/lieux-pf-contours.js",
                "../assets/lieux-multiechelon.js?v=20261118-interface1",
            ],
        )
        for path in (
            "docs/assets/lieux-chronologie-core.js", "docs/assets/lieux-search.js",
            "docs/assets/lieux-multiechelon.js", "docs/assets/lieux-corse-pactols.js", "docs/assets/lieux-bfc-pactols.js", "docs/assets/lieux-pdl-pactols.js", "docs/assets/lieux-pdl-uuid-resolus.js", "docs/assets/lieux-pdl-communes-nouvelles-lot01.js", "docs/assets/lieux-pdl-chemille-2026.js", "docs/assets/lieux-pdl-communes-nouvelles-lot02.js", "docs/assets/lieux-pdl-oree-mod50.js", "docs/assets/lieux-pdl-wikidata-p374.js", "docs/assets/lieux-pdl-trois-collisions.js", "docs/assets/lieux-pdl-deux-2024.js", "docs/assets/lieux-paca-pactols.js", "docs/assets/lieux-paca-renommages.js", "docs/assets/lieux-paca-communes-nouvelles.js", "docs/assets/lieux-paca-abries-ristolas.js", "docs/assets/lieux-drom-contours.js", "docs/assets/lieux-spm-contours.js", "docs/assets/lieux-nc-contours.js", "docs/assets/lieux-pf-contours.js", "docs/assets/lieux-outremer-search.js",
            "docs/assets/lieux-guyane-historique.js",
            "docs/assets/lieux-martinique-historique.js",
            "docs/assets/lieux-guadeloupe-historique.js",
            "docs/assets/lieux-reunion-historique.js",
            "docs/assets/lieux-mayotte-historique.js",
            "docs/assets/lieux-saint-pierre-miquelon-historique.js",
            "docs/assets/lieux-antilles-collectivites-2007.js",
            "docs/assets/lieux-wallis-futuna-historique.js",
            "docs/assets/lieux-polynesie-historique.js",
            "docs/assets/lieux-polynesie-associees.js",
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

    def test_reunion_historique_24_etats_et_division_1965_sans_geometrie(self):
        reunion = self.manifest["modules"]["lieux"]["historique_communes_reunion"]
        self.assertEqual(reunion["periodes_COG"], 24)
        self.assertEqual(reunion["lignes_mouvements_COG"], 25)
        self.assertEqual(reunion["division_Saint_Louis_Cilaos"], "1965-02-05")
        self.assertEqual(reunion["correspondances_pactols_2026_conservees"], 24)
        self.assertEqual(reunion["nouveaux_alignements_pactols"], 0)
        self.assertEqual(reunion["contours_historiques_publies"], 0)
        data=json.loads((ROOT/"docs/data/lieux-reunion/chronologie-cog-2026.json").read_text())
        self.assertEqual(len(data["episodes"].splitlines()), 24)
        self.assertEqual(data["mouvement_division_1965"]["codes_apres"], ["97414","97424"])
        self.assertIsNone(data["mouvement_division_1965"]["contour_avant_1965"])
        self.assertIsNone(data["mouvement_division_1965"]["contour_apres_1965"])

    def test_mayotte_historique_34_etats_comer_drom_non_geometriques(self):
        mayotte=self.manifest["modules"]["lieux"]["historique_communes_mayotte"]
        self.assertEqual(mayotte["total_episodes_COG"], 34)
        self.assertEqual(mayotte["episodes_COG_COMER"], 17)
        self.assertEqual(mayotte["episodes_COG_DROM"], 17)
        self.assertEqual(mayotte["codes_communes"], 17)
        self.assertEqual(mayotte["transition_COMER_DROM"], "2011-03-31")
        self.assertEqual(mayotte["date_premiere_attestation_COMER"], "2007-02-23")
        self.assertEqual(mayotte["code_collectivite_2011_2025"], "976D")
        self.assertEqual(mayotte["code_collectivite_2026"], "976R")
        self.assertEqual(mayotte["correspondances_pactols_2026_conservees"],16)
        self.assertEqual(mayotte["ark_dembeni_confirme_non_aligne"], "26678/crtZcuFSJVYZU")
        self.assertEqual(mayotte["nouveaux_alignements_pactols"], 0)
        self.assertEqual(mayotte["contours_historiques_publies"], 0)
        data=json.loads((ROOT/"docs/data/lieux-mayotte/chronologie-cog-2026.json").read_text())
        self.assertEqual(data["schema"],"adlfi.lieux.mayotte.etats_cog_public.v1")
        self.assertEqual(len(data["episodes"].splitlines()),34)
        self.assertIsNone(data["transition_famille_cog"]["date_creation_des_communes"])
        self.assertFalse(data["transition_famille_cog"]["creation_de_communes_par_cette_transition"])
        self.assertEqual(data["correspondances_pactols_COG_2026_conservees"],16)
        self.assertEqual(data["ark_confirme_sans_alignement_valide"],{
            "code":"97607","ark":"26678/crtZcuFSJVYZU"})
        self.assertEqual(data["nouvelles_relations_successions_inferrees"],0)

    def test_saint_pierre_miquelon_deux_communes_et_collectivite_distinctes(self):
        spm=self.manifest["modules"]["lieux"]["historique_communes_saint_pierre_miquelon"]
        self.assertEqual(spm["communes_COG_2026"],2)
        self.assertEqual(spm["episodes_communes_COMER"],2)
        self.assertEqual(spm["episodes_communes_DROM"],0)
        self.assertEqual(spm["episodes_collectivite_COG"],1)
        self.assertEqual(spm["code_collectivite"],"975")
        self.assertTrue(spm["famille_COG_distincte_statut_juridique"])
        self.assertEqual(spm["premiere_date_code_communal_COG"],"1976-07-21")
        self.assertEqual(spm["premiere_date_code_collectivite_COG"],"1985-06-15")
        self.assertEqual(spm["annees_lois_statutaires"],[1976,1985,2003,2007])
        self.assertEqual(spm["correspondances_pactols_2026_conservees"],0)
        self.assertEqual(spm["nouveaux_alignements_pactols"],0)
        self.assertEqual(spm["contours_historiques_publies"],0)
        self.assertEqual(spm["identites_historiques_retroprojetees"],0)
        data=json.loads((ROOT/"docs/data/lieux-saint-pierre-miquelon/chronologie-cog-2026.json").read_text())
        self.assertEqual(data["schema"],"adlfi.lieux.spm.etats_cog_public.v1")
        self.assertEqual(len(data["episodes_communes_COMER"].splitlines()),2)
        self.assertEqual(data["episodes_communes_DROM"],"")
        self.assertEqual(data["episodes_collectivite_COG"],"975|Saint-Pierre-et-Miquelon|1985-06-15|")
        self.assertTrue(data["famille_COG_non_equivalente_au_statut_juridique"])
        self.assertEqual(data["nouveaux_alignements_pactols"],0)
        self.assertEqual(data["contours_historiques_publies"],0)

    def test_saint_barthelemy_saint_martin_2007_successions_distinctes_du_cog(self):
        m=self.manifest["modules"]["lieux"]["historique_collectivites_antilles_2007"]
        self.assertEqual(m["anciens_codes_communes_971"],["97123","97127"])
        self.assertEqual(m["codes_collectivites_2026"],["977","978"])
        self.assertEqual(m["codes_application_cinq_positions_non_communaux"],["97701","97801"])
        self.assertEqual(m["date_fin_communes_COG"],"2007-02-23")
        self.assertEqual(m["date_debut_collectivites_COG"],"2007-02-23")
        self.assertEqual(m["date_entree_vigueur_loi_organique"],"2007-02-22")
        self.assertEqual(m["mouvements_COG_MOD30_sans_destination"],2)
        self.assertEqual(m["successions_juridiques_attestees"],2)
        self.assertEqual(m["nouveaux_alignements_pactols"],0)
        self.assertEqual(m["communes_actuelles_creees"],0)
        self.assertEqual(m["contours_historiques_publies"],0)
        data=json.loads((ROOT/"docs/data/lieux-antilles-collectivites-2007/chronologie-cog-juridique-2026.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema"],"adlfi.lieux.antilles2007.etats_cog_juridique_public.v1")
        self.assertEqual(len(data["episodes_anciens"].splitlines()),2)
        self.assertEqual(len(data["episodes_collectivites"].splitlines()),2)
        self.assertEqual(len(data["episodes_codes_cinq_positions"].splitlines()),2)
        self.assertEqual(data["relations_successions_juridiques_documentees"],2)
        self.assertEqual(data["nouvelles_relations_successions_COG_inferrees"],0)
        self.assertTrue(all(x["mouvement_COG"]["COM_AP"] is None for x in data["relations"]))
        self.assertTrue(all(x["code_cinq_positions"]["type"]=="CODE_APPLICATION_5_POSITIONS_NON_COMMUNE" for x in data["relations"]))
        self.assertTrue(all(x["succession_juridique"]["identite_pactols_deduite"] is False for x in data["relations"]))
        self.assertEqual(data["nouveaux_alignements_pactols"],0)
        self.assertEqual(data["nouveaux_contours_historiques"],0)

    def test_wallis_futuna_trois_circonscriptions_jamais_communes(self):
        m=self.manifest["modules"]["lieux"]["historique_circonscriptions_wallis_futuna"]
        self.assertEqual(m["territoire_COG_2026"],"986")
        self.assertEqual(m["ancien_code_territorial_documentaire"],"98609")
        self.assertEqual(m["episode_98609"],["1961-07-31","1985-01-01"])
        self.assertEqual(m["episode_986"],["1985-01-01",None])
        self.assertEqual(m["circonscriptions_COG_2026"],["98611","98612","98613"])
        self.assertEqual(m["nombre_circonscriptions"],3)
        self.assertEqual(m["nombre_communes"],0)
        self.assertEqual(m["loi_statutaire_circonscriptions"],"1961-07-30")
        self.assertEqual(m["premieres_attestations_COG_circonscriptions"],"1985-01-01")
        self.assertEqual(m["ancien_code_98607_entite_COG"],"Nouvelle-Calédonie")
        self.assertIs(m["relation_98607_vers_986_inferree"],False)
        self.assertEqual(m["nouvelle_relation_Pactols_validee"],0)
        self.assertEqual(m["contours_historiques_publies"],0)
        d=json.loads((ROOT/"docs/data/lieux-wallis-futuna/chronologie-cog-2026.json").read_text(encoding="utf-8"))
        self.assertEqual(d["schema"],"adlfi.lieux.wallis-futuna.etats_cog_public.v1")
        self.assertEqual(len(d["circonscriptions_2026"].splitlines()),3)
        self.assertEqual(len(d["episodes_circonscriptions"].splitlines()),3)
        self.assertEqual(d["episodes_territoire"],"986|Wallis-et-Futuna|1985-01-01|")
        self.assertEqual(d["code_territorial_ancien_documente"],"98609|Wallis-et-Futuna|1961-07-31|1985-01-01")
        self.assertEqual(d["ancien_code_contextuel_non_adopte"]["libelle"],"Nouvelle-Calédonie")
        self.assertEqual(d["territoire_courant"]["communes"],0)
        self.assertFalse(d["creation_circonscriptions_inferree_de_1985"])
        self.assertFalse(d["succession_juridique_98609_986_inferree"])
        self.assertEqual(d["nouveaux_alignements_pactols"],0)
        self.assertEqual(d["contours_historiques_publies"],0)

    def test_polynesie_48_communes_sans_assimilation_des_98_associees(self):
        m=self.manifest["modules"]["lieux"]["historique_communes_polynesie"]
        self.assertEqual(m["communes_COG_2026"],48)
        self.assertEqual(m["episodes_COG_2026"],48)
        self.assertEqual(m["date_premier_episode_COG"],"1972-05-21")
        self.assertIs(m["date_creation_de_toutes_les_communes_inferree"],False)
        self.assertEqual(m["communes_preexistantes_reforme_1971"],4)
        self.assertEqual(m["communes_ajoutees_reforme"],44)
        self.assertEqual(m["nombre_communes_associees_ISPF_a_instruire"],98)
        self.assertEqual(m["nombre_communes_avec_associees_ISPF"],30)
        self.assertEqual(m["nombre_communes_sans_associees_ISPF"],18)
        self.assertEqual(m["nombre_subdivisions_administratives"],5)
        self.assertEqual(m["Clipperton_ancien_code_COG"],"98799")
        self.assertEqual(m["Clipperton_date_fin_exclusive"],"2007-02-23")
        self.assertEqual(m["nombre_nouveaux_alignements_pactols"],0)
        self.assertEqual(m["correspondances_pactols_2026_validees"],48)
        self.assertIs(m["validation_identifiants_independante_geometries"],True)
        self.assertEqual(m["codes_contours_audites_invalides"],["98745"])
        self.assertEqual(m["nombre_contours_historiques_publies"],0)
        self.assertEqual(m["nombre_communes_associees_creees_automatiquement"],0)
        data=json.loads((ROOT/"docs/data/lieux-polynesie/chronologie-cog-2026.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema"],"adlfi.lieux.polynesie.etats_cog_public.v1")
        self.assertEqual(len(data["communes_actuelles_2026"].splitlines()),48)
        self.assertEqual(len(data["episodes_communes_COG"].splitlines()),48)
        self.assertEqual(data["episode_territoire_COG"],"987|Polynésie française|1972-05-21|")
        self.assertEqual(data["ancien_code_Clipperton_COG"]["code"],"98799")
        self.assertEqual(data["ancien_code_Clipperton_COG"]["fin_exclue"],"2007-02-23")
        self.assertEqual(data["decoupage_ISPF"]["nombre_unites_de_nomenclature_fine"],116)
        self.assertIs(data["historique_juridique"]["creation_juridique_toutes_communes_deduite_1972"],False)
        self.assertEqual(data["nouveaux_alignements_pactols"],0)
        self.assertEqual(data["alignements_pactols_2026_valides"],48)
        self.assertIs(data["alignements_uniquement_millesime_2026"],True)
        self.assertIs(data["contour_tahaa_98745_non_homologue"],True)
        self.assertEqual(data["communes_associees_creees"],0)

    def test_ispf_polynesie_98_associees_hors_48_communes_cog(self):
        m=self.manifest["modules"]["lieux"]["communes_associees_ispf_polynesie"]
        self.assertEqual(m["communes_associees_ispf"],98)
        self.assertEqual(m["communes_avec_associees"],30)
        self.assertEqual(m["communes_non_subdivisees_ispf"],18)
        self.assertEqual(m["codes_fins_ispf"],116)
        self.assertEqual(m["subdivisions_ispf"],5)
        self.assertEqual(m["source_sha256"],
          "d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6")
        self.assertEqual(m["feuille_Geo_iles_rattachees"],64)
        self.assertEqual(m["notice_ISPF_iles_rattachees"],63)
        self.assertEqual(m["code_unite_non_subdivisee_sans_ligne_de_base_Geo"],"190")
        self.assertEqual(m["nombre_iles_Gambier_lignes_Geo"],16)
        self.assertEqual(m["double_homonyme_Avera"],["441","501"])
        self.assertEqual(m["identifiants_INSEE_communes_associees_crees"],0)
        self.assertEqual(m["nouveaux_ARK_pactols"],0)
        self.assertEqual(m["nouvelles_geometries"],0)
        self.assertEqual(m["validites_historiques_inferrees"],0)
        d=json.loads((ROOT/"docs/data/lieux-polynesie/communes-associees-ispf-2026.json").read_text(encoding="utf-8"))
        self.assertEqual(d["schema"],"adlfi.lieux.polynesie.associees_ispf_nomenclature.v1")
        self.assertEqual(len(d["communes_associees"]),98)
        self.assertEqual(len(d["unites_communes_non_subdivisees"]),18)
        self.assertEqual(len(d["subdivisions"]),5)
        self.assertEqual(d["ecarts_libelles_48_parents_ISPF_COG"],[])
        self.assertEqual({x["commune_parent_cog"] for x in d["communes_associees"]}.__len__(),30)
        self.assertEqual(d["statistiques"]["nouveaux_ARK_Pactols_crees"],0)
        self.assertEqual(d["statistiques"]["geometries_nouvelles_publiees"],0)
        self.assertEqual({r["code_ispf"]:r["commune_parent_cog"] for r in d["communes_associees"] if r["code_ispf"] in ("441","501")},
           {"441":"98744","501":"98750"})

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
        self.assertEqual(outremer["relations_pactols_cog_validees_2026"], 212)
        self.assertEqual(outremer["relations_pactols_collectivites_2026"], 4)
        self.assertEqual(outremer["codes_collectivites_pactols_2026"],["977","978","986","987"])
        self.assertEqual(outremer["source_validations_collectivites"],
            "recette/lieux/COLLECTIVITES-COMER-VALIDATIONS-PACTOLS-COG-2026.csv")
        self.assertIs(outremer["relations_pactols_collectivites_2026_distinctes_des_communes"],True)
        self.assertEqual(outremer["alignements_codes_5_positions_97701_97801_inferes"],0)
        self.assertEqual(outremer["alignements_circonscriptions_98611_98612_98613_inferes"],0)
        self.assertEqual(outremer["alignements_communes_historiques_97123_97127_inferes"],0)
        self.assertIs(outremer["retroprojection_identifiants_2026"],False)
        self.assertEqual(outremer["relations_pactols_cog_validees_polynesie_2026"], 48)
        self.assertEqual(outremer["source_validations_polynesie"],
                         "recette/lieux/POLYNESIE-VALIDATIONS-PACTOLS-COG-2026.csv")
        self.assertEqual(outremer["relations_pactols_cog_validees_guadeloupe_2026"], 32)
        self.assertEqual(outremer["relations_pactols_cog_validees_reunion_2026"], 24)
        self.assertEqual(outremer["relations_pactols_cog_validees_martinique_2026"], 34)
        self.assertEqual(outremer["relations_pactols_cog_validees_guyane_2026"], 22)
        self.assertEqual(outremer["ark_confirmes_lien_non_valide"], 0)
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


    def test_paca_sept_communes_nouvelles_file_is_versioned(self):
        path=ROOT/"docs/data/lieux-chronologie/pactols-paca-communes-nouvelles-2026.json"
        self.assertTrue(path.is_file(), "Le fichier des sept communes nouvelles doit être versionné avant Chromium")
        data=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"],"adlfi.lieux.pactols.paca.sept_communes_nouvelles.2026.public.v1")
        self.assertEqual(data["alignements_total_PACA_2026"],945)
        self.assertEqual(data["exceptions_restantes"],["05001"])
        self.assertEqual(len(data["alignements_Pactols_COG_valides_2026"]),7)
        self.assertNotIn("05001",{x["code_insee"] for x in data["alignements_Pactols_COG_valides_2026"]})
        self.assertIn("lieux-paca-communes-nouvelles.js",self.html)

    def test_paca_abries_ristolas_editorial_json_is_published_before_browser(self):
        path=ROOT/"docs/data/lieux-chronologie/pactols-paca-abries-ristolas-2026.json"
        self.assertTrue(path.is_file(), "Le fichier de la validation éditoriale doit être versionné avant Chromium")
        data=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"],"adlfi.lieux.pactols.paca.abries_ristolas.editorial.2026.public.v1")
        self.assertEqual(data["total_PACA_alignements_2026"],946)
        self.assertEqual(data["exceptions_restantes"],[])
        self.assertIsNone(data["alignements_Pactols_COG_valides_2026"][0]["uri_insee_exactMatch_direct_pactols"])
        self.assertEqual(data["alignements_Pactols_COG_valides_2026"][0]["ark_pactols"],"26678/pcrtm96gvvfnwmggc9z0wrxn")
        self.assertIn("lieux-paca-abries-ristolas.js",self.html)


    def test_pdl_uuid_proofs_are_versioned_before_browser(self):
        path=ROOT/"docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json"
        self.assertTrue(path.is_file(), "Le JSON des trois preuves UUID doit être présent avant Chromium")
        data=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"],"adlfi.lieux.pactols.pdl.trois_uuid_resolus.2026.public.v1")
        self.assertEqual(data["total_alignements_PDL_2026"],1143)
        self.assertEqual(data["communes_a_instruire"],85)
        self.assertEqual([r["code_insee"] for r in data["alignements_Pactols_COG_valides_2026"]],
                         ["44066","85165","85212"])
        self.assertTrue(all(r["nature_validation"]=="INSEE_RDF_UUID_codeINSEE_owl_sameAs"
                         for r in data["alignements_Pactols_COG_valides_2026"]))
        self.assertIn("lieux-pdl-uuid-resolus.js",self.html)



if __name__ == "__main__":
    unittest.main()
