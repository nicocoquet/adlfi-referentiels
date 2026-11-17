"""La projection publique COG 2026 provient du socle et des décisions datées."""
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
GUYANE=ROOT/"recette/lieux/GUYANE-VALIDATIONS-PACTOLS-COG-2026.csv"


class AlignementsGuyaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public=json.loads(INDEX.read_text(encoding="utf8"))
        with GUYANE.open(encoding="utf-8-sig",newline="") as f:
            cls.csv=list(csv.DictReader(f,delimiter=";"))

    def socle(self):
        data=copy.deepcopy(self.public)
        data["pactols_valides"]={
            code:ark for code,ark in data["pactols_valides"].items()
            if not code.startswith("973")
        }
        return data

    def appliquer_copie(self,rows):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"decision.csv"
            with path.open("w",encoding="utf8",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=list(self.csv[0]),delimiter=";")
                writer.writeheader()
                writer.writerows(rows)
            return appliquer_validations(self.socle(),[path])

    def test_les_22_validations_documentees_correspondent_exactement_au_site(self):
        self.assertEqual(len(self.csv),22)
        result=appliquer_validations(self.socle(),[GUYANE])
        self.assertEqual(result,self.public)
        self.assertEqual(len(result["pactols_valides"]),104)
        self.assertEqual(sum(c.startswith("971") for c in result["pactols_valides"]),32)
        self.assertEqual(sum(c.startswith("972") for c in result["pactols_valides"]),34)
        self.assertEqual(sum(c.startswith("973") for c in result["pactols_valides"]),22)
        self.assertEqual(sum(c.startswith("976") for c in result["pactols_valides"]),16)
        self.assertEqual(result["ark_confirmes_non_valides"],{
            "97407":"26678/pcrtIKvRT9vwUl",
            "97607":"26678/crtZcuFSJVYZU",
        })

    def test_independance_historique_cartographique_et_codes_disparus(self):
        self.assertTrue(all(x["portee_COG"]=="2026-01-01" for x in self.csv))
        self.assertFalse(any(x["code_insee"] in {"97351","97354","97355","97359"}
                             for x in self.csv))
        self.assertEqual(self.public["contours_invalides"],["98745","98805"])

    def test_closematch_n_est_pas_une_preuve_exacte(self):
        rows=copy.deepcopy(self.csv)
        rows[0]["predicat_source"]="closeMatch"
        with self.assertRaisesRegex(ValueError,"insuffisante"):
            self.appliquer_copie(rows)

    def test_mauvais_code_historique_refuse(self):
        rows=copy.deepcopy(self.csv)
        rows[0]["code_insee"]="97351"
        rows[0]["uri_insee"]="http://id.insee.fr/geo/commune/97351"
        with self.assertRaisesRegex(ValueError,"Code non courant"):
            self.appliquer_copie(rows)

    def test_un_concept_deprecie_est_exclu(self):
        rows=copy.deepcopy(self.csv)
        rows[0]["concept_deprecie"]="oui"
        with self.assertRaisesRegex(ValueError,"insuffisante"):
            self.appliquer_copie(rows)

    def test_conflit_de_paire_et_ark_refuse(self):
        rows=copy.deepcopy(self.csv)
        rows[0]["ark_pactols"]=rows[1]["ark_pactols"]
        with self.assertRaisesRegex(ValueError,"insuffisante"):
            self.appliquer_copie(rows)

    def test_desaccord_de_libelle_non_qualifie_refuse(self):
        rows=copy.deepcopy(self.csv)
        rows[0]["prefLabel_fr_pactols"]="Paris"
        with self.assertRaisesRegex(ValueError,"divergent"):
            self.appliquer_copie(rows)

    def test_parenthese_de_desambiguïsation_st_georges_acceptee(self):
        row=next(x for x in self.csv if x["code_insee"]=="97308")
        self.assertEqual(row["prefLabel_fr_pactols"],"Saint-Georges (Guyane)")
        self.assertEqual(row["libelle_COG_2026"],"Saint-Georges")
        self.assertEqual(self.appliquer_copie(self.csv)["pactols_valides"]["97308"],
                         "26678/pcrtFDuzqh49Ol")


if __name__=="__main__":
    unittest.main()
