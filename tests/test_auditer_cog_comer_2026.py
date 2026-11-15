"""Tests de qualification COMER : aucune source réelle ni ARK Pactols."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from auditer_cog_comer_2026 import construire

class AuditerCOMER(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.src=self.base/"sources";self.src.mkdir()
        self.out=self.base/"export"
        self.csv("v_comer_2026.csv",["COMER","LIBELLE"],[
            ["984","Terres australes et antarctiques françaises"],
            ["986","Wallis et Futuna"],["977","Saint-Barthélemy"]])
        self.csv("v_tom_depuis_1943.csv",["COMER","LIBELLE","DATE_DEBUT","DATE_FIN"],[
            ["984","TAAF","1955-01-01",""],["977","Saint-Barthélemy","2007-02-23",""]])
        self.csv("v_commune_comer_2026.csv",
                 ["COM_COMER","LIBELLE","NATURE_ZONAGE","COMER","LIBELLE_COMER"],[
            ["98411","Archipel Crozet","DIS","984","TAAF"],
            ["98412","Îles Kerguelen","DIS","984","TAAF"],
            ["98413","Îles Saint-Paul et Amsterdam","DIS","984","TAAF"],
            ["98414","Terre Adélie","DIS","984","TAAF"],
            ["98415","Îles Éparses","DIS","984","TAAF"],
            ["98611","Alo","CIR","986","Wallis et Futuna"],
            ["97701","Saint-Barthélemy","COM","977","Saint-Barthélemy"]])
        self.csv("v_commune_outremer_depuis_1943.csv",
                 ["COM_COMER","LIBELLE","NATURE_ZONAGE","DATE_DEBUT","DATE_FIN"],[
            ["98411","Archipel Crozet","DIS","1955-01-01",""],
            ["98412","Îles Kerguelen","DIS","1955-01-01",""],
            ["98611","Alo","CIR","1961-01-01",""],
            ["97701","Saint-Barthélemy","COM","2007-02-23",""]])
    def csv(self,name,headers,records):
        with (self.src/name).open("w",encoding="utf-8",newline="") as f:
            writer=csv.writer(f);writer.writerow(headers);writer.writerows(records)
    def test_recette_non_validante_types_et_taaf(self):
        r=construire(self.src,self.out)
        self.assertEqual(r["volumes"]["zonages_2026"],7)
        self.assertEqual(r["natures_zonages_actuels"],{"CIR":1,"COM":1,"DIS":5})
        self.assertTrue(r["taaf_tous_districts"])
        self.assertEqual(len(r["taaf_2026"]),5)
        self.assertEqual(r["nombre_ark_pactols_attribues"],0)
        self.assertEqual(r["nombre_geometries_historiques_attribuees"],0)
        t=(self.out/"taaf_zonages_2026.csv").read_text(encoding="utf-8-sig")
        self.assertIn("98414",t)
        self.assertEqual(json.loads((self.out/"rapport_comer_2026.json").read_text())
                         ["statut"],"RECETTE_NON_VALIDANTE_NON_PUBLIEE")
    def test_interdit_ecrire_dans_docs(self):
        with self.assertRaisesRegex(ValueError,"docs"):
            construire(self.src,self.base/"docs"/"json")
    def test_refuse_zonage_sans_parent(self):
        f=self.src/"v_commune_comer_2026.csv"
        f.write_text(f.read_text()+"99999,Absent,COM,999,Inconnu\n")
        with self.assertRaisesRegex(ValueError,"sans COMER"):
            construire(self.src,self.out)
    def test_refuse_zonage_sans_nature(self):
        p=self.src/"v_commune_comer_2026.csv"
        p.write_text(p.read_text().replace(",DIS,",",INCONNU,",1))
        with self.assertRaisesRegex(ValueError,"Nature de zonage inconnue"):
            construire(self.src,self.out)
    def test_refuse_date_inversee(self):
        p=self.src/"v_tom_depuis_1943.csv"
        p.write_text(p.read_text().replace("2007-02-23,","2007-02-23,2000-01-01",1))
        with self.assertRaisesRegex(ValueError,"Période incohérente"):
            construire(self.src,self.out)
    def test_sortie_reproductible(self):
        construire(self.src,self.out)
        before={f.name:f.read_bytes() for f in self.out.iterdir()}
        construire(self.src,self.base/"export2")
        self.assertEqual(before,{f.name:f.read_bytes() for f in (self.base/"export2").iterdir()})

if __name__=="__main__":
    unittest.main()
