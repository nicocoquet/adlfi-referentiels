"""BFC : univocité, exceptions et vérification de toutes les URI INSEE."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from preparer_validations_pactols_bfc_2026 import (
    preparer_depuis_rapport, verifier_toutes_uris_insee,
)


def commune(code, name, status, ark="26678/pcrtTest"):
    hit = {
        "ark": ark, "prefLabels_fr": [name],
        "insee_exactMatch": [{
            "famille": "commune", "code": code,
            "uri": "http://id.insee.fr/geo/commune/" + code,
        }]
    }
    return {
        "region": "27", "departement": "25",
        "code": code, "nom": name, "etat": status,
        "preuves_RDF_exactMatch": [] if status == "SANS_EXACTMATCH" else [hit],
    }


def rdf_for(uris):
    exact = "".join(
        '<skos:exactMatch rdf:resource="' + uri + '"/>'
        for uri in uris
    )
    return (
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        'xmlns:skos="http://www.w3.org/2004/02/skos/core#">'
        '<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtTest">'
        '<skos:prefLabel xml:lang="fr">Commune-témoin</skos:prefLabel>'
        + exact + '</skos:Concept></rdf:RDF>'
    )


class TestBFC(unittest.TestCase):
    def test_preparation_isole_les_exceptions(self):
        r = {"pactols": {"sha256": "source"},
             "communes": [
                 commune("25060", "Val-d'Usiers", "SANS_EXACTMATCH"),
                 commune("25100", "Commune-témoin", "ELIGIBLE_SELON_REGLE"),
             ]}
        records, exceptions, stats = preparer_depuis_rapport(
            r, {"ELIGIBLE_SELON_REGLE": 1, "SANS_EXACTMATCH": 1},
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["code_insee"], "25100")
        self.assertEqual(records[0]["statut_validation"], "VALIDE_ADLFI_2026")
        self.assertEqual(records[0]["publication_site"], "EN_ATTENTE_RECETTE_PUBLICATION")
        self.assertEqual(exceptions[0]["code_insee"], "25060")
        self.assertEqual(exceptions[0]["decision_editoriale"], "NON_PRISE")

    def check_rdf(self, uris):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "rdf.xml"
            p.write_text(rdf_for(uris), encoding="utf-8")
            verifier_toutes_uris_insee(p, [{
                "ark_pactols": "26678/pcrtTest",
                "uri_insee": "http://id.insee.fr/geo/commune/25100",
            }])

    def test_uris_exactes_acceptees(self):
        self.check_rdf(["http://id.insee.fr/geo/commune/25100",
                        "https://www.wikidata.org/wiki/Q1234"])

    def test_uri_uuid_supplementaire_bloquee(self):
        with self.assertRaisesRegex(ValueError, "non reconnu"):
            self.check_rdf([
                "http://id.insee.fr/geo/commune/25100",
                "http://id.insee.fr/geo/commune/52976ff6-5685-48c9-b468-7417ad44b653",
            ])

    def test_uri_insee_autre_famille_bloquee(self):
        with self.assertRaisesRegex(ValueError, "non reconnu"):
            self.check_rdf([
                "http://id.insee.fr/geo/commune/25100",
                "http://id.insee.fr/geo/departement/25",
            ])

    def test_ark_absent_bloque(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "rdf.xml"
            p.write_text('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>',
                         encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "absents"):
                verifier_toutes_uris_insee(p, [{
                    "ark_pactols": "26678/pcrtTest",
                    "uri_insee": "http://id.insee.fr/geo/commune/25100",
                }])


if __name__ == "__main__":
    unittest.main()
