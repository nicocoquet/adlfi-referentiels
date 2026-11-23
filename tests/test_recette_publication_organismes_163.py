
"""Recette AdlFI 1.63 : quatorze qualifications d'activité.

Comparaison stricte avec le JSON 1.62 publié,
au commit de référence immuable.
"""
import copy
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = 'c62987da745cab8289b7874f0f1c757c52d22855'

MASTER = (
    "AdlFI_referentiel_1-63_lot02_"
    "quatorze_activites_CANDIDAT.xlsx"
)
MASTER_SHA = (
    "2e268a62f160df289ce3b85e078ea01deb888e005408"
    "beaebc37811cc9c50ad6"
)
BASE_SHA = (
    "430cef30bd9aa2cd0a70e2b6c384f9cbc91cc7aca4e8"
    "d70b53de7a666645cc52"
)

IDS = (
    "ORG-0322", "ORG-0330", "ORG-0335",
    "ORG-0357", "ORG-0363", "ORG-0372",
    "ORG-0404", "ORG-0423", "ORG-0453",
    "ORG-0454", "ORG-0455", "ORG-0460",
    "ORG-0473", "ORG-0710",
)


def differences(before, after, path=()):
    if type(before) is not type(after):
        yield path, before, after
    elif isinstance(before, dict):
        for key in sorted(before.keys() | after.keys()):
            if key not in before or key not in after:
                yield path + (key,), before.get(key), after.get(key)
            else:
                yield from differences(
                    before[key], after[key], path + (key,)
                )
    elif isinstance(before, list):
        if len(before) != len(after):
            yield path + ("length",), len(before), len(after)
        for i, (a, b) in enumerate(zip(before, after)):
            yield from differences(a, b, path + (i,))
    elif before != after:
        yield path, before, after


class Publication163Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        raw = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:docs/data/organismes.json"],
            cwd=ROOT,
        )
        cls.before = json.loads(raw)
        cls.after = json.loads(
            (ROOT / "docs/data/organismes.json").read_text(
                encoding="utf-8"
            )
        )
        cls.old = {
            a["id"]: a for a in cls.before["authorities"]
        }
        cls.new = {
            a["id"]: a for a in cls.after["authorities"]
        }

    def expected_paths(self):
        index = {
            a["id"]: i
            for i, a in enumerate(self.before["authorities"])
        }
        paths = {
            ("provenance", "source_filename"),
            ("provenance", "source_sha256"),
        }
        for ident in IDS:
            i = index[ident]
            paths.add(("authorities", i, "activity", "active"))
            paths.add(
                ("authorities", i, "quality", "activity_unknown")
            )
        return paths

    def test_provenance(self):
        self.assertEqual(
            self.before["provenance"]["source_sha256"],
            BASE_SHA,
        )
        self.assertEqual(
            self.after["provenance"]["source_filename"],
            MASTER,
        )
        self.assertEqual(
            self.after["provenance"]["source_sha256"],
            MASTER_SHA,
        )

    def test_effectifs_et_relations(self):
        d = self.after
        self.assertEqual(len(d["authorities"]), 935)
        self.assertEqual(len(d["relations"]), 600)
        self.assertEqual(d["totals"]["organismes"], 735)
        self.assertEqual(d["totals"]["services"], 200)
        self.assertEqual(d["totals"]["catalog_included"], 683)
        self.assertEqual(d["totals"]["catalog_excluded"], 252)
        self.assertEqual(
            {
                value: sum(
                    a["activity"]["active"] is value
                    for a in d["authorities"]
                )
                for value in (True, False, None)
            },
            {True: 741, False: 142, None: 52},
        )

    def test_quatorze_qualifications(self):
        self.assertEqual(len(IDS), 14)
        self.assertEqual(len(set(IDS)), 14)

        for ident in IDS:
            with self.subTest(ident=ident):
                self.assertIn(ident, self.old)
                self.assertIn(ident, self.new)
                self.assertIsNone(
                    self.old[ident]["activity"]["active"]
                )
                self.assertIs(
                    self.new[ident]["activity"]["active"],
                    True,
                )
                self.assertIs(
                    self.old[ident]["quality"]["activity_unknown"],
                    True,
                )
                self.assertIs(
                    self.new[ident]["quality"]["activity_unknown"],
                    False,
                )

    def test_trente_differences_exactes(self):
        found = list(differences(self.before, self.after))
        expected = self.expected_paths()

        self.assertEqual(len(found), 30)
        self.assertEqual(
            {path for path, _, _ in found},
            expected,
        )

    def test_mutation_institutionnelle_interdite(self):
        modified = copy.deepcopy(self.after)
        modified["relations"][0]["type"] = "autre"

        found = {
            path
            for path, _, _ in differences(self.before, modified)
        }
        self.assertNotEqual(found, self.expected_paths())
        self.assertTrue(
            any(path[0] == "relations" for path in found)
        )


if __name__ == "__main__":
    unittest.main()
