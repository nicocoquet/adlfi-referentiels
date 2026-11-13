"""Tests synthétiques de l'audit : aucune variante fictive n'est publiée."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_lieux_pactols", ROOT / "scripts/audit_variantes_pactols.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

RDF = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#">
 <rdf:Description rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtTestA">
  <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
  <skos:prefLabel xml:lang="fr">Commune exemple</skos:prefLabel>
  <skos:altLabel xml:lang="fr">Variante d'essai</skos:altLabel>
  <skos:altLabel xml:lang="en">Test place</skos:altLabel>
  <skos:altLabel xml:lang="fr">Variante d'essai</skos:altLabel>
  <skos:hiddenLabel xml:lang="fr">Ne pas indexer</skos:hiddenLabel>
 </rdf:Description>
 <rdf:Description rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtOther">
  <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
  <skos:altLabel xml:lang="fr">Exclue</skos:altLabel>
 </rdf:Description>
</rdf:RDF>
"""


class AuditPactolsTests(unittest.TestCase):
    def test_jointure_par_ark_filtrage_et_dedoublonnage(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.rdf"
            src.write_text(RDF, encoding="utf-8")
            trouves, anomalies = MOD.lire_rdf(src, {"26678/pcrtTestA": {}})
            self.assertEqual(set(trouves), {"26678/pcrtTestA"})
            self.assertEqual(len(trouves["26678/pcrtTestA"]["variantes"]), 2)
            self.assertEqual(trouves["26678/pcrtTestA"]["pref_labels"]["fr"], ["Commune exemple"])
            self.assertNotIn("Ne pas indexer", str(trouves))
            self.assertEqual(anomalies, [])

    def test_refus_source_non_conforme_et_absence_ark(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.rdf"
            src.write_text(RDF, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Empreinte SHA-256"):
                MOD.produire(ROOT / "docs/data/lieux.json", src)
            rapport, candidats, _ = MOD.produire(
                ROOT / "docs/data/lieux.json", src, verification_source=False)
            self.assertEqual(rapport["resume"]["nombre_ark_pilote"], 103)
            self.assertEqual(rapport["resume"]["nombre_ark_trouves"], 0)
            self.assertEqual(len(candidats), 103)
            self.assertEqual(rapport["resume"]["anomalies_par_type"]["ark_absent_export"], 103)

    def test_donnees_publiees_inchangees(self):
        data = json.loads((ROOT / "docs/data/lieux.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["autorites"]), 103)
        self.assertTrue(all("variantes_pactols" not in a for a in data["autorites"]))


if __name__ == "__main__":
    unittest.main()
