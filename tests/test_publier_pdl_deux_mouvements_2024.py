"""Contrôle non régressif de la publication Ingrandes MOD32 + Essarts MOD21."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_pdl_deux_mouvements_2024_2026 import SCHEMA,PUBS,ARK_ING,ARK_ING_OLD,ARK_ESS,ARK_ESS_OLD
class TestPublicationDeux2024(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/"docs/data/lieux-chronologie"
  cls.p=json.loads((base/"pactols-pdl-deux-mouvements-2024-2026.json").read_text(encoding="utf8"))
  cls.cog=json.loads((base/"cog-pdl.json").read_text(encoding="utf8"))
  cls.prev=[json.loads((base/n).read_text(encoding="utf8")) for n in PUBS]
 def test_uniques_1217(self):
  p=self.p
  self.assertEqual(p["schema"],SCHEMA)
  self.assertEqual(p["alignements_publies_precedemment"],1215)
  self.assertEqual(p["nouveaux_alignements"],2)
  self.assertEqual(p["total_alignements_PDL_2026"],1217)
  self.assertEqual(p["communes_a_instruire"],11)
  rows=[r for d in self.prev for r in d["alignements_Pactols_COG_valides_2026"]]+p["alignements_Pactols_COG_valides_2026"]
  self.assertEqual(len(rows),1217)
  self.assertEqual(len({x["code_insee"] for x in rows}),1217)
  self.assertEqual(len({x["ark_pactols"] for x in rows}),1217)
  self.assertFalse({ARK_ING_OLD,ARK_ESS_OLD}&{x["ark_pactols"] for x in rows})
 def test_provenance_et_mouvements(self):
  by={r["code_insee"]:r for r in self.p["alignements_Pactols_COG_valides_2026"]}
  self.assertEqual(set(by),{"49160","85084"})
  self.assertEqual(by["49160"]["ark_pactols"],ARK_ING)
  self.assertEqual(by["85084"]["ark_pactols"],ARK_ESS)
  self.assertEqual(by["49160"]["qid_Wikidata"],"Q123475717")
  self.assertEqual(by["49160"]["revision_Wikidata"],2309862185)
  self.assertFalse(by["49160"]["uri_insee_uuid_resolue"])
  self.assertEqual(by["49160"]["nature_evenement_COG"],"MOD32_CREATION_COMMUNE_NOUVELLE")
  self.assertEqual(by["85084"]["nature_evenement_COG"],"MOD21_RETABLISSEMENT_COMMUNES")
  self.assertEqual(by["85084"]["codes_communes_retablies"],["85165","85212"])
  for code,mod in (("49160","32"),("85084","21")):
   self.assertTrue(any(m["code_avant"]==code and m["code_apres"]==code and m["date_effet"]=="2024-01-01" and m["mod"]==mod for m in self.cog["lignes_mouvements_cog"]))
   self.assertEqual(by[code]["portee_chronologique"],"2026_SEULEMENT")
   self.assertEqual(by[code]["relations_historiques_inferees"],0)
  self.assertEqual(self.p["geometries_nouvelles"],0)
  self.assertEqual(self.p["liens_historiques_inferes"],0)
if __name__=="__main__":unittest.main()
