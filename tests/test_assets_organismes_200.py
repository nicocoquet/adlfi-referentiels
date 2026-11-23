"""Recette des 45 logos ajoutés au référentiel Organismes 1.62.

Sans Pillow : un parseur minimal lit les marqueurs JPEG et vérifie les
dimensions de l'image, sa profondeur et ses trois composantes. Le profil ICC
exact n'est pas attesté par ce test (contrôle possible avec sips sur macOS).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/assets/organismes"
IDS = (
    "ORG-0413", "ORG-0419", "ORG-0625", "ORG-0678", "ORG-0681", "ORG-0683", "ORG-0684",
    "ORG-0687", "ORG-0689", "ORG-0691", "ORG-0693", "ORG-0699", "ORG-0701", "ORG-0706",
    "ORG-0707", "ORG-0711", "ORG-0713", "ORG-0714", "ORG-0717", "ORG-0719", "ORG-0721",
    "ORG-0723", "ORG-0724", "ORG-0726", "ORG-0729", "ORG-0733", "ORG-0734", "ORG-0735",
    "ORG-0738", "ORG-0740", "ORG-0743", "ORG-0744", "ORG-0749", "ORG-0750", "SER-0176",
    "SER-0179", "SER-0180", "SER-0181", "SER-0182", "SER-0186", "SER-0191", "SER-0196",
    "SER-0199", "SER-0200", "SER-0201",
)


def jpeg_geometry(data: bytes):
    """Retourne (largeur, hauteur, précision, composantes) depuis un SOF JPEG."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("Signature JPEG absente")
    pos = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while pos < len(data):
        if data[pos] != 0xFF:
            raise ValueError("Marqueur JPEG absent avant le premier SOF")
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        if pos == len(data):
            break
        marker = data[pos]
        pos += 1
        if marker == 0x00:
            raise ValueError("Octet échappé rencontré avant le SOF")
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            continue
        if pos + 2 > len(data):
            break
        length = int.from_bytes(data[pos:pos + 2], "big")
        if length < 2 or pos + length > len(data):
            raise ValueError("Segment JPEG tronqué")
        if marker in sof:
            if length < 8:
                raise ValueError("Segment SOF trop court")
            precision = data[pos + 2]
            height = int.from_bytes(data[pos + 3:pos + 5], "big")
            width = int.from_bytes(data[pos + 5:pos + 7], "big")
            channels = data[pos + 7]
            return width, height, precision, channels
        if marker in (0xDA, 0xD9):
            break
        pos += length
    raise ValueError("Aucun segment SOF lisible")


class NouveauxLogosOrganismesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/data/organismes.json").read_text(encoding="utf-8"))
        cls.by_id = {a["id"]: a for a in cls.data["authorities"]}

    def test_45_identifiants_uniques_et_presents(self):
        self.assertEqual(len(IDS), 45)
        self.assertEqual(len(set(IDS)), 45)
        self.assertTrue(set(IDS).issubset(self.by_id.keys()))

    def test_45_logos_references_par_le_json(self):
        for ident in IDS:
            with self.subTest(ident=ident):
                a = self.by_id[ident]
                self.assertEqual(
                    a["presentation"]["media"]["logo"],
                    f"assets/organismes/{ident}.jpg",
                )
                self.assertIsNone(a["presentation"]["media"]["image"])

    def test_45_jpeg_320_carre_trois_composantes(self):
        for ident in IDS:
            with self.subTest(ident=ident):
                file = ASSETS / f"{ident}.jpg"
                self.assertTrue(file.is_file(), str(file))
                b = file.read_bytes()
                self.assertGreater(len(b), 100, str(file))
                self.assertEqual(
                    jpeg_geometry(b),
                    (320, 320, 8, 3),
                    str(file) + " : dimensions, précision ou composantes incorrectes",
                )


if __name__ == "__main__":
    unittest.main()
