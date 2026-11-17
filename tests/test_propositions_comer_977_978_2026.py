"""Deux propositions de collectivités COMER, pas d'alignement communal ni de publication."""
from __future__ import annotations
import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"recette/lieux/ANTILLES-COLLECTIVITES-977-978-ALIGNEMENTS-PROPOSES-2026.csv"
class TestPropositionCOMER(unittest.TestCase):
 def test_deux_preuves_typees_etaucun_lien_publie(self):
  with REG.open(encoding="utf-8",newline="") as f:
   rows=list(csv.DictReader(f,delimiter=";"))
  ref={
   "977":("Saint-Barthélemy","26678/pcrtrGdtY56gmH"),
   "978":("Saint-Martin","26678/pcrty5LooX8FgU")}
  self.assertEqual({x["code_cog_2026"] for x in rows},set(ref))
  self.assertEqual(len(rows),2)
  self.assertEqual(len({x["ark_pactols"] for x in rows}),2)
  for r in rows:
   c=r["code_cog_2026"];name,ark=ref[c]
   self.assertEqual(r["libelle_COG_2026"],name)
   self.assertEqual(r["nature_autorite"],"COLLECTIVITE_OUTREMER")
   self.assertEqual(r["ark_pactols"],ark)
   self.assertEqual(r["uri_insee_exactMatch_collectivite"],
    f"http://id.insee.fr/geo/collectiviteDOutreMer/{c}")
   self.assertEqual(r["uri_insee_exactMatch_cinq_positions"],
    f"http://id.insee.fr/geo/commune/{c}01")
   self.assertEqual(r["predicat_rdf"],"skos:exactMatch")
   self.assertEqual(r["source_rdf_sha256"],
    "3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7")
   self.assertEqual(r["statut_proposition"],"PROPOSITION_A_VALIDER")
   self.assertEqual(r["validation_site_publiee"],"non")
   self.assertEqual(r["homologie_anciennes_communes_inferree"],"non")
   self.assertEqual(r["portee_COG"],"2026-01-01")
  published=json.loads((ROOT/"docs/data/lieux-outremer/recherche-2026.json").read_text())
  self.assertEqual(len(published["pactols_valides"]),128)
  self.assertEqual(set(published["pactols_valides"]).intersection(
   {"977","978","97701","97801","97123","97127"}),set())
  self.assertEqual({x[0] for x in published["autres"] if x[0].endswith(
   (":977",":978",":97701",":97801"))},
   {"COMER:TERRITOIRE:977","COMER:TERRITOIRE:978",
    "COMER:COM:97701","COMER:COM:97801"})
if __name__=="__main__":unittest.main()
