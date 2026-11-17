"""Mayotte : tests synthétiques d'une comparaison exploratoire de 17 partitions."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_geofla_mayotte_2015 import (
 SCHEMA,CODES,SHA_2015,code_insee,comparaison,
 principales_composantes,controler_partition
)
try:
 from shapely.geometry import box
 from pyproj import Transformer
except ImportError:
 box=None
 Transformer=None

class AuditGeoflaMayotteTests(unittest.TestCase):
 def test_codes_et_provenance(self):
  self.assertEqual(SCHEMA,"adlfi.lieux.mayotte.audit.geofla2015-etalab2026.v1")
  self.assertEqual(SHA_2015,"7d9747f01a47a70ba8afb14dab7077fe04268a37c0a89eb196706b5cd3d1b47e")
  self.assertEqual(len(CODES),17)
  self.assertEqual(CODES,{f"976{i:02d}" for i in range(1,18)})
  self.assertEqual(code_insee({"INSEE_COM":"97607"}),("97607","INSEE_COM"))
  self.assertEqual(code_insee({"CODE_INSEE":"97617"}),("97617","CODE_INSEE"))
  self.assertEqual(code_insee({"CODE_INSEE":"97407"}),(None,None))
  self.assertEqual(code_insee({"NOM_COM":"Dembeni"}),(None,None))
  self.assertEqual(code_insee({"INSEE_COM":"97607","CODE_INSEE":"97617"}),(None,None))

 def partitions(self):
  a={c:box(i*1000,0,(i+1)*1000,1000) for i,c in enumerate(sorted(CODES))}
  b=dict(a)
  b["97601"]=box(-50,0,1100,1000)
  b["97602"]=box(1100,0,2000,1000)
  b["97617"]=box(16000,0,17025,1000)
  return a,b

 @unittest.skipIf(box is None or Transformer is None,"Shapely et pyproj requis")
 def test_decomposition_et_fermeture(self):
  a,b=self.partitions()
  proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
  out=comparaison(a,b,"Etalab2026_100m",proj)
  self.assertEqual(out["communes"],17)
  self.assertEqual({x["code"] for x in out["toutes_communes"]},CODES)
  self.assertAlmostEqual(out["ecart_emprise_exterieure_km2"],.075,places=5)
  self.assertAlmostEqual(out["ecart_entre_codes_interieur_unique_km2"],.1,places=5)
  self.assertAlmostEqual(out["cumul_ecarts_communaux_km2"],.275,places=5)
  self.assertAlmostEqual(out["cumul_ecarts_communaux_km2"],
   out["ecart_emprise_exterieure_km2"]+
   2*out["ecart_entre_codes_interieur_unique_km2"],places=5)

 @unittest.skipIf(box is None,"Shapely requis")
 def test_refuser_recouvrements_et_codes_manquants(self):
  a,b=self.partitions()
  b["97603"]=box(1900,0,3000,1000)
  with self.assertRaisesRegex(ValueError,"recouvrement"):
   controler_partition(b,"essai")
  a.pop("97607")
  with self.assertRaisesRegex(ValueError,"incomplets"):
   controler_partition(a,"essai")

 @unittest.skipIf(box is None or Transformer is None,"Shapely et pyproj requis")
 def test_ne_jamais_exporter_de_polygone(self):
  proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
  res=principales_composantes(box(0,0,300,300),proj,seuil_km2=.01)
  self.assertEqual(res["composantes"],1)
  x=res["plus_grandes"][0]
  self.assertEqual(x["aire_km2"],.09)
  self.assertEqual(len(x["point_interieur_wgs84_lonlat"]),2)
  self.assertEqual(len(x["enveloppe_approximative_wgs84_lonlat"]),4)
  self.assertFalse(any(k in x for k in ("geometry","coordinates","polygon","wkt")))

if __name__=="__main__":
 unittest.main()
