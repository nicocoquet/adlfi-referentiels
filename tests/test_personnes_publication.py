"""Non-régression du catalogue public Personnes AdlFI (sans dépendance externe)."""
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data/personnes.json"
MANIFEST = ROOT / "docs/data/manifest.json"

FIRST_12 = [
    ("Dominique Dussot", "028293290", 15),
    ("Yves Menez", "028311817", 2),
    ("Éric Gailledrat", "035608277", 2),
    ("Serge Cassen", "059736984", 10),
    ("Laurent Schneider", "061051314", 2),
    ("Nelly Connet", "070441375", 28),
    ("Cyril Marcigny", "072319577", 35),
    ("Christophe Maniquet", "080825303", 66),
    ("Ludovic Slimak", "084576324", 11),
    ("Daniel Istria", "086150634", 16),
    ("Dominique Bonnissent", "132435764", 45),
    ("Luc Jaccottey", "155372599", 67),
]


class PublicationPersonnesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pub = json.loads(DATA.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_et_effectifs(self):
        data = self.pub
        module = self.manifest["modules"]["personnes"]
        self.assertEqual(module["data_schema"], data["schema_version"])
        self.assertEqual(module["autorites_validees"], len(data["authorities"]))
        self.assertEqual(module["contributions_adlfi"], len(data["contributions"]))
        urls = {c["notice"]["url"] for c in data["contributions"]}
        self.assertEqual(module["notices_adlfi"], len(urls))
        self.assertEqual(data["totals"], {
            "authorities": len(data["authorities"]),
            "contributions": len(data["contributions"]),
            "notices": len(urls),
        })
        self.assertGreaterEqual(len(data["authorities"]), 42)
        self.assertGreaterEqual(len(data["contributions"]), 956)
        self.assertGreaterEqual(len(urls), 930)

    def test_identifiants_per_stables(self):
        authorities = self.pub["authorities"]
        ids = [a["id"] for a in authorities]
        self.assertEqual(ids, [f"PER-{n:06d}" for n in range(1, len(ids) + 1)])
        self.assertEqual(len({a["identifiers"]["idref"] for a in authorities}), len(ids))
        for n, (name, idref, count) in enumerate(FIRST_12, start=1):
            a = authorities[n - 1]
            self.assertEqual((a["id"], a["name"], a["identifiers"]["idref"], a["contributions_count"]),
                             (f"PER-{n:06d}", name, idref, count))

    def test_relations_et_roles(self):
        data = self.pub
        refs = {a["id"] for a in data["authorities"]}
        counts = Counter()
        relations = set()
        for c in data["contributions"]:
            self.assertIn(c["person_id"], refs)
            self.assertEqual(c["journal"], "adlfi")
            self.assertTrue(c["notice"]["title"].strip())
            self.assertTrue(c["notice"]["url"].startswith("https://journals.openedition.org/adlfi/"))
            self.assertTrue(c["handle"].startswith("20.500.13089/"))
            roles = c["roles"]
            self.assertTrue(roles)
            self.assertTrue(set(roles) <= {"aut", "fld"})
            expected = (["responsable_operation"] if "fld" in roles else []) + (["auteur"] if "aut" in roles else [])
            self.assertEqual(c["normalized_roles"], expected)
            key = (c["person_id"], c["notice"]["url"])
            self.assertNotIn(key, relations)
            relations.add(key)
            counts[c["person_id"]] += 1
        for a in data["authorities"]:
            self.assertEqual(a["contributions_count"], counts[a["id"]])
            self.assertTrue(a["family_name"].strip())
            self.assertIsInstance(a["name_variants"], list)

    def test_protection_des_donnees_internes_et_alerte_persee(self):
        forbidden = {
            "reference_visa", "reference_attribution", "publication_nouvelle_autorisee",
            "reserve_identifiants", "sha256_xml_source", "source_xml",
            "h_id_heurist", "source_identite", "statut_contribution",
        }
        def keys(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    yield k
                    yield from keys(v)
            elif isinstance(obj, list):
                for v in obj:
                    yield from keys(v)
        self.assertFalse(set(keys(self.pub)) & forbidden)
        by_per = {a["id"]: a for a in self.pub["authorities"]}
        self.assertNotIn("persee", by_per["PER-000035"]["identifiers"])
        self.assertEqual(by_per["PER-000029"]["identifiers"]["persee"], "254845")


if __name__ == "__main__":
    unittest.main()
