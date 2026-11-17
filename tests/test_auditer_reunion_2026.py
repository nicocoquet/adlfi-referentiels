"""Tests sans accès réseau du contrat de qualification Réunion 2026."""
from __future__ import annotations
import csv
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_reunion_2026 import EXPECTED,libelle_compatible,candidats_rdf

REGISTRE=ROOT/"recette/lieux/REUNION-CANDIDATS-PACTOLS-COG-2026.csv"

class ReunionTests(unittest.TestCase):
    def test_registre_24_et_1965(self):
        with REGISTRE.open(encoding="utf-8-sig",newline="") as f:
            rows=list(csv.DictReader(f,delimiter=";"))
        self.assertEqual(len(rows),24)
        self.assertEqual({r["code_INSEE_2026"] for r in rows},EXPECTED)
        self.assertEqual(len({r["ark_Pactols_candidat"] for r in rows}),24)
        self.assertEqual({r["code_INSEE_2026"] for r in rows if r["categorie"]=="DIVISION_1965"},
                         {"97414","97424"})
        leport=next(r for r in rows if r["code_INSEE_2026"]=="97407")
        self.assertEqual(leport["ark_Pactols_candidat"],"26678/pcrtIKvRT9vwUl")
        self.assertTrue(all(r["uri_INSEE_declaree_dans_Pactols"]==
                            "http://id.insee.fr/geo/commune/"+r["code_INSEE_2026"] for r in rows))

    def test_libelles_desambiguises(self):
        self.assertTrue(libelle_compatible("Saint-Denis","Saint-Denis (La Réunion)"))
        self.assertTrue(libelle_compatible("L'Étang-Salé","L'Étang-Salé"))
        self.assertFalse(libelle_compatible("Saint-Denis","Saint-Denis (Seine-Saint-Denis)"))
        self.assertFalse(libelle_compatible("Le Port","Port"))

    def test_rdf_exactmatch_et_non_homonymie(self):
        src='''<?xml version="1.0" encoding="UTF-8"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
                 xmlns:owl="http://www.w3.org/2002/07/owl#">
          <skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtIKvRT9vwUl">
            <skos:prefLabel xml:lang="fr">Le Port (La Réunion)</skos:prefLabel>
            <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97407"/>
          </skos:Concept>
          <skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtTESTXYZ">
            <skos:prefLabel xml:lang="fr">Le Port (Ariège)</skos:prefLabel>
            <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/09212"/>
          </skos:Concept>
        </rdf:RDF>'''
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"pactols.rdf"
            file.write_text(src,encoding="utf-8")
            res=candidats_rdf(file)
        self.assertEqual(len(res),24)
        self.assertEqual([x["ark"] for x in res["97407"]],["26678/pcrtIKvRT9vwUl"])
        self.assertEqual(res["97407"][0]["codes_exactmatch"],["97407"])
        self.assertEqual(res["97414"],[])

if __name__=="__main__":
    unittest.main()
