"""Garde-fous de l'audit géométrique GEOFLA Guyane 2015."""
import sys
import unittest
from pathlib import Path
try:
    from shapely.geometry import Polygon, box
except ImportError:
    Polygon=None
    box=None

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_geofla_guyane_2015 import reconnaitre_code, comparer_geometries,decomposer_ecarts_cartographiques,SCHEMA


class GEOFLAGuyaneTests(unittest.TestCase):
    def test_code_communal_explicite(self):
        self.assertEqual(reconnaitre_code({"CODE_INSEE":"97306"}),("97306","CODE_INSEE"))
        self.assertEqual(reconnaitre_code({"insee_com":"97301"}),("97301","INSEE_COM"))
        self.assertEqual(reconnaitre_code({"CODE_INSEE":"97306","INSEE_COM":"97306"})[0],"97306")

    def test_homonymie_ou_contradiction_ne_produit_pas_code(self):
        self.assertEqual(reconnaitre_code({"NOM_COM":"Mana"}),(None,None))
        self.assertEqual(reconnaitre_code({"CODE_INSEE":"75056"}),(None,None))
        self.assertEqual(reconnaitre_code({"CODE_INSEE":"97306","INSEE_COM":"97351"}),(None,None))

    @unittest.skipIf(Polygon is None, 'Shapely disponible dans la CI géométrique')
    def test_differences_surfaciques_symetriques(self):
        a=Polygon([(0,0),(1000,0),(1000,1000),(0,1000)])
        b=Polygon([(500,0),(1500,0),(1500,1000),(500,1000)])
        r=comparer_geometries(a,b)
        self.assertAlmostEqual(r["source2015_km2"],1)
        self.assertAlmostEqual(r["national2026_km2"],1)
        self.assertAlmostEqual(r["difference_symetrique_km2"],1)
        self.assertAlmostEqual(r["source2015_hors_2026_km2"],0.5)
        self.assertAlmostEqual(r["national2026_hors_2015_km2"],0.5)
        self.assertAlmostEqual(r["jaccard_pct"],33.333333,places=5)


    @unittest.skipIf(Polygon is None, 'Shapely requis')
    def test_decomposition_interne_externe_et_equation(self):
        codes=([f"973{i:02d}" for i in range(1,15)] +
               ["97352","97353","97356","97357","97358","97360","97361","97362"])
        self.assertEqual(len(codes),22)
        a={code:box(i*1000,0,(i+1)*1000,1000)
           for i,code in enumerate(codes)}
        b=dict(a)
        b["97301"]=box(-50,0,1100,1000)
        b["97302"]=box(1100,0,2000,1000)
        b[codes[-1]]=box(21000,0,22025,1000)
        result=decomposer_ecarts_cartographiques(a,b)
        d=result["decomposition_global_km2"]
        self.assertAlmostEqual(d["ecart_externe_total_km2"],0.075)
        self.assertAlmostEqual(d["ecart_interne_unique_km2"],0.1)
        self.assertAlmostEqual(d["somme_ecarts_communaux_km2"],0.275)
        self.assertAlmostEqual(
            d["ecart_externe_total_km2"]+2*d["ecart_interne_unique_km2"],
            d["somme_ecarts_communaux_km2"])
        local={x["code"]:x for x in result["par_commune"]}
        self.assertAlmostEqual(local["97301"]["ecart_externe_total_km2"],0.05)
        self.assertAlmostEqual(local["97301"]["ecart_interne_entrant_autre_code_2015_vers_2026_km2"],0.1)
        self.assertAlmostEqual(local["97302"]["ecart_interne_sortant_2015_vers_autre_code_2026_km2"],0.1)
        self.assertEqual(
            result["priorites"]["97301"]["ecarts_de_codes_cartographiques_2026_depuis_2015"],
            [{"code_2015":"97302","intersection_km2":0.1}])

    @unittest.skipIf(Polygon is None, 'Shapely requis')
    def test_decomposition_refuse_partition_incomplete(self):
        a={"97301":box(0,0,1000,1000)}
        with self.assertRaisesRegex(ValueError,"incomplètes"):
            decomposer_ecarts_cartographiques(a,a)

    @unittest.skipIf(Polygon is None, 'Shapely requis')
    def test_decomposition_refuse_recouvrement(self):
        codes=([f"973{i:02d}" for i in range(1,15)] +
               ["97352","97353","97356","97357","97358","97360","97361","97362"])
        a={code:box(i*1000,0,(i+1)*1000,1000)
           for i,code in enumerate(codes)}
        b=dict(a)
        b["97302"]=box(900,0,2000,1000)
        with self.assertRaisesRegex(ValueError,"Recouvrement"):
            decomposer_ecarts_cartographiques(a,b)

    @unittest.skipIf(Polygon is None, 'Shapely disponible dans la CI géométrique')
    def test_geom_invalide_refusee(self):
        invalide=Polygon([(0,0),(2,2),(0,2),(2,0)])
        saine=Polygon([(0,0),(2,0),(2,2),(0,2)])
        with self.assertRaisesRegex(ValueError,"non valide"):
            comparer_geometries(invalide,saine)


if __name__=="__main__":
    unittest.main()
