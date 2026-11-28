"""Recette publique préalable au pilote Heurist 30.

N'utilise aucun export Heurist, aucune matrice nominative et aucune donnée
d'évaluation éditoriale. Contrôle les catalogues disponibles sur la branche.
Le rapprochement des 40 relations à la source privée reste une étape séparée.
"""
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT_BASE = {"people": 1402, "articles": 2193, "links": 3738}
PROHIBITED_KEYS = {
    "rec_ID", "heurist_person_id", "heurist_article_id",
    "source_person_record_id", "source_article_record_id",
    "source_field_id", "reference_visa", "visa_identite",
    "visa_alignements", "visa_relation", "visa_bibliographie",
    "expert", "reviewer", "private_source_field",
}

def valid_ppn(ppn):
    return (
        isinstance(ppn, str)
        and bool(re.fullmatch(r"[0-9]{8}[0-9X]", ppn))
        and sum((10 if char == "X" else int(char)) * (9 - i)
                for i, char in enumerate(ppn)) % 11 == 0
    )


def collisions(values):
    counts = Counter(value for value in values if value)
    return {value for value, n in counts.items() if n > 1}


def public_fields_only(node):
    """Inspecte récursivement les clés des champs publiés."""
    if isinstance(node, dict):
        if PROHIBITED_KEYS.intersection(node):
            return False
        return all(public_fields_only(v) for v in node.values())
    if isinstance(node, list):
        return all(public_fields_only(v) for v in node)
    return True


class TestRecettePubliquePilote30(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persons = json.loads(
            (ROOT / "docs/data/personnes.json").read_text(encoding="utf-8")
        )
        cls.biblio = json.loads(
            (ROOT / "docs/data/personnes-articles.json").read_text(encoding="utf-8")
        )
        cls.manifest = json.loads(
            (ROOT / "docs/data/manifest.json").read_text(encoding="utf-8")
        )["modules"]["personnes"]

    def test_jalon_publie_et_sans_attribution_prematuree(self):
        p = self.persons["authorities"]
        a = self.biblio["articles"]
        links = self.biblio["contributions"]
        self.assertGreaterEqual(len(p), PILOT_BASE["people"])
        self.assertGreaterEqual(len(a), PILOT_BASE["articles"])
        self.assertGreaterEqual(len(links), PILOT_BASE["links"])
        self.assertEqual(len(self.persons["contributions"]), 1980)
        self.assertEqual(self.persons["totals"]["notices"], 1779)
        self.assertEqual(self.persons["totals"]["contributions"], 1980)
        self.assertEqual(self.persons["totals"]["authorities"], len(p))

    def test_unicite_globale_des_identifiants(self):
        p = self.persons["authorities"]
        ids = [row["id"] for row in p]
        ppns = [row["identifiers"]["idref"] for row in p]
        self.assertFalse(collisions(ids), "PER répétés")
        self.assertFalse(collisions(ppns), "IdRef répétés")
        self.assertTrue(all(valid_ppn(ppn) for ppn in ppns))
        self.assertEqual(ids, [f"PER-{i:06d}" for i in range(1, len(ids) + 1)])

    def test_integrite_relations_et_bibliographie(self):
        pids = {row["id"] for row in self.persons["authorities"]}
        aids = [row["id"] for row in self.biblio["articles"]]
        self.assertFalse(collisions(aids), "Identifiants d'articles répétés")
        triples = [
            (r["article_id"], r["person_id"], r["role"])
            for r in self.biblio["contributions"]
        ]
        self.assertFalse(collisions(triples), "Relations bibliographiques répétées")
        self.assertTrue(all(r["role"] in {"auteur", "collaborateur"}
                            for r in self.biblio["contributions"]))
        self.assertTrue(all(a in set(aids) and p in pids for a, p, _ in triples))
        self.assertFalse(collisions([a.get("doi") for a in self.biblio["articles"]]),
                         "DOI répétés")
        self.assertFalse(collisions([a.get("url") for a in self.biblio["articles"]]),
                         "URL répétées")

    def test_manifestes_coherents(self):
        p, a, m = self.persons, self.biblio, self.manifest
        self.assertEqual(m["autorites_validees"], len(p["authorities"]))
        self.assertEqual(m["contributions_adlfi"], 1980)
        self.assertEqual(m["notices_adlfi"], 1779)
        self.assertEqual(m["articles_lies"]["articles"], len(a["articles"]))
        self.assertEqual(m["articles_lies"]["contributions"], len(a["contributions"]))
        self.assertEqual(m["articles_lies"]["autorites_reliees"],
                         len({r["person_id"] for r in a["contributions"]}))

    def test_aucune_donnee_interne_dans_catalogues_publics(self):
        self.assertTrue(public_fields_only(self.persons))
        self.assertTrue(public_fields_only(self.biblio))

    def test_tests_synthetiques_des_controles(self):
        self.assertTrue(valid_ppn("000000000"))
        self.assertFalse(valid_ppn("000000001"))
        self.assertEqual(collisions(["a", "a", "b", ""]), {"a"})
        self.assertTrue(public_fields_only({"identifiers": {"idref": "000000000"}}))
        self.assertFalse(public_fields_only({"nested": [{"rec_ID": "1"}]}))


if __name__ == "__main__":
    unittest.main()
