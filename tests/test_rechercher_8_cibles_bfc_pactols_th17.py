import csv
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rechercher_8_cibles_bfc_pactols_th17 import (
    SKOS, RDF, apercu_concept, lire_cibles, norm, signals, types_liens,
)

class RecherchePactolsComplet(unittest.TestCase):
    def test_huit_cibles_et_quatorze_dossiers(self):
        file = (Path(__file__).resolve().parents[1] / "docs/lieux/recette" /
                "cibles-a-rechercher-pactols-bfc-8.csv")
        rows = lire_cibles(file)
        self.assertEqual(len(rows), 8)
        self.assertEqual(sum(int(r["nb_anciennes_autorites_source"]) for r in rows), 14)
        self.assertEqual({r["code_cible_insee"] for r in rows}, {
            "25147", "39021", "39137", "39177",
            "39290", "39485", "39530", "71566",
        })

    def test_exactmatch_commune_deleguee_et_variantes(self):
        el = ET.fromstring(
            '<skos:Concept xmlns:skos="http://www.w3.org/2004/02/skos/core#" '
            'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
            'rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtXyz">'
            '<skos:prefLabel xml:lang="fr">La Chailleuse</skos:prefLabel>'
            '<skos:altLabel xml:lang="fr">Chailleuse</skos:altLabel>'
            '<skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/39021"/>'
            '<skos:broader rdf:resource="https://ark.frantiq.fr/ark:/26678/pcrtParent"/>'
            '</skos:Concept>'
        )
        c = apercu_concept(el)
        self.assertEqual(c["ark"], "26678/pcrtXyz")
        self.assertEqual(c["broader"], ["https://ark.frantiq.fr/ark:/26678/pcrtParent"])
        s, codes = signals(c, "39021", "La Chailleuse")
        self.assertEqual(s, ["exactMatch_insee_code", "prefLabel_fr_exact"])
        self.assertEqual(codes["39021"], {"commune"})
        self.assertEqual(norm("Saint-Hymetière-sur-Valouse"),
                         norm("Saint Hymetiere sur Valouse"))

    def test_code_seul_ou_nom_seul_sont_distincts(self):
        c = {"urls": ["http://id.insee.fr/geo/commune/39137"],
             "pref_fr": ["Chemilla"], "alt_fr": []}
        s, _ = signals(c, "39137", "Saint-Hymetière-sur-Valouse")
        self.assertEqual(s, ["exactMatch_insee_code"])
        c["urls"] = []
        c["pref_fr"] = ["Hauteroche (Jura)"]
        s, _ = signals(c, "39177", "Hauteroche")
        self.assertEqual(s, ["prefLabel_fr_qualifie"])
        self.assertEqual(types_liens(["http://id.insee.fr/geo/communeDeleguee/39021"])["39021"],
                         {"communeDeleguee"})

if __name__ == "__main__":
    unittest.main()
