"""Audit des URI INSEE UUID : jamais de promotion par homonymie."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from auditer_uris_insee_uuid_pactols_2026 import UUID_URI, CODE_URI, scanner_uuid

HEADER = '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:owl="http://www.w3.org/2002/07/owl#">'
UUID = "52976ff6-5685-48c9-b468-7417ad44b653"


def concept(ark, name, uris, extra=""):
    return (
        '<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/' + ark + '">'
        '<skos:prefLabel xml:lang="fr">' + name + '</skos:prefLabel>'
        + "".join('<skos:exactMatch rdf:resource="' + u + '"/>' for u in uris)
        + extra + "</skos:Concept>"
    )


class TestUUID(unittest.TestCase):
    def scan(self, fragments):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "source.rdf"
            f.write_text(HEADER + fragments + "</rdf:RDF>", encoding="utf-8")
            return scanner_uuid(f, {"25060": "Val-d'Usiers", "25100": "Commune-témoin"})

    def test_reconnaitre_uuid_et_code_distincts(self):
        self.assertTrue(UUID_URI.fullmatch("http://id.insee.fr/geo/commune/" + UUID))
        self.assertTrue(UUID_URI.fullmatch("https://id.insee.fr/geo/commune/" + UUID))
        self.assertIsNone(CODE_URI.fullmatch("http://id.insee.fr/geo/commune/" + UUID))
        self.assertIsNone(UUID_URI.fullmatch("http://id.insee.fr/geo/commune/25060"))

    def test_val_d_usiers_reste_non_valide(self):
        result = self.scan(concept("pcrtTest", "Val-d'Usiers", [
            "http://id.insee.fr/geo/commune/" + UUID
        ]))
        self.assertEqual(result["concepts_RDF_examines"], 1)
        self.assertEqual(len(result["concepts_uuid"]), 1)
        row = result["concepts_uuid"][0]
        self.assertEqual(row["codes_bfc_par_libelle_non_validants"], ["25060"])
        self.assertEqual(row["codes_bfc_directement_assertes"], [])
        self.assertIsNone(row["code_cog_resolu_par_uuid"])
        self.assertEqual(row["decision_editoriale"], "NON_PRISE")
        self.assertEqual(row["publication"], "NON_PUBLIE")

    def test_conserver_uuid_et_code_present_ensemble(self):
        result = self.scan(concept("pcrtTest", "Val-d'Usiers", [
            "http://id.insee.fr/geo/commune/25060",
            "http://id.insee.fr/geo/commune/" + UUID,
        ]))
        row = result["concepts_uuid"][0]
        self.assertEqual(row["codes_bfc_directement_assertes"], ["25060"])
        self.assertEqual(len(row["uris_insee_uuid_exactMatch"]), 1)
        self.assertEqual(row["statut"], "A_INSTRUIRE_RESOLUTION_URI_INSEE_UUID")

    def test_pas_d_uuid_aucun_resultat(self):
        result = self.scan(concept("pcrtTest", "Val-d'Usiers", [
            "http://id.insee.fr/geo/commune/25060",
        ]))
        self.assertEqual(result["concepts_uuid"], [])

    def test_autre_libelle_sans_code_non_infere(self):
        result = self.scan(concept("pcrtTest", "Ailleurs", [
            "http://id.insee.fr/geo/commune/" + UUID,
        ]))
        row = result["concepts_uuid"][0]
        self.assertEqual(row["codes_bfc_par_libelle_non_validants"], [])
        self.assertFalse(row["concerne_potentiellement_bfc"])


if __name__ == "__main__":
    unittest.main()
