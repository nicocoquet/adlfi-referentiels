"""Tests synthétiques de la comparaison GEOFLA 2015 / Etalab 2026 (24 communes 974)."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_geofla_reunion_2015 import (
 SCHEMA,CODES,SHA_2015,code_insee,comparaison,
 principales_composantes,controler_partition
)
try:
 from shapely.geometry import box
 from pyproj import Transformer
except ImportError:
 box=None
 Transformer=None

class AuditGeoflaReunionTests(unittest.TestCase):
 def test_codes_attributaires_et_provenance(self):
  self.assertEqual(len(CODES),24)
  self.assertEqual(SCHEMA,"adlfi.lieux.reunion.audit.geofla2015-etalab2026.v1")
  self.assertEqual(SHA_2015,"6ab4183681f0d15472678f958ca7a6a2c4b95b1b3bc694f7aefe7ec4c67dfea2")
  self.assertEqual(CODES,{f"974{i:02d}" for i in range(1,25)})
  self.assertIn("97414",CODES)
  self.assertIn("97424",CODES)
  self.assertEqual(code_insee({"INSEE_COM":"97414"}),("97414","INSEE_COM"))
  self.assertEqual(code_insee({"CODE_INSEE":"97424"}),("97424","CODE_INSEE"))
  self.assertEqual(code_insee({"NOM_COM":"CILAOS"}),(None,None))
  self.assertEqual(code_insee({"CODE_INSEE":"97114"}),(None,None))
  self.assertEqual(code_insee({"INSEE_COM":"97414","CODE_INSEE":"97424"}),(None,None))
  self.assertEqual(code_insee({"INSEE_COM":"97414","CODE_COM":"414"}),("97414","INSEE_COM"))

 def partitions(self):
  codes=sorted(CODES)
  a={c:box(i*1000,0,(i+1)*1000,1000) for i,c in enumerate(codes)}
  b=dict(a)
  b["97401"]=box(-50,0,1100,1000)
  b["97402"]=box(1100,0,2000,1000)
  b["97424"]=box(23000,0,24025,1000)
  return a,b

 @unittest.skipIf(box is None or Transformer is None,"Shapely et pyproj requis")
 def test_equation_partition_surfaces(self):
  a,b=self.partitions()
  proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
  out=comparaison(a,b,"Etalab 2026",proj)
  self.assertEqual(out["communes"],24)
  self.assertAlmostEqual(out["ecart_emprise_exterieure_km2"],.075,places=5)
  self.assertAlmostEqual(out["ecart_entre_codes_interieur_unique_km2"],.1,places=5)
  self.assertAlmostEqual(out["cumul_ecarts_communaux_km2"],.275,places=5)
  self.assertEqual(out["communes"],len(out["toutes_communes"]))
  self.assertEqual({r["code"] for r in out["toutes_communes"]},CODES)
  self.assertAlmostEqual(out["cumul_ecarts_communaux_km2"],
                         out["ecart_emprise_exterieure_km2"]+
                         2*out["ecart_entre_codes_interieur_unique_km2"],places=5)

 @unittest.skipIf(box is None,"Shapely requis")
 def test_refus_doublons_spatiaux_et_communes_absentes(self):
  a,b=self.partitions()
  b["97403"]=box(1900,0,3000,1000)
  with self.assertRaisesRegex(ValueError,"recouvrement"):
   controler_partition(b,"test")
  a.pop("97424")
  with self.assertRaisesRegex(ValueError,"incomplets"):
   controler_partition(a,"test")

 @unittest.skipIf(box is None or Transformer is None,"Shapely et pyproj requis")
 def test_aucun_polygone_exporte(self):
  projection=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
  detail=principales_composantes(box(0,0,300,300),projection,seuil_km2=.01)
  self.assertEqual(detail["composantes"],1)
  self.assertEqual(detail["composantes_exportees"],1)
  r=detail["plus_grandes"][0]
  self.assertEqual(r["aire_km2"],.09)
  self.assertEqual(len(r["point_interieur_wgs84_lonlat"]),2)
  self.assertFalse(any(k in r for k in ("geometry","coordinates","polygon","wkt")))

if __name__=="__main__":
 unittest.main()
