from scripts.recette_historique_organismes_158 import sans_a05f
"""Tests positifs et négatifs de publication Organismes 1.56."""
import copy,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from scripts.recette_publication_organismes_156 import validate

ROOT=Path(__file__).resolve().parents[1]
class Publication156Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Restaurer la version historique 1.56 à partir du JSON public 1.57.
        current=json.loads((ROOT/"docs/data/organismes.json").read_text(encoding="utf-8"))
        cls.d=sans_a05f(current)
        cls.d["provenance"]["source_filename"]="AdlFI_referentiel_1-56_A05D_GAVS_PRETECH_QUALIFIE_CANDIDAT.xlsx"
        cls.d["provenance"]["source_sha256"]="0410751ceaea8831cac45935afc65dd71b2b187060f0641215c90ad1822ac389"
        next(a for a in cls.d["authorities"] if a["id"]=="ORG-0156")["usage"]["affiliations_validated"]=1
    def test_candidat(self):
        self.assertEqual(validate(self.d),[])
    def test_sha_bloquant(self):
        d=copy.deepcopy(self.d)
        d["provenance"]["source_sha256"]="0"*64
        self.assertTrue(any("SHA-256" in x for x in validate(d)))
    def test_pretech_non_survalidee(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0348")["usage"]["affiliations_validated"]=11
        self.assertTrue(any("ORG-0348" in x for x in validate(d)))
    def test_service_sad24_non_perdu(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="SER-0041")["usage"]["affiliations_validated"]=0
        self.assertTrue(any("SER-0041" in x for x in validate(d)))
    def test_nantes_historique_preservee(self):
        d=copy.deepcopy(self.d)
        next(a for a in d["authorities"] if a["id"]=="ORG-0156")["activity"]["end"]=None
        self.assertTrue(any("Nantes" in x for x in validate(d)))
    def test_pas_de_tutelle_inventee(self):
        d=copy.deepcopy(self.d)
        d["relations"].append({"id":"REL-TEMP","source":"ORG-0348","target":"ORG-0008",
                               "type":"tutelle","validation":"valide"})
        self.assertTrue(any("600 relations" in x for x in validate(d)))
    @unittest.skipUnless(shutil.which("node"),"Node.js indisponible")
    def test_reconstruction_exacte_155(self):
        with tempfile.TemporaryDirectory() as tmp:
            historic=Path(tmp)/"organismes-156.json"
            historic.write_text(json.dumps(self.d,ensure_ascii=False),encoding="utf-8")
            p=subprocess.run(["node",str(ROOT/"scripts/recette_organismes_156_diff.cjs"),
                              str(historic)],cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stdout+"\n"+p.stderr)
if __name__=="__main__":unittest.main()
