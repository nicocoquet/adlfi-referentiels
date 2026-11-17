"""Le registre des 4 collectivités ne doit pas élargir les 176 communes."""
from __future__ import annotations
import csv,json,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from verifier_publication_pactols_collectivites_2026 import (
  CODES,ARKS,INTERDITS,SOURCE_CSV,decisions)
class TestValidationsCollectivites(unittest.TestCase):
 def test_quatre_autorites_institutionnelles_non_communales(self):
  rows=decisions(ROOT/SOURCE_CSV)
  self.assertEqual(set(rows),{"977","978","986","987"})
  self.assertEqual({r["ark_pactols"] for r in rows.values()},set(ARKS.values()))
  data=json.loads((ROOT/"recette/lieux/SOCLE-PACTOLS-COG-OUTREMER-176-2026.json").read_text(encoding="utf-8"))
  communes=data["pactols_valides"]
  coll=data["pactols_collectivites_valides"]
  self.assertEqual(len(communes),176)
  self.assertEqual(coll,ARKS)
  self.assertFalse(set(ARKS.values())&set(communes.values()))
  self.assertEqual(data["ark_confirmes_non_valides"],{"97607":"26678/crtZcuFSJVYZU"})
  self.assertEqual(data["contours_invalides"],["98745","98805"])
  self.assertEqual({x[0] for x in data["autres"] if x[0].startswith("COMER:TERRITOIRE:") and x[0].split(":")[-1] in CODES},
    {"COMER:TERRITOIRE:977","COMER:TERRITOIRE:978","COMER:TERRITOIRE:986","COMER:TERRITOIRE:987"})
  self.assertFalse(set(coll)&INTERDITS)
  self.assertFalse(set(communes)&INTERDITS)
  self.assertEqual(communes["98745"],"26678/pcrteZcqWgVUaT")
  for code in ("977","978"):
   self.assertEqual(rows[code]["uri_secondaire_exactMatch_non_publiee"],
      "http://id.insee.fr/geo/commune/"+code+"01")
   self.assertNotIn(code+"01",coll)
  for code in ("986","987"):
   self.assertEqual(rows[code]["uri_secondaire_exactMatch_non_publiee"],"")
  manifest=json.loads((ROOT/"docs/data/manifest.json").read_text(encoding="utf-8"))["modules"]["lieux"]
  m=manifest["recherche_cog_outremer_2026"]
  self.assertEqual(m["relations_pactols_cog_validees_2026"],212)
  self.assertEqual(m["relations_pactols_collectivites_2026"],4)
  self.assertTrue(m["relations_pactols_collectivites_2026_distinctes_des_communes"])
  self.assertEqual(m["alignements_codes_5_positions_97701_97801_inferes"],0)
  self.assertEqual(m["alignements_circonscriptions_98611_98612_98613_inferes"],0)
  self.assertEqual(m["alignements_communes_historiques_97123_97127_inferes"],0)
  self.assertFalse(m["retroprojection_identifiants_2026"])
  self.assertEqual(m["geometries_publiees"],0)
  self.assertTrue(manifest["historique_communes_polynesie"]["correspondance_pactols_territoire_987_2026_validee"])
 def test_refuser_fausses_propositions(self):
  header=(ROOT/SOURCE_CSV).read_text(encoding="utf-8")
  with TemporaryDirectory() as d:
   p=Path(d)/"proposition.csv"
   p.write_text(header.replace("VALIDE_ADLFI_2026","PROPOSITION_A_VALIDER"),encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"Décision"):decisions(p)
   p.write_text(header.replace("skos:exactMatch","skos:closeMatch"),encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"Décision"):decisions(p)
   p.write_text(header.replace("http://id.insee.fr/geo/collectiviteDOutreMer/977",
       "http://id.insee.fr/geo/commune/97701"),encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"Décision"):decisions(p)
   p.write_text(header+header.splitlines()[-1]+"\n",encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"Quatre collectivités"):decisions(p)
if __name__=="__main__":unittest.main()
