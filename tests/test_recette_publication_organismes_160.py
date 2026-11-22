"""Recette lot 1.60 : quatre activités documentées, sans dérive du JSON 1.59.

La comparaison contre le commit de publication 1.59 est exhaustive. Elle ne se
contente pas de vérifier quatre valeurs positives.
"""
import json
import subprocess
import unittest
from pathlib import Path
from scripts.recette_instantanes_organismes import charger_instantane

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "3b34b353f11cc702531de0e83237bcb4c81fac90"
SOURCE = "AdlFI_referentiel_1-60_lot01_quatre_activites_CANDIDAT.xlsx"
SHA = "70aeff4fedc66a54d1a45240af0d22cee1130565e2b29cefb1495e83aa434098"
IDS = {"ORG-0179", "ORG-0328", "ORG-0347", "ORG-0446"}


def diff(a, b, path=()):
    if type(a) is not type(b):
        yield path, a, b
    elif isinstance(a, dict):
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                yield path+(key,), a.get(key), b.get(key)
            else:
                yield from diff(a[key], b[key], path+(key,))
    elif isinstance(a, list):
        if len(a) != len(b):
            yield path+("length",), len(a), len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            yield from diff(x, y, path+(i,))
    elif a != b:
        yield path, a, b


class Publication160Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = charger_instantane("1.60")
        p = subprocess.run(
            ["git", "show", f"{BASE_COMMIT}:docs/data/organismes.json"],
            cwd=ROOT, capture_output=True, check=True,
        )
        cls.base = json.loads(p.stdout)

    def test_provenance(self):
        p = self.d["provenance"]
        self.assertEqual((p["source_filename"], p["source_sha256"]), (SOURCE, SHA))
        self.assertEqual(p["exported_at_utc"], "2026-11-22T00:00:00+00:00")

    def test_invariants_et_statuts(self):
        d = self.d
        self.assertEqual((d["totals"]["authorities"], d["totals"]["organismes"],
                          d["totals"]["services"]), (935, 735, 200))
        self.assertEqual((d["totals"]["catalog_included"],
                          d["totals"]["catalog_excluded"]), (683, 252))
        self.assertEqual(len(d["relations"]), 600)
        counts = {True: 0, False: 0, None: 0}
        for a in d["authorities"]:
            counts[a["activity"]["active"]] += 1
        self.assertEqual(counts, {True: 713, False: 141, None: 81})

    def test_les_quatre_corrections_exactes(self):
        older = {x["id"]: x for x in self.base["authorities"]}
        newer = {x["id"]: x for x in self.d["authorities"]}
        self.assertEqual(list(older), list(newer))
        for ident in IDS:
            with self.subTest(ident=ident):
                self.assertIsNone(older[ident]["activity"]["active"])
                self.assertIs(newer[ident]["activity"]["active"], True)
                self.assertIs(older[ident]["quality"]["activity_unknown"], True)
                self.assertIs(newer[ident]["quality"]["activity_unknown"], False)
        self.assertIsNone(newer["SER-0195"]["activity"]["active"])

    def test_aucune_autre_difference(self):
        older = {x["id"]: i for i, x in enumerate(self.base["authorities"])}
        expected = {("provenance", "source_filename"),
                    ("provenance", "source_sha256")}
        for ident in IDS:
            idx = older[ident]
            expected.add(("authorities", idx, "activity", "active"))
            expected.add(("authorities", idx, "quality", "activity_unknown"))
        observed = {path for path, _, _ in diff(self.base, self.d)}
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
