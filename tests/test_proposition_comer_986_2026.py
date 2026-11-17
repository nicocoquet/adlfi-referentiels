"""Proposition d'alignement COMER 986 non publiée, jamais utilisée pour une CIR."""
from __future__ import annotations
import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestPropositionWallis(unittest.TestCase):
 def test_986_collectivite_proposition_only(self):
  path=ROOT/"recette/lieux/WALLIS-FUTUNA-COLLECTIVITE-986-ALIGNEMENT-PROPOSE-2026.csv"
  with path.open(encoding="utf-8",newline="") as f:
   rows=list(csv.DictReader(f,delimiter=";"))
  self.assertEqual(len(rows),1)
  r=rows[0]
  self.assertEqual(r["code_cog_2026"],"986")
  self.assertEqual(r["nature_autorite"],"TERRITOIRE_COMER")
  self.assertEqual(r["ark_pactols"],"26678/pcrtwFq5jKHO3k")
  self.assertEqual(r["prefLabel_fr_Pactols"],"Wallis et Futuna")
  self.assertEqual(r["altLabel_fr_Pactols"],"Territoire des îles Wallis et Futuna")
  self.assertEqual(r["uri_insee_exactMatch_collectivite"],
   "http://id.insee.fr/geo/collectiviteDOutreMer/986")
  self.assertEqual(r["source_rdf_sha256"],
   "3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7")
  self.assertEqual(r["predicat_rdf"],"skos:exactMatch")
  self.assertEqual(r["statut_proposition"],"PROPOSITION_A_VALIDER")
  self.assertEqual(r["portee_COG"],"2026-01-01")
  self.assertEqual(r["report_autres_niveaux"],"interdit")
  self.assertEqual(r["validation_site_publiee"],"non")
  index=json.loads((ROOT/"docs/data/lieux-outremer/recherche-2026.json").read_text())
  self.assertEqual(len(index["pactols_valides"]),212)
  self.assertFalse(set(index["pactols_valides"])&
                   {"986","98611","98612","98613","98609","98607"})
  autres={row[0] for row in index["autres"]}
  self.assertTrue({"COMER:TERRITOIRE:986","COMER:CIR:98611",
    "COMER:CIR:98612","COMER:CIR:98613"}<=autres)
  m=json.loads((ROOT/"docs/data/manifest.json").read_text())["modules"]["lieux"]
  self.assertEqual(m["historique_circonscriptions_wallis_futuna"]["nombre_communes"],0)
  self.assertEqual(m["historique_circonscriptions_wallis_futuna"]["nouvelle_relation_Pactols_validee"],0)
if __name__=="__main__":unittest.main()
