"""34 validations Martinique issues des exactMatch Pactols RDF figés au 22 juillet 2026."""
import copy
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from extraire_index_public_outremer_2026 import appliquer_validations

INDEX=ROOT/"docs/data/lieux-outremer/recherche-2026.json"
DECISIONS=ROOT/"recette/lieux/MARTINIQUE-VALIDATIONS-PACTOLS-COG-2026.csv"


class ValidationMartiniqueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public=json.loads(INDEX.read_text(encoding="utf-8"))
        with DECISIONS.open(encoding="utf-8-sig",newline="") as fd:
            cls.records=list(csv.DictReader(fd,delimiter=";"))

    def socle(self):
        data=copy.deepcopy(self.public)
        data["pactols_valides"]={code:ark
             for code,ark in data["pactols_valides"].items() if not code.startswith("972")}
        return data

    def appliquer_lignes(self,rows):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"validation.csv"
            with p.open("w",encoding="utf-8",newline="") as stream:
                w=csv.DictWriter(stream,fieldnames=list(self.records[0]),delimiter=";")
                w.writeheader()
                w.writerows(rows)
            return appliquer_validations(self.socle(),[p])

    def test_34_validations_reproduisent_index_public(self):
        self.assertEqual(len(self.records),34)
        self.assertEqual([x["code_insee"] for x in self.records],
                         [f"972{i:02d}" for i in range(1,35)])
        actual=self.appliquer_lignes(self.records)
        self.assertEqual(actual,self.public)
        self.assertEqual(len(actual["pactols_valides"]),176)
        self.assertEqual(len([x for x in actual["pactols_valides"] if x.startswith("971")]),32)
        self.assertEqual(len([x for x in actual["pactols_valides"] if x.startswith("972")]),34)
        self.assertEqual(len([x for x in actual["pactols_valides"] if x.startswith("973")]),22)
        self.assertEqual(len([x for x in actual["pactols_valides"] if x.startswith("976")]),16)
        self.assertEqual(set(actual["ark_confirmes_non_valides"]),{"97607"})

    def test_sept_preflabels_precises_par_martinique(self):
        precisions={r["code_insee"] for r in self.records
            if r["prefLabel_fr_pactols"]!=r["libelle_COG_2026"]}
        self.assertEqual(precisions,{"97224","97225","97226","97227",
                                      "97228","97230","97234"})
        self.assertTrue(all(r["prefLabel_fr_pactols"]==r["libelle_COG_2026"]+" (Martinique)"
                            for r in self.records if r["code_insee"] in precisions))

    def test_code_historique_refuse(self):
        rows=copy.deepcopy(self.records)
        rows[0]["code_insee"]="97250"
        rows[0]["uri_insee"]="http://id.insee.fr/geo/commune/97250"
        with self.assertRaisesRegex(ValueError,"Code non courant"):
            self.appliquer_lignes(rows)

    def test_closematch_refuse(self):
        rows=copy.deepcopy(self.records)
        rows[0]["predicat_source"]="closeMatch"
        with self.assertRaisesRegex(ValueError,"insuffisante"):
            self.appliquer_lignes(rows)

    def test_depreciation_refusee(self):
        rows=copy.deepcopy(self.records)
        rows[0]["concept_deprecie"]="oui"
        with self.assertRaisesRegex(ValueError,"insuffisante"):
            self.appliquer_lignes(rows)

    def test_ark_duplique_refuse(self):
        rows=copy.deepcopy(self.records)
        rows[0]["ark_pactols"]=rows[1]["ark_pactols"]
        with self.assertRaisesRegex(ValueError,"insuffisante"):
            self.appliquer_lignes(rows)

    def test_libelle_incompatible_refuse(self):
        rows=copy.deepcopy(self.records)
        rows[0]["prefLabel_fr_pactols"]="Paris"
        with self.assertRaisesRegex(ValueError,"divergent"):
            self.appliquer_lignes(rows)


if __name__=="__main__":
    unittest.main()
