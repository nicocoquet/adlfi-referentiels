"""Tests positifs/négatifs du JSON publié 1.55, et contrôle différentiel avec 1.54."""
import copy
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from scripts.recette_publication_organismes_155 import validate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "AdlFI_referentiel_1-55_A05C_GAVS_PRETECH_INRAP_CANDIDAT.xlsx"

class Publication155Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/data/organismes.json").read_text(encoding="utf-8"))

    def test_candidat(self):
        self.assertEqual(validate(self.data), [])

    def test_sha_bloquant(self):
        d = copy.deepcopy(self.data)
        d["provenance"]["source_sha256"] = "0"*64
        self.assertTrue(any("SHA-256" in x for x in validate(d)))

    def test_gavs_non_retrograde(self):
        d = copy.deepcopy(self.data)
        next(a for a in d["authorities"] if a["id"] == "ORG-0451")["validation"]["established"] = False
        self.assertTrue(any("GAVS" in x or "569" in x for x in validate(d)))

    def test_pretech_non_confondue_avec_temps(self):
        d = copy.deepcopy(self.data)
        next(a for a in d["authorities"] if a["id"] == "ORG-0348")["identifiers"]["lab"] = "UMR 8068"
        self.assertTrue(any("UMR 7055" in x for x in validate(d)))

    def test_aucune_tutelle_inventee(self):
        d = copy.deepcopy(self.data)
        d["relations"].append({"id": "REL-TEMP", "source": "ORG-0451",
                               "target": "ORG-0008", "type": "tutelle", "validation": "valide"})
        self.assertTrue(any("600 relations" in x or "GAVS" in x for x in validate(d)))

    @unittest.skipUnless(shutil.which("node"), "Node.js indisponible")
    def test_diff_strict_contre_154(self):
        result = subprocess.run(
            ["node", str(ROOT / "scripts/recette_organismes_155_diff.cjs"),
             str(ROOT / "docs/data/organismes.json")],
            cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)

if __name__ == "__main__":
    unittest.main()
