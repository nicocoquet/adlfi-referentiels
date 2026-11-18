"""Contrats de qualification P374 Wikidata et triage sans publication."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from croiser_pdl_17_wikidata_p374_2026 import (
    SCHEMA,p374_qualifies,liste_qids,qualifier
)

class WikidataP374Tests(unittest.TestCase):
    def claim(self,code,rank="normal",debut=None,fin=None):
        qual={}
        for key,date in (("P580",debut),("P582",fin)):
            if date:
                qual[key]=[{"snaktype":"value","datavalue":{"value":{
                  "time":"+"+date+"T00:00:00Z"}}}]
        return {"rank":rank,"mainsnak":{"snaktype":"value",
                  "datavalue":{"value":code}},"qualifiers":qual}
    def test_p374_courant_exclut_l_historique(self):
        entity={"claims":{"P374":[
            self.claim("11111",fin="2024-12-31"),
            self.claim("22222",debut="2025-01-01")
        ]}}
        claims=p374_qualifies(entity)
        self.assertEqual([x["code"] for x in claims if x["actif_2026"]],["22222"])

    def test_p374_deprecie_exclu(self):
        d={"claims":{"P374":[self.claim("11111",rank="deprecated"),
                              self.claim("22222")]}}
        self.assertEqual([x["code"] for x in p374_qualifies(d) if x["actif_2026"]],["22222"])

    def test_registre_wikidata_17_codes_et_revisions(self):
        import json
        evidence=json.loads((ROOT/"recette/lieux/PDL-17-WIKIDATA-P374-2026.json").read_text(encoding="utf8"))
        cog=json.loads((ROOT/"docs/data/lieux-chronologie/cog-pdl.json").read_text(encoding="utf8"))
        rows=evidence["dossiers"]
        self.assertEqual(evidence["nombre_dossiers"],17)
        self.assertEqual(evidence["identifiants_P374_concordants"],17)
        self.assertEqual(evidence["nouveaux_alignements"],0)
        self.assertEqual(len({r["code_insee_2026"] for r in rows}),17)
        self.assertEqual(len({r["qid_wikidata"] for r in rows}),17)
        for r in rows:
            self.assertEqual(r["insee_P374_actif_2026"],[r["code_insee_2026"]])
            self.assertEqual(r["P31_instances"],["Q484170"])
            self.assertEqual(len(r["P571_creation"]),1)
            self.assertTrue(r["revision_wikidata"]>0)
            self.assertEqual(r["publication"],"NON_PUBLIE")
            x=[p for p in cog["periodes_com"] if
                p["code_insee"]==r["code_insee_2026"] and
                p["typecom"]=="COM" and
                p["debut_inclus"]<="2026-01-01" and
                (p["fin_exclue"] is None or p["fin_exclue"]>"2026-01-01")]
            self.assertEqual(len(x),1)
            self.assertEqual(x[0]["debut_inclus"],r["P571_creation"][0])
    def test_schema_non_validant(self):
        self.assertIn("prequalification",SCHEMA)
        source={"schema":"adlfi.lieux.pdl.17-ark-sans-insee.prequalification.2026.v1",
                "dossiers":[
                    {"code_insee":f"{i:05d}",
                     "rdf":{"exactMatch_tous":[f"https://www.wikidata.org/wiki/Q{i+1}"]}}
                    for i in range(17)]}
        self.assertEqual(len(liste_qids(source)),17)
        source["dossiers"][0]["rdf"]["exactMatch_tous"].append(
            "http://id.insee.fr/geo/commune/00000")
        with self.assertRaisesRegex(ValueError,"URI INSEE"):
            liste_qids(source)

if __name__=="__main__":
    unittest.main()
