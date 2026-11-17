"""Validation des 48 décisions éditoriales Pactols–COG 2026 et invariants publics."""
from __future__ import annotations
import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/"recette/lieux/POLYNESIE-VALIDATIONS-PACTOLS-COG-2026.csv"
class TestPublicationPolynesie(unittest.TestCase):
 def test_registre_et_index_public(self):
  with CSV.open(encoding="utf-8",newline="") as file:
   rows=list(csv.DictReader(file,delimiter=";"))
  public=json.loads((ROOT/"docs/data/lieux-outremer/recherche-2026.json").read_text(encoding="utf-8"))
  self.assertEqual(len(rows),48)
  self.assertEqual({r["code_insee"] for r in rows},{f"987{x}" for x in range(11,59)})
  self.assertEqual(len({r["ark_pactols"] for r in rows}),48)
  codes=dict(s.split("|") for s in public["communes"]["987"].splitlines())
  self.assertEqual(len(codes),48)
  self.assertEqual(len(public["pactols_valides"]),212)
  self.assertEqual(len(set(public["pactols_valides"].values())),212)
  self.assertEqual(public["ark_confirmes_non_valides"],{})
  self.assertEqual(public["contours_invalides"],["98745","98805"])
  self.assertNotIn("98799",public["pactols_valides"])
  self.assertNotIn("987",public["pactols_valides"])
  for row in rows:
   c=row["code_insee"]
   self.assertEqual(row["libelle_COG_2026"],codes[c])
   self.assertEqual(row["uri_insee"],"http://id.insee.fr/geo/commune/"+c)
   self.assertEqual(row["predicat_source"],"exactMatch")
   self.assertEqual(row["concept_deprecie"],"non")
   self.assertEqual(row["statut_validation"],"VALIDE_ADLFI_2026")
   self.assertEqual(row["portee_COG"],"2026-01-01")
   self.assertEqual(public["pactols_valides"][c],row["ark_pactols"])
   self.assertTrue(row["ark_pactols"].startswith("26678/"))
  self.assertEqual(public["pactols_valides"]["98711"],"26678/pcrtwSlYRcWVFw")
  self.assertEqual(public["pactols_valides"]["98735"],"26678/pcrtr90gKcAXiG")
  self.assertEqual(public["pactols_valides"]["98745"],"26678/pcrteZcqWgVUaT")
  self.assertEqual(public["pactols_valides"]["98758"],"26678/pcrtRw9F7i5M8l")
  manifest=json.loads((ROOT/"docs/data/manifest.json").read_text(encoding="utf-8"))["modules"]["lieux"]
  outre=manifest["recherche_cog_outremer_2026"]
  self.assertEqual(outre["relations_pactols_cog_validees_2026"],212)
  self.assertEqual(outre["relations_pactols_cog_validees_polynesie_2026"],48)
  self.assertEqual(outre["geometries_publiees"],0)
  poly=json.loads((ROOT/"docs/data/lieux-polynesie/chronologie-cog-2026.json").read_text(encoding="utf-8"))
  self.assertEqual(poly["alignements_pactols_2026_valides"],48)
  self.assertEqual(poly["communes_associees_creees"],0)
  self.assertTrue(poly["contour_tahaa_98745_non_homologue"])
  self.assertTrue(poly["alignements_uniquement_millesime_2026"])
if __name__=="__main__":unittest.main()
