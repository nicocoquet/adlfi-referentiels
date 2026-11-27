"""Non-régression permanente du lot 08 — référentiel Personnes AdlFI."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASE_AUTHORITIES = "b4f075587d38984f9ad9238ec542311427e1198f254aaf84491caea39035f021"
EXPECTED_BASE_CONTRIBUTIONS = "923034ee1d65c29561599320fb258eb241d2529320560bc34f4004eea45368c4"
# Bornes de non-régression des 202 fiches et 1 980 relations validées avant l'extension Heurist.
EXPECTED_LOT08_AUTHORITIES = "04d941527e4aec2f6a7c6d2a040633c7bf00fc36de88729f14c24b8867484cc7"
EXPECTED_LOT08_CONTRIBUTIONS = "a3702aa0b75446add146f9c907bd2ebad5112a5ab9e5aa833fdfbbae601aea76"
EXPECTED_IDENTIFIERS = {
    193: {"idref": "235280070", "persee": "148661", "wikidata": "Q130530468"},
    194: {"idref": "09016945X", "orcid": "0000-0003-3565-8681", "persee": "426599", "wikidata": "Q86982487", "idhal": "nicolas-garnier"},
    195: {"idref": "197593097", "orcid": "0000-0002-2728-2031", "wikidata": "Q138572604", "idhal": "simon-ritz"},
    196: {"idref": "061626937", "persee": "170157", "wikidata": "Q55620345"},
    197: {"idref": "118228838", "persee": "148331"},
    198: {"idref": "281433968", "wikidata": "Q138572692"},
    199: {"idref": "060904321", "bnf": "cb14539821j", "orcid": "0000-0002-5550-7197", "persee": "171845", "wikidata": "Q116790786", "idhal": "agnes-lamotte"},
    200: {"idref": "028611624", "bnf": "cb12041196n", "persee": "401015", "wikidata": "Q112468247"},
    201: {"idref": "112277691", "bnf": "cb16584156c", "orcid": "0000-0001-6244-8167", "persee": "1618429", "wikidata": "Q21541966", "idhal": "aldo-borlenghi"},
    202: {"idref": "068696310", "bnf": "cb15579302v", "orcid": "0000-0003-3763-0893", "persee": "173570", "wikidata": "Q138572326", "idhal": "alexis-gorgues"},
}
EXPECTED_HANDLES = {
    193: "91pj 92o2 92o8 931b",
    194: "8y2q 937u w19u",
    195: "90mm 93tx 93ty",
    196: "929d 92bz 92c3",
    197: "8zcc 8z25 8vfy",
    198: "90jj 93qy 93r1",
    199: "8yts 918t",
    200: "92qg 92l6",
    201: "95wm 93av",
    202: "97km 137h7",
}


def checksum(value):
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class TestPersonnesLot08Publication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/data/personnes.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "docs/data/manifest.json").read_text(encoding="utf-8"))

    def test_invariants_et_compteurs(self):
        data = self.data
        self.assertGreaterEqual(len(data["authorities"]), 202)
        self.assertGreaterEqual(len(data["contributions"]), 1980)
        handles = {row["handle"] for row in data["contributions"]}
        self.assertEqual(data["totals"], {
            "authorities": len(data["authorities"]),
            "contributions": len(data["contributions"]),
            "notices": len(handles),
        })
        module = self.manifest["modules"]["personnes"]
        self.assertEqual(
            [module["autorites_validees"], module["contributions_adlfi"], module["notices_adlfi"]],
            [data["totals"][key] for key in ("authorities", "contributions", "notices")],
        )
        self.assertEqual(data["publication_status"], "PUBLIC_PILOT")
        self.assertNotIn("non validée", data["scope_note"])

    def test_integrite_du_lot07(self):
        self.assertEqual(checksum(self.data["authorities"][:192]), EXPECTED_BASE_AUTHORITIES)
        self.assertEqual(checksum(self.data["contributions"][:1953]), EXPECTED_BASE_CONTRIBUTIONS)

    def test_integrite_du_lot08_pour_extensions_heurist(self):
        self.assertEqual(checksum(self.data["authorities"][:202]), EXPECTED_LOT08_AUTHORITIES)
        self.assertEqual(checksum(self.data["contributions"][:1980]), EXPECTED_LOT08_CONTRIBUTIONS)

    def test_dix_autorites_et_alignements(self):
        by_id = {row["id"]: row for row in self.data["authorities"]}
        for number, identifiers in EXPECTED_IDENTIFIERS.items():
            key = f"PER-{number:06d}"
            with self.subTest(person=key):
                self.assertEqual(by_id[key]["identifiers"], identifiers)
                self.assertEqual(by_id[key]["contributions_count"], len(EXPECTED_HANDLES[number].split()))
        self.assertNotIn("####", json.dumps(self.data))
        for field in ("idref", "idhal", "wikidata", "persee"):
            values = [a["identifiers"][field] for a in self.data["authorities"] if field in a["identifiers"]]
            self.assertEqual(len(values), len(set(values)))

    def test_27_relations_et_roles(self):
        relations = {(c["person_id"], c["handle"]): c for c in self.data["contributions"]}
        self.assertEqual(len(relations), len(self.data["contributions"]))
        self.assertEqual(sum(len(s.split()) for s in EXPECTED_HANDLES.values()), 27)
        for number, suffixes in EXPECTED_HANDLES.items():
            for suffix in suffixes.split():
                key = (f"PER-{number:06d}", f"20.500.13089/{suffix}")
                with self.subTest(person=number, handle=suffix):
                    c = relations[key]
                    self.assertEqual(c["journal"], "adlfi")
                    self.assertEqual(
                        c["normalized_roles"],
                        (["responsable_operation"] if "fld" in c["roles"] else [])
                        + (["auteur"] if "aut" in c["roles"] else []),
                    )

    def test_provenance_privee_absente(self):
        forbidden = {
            "id_mention_xml", "source_xml", "sha256_fragment_tei",
            "sha256_xml_source", "reference_visa", "publication_autorisee",
            "per_propose", "statut_contribution",
        }

        def keys(value):
            if isinstance(value, dict):
                for key, inner in value.items():
                    yield key
                    yield from keys(inner)
            elif isinstance(value, list):
                for inner in value:
                    yield from keys(inner)

        self.assertFalse(forbidden.intersection(keys(self.data)))


if __name__ == "__main__":
    unittest.main()
