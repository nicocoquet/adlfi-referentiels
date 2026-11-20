"""Non-régressions du premier lot d'identités normandes Pactols–COG 2026."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import auditer_normandie_lot01_identites_2026 as audit  # noqa: E402


def preuve(code, ark, label):
    return {
        "ark": ark, "prefLabels_fr": [label], "altLabels_fr": [],
        "deprecie": False, "insee_exactMatch": [{
            "famille": "commune", "code": code,
            "uri": "http://id.insee.fr/geo/commune/" + code,
        }], "codes_communaux_cites": [code],
    }


def details(label):
    return {
        "prefLabels_fr": [label], "altLabels_fr": [],
        "owl_deprecated": False, "dct_isReplacedBy": [],
        "dct_replaces": [], "notes": [], "exactMatch": [],
    }


class Lot01NormandieTests(unittest.TestCase):
    def test_codes_et_arks_figes_par_le_preflight(self):
        self.assertEqual(len(audit.CASES), 10)
        self.assertEqual(sum(len(audit.arks_attendus(c)) for c in audit.CASES), 19)
        self.assertEqual(audit.CASES["50412"]["actuel"], None)
        self.assertTrue(audit.CASES["27467"]["cas_homonyme"])
        self.assertEqual(audit.CASES["27467"]["actuel"], "26678/pcrttaqrTGrSS9")
        self.assertEqual(audit.CASES["50129"]["date"], "2016-01-01")
        self.assertEqual(audit.CASES["61194"]["date"], "2018-01-01")
        self.assertEqual(audit.CASES["14456"]["date"], "2017-01-01")

    def test_anciennes_identites_non_promues_et_homonymie_bloquee(self):
        for code, spec in audit.CASES.items():
            d = details(spec["ancienne"])
            if spec.get("cas_homonyme"):
                d["exactMatch"] = ["http://www.wikidata.org/entity/Q367667"]
                d["notes"] = [{"type": "definition", "texte": "Pont-Audemer est une ancienne commune française"}]
            self.assertIn(
                audit.classer(code, spec["ancien"], d),
                {"IDENTITE_ANCIENNE_COMMUNE_A_PRESERVER",
                 "ANCIENNE_COMMUNE_DELEGUEE_IDENTIFIEE"},
            )
            if spec["actuel"]:
                current = details(spec["nom"])
                if spec.get("cas_homonyme"):
                    current["exactMatch"] = ["http://www.wikidata.org/entity/Q47067820"]
                    current["notes"] = [{"type": "definition", "texte": "Pont-Audemer est une commune française"}]
                self.assertEqual(
                    audit.classer(code, spec["actuel"], current),
                    "CANDIDAT_COMMUNE_NOUVELLE_2026_A_ARBITRER",
                )
        self.assertEqual(
            audit.classer("27467", "26678/pcrttaqrTGrSS9", details("Pont-Audemer")),
            "HOMONYMIE_PERSISTANTE_A_INSTRUIRE",
        )  # Pas de promotion sans URI Wikidata + définition explicite.
        wrong_q = details("Pont-Audemer")
        wrong_q["exactMatch"] = ["http://www.wikidata.org/entity/Q367667"]
        wrong_q["notes"] = [{"type": "definition", "texte": "Pont-Audemer est une commune française"}]
        self.assertEqual(
            audit.classer("27467", "26678/pcrttaqrTGrSS9", wrong_q),
            "HOMONYMIE_PERSISTANTE_A_INSTRUIRE",
        )
        dep = details("Vire Normandie")
        dep["owl_deprecated"] = True
        self.assertEqual(
            audit.classer("14762", "26678/pcrt78ZZg0wMbU", dep),
            "A_INSTRUIRE_CONCEPT_REMPLACE",
        )

    def fabriquer_preuves(self):
        hits = {}
        metadata = {}
        for code, spec in audit.CASES.items():
            rows = []
            for ark in sorted(audit.arks_attendus(code)):
                if spec.get("cas_homonyme"):
                    label = ("Pont-Audemer (commune déléguée)" if ark == spec["ancien"]
                             else "Pont-Audemer")
                else:
                    label = spec["nom"] if ark == spec["actuel"] else spec["ancienne"]
                rows.append(preuve(code, ark, label))
                metadata[ark] = details(label)
                if spec.get("cas_homonyme"):
                    if ark == spec["actuel"]:
                        metadata[ark]["exactMatch"] = ["http://www.wikidata.org/entity/Q47067820"]
                        metadata[ark]["notes"] = [{"type": "definition", "texte": "Pont-Audemer est une commune française"}]
                    else:
                        metadata[ark]["exactMatch"] = ["http://www.wikidata.org/entity/Q367667"]
                        metadata[ark]["notes"] = [{"type": "definition", "texte": "Pont-Audemer est une ancienne commune française"}]
            hits[code] = rows
        return hits, metadata

    def test_dix_dossiers_auditables_sans_publication(self):
        hits, metadata = self.fabriquer_preuves()
        with patch.object(audit, "sha256", return_value=audit.RDF_SHA), \
             patch.object(audit, "analyser_rdf", return_value={"explicites": hits}), \
             patch.object(audit, "rdf_complementaire", return_value=metadata):
            result = audit.produire(Path("fiction-rdf.xml"))
        self.assertEqual(result["bilan"]["dossiers"], 10)
        self.assertEqual(result["bilan"]["candidats_Pactols"], 19)
        self.assertEqual(result["bilan"]["codes_avec_candidat_distinct_commune_actuelle"], 9)
        self.assertEqual(result["bilan"]["codes_sans_arbitrage_identite_actuelle"], 1)
        self.assertEqual(result["bilan"]["nouvelles_validations_publiees"], 0)
        self.assertEqual(result["bilan"]["limites_historiques_inferrees"], 0)
        self.assertTrue(all(
            d["decision_editoriale"] == "NON_PRISE" and
            d["nouveaux_alignements_publies"] == 0
            for d in result["dossiers"]
        ))
        public = json.dumps(result)
        self.assertNotIn("notice_id", public)
        self.assertNotIn("fichier_relatif", public)

    def test_modification_des_preuves_bloquante(self):
        hits, metadata = self.fabriquer_preuves()
        hits["50129"].pop()
        with patch.object(audit, "sha256", return_value=audit.RDF_SHA), \
             patch.object(audit, "analyser_rdf", return_value={"explicites": hits}), \
             patch.object(audit, "rdf_complementaire", return_value=metadata):
            with self.assertRaisesRegex(ValueError, "Changement des ARK concurrents"):
                audit.produire(Path("fiction-rdf.xml"))

    def test_rdf_mauvaise_empreinte_refuse(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "wrong.rdf"
            path.write_text("pas un RDF", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "snapshot"):
                audit.produire(path)


if __name__ == "__main__":
    unittest.main()
