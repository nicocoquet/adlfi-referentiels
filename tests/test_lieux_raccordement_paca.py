"""Non-régression des limites du module Lieux : Marseille et voisinage PACA.

La référence vient du fichier "communes-1000m.geojson" (106 communes) utilisé
pour l'export des 103 communes du pilote Lieux. Marseille fait partie des
trois communes exclues pour défaut de validation éditoriale Pactols–COG,
mais sa géométrie est conservée comme témoin de raccordement.
Aucune dépendance géospatiale externe nécessaire.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "docs/lieux/references/marseille-13055-source-paca-2026.geojson"
ARM_PARENTS = ROOT / "docs/data/lieux-communes-plm-reconstituees.geojson"
PACA = ROOT / "docs/data/lieux-communes.geojson"


def charger(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def anneaux(geometry):
    geom_type = geometry["type"]
    if geom_type == "Polygon":
        return geometry["coordinates"]
    if geom_type == "MultiPolygon":
        return [r for poly in geometry["coordinates"] for r in poly]
    raise ValueError("Seuls Polygon et MultiPolygon sont admis : " + geom_type)


def segment(a, b):
    """Coordonnées source conservées à 4 décimales (arrondi de calcul géométrique)."""
    def cle(coord):
        return f"{coord[0]:.4f},{coord[1]:.4f}"
    p, q = cle(a), cle(b)
    return (p, q) if p < q else (q, p)


def segments(geometry):
    result = set()
    for ring in anneaux(geometry):
        if ring[0] != ring[-1]:
            # Le calcul de l'union a parfois un bruit flottant de ~1e-14.
            if segment(ring[0], ring[-1])[0] != segment(ring[0], ring[-1])[1]:
                raise ValueError("Anneau non fermé")
        for a, b in zip(ring, ring[1:]):
            result.add(segment(a, b))
    return result


class RaccordementPilotePaca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = charger(REF)
        cls.parents = charger(ARM_PARENTS)
        cls.paca = charger(PACA)
        cls.marseille_source = cls.reference["features"][0]
        cls.marseille_derivee = next(
            f for f in cls.parents["features"]
            if f["properties"]["code_commune"] == "13055"
        )
        cls.bordure = segments(cls.marseille_derivee["geometry"])

    def test_provenance_du_temoin(self):
        metadata = self.reference["metadata"]
        self.assertEqual(metadata["source_commit"], "bc0455c7d1dbf65f579e9b25a01eb7928a8054d5")
        self.assertEqual(metadata["source_blob_sha"], "0525607f277ec4c915a3e3273e716a5b1f1108d5")
        self.assertEqual(self.marseille_source["properties"]["code"], "13055")

    def test_compatibilite_bordure_marseille(self):
        temoin = segments(self.marseille_source["geometry"])
        self.assertEqual(len(temoin), 318)
        self.assertEqual(self.bordure, temoin)

    def test_raccordement_avec_communes_voisines_exposees(self):
        voisins = {
            "13005": ("Aubagne", 18),
            "13002": ("Allauch", 13),
        }
        by_code = {str(f["properties"]["code"]): f for f in self.paca["features"]}
        for code, (nom, nombre) in voisins.items():
            with self.subTest(commune=nom):
                self.assertIn(code, by_code)
                touches = self.bordure & segments(by_code[code]["geometry"])
                self.assertEqual(len(touches), nombre)

    def test_pilotage_des_sources_sans_affirmer_une_validation_editoriale(self):
        self.assertEqual(self.paca["metadata"]["millesime_cog"], 2026)
        self.assertEqual(self.reference["metadata"]["millesime"], 2026)
        self.assertEqual(self.parents["metadata"]["nature"], "geometrie_derivee")
        self.assertEqual(
            self.parents["metadata"]["validation_independante"], "non_effectuee"
        )


if __name__ == "__main__":
    unittest.main()
