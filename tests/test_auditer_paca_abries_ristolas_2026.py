"""Abriès-Ristolas : une identité communale nouvelle ne recycle pas Abriès."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_paca_abries_ristolas_2026 import (
    SCHEMA, OLD, NEW, OLD_LABEL, NEW_LABEL, audit_cog, fragment, RDF, SKOS
)
import xml.etree.ElementTree as ET

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

class AbrièsRistolasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog=load("docs/data/lieux-chronologie/cog-paca.json")
        cls.published=load("docs/data/lieux-chronologie/pactols-paca-communes-nouvelles-2026.json")

    def test_creation_2019_distincte_ancien_code(self):
        a=audit_cog(self.cog,self.published)
        self.assertEqual(a["code_COG_2026"],"05001")
        self.assertEqual(a["debut_identite_commune_nouvelle"],"2019-01-01")
        self.assertEqual(a["ancienne_commune_code_conserve"],"Abriès")
        self.assertEqual(a["nom_COG_2026"],"Abriès-Ristolas")
        self.assertGreaterEqual(len(a["evenements_MOD32"]),2)

    def test_ancienne_commune_et_commune_nouvelle_differentes(self):
        self.assertNotEqual(OLD,NEW)
        self.assertNotEqual(OLD_LABEL,NEW_LABEL)
        self.assertEqual(SCHEMA,"adlfi.lieux.paca.abries_ristolas.2026.audit.v1")

    def test_un_arc_insee_ne_s_invente_pas(self):
        concept=ET.fromstring('''<skos:Concept xmlns:skos="http://www.w3.org/2004/02/skos/core#"
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xml:lang="fr" rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtm96gvvfnwmggc9z0wrxn">
          <skos:prefLabel xml:lang="fr">Abriès-Ristolas</skos:prefLabel>
          <skos:broader rdf:resource="https://ark.frantiq.fr/ark:/26678/pcrtSomewhere"/>
        </skos:Concept>''')
        f=fragment(concept,NEW)
        self.assertEqual(f["exactMatch_INSEE"],[])
        self.assertEqual(f["skos_relations"]["broader"],[
            "https://ark.frantiq.fr/ark:/26678/pcrtSomewhere"])

    def test_lien_entre_actuelle_et_ancienne_commune_interdit_sans_preuve(self):
        edited=load("docs/data/lieux-chronologie/pactols-paca-communes-nouvelles-2026.json")
        edited["exceptions_restantes"]=[]
        with self.assertRaisesRegex(ValueError,"couverture PACA précédente"):
            audit_cog(self.cog,edited)

if __name__=="__main__":
    unittest.main()
