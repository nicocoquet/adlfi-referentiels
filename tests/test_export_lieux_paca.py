"""Contrat de publication Pactols–COG PACA : aucun alignement implicite."""
import csv
import io
import json
import unittest
from pathlib import Path

from scripts.export_lieux_paca import (
    STATUS_VALID, SOURCE_CSV_BLOB, SOURCE_GEO_BLOB,
    construire, serialiser,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data/lieux.json"
GEO = ROOT / "docs/data/lieux-communes.geojson"

HEADER = [
    "ark_pactols", "libelle_pactols", "type_entite",
    "code_cog_propose", "libelle_cog_propose", "code_cog_valide",
    "statut_validation", "relation", "source_controle", "millesime_cog",
]


def entree(ark, nom, code, *, statut=STATUS_VALID):
    return dict(
        ark_pactols=ark, libelle_pactols=nom, type_entite="commune",
        code_cog_propose=code, libelle_cog_propose=nom,
        code_cog_valide=(code if statut == STATUS_VALID else ""),
        statut_validation=statut,
        relation=("correspondance_communale_validee" if statut == STATUS_VALID
                  else "correspondance_communale_proposee"),
        source_controle="Validation éditoriale en conversation + INSEE COG 2026",
        millesime_cog="2026",
    )


def csv_source(rows):
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=HEADER, delimiter=";", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return f.getvalue().encode("utf-8")


def feature(code, nom, *, region="93"):
    return {
        "type": "Feature",
        "properties": {
            "code": code, "nom": nom, "departement": code[:2],
            "region": region, "epci": "",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[5.0, 44.0], [5.1, 44.0],
                             [5.1, 44.1], [5.0, 44.0]]],
        },
    }


def geo_source(features):
    return json.dumps({"type": "FeatureCollection", "features": features},
                      ensure_ascii=False).encode("utf-8")


