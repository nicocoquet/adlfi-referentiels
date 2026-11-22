from scripts.recette_instantanes_organismes import charger_instantane
from scripts.recette_historique_organismes_158 import sans_a05f
"""Recette A05e : contrôles positifs, négatifs, et reconstruction de 1.56."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.recette_publication_organismes_157 import validate

ROOT=Path(__file__).resolve().parents[1]

class Publication157Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=charger_instantane("1.57")

    def test_candidat(self):
        self.assertEqual(validate(self.d),[])

    def test_sha_bloquant(self):
        d=copy.deepcopy(self.d)
        d["provenance"]["source_sha256"]="0"*64
        self.assertTrue(any("SHA-256" in msg for msg in validate(d)))

    def test_universite_nantes_historique_non_survalidee(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0156")["usage"]["affiliations_validated"]=3
        self.assertTrue(any("ORG-0156" in msg for msg in validate(d)))

    def test_gavs_pas_de_perturbation(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0451")["usage"]["affiliations_validated"]=7
        self.assertTrue(any("ORG-0451" in msg for msg in validate(d)))

    def test_succession_nantes_preservee(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0156")["activity"]["end"]=None
        self.assertTrue(any("Nantes" in msg for msg in validate(d)))

    def test_aucune_relation_ajoutee(self):
        d=copy.deepcopy(self.d)
        d["relations"].append({"id":"REL-TEST","source":"ORG-0156","target":"ORG-0451","type":"tutelle","validation":"valide"})
        self.assertTrue(any("600 relations" in msg for msg in validate(d)))

    @unittest.skipUnless(shutil.which("node"),"Node.js indisponible")
    def test_reconstruction_stricte_156(self):
        with tempfile.TemporaryDirectory() as tmp:
            historic=Path(tmp)/"organismes-157.json"
            historic.write_text(json.dumps(self.d,ensure_ascii=False),encoding="utf-8")
            p=subprocess.run(["node",str(ROOT/"scripts/recette_organismes_157_diff.cjs"),
                              str(historic)],cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stdout+"\n"+p.stderr)

    @unittest.skipUnless(shutil.which("node"),"Node.js indisponible")
    def test_reconstruction_detecte_modification_etrangere(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0348")["usage"]["source_occurrences_linked"]=12
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"altered.json"
            p.write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            result=subprocess.run(["node",str(ROOT/"scripts/recette_organismes_157_diff.cjs"),str(p)],
                                  cwd=ROOT,text=True,capture_output=True)
            self.assertNotEqual(result.returncode,0)

if __name__=="__main__":
    unittest.main()
