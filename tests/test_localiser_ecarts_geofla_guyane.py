"""Tests sans source externe des diagnostics des différences GEOFLA/Etalab Guyane."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from localiser_ecarts_geofla_guyane import (
    SCHEMA, CODES, FOCUS, metriques, localiser, composantes,
)
try:
    from shapely.geometry import Polygon,MultiPolygon,GeometryCollection,box
    from pyproj import Transformer
except ImportError:
    Polygon=None
    box=None
    Transformer=None


class LocalisationGuyaneTests(unittest.TestCase):
    def test_codes_attendus_et_priorite(self):
        self.assertEqual(len(CODES),22)
        self.assertEqual(set(FOCUS),{"97301","97312","97303"})
        self.assertEqual(SCHEMA,"adlfi.lieux.guyane.ecarts-localises-geofla15-etalab26.v1")

    @unittest.skipIf(Polygon is None, "Dépendances spatiales installées dans la CI géométrique")
    def test_metriques_symetriques(self):
        a=box(0,0,1000,1000)
        b=box(500,0,1500,1000)
        values=metriques(a,b)
        self.assertEqual(values["symdiff_km2"],1.0)
        self.assertEqual(values["a_hors_b_km2"],0.5)
        self.assertEqual(values["b_hors_a_km2"],0.5)
        self.assertAlmostEqual(values["jaccard_pct"],33.333333,places=5)

    @unittest.skipIf(Polygon is None, "Dépendances spatiales installées dans la CI géométrique")
    def test_composantes_et_positions_sans_geometry_exportee(self):
        a=box(0,0,1000,1000)
        b=box(2000,0,4000,1000)
        g=MultiPolygon([a,b])
        proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
        result=localiser(g,proj,seuil_km2=0.5,max_composantes=1)
        self.assertEqual(result["composantes_detectees"],2)
        self.assertEqual(result["composantes_au_dessus_du_seuil"],2)
        self.assertEqual(result["composantes_exportees"],1)
        self.assertEqual(result["surface_totale_km2"],3)
        self.assertEqual(result["surface_composantes_exportees_km2"],2)
        self.assertEqual(result["composantes"][0]["aire_km2"],2)
        self.assertEqual(len(result["composantes"][0]["enveloppe_wgs84_lonlat"]),4)
        self.assertFalse(any(k in result["composantes"][0] for k in ("geometry","coordinates","polygon","wkt")))
        self.assertEqual(len(composantes(GeometryCollection([a,b]))),2)

    @unittest.skipIf(Polygon is None, "Dépendances spatiales installées dans la CI géométrique")
    def test_filtrage_de_micro_composantes(self):
        proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
        small=box(0,0,100,100)
        result=localiser(small,proj,seuil_km2=0.5)
        self.assertEqual(result["surface_totale_km2"],0.01)
        self.assertEqual(result["composantes_exportees"],0)
        self.assertEqual(result["composantes_au_dessus_du_seuil"],0)

    @unittest.skipIf(Polygon is None, "Dépendances spatiales installées dans la CI géométrique")
    def test_composante_vide(self):
        empty=Polygon()
        proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
        result=localiser(empty,proj)
        self.assertEqual(result["surface_totale_km2"],0)
        self.assertEqual(result["composantes_detectees"],0)


if __name__=="__main__":
    unittest.main()
