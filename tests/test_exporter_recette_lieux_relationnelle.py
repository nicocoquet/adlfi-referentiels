"""Tests autonomes du modèle relationnel Lieux : aucune donnée éditoriale réelle."""
import csv
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from exporter_recette_lieux_relationnelle import SCHEMA, TABLES, generer


class RecetteRelationnelleLieuxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.tables = self.base / "tables_csv"
        self.tables.mkdir()
        self.sortie = self.base / "resultat"
        self.exemples = {
            "dossiers": [{"identifiant_dossier": "D-1", "libelle_source": "Commune ancienne"}],
            "validations": [{
                "identifiant_dossier": "D-1", "decision_editoriale": "Valider",
                "assertion_editoriale": "regle_collective",
            }],
            "concepts_pactols": [{"ark": "26678/concept-test", "nb_libelles": "1"}],
            "couples_neutres": [{"id_dossier": "D-1", "ark_a": "26678/concept-test"}],
            "evenements_cog": [{"id_evenement": "EV-1", "modalite_mod": "34"}],
            "liens_dossiers": [{
                "id_dossier": "D-1", "id_objet": "EV-1", "type_objet": "evenement"
            }],
            "mouvements_cog": [{"id_ligne": "M-1", "id_evenement": "EV-1"}],
            "periodes_cog": [{"id_periode": "PER-1", "code_insee": "12345"}],
            "groupes_pdl": [{"id_groupe": "GRP-1", "nb_lignes_rattachees": "2"}],
            "uri_pdl": [{"id_dossier": "D-1", "ark": "26678/concept-test"}],
            "conventions": [{"id_convention": "CONV-34", "MOD": "34", "statut": "Validée"}],
            "journal_arbitrages": [{"id_objet": "CONV-34", "acte": "Validation"}],
            "sources": [{"source": "Jeu de test"}],
        }
        self.ecrire()

    def ecrire(self):
        db = sqlite3.connect(":memory:")
        try:
            db.executescript(SCHEMA.read_text(encoding="utf-8"))
            for name in TABLES:
                champs = [r[1] for r in db.execute("PRAGMA table_info(" + name + ")")]
                with (self.tables / (name + ".csv")).open(
                    "w", encoding="utf-8", newline=""
                ) as handle:
                    writer = csv.DictWriter(handle, fieldnames=champs, delimiter=";")
                    writer.writeheader()
                    for row in self.exemples.get(name, []):
                        writer.writerow({k: row.get(k, "") for k in champs})
        finally:
            db.close()

    def test_export_de_recette_complet_et_non_publiable(self):
        bilan = generer(self.tables, self.sortie)
        self.assertFalse(bilan["publication_autorisee"])
        data = json.loads((self.sortie / "lieux-recette.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["tables"]), 13)
        self.assertEqual(data["tables"]["validations"][0]["assertion_editoriale"], "regle_collective")
        self.assertFalse(data["publication_gate"]["publication_autorisee"])
        self.assertEqual(data["publication_gate"]["nouvelles_relations_pactols_validees"], [])
        self.assertEqual(data["publication_gate"]["nouvelles_geometries_historiques_validees"], [])
        db = sqlite3.connect(self.sortie / "lieux-recette.sqlite")
        try:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0], 1)
        finally:
            db.close()

    def test_determinisme_du_json(self):
        generer(self.tables, self.sortie)
        premier = (self.sortie / "lieux-recette.json").read_bytes()
        generer(self.tables, self.base / "autre-sortie")
        self.assertEqual(premier, (self.base / "autre-sortie" / "lieux-recette.json").read_bytes())

    def test_interdiction_docs_pages(self):
        with self.assertRaisesRegex(ValueError, "docs"):
            generer(self.tables, self.base / "docs" / "data")
        self.assertFalse((self.base / "docs").exists())

    def test_interdiction_ecrasement_sources(self):
        with self.assertRaisesRegex(ValueError, "distincts"):
            generer(self.tables, self.tables / "sortie")

    def test_interdiction_ecrasement_resultats(self):
        generer(self.tables, self.sortie)
        with self.assertRaisesRegex(ValueError, "existe déjà"):
            generer(self.tables, self.sortie)

    def test_reference_polymorphe_invalide(self):
        self.exemples["liens_dossiers"][0]["id_objet"] = "EV-INCONNU"
        self.ecrire()
        with self.assertRaisesRegex(ValueError, "introuvable"):
            generer(self.tables, self.sortie)

    def test_reference_fk_invalide(self):
        self.exemples["couples_neutres"][0]["ark_a"] = "26678/absent"
        self.ecrire()
        with self.assertRaises(sqlite3.IntegrityError):
            generer(self.tables, self.sortie)

    def test_validation_individuelle_incomplete_refusee(self):
        self.exemples["validations"][0]["assertion_editoriale"] = "relation_historique"
        self.ecrire()
        with self.assertRaisesRegex(ValueError, "incomplète"):
            generer(self.tables, self.sortie)

    def test_colonnes_supplementaires_refusees(self):
        with (self.tables / "sources.csv").open("a", encoding="utf-8") as handle:
            handle.write(";colonne-furtive\n")
        with self.assertRaisesRegex(ValueError, "mal formé"):
            generer(self.tables, self.sortie)

    def test_sources_absentes_refusees(self):
        (self.tables / "conventions.csv").unlink()
        with self.assertRaises(FileNotFoundError):
            generer(self.tables, self.sortie)


if __name__ == "__main__":
    unittest.main()
