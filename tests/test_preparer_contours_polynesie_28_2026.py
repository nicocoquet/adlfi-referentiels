"""Vérifier le lot cartographique de recette sans déduction d'identité ni d'histoire."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CodesEtProvenanceTests(unittest.TestCase):
    def test_exactement_28_candidats_conservateurs(self):
        records=json.loads((ROOT/"recette/lieux/PF-COMPARAISON-GEOMETRIQUE-2022-2026.json").read_text(encoding="utf-8"))["communes"]
        codes=sorted(x["code_COG"] for x in records if
          x["etalab_topologie"]=="VALIDE" and
          x["etalab_vs_ispf"] is not None and x["etalab_vs_geopf"] is not None and
          x["etalab_vs_ispf"]["intersection_sur_union"]>=.90 and
          x["etalab_vs_geopf"]["intersection_sur_union"]>=.90 and
          x["geopf_vs_ispf"]["intersection_sur_union"]>=.95)
        self.assertEqual(len(codes),28)
        self.assertNotIn("98745",codes)
        self.assertIn("98735",codes)  # Papeete, test de recherche
        self.assertEqual(len(set(codes)),28)

@unittest.skipUnless(importlib.util.find_spec("shapely"),"Shapely disponible en recette géométrique")
class PreparationGeomTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0,str(ROOT/"scripts"))
        from preparer_contours_polynesie_28_2026 import prepare,EXPECTED
        self.prepare=prepare
        self.expected=EXPECTED
        self.index=json.loads((ROOT/"docs/data/lieux-outremer/recherche-2026.json").read_text(encoding="utf-8"))
        self.report=json.loads((ROOT/"recette/lieux/PF-COMPARAISON-GEOMETRIQUE-2022-2026.json").read_text(encoding="utf-8"))
        self.codes=[line.split("|",1)[0] for line in self.index["communes"]["987"].splitlines()]
        polygon={"type":"Polygon","coordinates":[[[-150,-20],[-149.9,-20],[-149.9,-19.9],[-150,-20]]]}
        self.source={"type":"FeatureCollection","features":[
          {"type":"Feature","properties":{"code":c},"geometry":polygon} for c in self.codes]}

    def test_filtre_28_et_exclusion_tahaa(self):
        output=self.prepare(self.source,self.index,self.report)
        codes=[f["properties"]["code"] for f in output["features"]]
        self.assertEqual(codes,list(self.expected))
        self.assertNotIn("98745",codes)
        self.assertEqual(len(output["provenance"]["exclues_a_instruire"]),20)
        self.assertTrue(all(f["properties"]["ark_pactols"] is None for f in output["features"]))
        self.assertTrue(all(f["properties"]["limite_juridique_homologuee"] is False for f in output["features"]))

    def test_manquant_et_doublon_refuses(self):
        self.source["features"].pop()
        with self.assertRaisesRegex(ValueError,"incomplète"):
            self.prepare(self.source,self.index,self.report)
        self.source["features"].append(self.source["features"][0])
        with self.assertRaisesRegex(ValueError,"dupliquée"):
            self.prepare(self.source,self.index,self.report)

    def test_diminution_des_seuils_recalcule_lot_donc_refuse(self):
        for row in self.report["communes"]:
            if row["code_COG"]=="98735":
                row["etalab_vs_ispf"]["intersection_sur_union"]=0.4
        with self.assertRaisesRegex(ValueError,"lot éditorial"):
            self.prepare(self.source,self.index,self.report)

if __name__=="__main__":
    unittest.main()
