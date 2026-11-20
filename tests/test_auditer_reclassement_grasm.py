"""Tests autonomes de l'audit GRASM : fichiers OOXML minimaux en mémoire."""
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from auditer_reclassement_grasm import audit, read_workbook, main


def make_xlsx(path, tables, shared=False):
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    sheets = []
    relations = []
    strings = []
    payloads = {}
    for i, (name, records) in enumerate(tables.items(), 1):
        sheets.append(
            f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>'
        )
        relations.append(
            f'<Relationship Id="rId{i}" Type="{rel}/worksheet" '
            f'Target="worksheets/sheet{i}.xml"/>'
        )
        body = []
        for row_num, values in enumerate(records, 1):
            cells = []
            for index, value in enumerate(values):
                if value is None:
                    continue
                letters = ""
                n = index + 1
                while n:
                    n, digit = divmod(n - 1, 26)
                    letters = chr(65 + digit) + letters
                cell_ref = f"{letters}{row_num}"
                if shared:
                    strings.append(str(value))
                    cells.append(
                        f'<c r="{cell_ref}" t="s"><v>{len(strings)-1}</v></c>'
                    )
                else:
                    cells.append(
                        f'<c r="{cell_ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
                    )
            body.append(f'<row r="{row_num}">{"".join(cells)}</row>')
        payloads[f"xl/worksheets/sheet{i}.xml"] = (
            f'<worksheet xmlns="{ns}"><sheetData>'
            + "".join(body) + "</sheetData></worksheet>"
        )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets>'
            + "".join(sheets) + "</sheets></workbook>",
        )
        xlsx.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(relations) + "</Relationships>",
        )
        for name, data in payloads.items():
            xlsx.writestr(name, data)
        if shared:
            xlsx.writestr(
                "xl/sharedStrings.xml",
                f'<sst xmlns="{ns}" count="{len(strings)}" uniqueCount="{len(strings)}">'
                + "".join(f"<si><t>{escape(s)}</t></si>" for s in strings) + "</sst>",
            )


def sample_tables():
    return {
        "Organismes": [
            ["organisme_id", "nom_normalise", "acronyme"],
            ["ORG-0120", "Fédération française d’études et de sports sous-marins", "FFESSM"],
            ["ORG-0422", "Comité départemental des Alpes-Maritimes", "CDS 06"],
        ],
        "Services": [
            ["service_id", "nom_normalise", "acronyme"],
            ["SER-0063", "Groupe de recherche archéologique sous-marine", "Grasm"],
        ],
        "Relations_services": [
            ["relation_service_id", "service_source_id", "organisme_cible_id",
             "type_relation", "statut_validation"],
            ["RSE-0083", "SER-0063", "ORG-0120", "rattachement_service", "valide"],
        ],
        "Correspondances_affiliations": [
            ["affiliation_source_id", "service_id", "organisme_id"],
            ["AFF-003", "SER-0063", None],
        ],
        "Notes_privees": [
            ["annotation", "entite"],
            ["Ancien alias SER-0063 à reprendre", None],
        ],
    }


class AuditGrasmTests(unittest.TestCase):
    def test_toutes_feuilles_et_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "maitre.xlsx"
            make_xlsx(path, sample_tables())
            result = audit(read_workbook(path), filename=path.name,
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertTrue(result["ready_for_editorial_arbitrage"])
            self.assertEqual(result["ser_0063_service_rows"], [2])
            self.assertEqual(result["occurrences_by_sheet"]["Services"], 1)
            self.assertEqual(result["occurrences_by_sheet"]["Relations_services"], 1)
            self.assertEqual(result["occurrences_by_sheet"]["Correspondances_affiliations"], 1)
            self.assertEqual(result["occurrences_by_sheet"]["Notes_privees"], 1)
            self.assertEqual(len(result["occurrences"]), 4)
            self.assertEqual(result["relations_services_implicated"][0]["target"], "ORG-0120")

    def test_doublon_org_et_relation_alteree_bloquent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "maitre.xlsx"
            tables = sample_tables()
            tables["Organismes"].append(
                ["ORG-0900", "Groupe de recherche archéologique sous-marine", "GRASM"]
            )
            tables["Relations_services"][1][3] = "tutelle"
            make_xlsx(path, tables)
            result = audit(read_workbook(path), filename=path.name, sha256="synthetic")
            self.assertFalse(result["ready_for_editorial_arbitrage"])
            self.assertEqual(result["potential_organisme_duplicates"][0]["id"], "ORG-0900")
            self.assertFalse(result["checks"]["rse_0083_rattachement_attendu_present"])

    def test_shared_strings_et_ecriture_rapport_sans_changer_le_classeur(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "maitre.xlsx"
            report = Path(tmp) / "rapport.json"
            make_xlsx(path, sample_tables(), shared=True)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(main([str(path), "--rapport", str(report)]), 0)
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
            content = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(content["source"]["sha256"], before)
            self.assertEqual(len(content["sheets_scanned"]), 5)
            self.assertEqual(content["occurrences_by_sheet"]["Notes_privees"], 1)


if __name__ == "__main__":
    unittest.main()
