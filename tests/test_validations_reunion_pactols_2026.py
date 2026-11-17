"""Valider 24 liens Pactols–COG Réunion, dont promotion contrôlée de Le Port."""
from __future__ import annotations
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
DECISIONS=ROOT/"recette/lieux/REUNION-VALIDATIONS-PACTOLS-COG-2026.csv"
PORT_ARK="26678/pcrtIKvRT9vwUl"
DEMBENI_ARK="26678/crtZcuFSJVYZU"

class ValidationReunionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public=json.loads(INDEX.read_text(encoding="utf-8"))
        with DECISIONS.open(encoding="utf-8",newline="") as f:
            cls.records=list(csv.DictReader(f,delimiter=";"))

    def socle(self):
        data=copy.deepcopy(self.public)
        data["pactols_valides"]={code:ark for code,ark in data["pactols_valides"].items()
                                 if not code.startswith("974")}
        # L'ARK de Le Port est confirmé mais non approuvé au socle PR30.
        data["ark_confirmes_non_valides"]["97407"]=PORT_ARK
        return data

    def appliquer_lignes(self,rows):
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/"validations.csv"
            with f.open("w",encoding="utf-8",newline="") as stream:
                writer=csv.DictWriter(stream,delimiter=";",fieldnames=list(self.records[0]))
                writer.writeheader();writer.writerows(rows)
            return appliquer_validations(self.socle(),[f])

    def test_24_exactmatch_et_promotion_le_port(self):
        self.assertEqual(len(self.records),24)
        self.assertEqual([r["code_insee"] for r in self.records],
                         [f"974{i:02d}" for i in range(1,25)])
        data=self.appliquer_lignes(self.records)
        self.assertEqual(data,self.public)
        self.assertEqual(len(data["pactols_valides"]),176)
        self.assertEqual(sum(c.startswith("974") for c in data["pactols_valides"]),24)
        self.assertEqual(data["pactols_valides"]["97407"],PORT_ARK)
        self.assertEqual(data["ark_confirmes_non_valides"],{"97607":DEMBENI_ARK})
        self.assertTrue(all(r["predicat_source"]=="exactMatch" and
                            r["portee_COG"]=="2026-01-01" and
                            r["statut_validation"]=="VALIDE_ADLFI_2026"
                            for r in self.records))

    def test_refus_de_promotion_port_sans_preuve_exacte(self):
        cases=[("predicat_source","closeMatch"),("concept_deprecie","oui"),
               ("ark_pactols","26678/pcrtAUTRE"),("prefLabel_fr_pactols","Port (Ariège)")]
        for field,value in cases:
            rows=copy.deepcopy(self.records)
            row=next(x for x in rows if x["code_insee"]=="97407")
            row[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                self.appliquer_lignes(rows)

    def test_dembeni_ne_peut_pas_etre_promue(self):
        rows=copy.deepcopy(self.records)
        new=copy.deepcopy(rows[-1])
        new.update(code_insee="97607",libelle_COG_2026="Dembeni",
                   uri_insee="http://id.insee.fr/geo/commune/97607",
                   ark_pactols=DEMBENI_ARK,prefLabel_fr_pactols="Dembeni")
        rows.append(new)
        with self.assertRaisesRegex(ValueError,"déjà arbitré"):
            self.appliquer_lignes(rows)

    def test_division_1965_sans_promotion_historique(self):
        r={x["code_insee"]:x for x in self.records}
        self.assertEqual(r["97414"]["ark_pactols"],"26678/pcrtBwoUOdthOV")
        self.assertEqual(r["97424"]["ark_pactols"],"26678/pcrtp3m5MZ822i")
        self.assertFalse(any(k.startswith("geo") or k.startswith("succession")
                             for row in self.records for k in row))

if __name__=="__main__":
    unittest.main()
