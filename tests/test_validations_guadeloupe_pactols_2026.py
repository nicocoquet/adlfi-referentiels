"""Contrat du registre des 32 décisions Pactols–COG Guadeloupe 2026."""
from __future__ import annotations
import copy,csv,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from extraire_index_public_outremer_2026 import appliquer_validations

INDEX=ROOT/"docs/data/lieux-outremer/recherche-2026.json"
DECISIONS=ROOT/"recette/lieux/GUADELOUPE-VALIDATIONS-PACTOLS-COG-2026.csv"


class ValidationGuadeloupeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public=json.loads(INDEX.read_text(encoding="utf-8"))
        with DECISIONS.open(encoding="utf-8-sig",newline="") as f:
            cls.records=list(csv.DictReader(f,delimiter=";"))

    def appliquer_lignes(self,records):
        base=copy.deepcopy(self.public)
        base["pactols_valides"]={c:a for c,a in base["pactols_valides"].items()
                                if not c.startswith("971")}
        with tempfile.TemporaryDirectory() as d:
            temp=Path(d)/"regle.csv"
            with temp.open("w",encoding="utf-8",newline="") as fd:
                writer=csv.DictWriter(fd,fieldnames=list(self.records[0]),delimiter=";")
                writer.writeheader();writer.writerows(records)
            return appliquer_validations(base,[temp])

    def test_32_decisions_reconstituent_publication(self):
        self.assertEqual(len(self.records),32)
        actual=self.appliquer_lignes(self.records)
        self.assertEqual(actual,self.public)
        valid=actual["pactols_valides"]
        self.assertEqual(len(valid),176)
        self.assertEqual(sum(x.startswith("971") for x in valid),32)
        self.assertEqual(sum(x.startswith("972") for x in valid),34)
        self.assertEqual(sum(x.startswith("973") for x in valid),22)
        self.assertEqual(sum(x.startswith("976") for x in valid),16)
        self.assertNotIn("97123",valid)
        self.assertNotIn("97127",valid)
        self.assertEqual(set(actual["ark_confirmes_non_valides"]),{"97607"})

    def test_sept_desambiguations_guadeloupe(self):
        found={r["code_insee"] for r in self.records
               if r["prefLabel_fr_pactols"]!=r["libelle_COG_2026"]}
        self.assertEqual(found,{"97122","97124","97125","97126","97128","97129","97132"})
        self.assertTrue(all(
            r["prefLabel_fr_pactols"]==r["libelle_COG_2026"]+" (Guadeloupe)"
            for r in self.records if r["code_insee"] in found))

    def test_anciens_codes_refuses(self):
        for old in ("97123","97127"):
            rows=copy.deepcopy(self.records)
            rows[0]["code_insee"]=old
            rows[0]["uri_insee"]="http://id.insee.fr/geo/commune/"+old
            with self.subTest(old=old),self.assertRaisesRegex(ValueError,"Code non courant"):
                self.appliquer_lignes(rows)

    def test_closematch_refuse(self):
        rows=copy.deepcopy(self.records)
        rows[0]["predicat_source"]="closeMatch"
        with self.assertRaisesRegex(ValueError,"insuffisante"):self.appliquer_lignes(rows)

    def test_concept_deprecie_refuse(self):
        rows=copy.deepcopy(self.records)
        rows[0]["concept_deprecie"]="oui"
        with self.assertRaisesRegex(ValueError,"insuffisante"):self.appliquer_lignes(rows)

    def test_ark_duplique_refuse(self):
        rows=copy.deepcopy(self.records)
        rows[0]["ark_pactols"]=rows[1]["ark_pactols"]
        with self.assertRaisesRegex(ValueError,"insuffisante"):self.appliquer_lignes(rows)

    def test_pref_label_incompatible_refuse(self):
        rows=copy.deepcopy(self.records)
        rows[0]["prefLabel_fr_pactols"]="Paris"
        with self.assertRaisesRegex(ValueError,"divergent"):self.appliquer_lignes(rows)


if __name__=="__main__":
    unittest.main()
