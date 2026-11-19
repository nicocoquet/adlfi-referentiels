"""Contrats de l'audit régional 2026 et du croisement AdlFI non publiant."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from auditer_pactols_cog_region_metropolitaine_2026 import (  # noqa: E402
    REGIONS, communes_region, croiser_corpus, write_result,
)


class TestRegionMetropolitaine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def csv(self, name, fields, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
        return path

    def report(self):
        return {
            "region": "Normandie", "code_region_COG_2026": "28",
            "communes": [
                {"code": "14001", "statut_candidat": "ELIGIBLE_SELON_REGLE",
                 "preuves_RDF_exactMatch": [{"ark": "26678/pcrtABC"}]},
                {"code": "14002", "statut_candidat": "A_INSTRUIRE_PLUSIEURS_ARK",
                 "preuves_RDF_exactMatch": [{"ark": "26678/pcrtDEF"}]},
            ],
        }

    def fixtures(self):
        auth = self.csv("autorites.csv",
            ["ark_pactols", "nombre_occurrences", "nombre_notices_distinctes"],
            [{"ark_pactols": "26678/pcrtABC", "nombre_occurrences": "2",
              "nombre_notices_distinctes": "2"},
             {"ark_pactols": "26678/pcrtDEF", "nombre_occurrences": "1",
              "nombre_notices_distinctes": "1"},
             {"ark_pactols": "26678/pcrtGHI", "nombre_occurrences": "1",
              "nombre_notices_distinctes": "1"}])
        norm = json.dumps(["Europe", "France", "France métropolitaine",
                           "Normandie", "Département du Calvados", "Une commune"])
        other = json.dumps(["Europe", "France", "France métropolitaine",
                            "Bretagne", "Département du Finistère", "Une commune"])
        occurrences = self.csv("occurrences.csv",
            ["ark_terminal", "notice_id", "chaine_libelles_fr"],
            [{"ark_terminal": "26678/pcrtABC", "notice_id": "notice-1", "chaine_libelles_fr": norm},
             {"ark_terminal": "26678/pcrtABC", "notice_id": "notice-2", "chaine_libelles_fr": norm},
             {"ark_terminal": "26678/pcrtDEF", "notice_id": "notice-2", "chaine_libelles_fr": norm},
             {"ark_terminal": "26678/pcrtGHI", "notice_id": "notice-3", "chaine_libelles_fr": other}])
        return auth, occurrences

    def test_croisement_et_protection_sources_privees(self):
        auth, occurrences = self.fixtures()
        result = croiser_corpus(self.report(), auth, occurrences)
        self.assertEqual(result["autorites_terminales_dans_region"], 2)
        self.assertEqual(result["occurrences_dans_region"], 3)
        self.assertEqual(result["notices_distinctes_dans_region"], 2)
        self.assertEqual(result["autorites_par_statut"], {
            "EXACTMATCH_COG_2026_A_INSTRUIRE": 1,
            "EXACTMATCH_UNIVOQUE_ELIGIBLE_SELON_REGLE": 1,
        })
        self.assertEqual(result["occurrences_par_statut"][
            "EXACTMATCH_UNIVOQUE_ELIGIBLE_SELON_REGLE"], 2)
        serial = json.dumps(result)
        self.assertNotIn("26678/pcrtABC", serial)
        self.assertNotIn("notice-1", serial)

    def test_autorite_incoherente_rejetee(self):
        auth, occurrences = self.fixtures()
        original = auth.read_text(encoding="utf-8")
        auth.write_text(original.replace(";2;2", ";3;2"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "incohérent"):
            croiser_corpus(self.report(), auth, occurrences)

    def test_codes_officiels_region(self):
        self.assertEqual(REGIONS["28"], "Normandie")
        self.assertEqual(REGIONS["84"], "Auvergne-Rhône-Alpes")
        bad = self.root / "cog.csv"
        bad.write_text("TYPECOM,COM,LIBELLE,REG,DEP\nCOM,14001,Commune,28,14\n",
                       encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Empreinte"):
            communes_region(bad, "28")

    def test_acquisition_communes_seulement_sans_sources_historiques(self):
        import hashlib
        from unittest.mock import patch
        import recuperer_cog_communes_2026 as acquisition
        raw = b"TYPECOM,COM,LIBELLE,REG,DEP\\nCOM,14001,Commune,28,14\\n"
        with patch.dict(acquisition.EXPECTED,
                        {"v_commune_2026.csv": hashlib.sha256(raw).hexdigest()},
                        clear=True):
            with patch.object(acquisition, "get", return_value=raw) as download:
                result = acquisition.collecter(self.root / "cog")
                self.assertEqual(set(result["fichiers"]), {"v_commune_2026.csv"})
                self.assertEqual((self.root / "cog" / "v_commune_2026.csv").read_bytes(), raw)
                self.assertEqual(download.call_count, 1)
        with self.assertRaises(KeyError):
                with patch.dict(acquisition.EXPECTED, {}, clear=True):
                    acquisition.collecter(self.root / "cog2")

    def test_sorties_hors_docs_et_sans_ecrasement(self):
        out = self.root / "rapport.json"
        write_result(out, {"status": "RECETTE"})
        with self.assertRaisesRegex(ValueError, "Sortie existante"):
            write_result(out, {"status": "RECETTE"})
        with self.assertRaisesRegex(ValueError, "hors docs"):
            write_result(self.root / "docs" / "publie.json", {"status": "RECETTE"})


if __name__ == "__main__":
    unittest.main()
