"""Préflight 17 alignements indirects Pactols–Wikidata–COG 2026."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_pdl_17_wikidata_p374_2026 import SCHEMA


class PublicationWikidataPDLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        read=lambda p:json.loads((ROOT/p).read_text(encoding="utf8"))
        base="docs/data/lieux-chronologie/"
        cls.pub=read(base+"pactols-pdl-wikidata-p374-2026.json")
        cls.cog=read(base+"cog-pdl.json")
        cls.proof=read("recette/lieux/PDL-17-WIKIDATA-P374-2026.json")
        cls.previous=[read(base+p) for p in (
            "pactols-pdl-2026.json",
            "pactols-pdl-uuid-resolus-2026.json",
            "pactols-pdl-communes-nouvelles-lot01-2026.json",
            "pactols-pdl-chemille-2026.json",
            "pactols-pdl-communes-nouvelles-lot02-2026.json",
            "pactols-pdl-oree-anjou-mod50-2026.json"
        )]

    def test_17_plus_1195_unique(self):
        p=self.pub
        self.assertEqual(p["schema"],SCHEMA)
        self.assertEqual(p["alignements_publies_precedemment"],1195)
        self.assertEqual(p["nouveaux_alignements"],17)
        self.assertEqual(p["total_alignements_PDL_2026"],1212)
        self.assertEqual(p["communes_a_instruire"],16)
        previous=[a for doc in self.previous for a in doc["alignements_Pactols_COG_valides_2026"]]
        entries=p["alignements_Pactols_COG_valides_2026"]
        self.assertEqual(len(previous),1195)
        self.assertEqual(len(entries),17)
        self.assertEqual(len({a["code_insee"] for a in entries+previous}),1212)
        self.assertEqual(len({a["ark_pactols"] for a in entries+previous}),1212)
        older={a["ark_ancienne_commune_distinct"] for a in entries}
        self.assertEqual(len(older),17)
        self.assertFalse(older & {a["ark_pactols"] for a in entries+previous})

    def test_provenance_wikidata_p374_p31_p571(self):
        source={x["code_insee_2026"]:x for x in self.proof["dossiers"]}
        self.assertEqual(len(source),17)
        for a in self.pub["alignements_Pactols_COG_valides_2026"]:
            x=source[a["code_insee"]]
            self.assertEqual(a["qid_Wikidata"],x["qid_wikidata"])
            self.assertEqual(a["revision_Wikidata"],x["revision_wikidata"])
            self.assertEqual(a["URI_Wikidata_exactMatch"],
                             "https://www.wikidata.org/wiki/"+x["qid_wikidata"])
            self.assertEqual(a["code_INSEE_Wikidata_P374"],x["code_insee_2026"])
            self.assertEqual(x["P31_instances"],["Q484170"])
            self.assertEqual(x["P571_creation"],[a["date_creation_COG"]])
            self.assertEqual(a["predicat_Pactols"],"skos:exactMatch")
            self.assertEqual(a["predicat_Wikidata_INSEE"],"P374")
            self.assertNotIn("uri_insee",a)
            self.assertEqual(a["relations_historiques_inferees"],0)

    def test_creation_mod32_2026_non_retroprojectee(self):
        events=self.cog["lignes_mouvements_cog"]
        for a in self.pub["alignements_Pactols_COG_valides_2026"]:
            code=a["code_insee"];day=a["date_creation_COG"]
            self.assertTrue(any(m["mod"]=="32" and m["date_effet"]==day and
                m["code_apres"]==code and m["typecom_apres"]=="COM" and
                m["libelle_apres"]==a["libelle_COG_2026"] for m in events),code)
            self.assertEqual(a["portee_chronologique"],"2026_SEULEMENT")
        self.assertEqual(self.pub["geometries_nouvelles"],0)
        self.assertEqual(self.pub["liens_historiques_inferes"],0)


if __name__=="__main__":
    unittest.main()
