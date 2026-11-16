"""Tests hors réseau du repérage du condominium dans les capacités WFS."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from auditer_condominium_wfs_ign import (
    lister_couches, candidat_condominium, analyser_geojson,
)

XML = b"""<?xml version="1.0"?>
<wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs/2.0"
 xmlns="http://www.opengis.net/wfs/2.0">
 <FeatureTypeList>
 <FeatureType><Name>BDTOPO_V3:commune</Name><Title>Commune</Title></FeatureType>
 <FeatureType><Name>BDTOPO_V3:condominium</Name><Title>Condominium</Title></FeatureType>
 </FeatureTypeList>
</wfs:WFS_Capabilities>"""


class WFSTests(unittest.TestCase):
    def test_une_seule_couche_condominium(self):
        couches = lister_couches(XML)
        self.assertEqual(len(couches), 2)
        self.assertEqual(
            candidat_condominium(couches),
            [{"name": "BDTOPO_V3:condominium", "title": "Condominium"}],
        )

    def test_aucune_couche_ne_devient_une_commune(self):
        couches = lister_couches(
            XML.replace(b"condominium", b"territoire_inconnu")
        )
        self.assertEqual(candidat_condominium(couches), [])


try:
    import shapely
    import pyproj
    HAS_GEO = True
except ImportError:
    HAS_GEO = False


@unittest.skipUnless(HAS_GEO, "Shapely et pyproj dans CI specialisee")
class GeomTests(unittest.TestCase):
    def test_geom_isolee_ne_valide_jamais_le_code_cog(self):
        fc = {"type": "FeatureCollection", "features": [{
            "type": "Feature", "properties": {"cleabs": "fake-test"},
            "geometry": {"type": "MultiPolygon", "coordinates": [
                [[[-1.8, 43.35], [-1.79, 43.35], [-1.79, 43.36],
                  [-1.8, 43.36], [-1.8, 43.35]]]
            ]},
        }]}
        x = analyser_geojson(fc)
        self.assertEqual(x["nombre_features"], 1)
        self.assertTrue(x["features"][0]["valide_topologiquement"])
        self.assertTrue(x["features"][0]["emprise_region_bidassoa"])
        self.assertFalse(x["identite_COG_98101_etablie"])
        self.assertEqual(x["geometries_publiees"], 0)


if __name__ == "__main__":
    unittest.main()
