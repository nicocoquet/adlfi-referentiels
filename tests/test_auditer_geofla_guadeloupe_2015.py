"""Tests synthétiques des 32 contours GEOFLA Guadeloupe et partition spatiale."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_geofla_guadeloupe_2015 import (
  SCHEMA,CODES,code_insee,comparaison,principales_composantes,controler_partition
)
try:
  from shapely.geometry import box
  from pyproj import Transformer
except ImportError:
  box=None
  Transformer=None


class AuditGeoflaGuadeloupeTests(unittest.TestCase):
    def test_codes_2026_non_contigus(self):
        self.assertEqual(len(CODES),32)
        self.assertEqual(SCHEMA,"adlfi.lieux.guadeloupe.audit.geofla2015-etalab2026.v1")
        self.assertNotIn("97123",CODES)
        self.assertNotIn("97127",CODES)
        self.assertIn("97134",CODES)
        self.assertEqual(code_insee({"INSEE_COM":"97101"}),("97101","INSEE_COM"))
        self.assertEqual(code_insee({"CODE_INSEE":"97134"}),("97134","CODE_INSEE"))
        self.assertEqual(code_insee({"NOM_COM":"Les Abymes"}),(None,None))
        self.assertEqual(code_insee({"CODE_INSEE":"97209"}),(None,None))
        self.assertEqual(code_insee({"CODE_INSEE":"97101","INSEE_COM":"97134"}),(None,None))

    def partitions(self):
        codes=sorted(CODES)
        a={c:box(i*1000,0,(i+1)*1000,1000) for i,c in enumerate(codes)}
        b=dict(a)
        b["97101"]=box(-50,0,1100,1000)
        b["97102"]=box(1100,0,2000,1000)
        b["97134"]=box(31000,0,32025,1000)
        return a,b

    @unittest.skipIf(box is None, "Shapely et pyproj requis")
    def test_decomposition_fermeture(self):
        a,b=self.partitions()
        proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
        r=comparaison(a,b,"2026",proj)
        self.assertEqual(r["communes"],32)
        self.assertAlmostEqual(r["ecart_emprise_exterieure_km2"],0.075,places=5)
        self.assertAlmostEqual(r["ecart_entre_codes_interieur_unique_km2"],0.1,places=5)
        self.assertAlmostEqual(r["cumul_ecarts_communaux_km2"],0.275,places=5)
        self.assertAlmostEqual(r["ecart_emprise_exterieure_km2"]+
                               2*r["ecart_entre_codes_interieur_unique_km2"],
                               r["cumul_ecarts_communaux_km2"],places=5)
        self.assertEqual(len(r["toutes_communes"]),32)
        self.assertTrue(r["composantes_exterieures"]["2026_hors_2015"]["plus_grandes"])

    @unittest.skipIf(box is None, "Shapely et pyproj requis")
    def test_recouvrement_refuse(self):
        a,b=self.partitions()
        b["97103"]=box(1900,0,3000,1000)
        with self.assertRaisesRegex(ValueError,"recouvrement"):
            controler_partition(b,"test")

    @unittest.skipIf(box is None, "Shapely et pyproj requis")
    def test_absence_code_refusee(self):
        a,b=self.partitions()
        a.pop("97102")
        with self.assertRaisesRegex(ValueError,"incomplets"):
            controler_partition(a,"test")

    @unittest.skipIf(box is None, "Shapely et pyproj requis")
    def test_pas_de_polygone_exporte(self):
        proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
        result=principales_composantes(box(0,0,300,300),proj,seuil_km2=0.01)
        self.assertEqual(result["composantes"],1)
        self.assertEqual(result["composantes_exportees"],1)
        entry=result["plus_grandes"][0]
        self.assertEqual(entry["aire_km2"],0.09)
        self.assertEqual(len(entry["point_interieur_wgs84_lonlat"]),2)
        self.assertEqual(len(entry["enveloppe_approximative_wgs84_lonlat"]),4)
        self.assertFalse(any(k in entry for k in ("geometry","coordinates","polygon","wkt")))


if __name__=="__main__":
    unittest.main()
