"""Contrats de validation éditoriale 2026 de neuf communes nouvelles normandes."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import valider_normandie_lot01_pactols_2026 as m  # noqa: E402

PUBLIC = ROOT / "docs/data/lieux-chronologie/pactols-normandie-lot01-2026.json"


def exemple_rapport():
    dossiers = []
    for code, spec in sorted(m.CASES.items()):
        candidats = []
        for ark in set((spec["ancien"], spec["actuel"])) - {None}:
            is_current = ark == spec["actuel"]
            if spec.get("cas_homonyme") and is_current:
                notes = [
                    {"type": "historyNote", "texte": (
                        "Création de la commune nouvelle de Pont-Audemer "
                        "[date d'effet : 2018-01-01]. (Insee)")},
                    {"type": "definition", "texte": "Pont-Audemer est une commune française."},
                ]
                extra = ["http://www.wikidata.org/entity/Q47067820"]
            elif spec.get("cas_homonyme"):
                notes = [{"type": "definition",
                          "texte": "Pont-Audemer est une ancienne commune française."}]
                extra = ["http://www.wikidata.org/entity/Q367667"]
            elif is_current and code == "27022":
                notes = [{"type": "definition",
                          "texte": "Le Val d'Hazey est, depuis le 1er janvier 2016, une commune nouvelle."}]
                extra = []
            elif is_current:
                notes = [{"type": "historyNote", "texte":
                          "Création de la commune nouvelle de " + spec["nom"] +
                          " [date d'effet : " + spec["date"] + "]. (Insee)"}]
                extra = []
            else:
                notes = [{"type": "historyNote",
                          "texte": spec["ancienne"] + " devient commune déléguée."}]
                extra = []
            candidates = {"ark": ark,
                          "classification": ("CANDIDAT_COMMUNE_NOUVELLE_2026_A_ARBITRER"
                            if is_current else "IDENTITE_ANCIENNE_COMMUNE_A_PRESERVER"),
                          "prefLabels_fr": [spec["nom"] if is_current else spec["ancienne"]],
                          "owl_deprecated": False, "dct_isReplacedBy": [],
                          "notes": notes,
                          "exactMatch": ["http://id.insee.fr/geo/commune/" + code] + extra}
            candidats.append(candidates)
        dossiers.append({
            "code_COG_2026": code, "nom_COG_2026": spec["nom"],
            "date_creation_INSEE": spec["date"], "source_INSEE":
                "https://www.insee.fr/fr/statistiques/2011101?geo=COM-" + code,
            "statut": ("INDECIDABLE_ARK_COMMUNE_ACTUELLE" if spec["actuel"] is None
                       else "CANDIDAT_EDITION_2026_SANS_PUBLICATION"),
            "decision_editoriale": "NON_PRISE",
            "nouveaux_alignements_publies": 0,
            "candidats_Pactols": candidats,
        })
    return {
        "schema": "adlfi.lieux.normandie.communes-nouvelles.lot01.2026.audit.v1",
        "statut": "RECETTE_NON_PUBLIANTE",
        "bilan": {"dossiers": 10, "candidats_Pactols": 19},
        "sources": {"rdf_Pactols_sha256": m.RDF_SHA},
        "dossiers": dossiers,
    }


class ValidationsNormandieLot01(unittest.TestCase):
    def test_registre_est_une_prepublication_non_active(self):
        doc = json.loads(PUBLIC.read_text(encoding="utf-8"))
        self.assertEqual(doc["schema"], m.SCHEMA)
        self.assertFalse(doc["active_dans_interface"])
        self.assertFalse(doc["couverture_region_entiere"])
        self.assertEqual(doc["nombre_communes"], 9)
        self.assertEqual(doc["communes_lot01_a_instruire"], 1)
        self.assertEqual(doc["nouvelles_geometries"], 0)
        self.assertEqual(doc["liens_historiques_inferes"], 0)
        codes = [x["code_insee"] for x in doc["alignements_Pactols_COG_valides_2026"]]
        self.assertEqual(codes, sorted(set(m.CASES) - {"50412"}))
        self.assertNotIn("50412", codes)
        self.assertTrue(all(x["millesime_validation"] == 2026
                            for x in doc["alignements_Pactols_COG_valides_2026"]))
        self.assertEqual(
            len({x["ark_pactols"] for x in doc["alignements_Pactols_COG_valides_2026"]}), 9)

    def test_construction_reproductible_concordante(self):
        doc = m.construire(exemple_rapport())
        published = json.loads(PUBLIC.read_text(encoding="utf-8"))
        self.assertEqual(doc, published)

    def test_ancien_ark_et_portbail_non_promus(self):
        doc = m.construire(exemple_rapport())
        for row in doc["alignements_Pactols_COG_valides_2026"]:
            self.assertNotEqual(row["ark_pactols"], row["ancien_ark_non_promu"])
        wrong = exemple_rapport()
        next(d for d in wrong["dossiers"] if d["code_COG_2026"] == "50412")[
            "statut"] = "CANDIDAT_EDITION_2026_SANS_PUBLICATION"
        with self.assertRaisesRegex(ValueError, "Port-Bail-sur-Mer"):
            m.construire(wrong)

    def test_pont_audemer_exige_deux_wikidata(self):
        data = exemple_rapport()
        case = next(x for x in data["dossiers"] if x["code_COG_2026"] == "27467")
        old = next(x for x in case["candidats_Pactols"]
                   if x["ark"] == m.CASES["27467"]["ancien"])
        old["exactMatch"].remove("http://www.wikidata.org/entity/Q367667")
        with self.assertRaisesRegex(ValueError, "Pont-Audemer"):
            m.construire(data)

    def test_creation_2016_doit_etre_attestee(self):
        data = exemple_rapport()
        case = next(x for x in data["dossiers"] if x["code_COG_2026"] == "50129")
        current = next(x for x in case["candidats_Pactols"]
                       if x["ark"] == m.CASES["50129"]["actuel"])
        current["notes"] = []
        with self.assertRaisesRegex(ValueError, "Création de commune nouvelle"):
            m.construire(data)


if __name__ == "__main__":
    unittest.main()
