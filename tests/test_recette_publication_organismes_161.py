"""Recette 1.61 : sept activités et la création de CARA, sans autre modification.

Compare exhaustivement le JSON proposé au commit fusionné de publication 1.60.
Les indicateurs quality dérivés font partie des changements autorisés.
"""
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "8dbac1ed2afe0e7a65022da8f332d0338f54bc3b"
SOURCE = "AdlFI_referentiel_1-61_lot01_activites_et_date_CANDIDAT.xlsx"
SHA = "fb475d0270ca74757c7d34dc97978897dccdf5b12cc10c2ec8aa3f35a65e8b98"
ACTIVE = ("ORG-0349", "ORG-0438", "ORG-0468", "ORG-0494", "ORG-0716", "SER-0195")
INACTIVE = "ORG-0375"
DATING = "SER-0193"


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


class Publication161Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/data/organismes.json").read_text(encoding="utf-8"))
        proc = subprocess.run(
            ["git", "show", f"{BASE}:docs/data/organismes.json"],
            cwd=ROOT, capture_output=True, check=True
        )
        cls.previous = json.loads(proc.stdout)
        cls.before = {a["id"]: a for a in cls.previous["authorities"]}
        cls.after = {a["id"]: a for a in cls.data["authorities"]}

    def test_provenance_exacte(self):
        p = self.data["provenance"]
        self.assertEqual((p["source_filename"], p["source_sha256"]), (SOURCE, SHA))
        self.assertEqual(p["exported_at_utc"], "2026-11-22T00:00:00+00:00")

    def test_totaux_inchanges_et_activites(self):
        d = self.data
        self.assertEqual(len(d["authorities"]), 935)
        self.assertEqual(len(d["relations"]), 600)
        self.assertEqual(
            (d["totals"]["authorities"], d["totals"]["organismes"],
             d["totals"]["services"], d["totals"]["catalog_included"],
             d["totals"]["catalog_excluded"]),
            (935, 735, 200, 683, 252))
        self.assertEqual(
            {v: sum(a["activity"]["active"] is v for a in d["authorities"])
             for v in (True, False, None)},
            {True: 719, False: 142, None: 74})

    def test_six_activites_positive_et_une_negative(self):
        self.assertEqual(list(self.before), list(self.after))
        for ident in ACTIVE:
            with self.subTest(ident=ident):
                self.assertIsNone(self.before[ident]["activity"]["active"])
                self.assertIs(self.after[ident]["activity"]["active"], True)
                self.assertIs(self.after[ident]["quality"]["activity_unknown"], False)
                self.assertIs(self.after[ident]["quality"]["end_missing"], False)
        self.assertIsNone(self.before[INACTIVE]["activity"]["active"])
        self.assertIs(self.after[INACTIVE]["activity"]["active"], False)
        self.assertIsNone(self.after[INACTIVE]["activity"]["end"])
        self.assertIs(self.after[INACTIVE]["quality"]["activity_unknown"], False)
        self.assertIs(self.after[INACTIVE]["quality"]["end_missing"], True)

    def test_cara_dotation_sans_inference_activite(self):
        self.assertIsNone(self.before[DATING]["activity"]["start"])
        self.assertEqual(self.after[DATING]["activity"]["start"], "2011")
        self.assertIsNone(self.after[DATING]["activity"]["active"])
        self.assertIsNone(self.after["SER-0202"]["activity"]["active"])

    def test_difference_stricte_avec_160(self):
        positions = {a["id"]: i for i, a in enumerate(self.previous["authorities"])}
        expected = {
            ("provenance", "source_filename"),
            ("provenance", "source_sha256"),
            ("authorities", positions[DATING], "activity", "start"),
            ("authorities", positions[INACTIVE], "quality", "end_missing"),
        }
        for ident in (*ACTIVE, INACTIVE):
            i = positions[ident]
            expected.add(("authorities", i, "activity", "active"))
            expected.add(("authorities", i, "quality", "activity_unknown"))
        actual = list(differences(self.previous, self.data))
        self.assertEqual(len(actual), 18)
        self.assertEqual({path for path, _, _ in actual}, expected)

    def test_mutation_etrangere_refusee(self):
        import copy
        modified = copy.deepcopy(self.data)
        modified["relations"][0]["type"] = "autre_valeur"
        self.assertTrue(any(
            path[:1] == ("relations",)
            for path, _, _ in differences(self.previous, modified)
        ))


if __name__ == "__main__":
    unittest.main()
