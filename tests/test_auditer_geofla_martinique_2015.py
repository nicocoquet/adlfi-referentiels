"""Tests géométriques synthétiques du lot GEOFLA 2015 Martinique."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_geofla_martinique_2015 import (
    SCHEMA,CODES,code_insee,comparaison,principales_composantes,controler_partition,
)

from shapely.geometry import box
from pyproj import Transformer


class AuditerGEOFLAMartiniqueTests(unittest.TestCase):
    def test_codes_attributaires(self):
        self.assertEqual(len(CODES),34)
        self.assertEqual(SCHEMA,"adlfi.lieux.martinique.audit.geofla2015-etalab2026.v1")
        self.assertEqual(code_insee({"INSEE_COM":"97209"}),("97209","INSEE_COM"))
        self.assertEqual(code_insee({"CODE_INSEE":"97234"}),("97234","CODE_INSEE"))
        self.assertEqual(code_insee({"CODE_INSEE":"97209","INSEE_COM":"97209"})[0],"97209")
        self.assertEqual(code_insee({"NOM_COM":"Fort-de-France"}),(None,None))
        self.assertEqual(code_insee({"CODE_INSEE":"97302"}),(None,None))
        self.assertEqual(code_insee({"CODE_INSEE":"97209","INSEE_COM":"97234"}),(None,None))

    def partition(self):
        a={c:box(i*1000,0,(i+1)*1000,1000) for i,c in enumerate(sorted(CODES))}
        b=dict(a)
        b["97201"]=box(-50,0,1100,1000)
        b["97202"]=box(1100,0,2000,1000)
        b["97234"]=box(33000,0,34025,1000)
        return a,b

    def test_decomposition_et_cloture_comptable(self):
        a,b=self.partition()
        proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
        r=comparaison(a,b,"2026",proj)
        self.assertEqual(r["communes"],34)
        self.assertAlmostEqual(r["ecart_emprise_exterieure_km2"],0.075,places=4)
        self.assertAlmostEqual(r["ecart_entre_codes_interieur_unique_km2"],0.1,places=4)
        self.assertAlmostEqual(r["cumul_ecarts_communaux_km2"],0.275,places=4)
        self.assertAlmostEqual(
            r["ecart_emprise_exterieure_km2"]+2*r["ecart_entre_codes_interieur_unique_km2"],
            r["cumul_ecarts_communaux_km2"],places=5)
        self.assertEqual(len(r["toutes_communes"]),34)
        self.assertTrue(r["composantes_exterieures"]["2015_hors_2026"]["plus_grandes"])

    def test_recouvrement_de_communes_refuse(self):
        a,b=self.partition()
        b["97203"]=box(1900,0,3000,1000)
        with self.assertRaisesRegex(ValueError,"recouvrement"):
            controler_partition(b,"source_invalide")

    def test_codes_incomplets_refuses(self):
        a,b=self.partition()
        a.pop("97201")
        with self.assertRaisesRegex(ValueError,"incomplets"):
            controler_partition(a,"source")

    def test_points_et_enveloppes_sans_geometrie(self):
        proj=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
        r=principales_composantes(box(0,0,300,300),proj,seuil_km2=0.01)
        self.assertEqual(r["composantes"],1)
        self.assertEqual(r["composantes_exportees"],1)
        c=r["plus_grandes"][0]
        self.assertAlmostEqual(c["aire_km2"],0.09)
        self.assertEqual(len(c["point_interieur_wgs84_lonlat"]),2)
        self.assertEqual(len(c["enveloppe_approximative_wgs84_lonlat"]),4)
        self.assertFalse(any(k in c for k in ("coordinates","geometry","polygon","wkt")))


if __name__=="__main__":
    unittest.main()
