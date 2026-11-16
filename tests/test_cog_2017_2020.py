"""Règles scientifiques : comparer 2017/2020 sans géolocalisation extrapolée."""
from __future__ import annotations

import csv
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import auditer_cog_2017_2020 as cog
import inventorier_admin_express_2017_2020 as ign

class Qualification(unittest.TestCase):
    def test_sources_et_dates(self):
        self.assertEqual(cog.YEARS,(2017,2020))
        self.assertIn("2017",cog.SOURCES[2017]["region"])
        self.assertIn("2020",cog.SOURCES[2020]["ensemble"])
        self.assertEqual(len(cog.ARCHIVES_SHA256),3)

    def test_archives_corrompues_refusees(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"reg2017-txt.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("reg2017.txt","REGION\tNCCENR\n11\tÎle-de-France\n".encode("latin-1"))
            with self.assertRaisesRegex(ValueError,"empreinte"):
                cog.lire(p,2017,"region")

    def test_parseur_atom_et_lien_source(self):
        xml=b'''<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry><id>urn:2017</id><title>ADMIN-EXPRESS-COG_2017</title>
          <link href="https://data.geopf.fr/telechargement/resource/A/2017"
             rel="alternate" type="application/atom+xml"/></entry>
        </feed>'''
        result=ign.parse_entries(xml)
        self.assertEqual(len(result["entries"]),1)
        self.assertEqual(result["entries"][0]["title"],"ADMIN-EXPRESS-COG_2017")
        self.assertEqual(result["entries"][0]["links"][0]["type"],"application/atom+xml")

    def test_pas_de_geometrie_generee(self):
        a=(ROOT/"scripts/auditer_cog_2017_2020.py").read_text(encoding="utf8")
        self.assertNotIn("docs/data",a)
        self.assertIn('"nouvelles_correspondances_pactols":0',a)

if __name__=="__main__":
    unittest.main()
