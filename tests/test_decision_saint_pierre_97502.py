"""Saint-Pierre : exception éditoriale individuelle, sans mutation Pactols."""
from __future__ import annotations
import csv
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEC=ROOT/"recette/lieux/SAINT-PIERRE-97502-DECISION-PACTOLS-COG-2026.csv"
INDEX=ROOT/"docs/data/lieux-outremer/recherche-2026.json"

class TestDecisionSaintPierre(unittest.TestCase):
    def test_decision_isolee_source_et_limite(self):
        with DEC.open(encoding="utf-8",newline="") as f:
            rows=list(csv.DictReader(f,delimiter=";"))
        self.assertEqual(len(rows),1)
        r=rows[0]
        self.assertEqual(r["code_insee"],"97502")
        self.assertEqual(r["ark_pactols"],"26678/pcrtYQmFfwxLq8")
        self.assertEqual(r["uri_insee"],"http://id.insee.fr/geo/commune/97502")
        self.assertEqual(r["predicat_source"],"skos:exactMatch")
        self.assertEqual(r["prefLabel_fr_pactols"],"île Saint-Pierre (Saint-Pierre-et-Miquelon)")
        self.assertEqual(r["source_rdf_sha256"],"3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7")
        self.assertEqual(r["type_decision"],"ARBITRAGE_EDITORIAL_EXPLICITE")
        self.assertEqual(r["statut_validation"],"VALIDE_ADLFI_2026")
        self.assertEqual(r["portee_COG"],"2026-01-01")
        self.assertEqual(r["statut_libelle_pactols"],"CORRECTION_PREFLABEL_A_DEMANDER")
        self.assertEqual(r["publication_site"],"EN_ATTENTE_RECETTE_PUBLICATION")  # État du registre initial, conservé historiquement
        public=json.loads(INDEX.read_text(encoding="utf-8"))
        self.assertEqual(public["pactols_valides"]["97502"],"26678/pcrtYQmFfwxLq8")
        self.assertEqual(public["pactols_valides"]["97501"],"26678/pcrtQAMzeGHldU")
        self.assertEqual(len(public["pactols_valides"]),212)
        ancien=json.loads((ROOT/"recette/lieux/SOCLE-PACTOLS-COG-OUTREMER-176-2026.json").read_text(encoding="utf-8"))
        self.assertNotIn("97502",ancien["pactols_valides"])

if __name__=="__main__":
    unittest.main()
