"""Contrats hors réseau de l'extraction des 2 644 communes normandes 2026."""
from __future__ import annotations
import csv
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import preparer_lieux_normandie_2026 as m  # noqa:E402


class NormandieCOGContours(unittest.TestCase):
    def test_region_code_et_provenance_epingles(self):
        self.assertEqual(m.REGION["normandie"]["reg"],"28")
        self.assertEqual(m.REGION["normandie"]["departements"],("14","27","50","61","76"))
        self.assertEqual(m.CODES_ATTENDUS,2644)
        self.assertEqual(m.SOURCE_SHA,"4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778")
        self.assertEqual(m.SOURCE_GEO,m.base.GEO_URL)

    def test_polygones_et_multipolygones_fermes(self):
        ring=[[-1.5,49.0],[-1.1,49.0],[-1.1,49.3],[-1.5,49.0]]
        p={"type":"Polygon","coordinates":[ring]}
        mp={"type":"MultiPolygon","coordinates":[[ring],[ring]]}
        self.assertEqual(m.verifier_geometrie(p),4)
        self.assertEqual(m.verifier_geometrie(mp),8)
        self.assertRaisesRegex(ValueError,"ouvert",
             m.verifier_geometrie,{"type":"Polygon","coordinates":[ring[:-1]]})
        self.assertRaisesRegex(ValueError,"non polygonale",
             m.verifier_geometrie,{"type":"Point","coordinates":[0,0]})
        self.assertRaisesRegex(ValueError,"hors emprise",
             m.verifier_geometrie,{"type":"Polygon","coordinates":[
                 [[-1.5,49],[9.0,49],[-1.1,49.3],[-1.5,49]]]})

    def test_reparation_cahagnes_sans_interpolation(self):
        ring=[[-1+i*.001,49+i*.0002] for i in range(64)]
        ring.append(ring[0])
        ring[14]=[-.7694,49.0457]
        ring[26]=[-.7694,49.0457]
        feat={"type":"Feature","properties":{"code":"14120"},
              "geometry":{"type":"Polygon","coordinates":[ring]}}
        result=m.reparer_cahagnes(feat)
        self.assertEqual(result["code"],"14120")
        self.assertFalse(result["interpolation"])
        self.assertFalse(result["lissage"])
        self.assertEqual(feat["geometry"]["type"],"MultiPolygon")
        polys=feat["geometry"]["coordinates"]
        self.assertEqual([len(p[0]) for p in polys],[13,53])
        self.assertEqual(polys[0][0][0],[-.7694,49.0457])
        self.assertEqual(polys[0][0][-1],[-.7694,49.0457])
        self.assertEqual(polys[1][0][0],polys[1][0][-1])
        feat["properties"]["code"]="99999"
        with self.assertRaisesRegex(ValueError,"réservée"):
            m.reparer_cahagnes(feat)

    def test_communes_selon_reg_pas_prefixe_seul(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"v_commune_2026.csv"
            with path.open("w",encoding="utf8",newline="") as f:
                w=csv.DictWriter(f,fieldnames=("TYPECOM","COM","LIBELLE","REG","DEP"))
                w.writeheader()
                w.writerows([
                    {"TYPECOM":"COM","COM":"14001","LIBELLE":"Une commune","REG":"28","DEP":"14"},
                    {"TYPECOM":"COM","COM":"27001","LIBELLE":"Autre commune","REG":"28","DEP":"27"},
                    {"TYPECOM":"COMD","COM":"14009","LIBELLE":"Déléguée","REG":"28","DEP":"14"},
                    {"TYPECOM":"COM","COM":"14003","LIBELLE":"Hors région","REG":"84","DEP":"14"},
                ])
            with patch.object(m,"sha",return_value=m.base.COG_SHA256["communes"]), \
                 patch.object(m,"CODES_ATTENDUS",2):
                self.assertEqual(m.courant_normand(path),{
                    "14001":"Une commune","27001":"Autre commune"})

    def test_doublon_cog_bloquant(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"v_commune_2026.csv"
            with path.open("w",encoding="utf8",newline="") as f:
                w=csv.DictWriter(f,fieldnames=("TYPECOM","COM","LIBELLE","REG","DEP"))
                w.writeheader()
                for _ in range(2):
                    w.writerow({"TYPECOM":"COM","COM":"14001","LIBELLE":"Doublon","REG":"28","DEP":"14"})
            with patch.object(m,"sha",return_value=m.base.COG_SHA256["communes"]), \
                 patch.object(m,"CODES_ATTENDUS",2):
                with self.assertRaisesRegex(ValueError,"Doublon"):
                    m.courant_normand(path)

    def test_regionalisation_normandie_seulement_en_2026(self):
        self.assertEqual(tuple(m.REGION),("normandie",))
        self.assertEqual(m.REGION["normandie"]["reg"],"28")
        self.assertEqual(m.base.SCHEMA,"adlfi.lieux.chronologie.4regions.public-recette.v1")


if __name__=="__main__":
    unittest.main()