class PublicationLieuxPACA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lieux = json.loads(DATA.read_text(encoding="utf-8"))
        cls.geo = json.loads(GEO.read_text(encoding="utf-8"))
        cls.arks = {r["ark_pactols"] for r in cls.lieux["autorites"]}
        cls.codes = {r["correspondances"][0]["code_insee"]
                     for r in cls.lieux["autorites"]}

    def test_provenance_et_contrat(self):
        self.assertEqual(self.lieux["schema_version"], "0.1.0")
        self.assertEqual(self.lieux["module"], "lieux")
        self.assertEqual(self.lieux["perimetre"], "PACA")
        self.assertEqual(self.lieux["statut_publication"], "pilote_valide")
        self.assertEqual(self.lieux["provenance"]["millesime_cog"], 2026)
        self.assertEqual(self.lieux["provenance"]["validation_editoriale"], "2026-10-18")
        self.assertEqual(self.lieux["provenance"]["autorites"]["git_blob_sha"], SOURCE_CSV_BLOB)
        self.assertEqual(self.lieux["provenance"]["geometries"]["git_blob_sha"], SOURCE_GEO_BLOB)
        self.assertEqual(self.geo["metadata"]["source"]["git_blob_sha"], SOURCE_GEO_BLOB)

    def test_exactement_103_autorites_validees_sans_doublon(self):
        self.assertEqual(len(self.lieux["autorites"]), 103)
        self.assertEqual(len(self.arks), 103)
        self.assertEqual(len(self.codes), 103)
        self.assertEqual(self.lieux["totaux"], {
            "autorites_pactols": 103, "communes_cog": 103,
            "geometries": 103, "lignes_source": 218,
            "lignes_non_validees_exclues": 115,
        })
        for row in self.lieux["autorites"]:
            self.assertEqual(row["type_entite"], "commune")
            self.assertEqual(len(row["correspondances"]), 1)
            lien = row["correspondances"][0]
            self.assertEqual(lien["referentiel"], "COG")
            self.assertEqual(lien["millesime_cog"], 2026)
            self.assertEqual(lien["relation_editoriale"],
                             "correspondance_communale_validee")
            self.assertEqual(lien["validation"]["statut"], STATUS_VALID)
            self.assertEqual(lien["validation"]["date"], "2026-10-18")
            self.assertTrue(lien["validation"]["source"])
            self.assertIn(lien["departement"], {"04", "05", "06", "13", "83", "84"})
            self.assertEqual(lien["region"], "93")

    def test_geometries_exactement_alignees_sur_les_codes_valides(self):
        features = self.geo["features"]
        self.assertEqual(self.geo["type"], "FeatureCollection")
        self.assertEqual(len(features), 103)
        self.assertEqual(
            {r["properties"]["code"] for r in features}, self.codes)
        self.assertEqual(
            {r["properties"]["ark_pactols"] for r in features}, self.arks)
        self.assertTrue(all(r["geometry"]["coordinates"] for r in features))
        self.assertTrue(all(r["properties"]["region"] == "93" for r in features))
        self.assertEqual(
            len({r["properties"]["code"] for r in features}), 103)

    def test_non_publication_des_trois_cas_paca_provisoires(self):
        codes = self.codes
        self.assertTrue(codes.isdisjoint({"06088", "13055", "83069"}))
        self.assertTrue(
            all(r["properties"]["code"] not in {"06088", "13055", "83069"}
                for r in self.geo["features"]))

    def test_export_synthetique_ecarte_les_propositions(self):
        rows = [
            entree("26678/pcrtTestA", "Lieu A", "04001"),
            entree("26678/pcrtTestB", "Lieu B", "05001"),
            entree("26678/pcrtTestC", "Lieu C", "06001",
                   statut="REVU_EDITEUR_A_DOCUMENTER"),
        ]
        geo = [feature("04001", "Lieu A"), feature("05001", "Lieu B"),
               feature("06001", "Lieu C")]
        lieux, geoms = construire(csv_source(rows), geo_source(geo),
                                 verification_sources=False, effectif_attendu=2)
        self.assertEqual(len(lieux["autorites"]), 2)
        self.assertEqual(len(geoms["features"]), 2)
        self.assertEqual(lieux["totaux"]["lignes_non_validees_exclues"], 1)
        self.assertNotIn("06001", {f["properties"]["code"] for f in geoms["features"]})
        self.assertEqual(serialiser(lieux), serialiser(lieux))

    def test_rejete_une_source_non_epinglee(self):
        with self.assertRaisesRegex(ValueError, "Source"):
            construire(b"autre CSV", b"autre GeoJSON")

    def test_rejete_une_geometrie_absente(self):
        rows = [entree("26678/pcrtTestA", "Lieu A", "04001")]
        with self.assertRaisesRegex(ValueError, "Géométrie absente"):
            construire(csv_source(rows), geo_source([feature("04002", "Lieu X")]),
                       verification_sources=False, effectif_attendu=1)

    def test_rejete_doublons_et_alignements_non_valides(self):
        a = entree("26678/pcrtTestA", "Lieu A", "04001")
        b = entree("26678/pcrtTestA", "Lieu B", "05001")
        geo = geo_source([feature("04001", "Lieu A"), feature("05001", "Lieu B")])
        with self.assertRaisesRegex(ValueError, "ARK.*dupliqué"):
            construire(csv_source([a, b]), geo,
                       verification_sources=False, effectif_attendu=2)
        b["ark_pactols"] = "26678/pcrtTestB"
        b["code_cog_valide"] = "04001"
        b["code_cog_propose"] = "04001"
        with self.assertRaisesRegex(ValueError, "Code COG.*dupliqué"):
            construire(csv_source([a, b]), geo,
                       verification_sources=False, effectif_attendu=2)
        b["code_cog_valide"] = "05001"
        b["code_cog_propose"] = "05001"
        b["relation"] = "correspondance_communale_proposee"
        with self.assertRaisesRegex(ValueError, "Qualification éditoriale"):
            construire(csv_source([a, b]), geo,
                       verification_sources=False, effectif_attendu=2)

    def test_rejete_statut_inconnu_et_geometrie_hors_region(self):
        row = entree("26678/pcrtTestA", "Lieu A", "04001")
        row["statut_validation"] = "VALIDATION_AUTOMATIQUE"
        with self.assertRaisesRegex(ValueError, "Statuts éditoriaux inconnus"):
            construire(csv_source([row]), geo_source([feature("04001", "Lieu A")]),
                       verification_sources=False, effectif_attendu=1)
        row["statut_validation"] = STATUS_VALID
        with self.assertRaisesRegex(ValueError, "hors PACA"):
            construire(csv_source([row]),
                       geo_source([feature("04001", "Lieu A", region="84")]),
                       verification_sources=False, effectif_attendu=1)


if __name__ == "__main__":
    unittest.main()
