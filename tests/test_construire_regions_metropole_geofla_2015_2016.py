"""Tests hors réseau : fabrication de 96 départements synthétiques et 35 régions."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
try:
    from shapely.geometry import box
except ImportError:
    box = None  # La CI générale n'installe pas les dépendances SIG.

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from construire_regions_metropole_geofla_2015_2016 import (
    FUSIONS_2016, construire, exporter, mesurer
)

REGIONS_MAINTENUES = ("11", "24", "52", "53", "93", "94")


def corpus_synthetique():
    avant_apres = {old: new for new, parents in FUSIONS_2016.items() for old in parents}
    anciennes = sorted((*avant_apres, *REGIONS_MAINTENUES))
    assert len(anciennes) == 22 and len(set(anciennes)) == 22
    # 65 départements affectés aux 16 régions fusionnées et 31 aux
    # six régions maintenues : cardinalités identiques à l'audit national.
    repartition = (
        [sorted(avant_apres)[i % 16] for i in range(65)]
        + [REGIONS_MAINTENUES[i % 6] for i in range(31)]
    )
    ancien, nouveau = {}, {}
    for i, old in enumerate(repartition):
        dep = f"D{i:03d}"
        new = avant_apres.get(old, old)
        geometrie = box(i % 12, i // 12, i % 12 + 1, i // 12 + 1)
        ancien[dep] = (old, geometrie)
        nouveau[dep] = (new, geometrie)
    noms15 = {code: f"Région {code}" for code in anciennes}
    noms16 = {code: f"Région {code}" for code in set(avant_apres.values()) | set(REGIONS_MAINTENUES)}
    return ancien, nouveau, noms15, noms16


@unittest.skipUnless(box is not None, "Shapely réservé aux workflows SIG")
class RegionsMetropoleTests(unittest.TestCase):
    def test_35_regions_7_fusions_et_6_continuites(self):
        collections, comparaisons = construire(*corpus_synthetique())
        self.assertEqual(len(collections["2015"]["features"]), 22)
        self.assertEqual(len(collections["2016"]["features"]), 13)
        self.assertEqual(sum(v["nature"] == "fusion" for v in comparaisons), 7)
        self.assertEqual(sum(v["nature"] == "continuite" for v in comparaisons), 6)
        self.assertTrue(all(v["intersection_sur_union_pct"] == 100 for v in comparaisons))
        for year in ("2015", "2016"):
            features = collections[year]["features"]
            self.assertEqual(len({f["properties"]["code_region"] for f in features}), len(features))
            self.assertTrue(all(f["properties"]["millesime_COG"] == int(year) for f in features))
            self.assertTrue(all(not f["properties"]["contour_regional_natif"] for f in features))
            self.assertTrue(all(not f["properties"]["alignement_Pactols_valide"] for f in features))

    def test_erreur_rattachement_entre_deux_millesimes(self):
        d15, d16, n15, n16 = corpus_synthetique()
        code = next(iter(d16))
        d16[code] = ("93", d16[code][1])
        with self.assertRaisesRegex(ValueError, "Rattachement impossible"):
            construire(d15, d16, n15, n16)

    def test_departement_manquant(self):
        d15, d16, n15, n16 = corpus_synthetique()
        d15.pop(next(iter(d15)))
        with self.assertRaisesRegex(ValueError, "96 départements"):
            construire(d15, d16, n15, n16)

    def test_recouvrement_non_acceptable(self):
        d15, d16, n15, n16 = corpus_synthetique()
        code = next(iter(d16))
        old, geometry = d16[code]
        d16[code] = (old, box(1000, 1000, 1001, 1001))
        with self.assertRaisesRegex(ValueError, "Discordance spatiale majeure"):
            construire(d15, d16, n15, n16)

    def test_mesures_identite(self):
        a = box(0, 0, 1, 1)
        m = mesurer(a, a)
        self.assertEqual(m["intersection_sur_union_pct"], 100)
        self.assertEqual(m["difference_symetrique_km2"], 0)

    def test_reproduction_octet_et_veto_docs(self):
        collections, comparaisons = construire(*corpus_synthetique())
        rapport = {"statut": "RECETTE_NON_PUBLIEE", "alignements_Pactols_crees": 0}
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaisesRegex(ValueError, "docs"):
                exporter(collections, comparaisons, rapport, base / "docs" / "lieux")
            exporter(collections, comparaisons, rapport, base / "recette")
            exporter(collections, comparaisons, rapport, base / "reproduction")
            first = base / "recette"
            for file in first.iterdir():
                self.assertEqual(file.read_bytes(), (base / "reproduction" / file.name).read_bytes())
            self.assertEqual(len(list(first.glob("*.geojson"))), 2)
            self.assertEqual(len(json.loads((first / "regions-metropole-2016-IGN-geofla.geojson").read_text())["features"]), 13)


if __name__ == "__main__":
    unittest.main()
