"""Recette A05f : publication 1.58 et reconstitution strictement réversible de 1.57."""
import copy,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from scripts.recette_publication_organismes_158 import validate

ROOT=Path(__file__).resolve().parents[1]

class Publication158Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/"docs/data/organismes.json").read_text(encoding="utf-8"))

    def test_publication_attendue(self):
        self.assertEqual(validate(self.d),[])

    def test_archaeo_atlantica_identite_et_visibilite(self):
        a=next(a for a in self.d["authorities"] if a["id"]=="ORG-0756")
        self.assertEqual(a["names"]["preferred"],"Archéo Atlantica")
        self.assertTrue(a["validation"]["established"])
        self.assertTrue(a["presentation"]["visible"])
        self.assertEqual(a["classification"]["bsr"],"PRIV")
        self.assertEqual(a["classification"]["sector"],"prive")
        self.assertIsNone(a["activity"]["start"])
        self.assertIsNone(a["activity"]["active"])
        self.assertEqual(a["geography"]["cities_label"],"Batz-sur-Mer")
        self.assertEqual(a["usage"],{
            "affiliations_linked":1,"affiliations_validated":1,"source_occurrences_linked":1})

    def test_provenance_empreinte_obligatoire(self):
        d=copy.deepcopy(self.d)
        d["provenance"]["source_sha256"]="0"*64
        self.assertTrue(any("SHA-256" in error for error in validate(d)))

    def test_archaeo_atlantica_non_survalidee(self):
        d=copy.deepcopy(self.d)
        a=next(a for a in d["authorities"] if a["id"]=="ORG-0756")
        a["usage"]["affiliations_validated"]=2
        self.assertTrue(any("ORG-0756" in error for error in validate(d)))

    def test_nantes_et_pretech_non_regression(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0156")["usage"]["affiliations_validated"]=1
        self.assertTrue(any("ORG-0156" in error for error in validate(d)))
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0348")["usage"]["affiliations_validated"]=11
        self.assertTrue(any("ORG-0348" in error for error in validate(d)))

    def test_pas_de_relation_inventee(self):
        d=copy.deepcopy(self.d)
        d["relations"].append({"id":"REL-TEST","source":"ORG-0756",
                               "target":"ORG-0348","type":"tutelle","validation":"valide"})
        self.assertTrue(any("600 relations" in error for error in validate(d)))

    @unittest.skipUnless(shutil.which("node"),"Node.js indisponible")
    def test_reconstitution_stricte_157(self):
        r=subprocess.run(["node",str(ROOT/"scripts/recette_organismes_158_diff.cjs"),
                          str(ROOT/"docs/data/organismes.json")],
                         cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stdout+"\n"+r.stderr)

    @unittest.skipUnless(shutil.which("node"),"Node.js indisponible")
    def test_reconstitution_refuse_mutation_inattendue(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0156")["usage"]["source_occurrences_linked"]=10
        with tempfile.TemporaryDirectory() as tmp:
            altered=Path(tmp)/"altered.json"
            altered.write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            r=subprocess.run(["node",str(ROOT/"scripts/recette_organismes_158_diff.cjs"),str(altered)],
                             cwd=ROOT,text=True,capture_output=True)
            self.assertNotEqual(r.returncode,0)

if __name__=="__main__":unittest.main()
