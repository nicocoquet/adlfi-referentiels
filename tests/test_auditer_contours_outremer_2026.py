"""Tests sans réseau de l'audit de couverture géométrique ultramarine 2026."""
from __future__ import annotations

import csv
import gzip
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from auditer_contours_outremer_2026 import construire, cibles, qualifier

SHAPELY = importlib.util.find_spec("shapely") is not None


def ligne_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, delimiter=";", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def carre(code):
    return {
        "type": "Feature", "properties": {"code": code},
        "geometry": {"type": "Polygon", "coordinates": [
            [[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]]
        ]},
    }


def preparer(root):
    source = root / "sources"
    source.mkdir()
    ligne_csv(
        source / "v_commune_2026.csv",
        ["COM", "TYPECOM", "DEP", "LIBELLE"],
        [
            {"COM": "97607", "TYPECOM": "COM", "DEP": "976", "LIBELLE": "Dembeni"},
            {"COM": "75056", "TYPECOM": "COM", "DEP": "75", "LIBELLE": "Paris"},
        ],
    )
    ligne_csv(
        source / "v_commune_comer_2026.csv",
        ["COM_COMER", "COMER", "NATURE_ZONAGE", "LIBELLE"],
        [
            {"COM_COMER": "97501", "COMER": "975", "NATURE_ZONAGE": "COM",
             "LIBELLE": "Miquelon-Langlade"},
            {"COM_COMER": "98412", "COMER": "984", "NATURE_ZONAGE": "DIS",
             "LIBELLE": "Archipel des Kerguelen"},
        ],
    )
    ligne_csv(
        source / "v_comer_2026.csv",
        ["COMER", "LIBELLE"],
        [
            {"COMER": "975", "LIBELLE": "Saint-Pierre-et-Miquelon"},
            {"COMER": "984", "LIBELLE": "Terres australes et antarctiques françaises"},
        ],
    )
    geopath = root / "communes-100m.geojson.gz"
    with gzip.open(geopath, "wt", encoding="utf-8") as stream:
        json.dump({"type": "FeatureCollection",
                   "features": [carre("97607"), carre("97501")]},
                  stream)
    return source, geopath


class COGTypage(unittest.TestCase):
    def test_codes_distincts_et_nature_explicitement_conservee(self):
        drom = [{"TYPECOM": "COM", "DEP": "976", "COM": "97607", "LIBELLE": "Dembeni"}]
        comer = [{"NATURE_ZONAGE": "DIS", "COM_COMER": "98412",
                  "COMER": "984", "LIBELLE": "Kerguelen"}]
        terr = [{"COMER": "984", "LIBELLE": "TAAF"}]
        result = cibles(drom, comer, terr, strict=False)
        self.assertEqual({r["cle"] for r in result},
                         {"DROM:COM:97607", "COMER:DIS:98412",
                          "COMER:TERRITOIRE:984"})
        self.assertEqual(next(r["nature"] for r in result
                              if r["code"] == "98412"), "DIS")
        with self.assertRaisesRegex(ValueError, "Cardinalités"):
            cibles(drom, comer, terr, strict=True)

    def test_nature_non_documentee_refusee(self):
        with self.assertRaisesRegex(ValueError, "NATURE_ZONAGE"):
            cibles([], [{"NATURE_ZONAGE": "XXX", "COM_COMER": "98412",
                          "COMER": "984", "LIBELLE": "Inconnu"}],
                   [{"COMER": "984", "LIBELLE": "TAAF"}], strict=False)

    def test_subdivision_sans_parent_refusee(self):
        with self.assertRaisesRegex(ValueError, "sans collectivité"):
            cibles([], [{"NATURE_ZONAGE": "DIS", "COM_COMER": "98412",
                          "COMER": "984", "LIBELLE": "Kerguelen"}],
                   [], strict=False)


@unittest.skipUnless(SHAPELY, "Shapely nécessaire au contrôle géométrique")
class QualifGeom(unittest.TestCase):
    def test_production_repetable_et_non_publiante(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            src, geo = preparer(base)
            a = construire(src, geo, base / "a", strict=False)
            b = construire(src, geo, base / "b", strict=False)
            self.assertEqual(a, b)
            self.assertEqual(a["nombre_cibles"], 5)
            self.assertEqual(a["geometries_publiees"], 0)
            self.assertEqual(a["nouveaux_alignements_pactols"], 0)
            self.assertEqual(
                (base / "a" / "controle_233_cibles.csv").read_bytes(),
                (base / "b" / "controle_233_cibles.csv").read_bytes()
            )
            lignes = list(csv.DictReader(
                (base / "a" / "controle_233_cibles.csv").open(
                    encoding="utf-8-sig"), delimiter=";"
            ))
            stats = {r["cle"]: r for r in lignes}
            self.assertEqual(stats["DROM:COM:97607"]["statut"],
                             "PRESENTE_VALIDE_A_QUALIFIER")
            self.assertEqual(stats["COMER:COM:97501"]["statut"],
                             "PRESENTE_VALIDE_A_QUALIFIER")
            self.assertEqual(stats["COMER:DIS:98412"]["statut"],
                             "ABSENTE_DU_FICHIER_COMMUNES")
            self.assertEqual(stats["COMER:TERRITOIRE:984"]["statut"],
                             "NON_EVALUE_TERRITOIRE_SANS_COUCHE_DEDIEE")
            with self.assertRaisesRegex(ValueError, "docs"):
                construire(src, geo, base / "docs" / "sortie", strict=False)

    def test_doublon_et_antimeridien_signales(self):
        c = {"cle": "DROM:COM:97607", "code": "97607", "famille": "DROM",
             "nature": "COM", "parent": "976", "libelle_cog": "Dembeni"}
        self.assertEqual(qualifier(c, {"97607": [carre("97607"), carre("97607")]})
                         ["statut"], "DOUBLON_CODE_DANS_SOURCE")
        scene = carre("97607")
        scene["geometry"]["coordinates"] = [
            [[179, -10], [-179, -10], [-179, -9], [179, -9], [179, -10]]
        ]
        result = qualifier(c, {"97607": [scene]})
        self.assertEqual(result["alerte_antimeridien"], "A_CONTROLER")


if __name__ == "__main__":
    unittest.main()
