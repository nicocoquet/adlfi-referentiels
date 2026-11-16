"""Tests du rapprochement diagnostique Tahaa / subdivisions polynésiennes 2022."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from comparer_tahaa_8_subdivisions_2022 import (
    CODES_ASSOCIES, COMPARAISON_DISPONIBLE, source_shapefile,
)

class SchemaTests(unittest.TestCase):
    def test_huit_codes_associes_distincts(self):
        self.assertEqual(CODES_ASSOCIES,{str(x) for x in range(451,459)})

    def test_ne_pas_confondre_codes_locaux_et_cog(self):
        self.assertNotIn("98745",CODES_ASSOCIES)
        self.assertEqual(len(CODES_ASSOCIES),8)


@unittest.skipUnless(COMPARAISON_DISPONIBLE,"Shapely et pyproj requis")
class GeometrieTests(unittest.TestCase):
    def test_empreinte_source_obligatoire(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"fixture.zip"
            path.write_bytes(b"incorrect")
            with self.assertRaisesRegex(ValueError,"Empreinte"):
                source_shapefile(path)


if __name__=="__main__":
    unittest.main()
