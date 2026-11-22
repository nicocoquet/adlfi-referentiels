"""Organismes 1.62 : huit statuts d'association, écart strict contre 1.61.

Tests bloquants : intégrité du catalogue, identité des autorités corrigées,
absence de toute modification hors des 8 statuts, indicateurs et provenance.
"""
from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "f319a8a0e0a2187656ff5f1bf7758fe30c4e05e3"
SOURCE = "AdlFI_referentiel_1-62_lot01_huit_associations_CANDIDAT.xlsx"
SHA = "430cef30bd9aa2cd0a70e2b6c384f9cbc91cc7aca4e8d70b53de7a666645cc52"

IDS = (
    "ORG-0176", "ORG-0231", "ORG-0321", "ORG-0341",
    "ORG-0422", "ORG-0496", "ORG-0524", "ORG-0525",
)
RESERVED = ("ORG-0212", "ORG-0342", "ORG-0355")


def differences(old, new, path=()):
    if type(old) is not type(new):
        yield path, old, new
    elif isinstance(old, dict):
        for key in sorted(old.keys() | new.keys()):
            if key not in old or key not in new:
                yield path + (key,), old.get(key), new.get(key)
            else:
                yield from differences(old[key], new[key], path + (key,))
    elif isinstance(old, list):
        if len(old) != len(new):
            yield path + ("length",), len(old), len(new)
        for i, (x, y) in enumerate(zip(old, new)):
            yield from differences(x, y, path + (i,))
    elif old != new:
        yield path, old, new


class Publication162Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = json.loads((ROOT / "docs/data/organismes.json").read_text(encoding="utf-8"))
        p = subprocess.run(
            ["git", "show", f"{BASE}:docs/data/organismes.json"],
            cwd=ROOT, capture_output=True, check=True,
        )
        cls.base = json.loads(p.stdout)
        cls.before = {a["id"]: a for a in cls.base["authorities"]}
        cls.after = {a["id"]: a for a in cls.current["authorities"]}

    def test_provenance_exacte(self):
        p = self.current["provenance"]
        self.assertEqual((p["source_filename"], p["source_sha256"]), (SOURCE, SHA))
        self.assertEqual(p["exported_at_utc"], "2026-11-22T00:00:00+00:00")

    def test_invariants_institutionnels(self):
        data = self.current
        self.assertEqual(list(self.before), list(self.after))
        self.assertEqual(len(data["authorities"]), 935)
        self.assertEqual(len(data["relations"]), 600)
        self.assertEqual(
            (data["totals"]["authorities"], data["totals"]["organismes"],
             data["totals"]["services"], data["totals"]["catalog_included"],
             data["totals"]["catalog_excluded"]),
            (935, 735, 200, 683, 252),
        )
        self.assertEqual(
            {value: sum(a["activity"]["active"] is value for a in data["authorities"])
             for value in (True, False, None)},
            {True: 727, False: 142, None: 66},
        )

    def test_huit_associations_actives(self):
        for ident in IDS:
            with self.subTest(ident=ident):
                a = self.after[ident]
                self.assertEqual(a["classification"]["type"], "association")
                self.assertIsNone(self.before[ident]["activity"]["active"])
                self.assertIs(a["activity"]["active"], True)
                self.assertIs(self.before[ident]["quality"]["activity_unknown"], True)
                self.assertIs(a["quality"]["activity_unknown"], False)

    def test_trois_reserves_non_modifiees(self):
        for ident in RESERVED:
            with self.subTest(ident=ident):
                self.assertEqual(self.before[ident], self.after[ident])
                self.assertIsNone(self.after[ident]["activity"]["active"])

    def test_differences_exclusivement_autorisees(self):
        idx = {a["id"]: i for i, a in enumerate(self.base["authorities"])}
        expected = {
            ("provenance", "source_filename"),
            ("provenance", "source_sha256"),
        }
        for ident in IDS:
            i = idx[ident]
            expected.add(("authorities", i, "activity", "active"))
            expected.add(("authorities", i, "quality", "activity_unknown"))
        found = list(differences(self.base, self.current))
        self.assertEqual(len(found), 18)
        self.assertEqual({p for p, _, _ in found}, expected)

    def test_mutation_etrangere_bloquee(self):
        modified = copy.deepcopy(self.current)
        modified["relations"][0]["type"] = "autre"
        idx = {a["id"]: i for i, a in enumerate(self.base["authorities"])}
        expected = {("provenance", "source_filename"), ("provenance", "source_sha256")}
        for ident in IDS:
            i = idx[ident]
            expected.add(("authorities", i, "activity", "active"))
            expected.add(("authorities", i, "quality", "activity_unknown"))
        found = {p for p, _, _ in differences(self.base, modified)}
        self.assertNotEqual(found, expected)
        self.assertTrue(any(p[0] == "relations" for p in found))


if __name__ == "__main__":
    unittest.main()
