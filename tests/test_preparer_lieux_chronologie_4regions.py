"""Recette synthétique du générateur des quatre régions, sans réseau."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from preparer_lieux_chronologie_4regions import construire, periode_active


class ChronologieQuatreRegionsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.paths = {n: self.base / (n + ".csv") for n in
                      ("communes", "historique", "mouvements")}
        self.paths["contours"] = self.base / "contours.geojson"
        self.paths["paca"] = self.base / "paca.json"
        self.sortie = self.base / "resultats"
        self.ecrire_csv("communes",
                        ("TYPECOM","COM","LIBELLE","REG","DEP","COMPARENT"), [
            ("COM","25368","Marchaux-Chaudefontaine","27","25",""),
            ("COM","49126","Orée d'Anjou","52","49",""),
            ("COMD","49069","Champtoceaux","","","49126"),
            ("COM","2A308","Sainte-Lucie-de-Tallano","94","2A",""),
            ("COM","06001","Aiglun","93","06",""),
        ])
        self.ecrire_csv("historique",
                        ("TYPECOM","COM","LIBELLE","DATE_DEBUT","DATE_FIN"), [
            ("COM","25368","Marchaux","1943-01-01","2018-01-01"),
            ("COM","25368","Marchaux-Chaudefontaine","2018-01-01",""),
            ("COM","49069","Orée d'Anjou","2015-12-15","2025-01-01"),
            ("COM","49126","Orée d'Anjou","2025-01-01",""),
            ("COM","20308","Sainte-Lucie-de-Tallano","1965-01-01","1976-01-01"),
            ("COM","2A308","Sainte-Lucie-de-Tallano","1976-01-01",""),
            ("COM","06001","Aiglun","1943-01-01",""),
        ])
        self.ecrire_csv("mouvements",
                        ("MOD","DATE_EFF","TYPECOM_AV","COM_AV","LIBELLE_AV",
                         "TYPECOM_AP","COM_AP","LIBELLE_AP"), [
            ("32","2018-01-01","COM","25368","Marchaux","COM",
             "25368","Marchaux-Chaudefontaine"),
            ("50","2025-01-01","COM","49069","Orée d'Anjou","COM",
             "49126","Orée d'Anjou"),
            ("41","1976-01-01","COM","20308","Sainte-Lucie-de-Tallano",
             "COM","2A308","Sainte-Lucie-de-Tallano"),
        ])
        self.paths["contours"].write_text(json.dumps({
            "type":"FeatureCollection","features":[
                {"type":"Feature","properties":{"code":code,"nom":nom},
                 "geometry":{"type":"Point","coordinates":[longitude,latitude]}}
                for code,nom,longitude,latitude in [
                    ("25368","Marchaux-Chaudefontaine",6.1,47.3),
                    ("49126","Orée d'Anjou",-1.2,47.3),
                    ("2A308","Sainte-Lucie-de-Tallano",9.0,41.7),
                    ("06001","Aiglun",7.0,43.8),
                ]]},ensure_ascii=False),encoding="utf8")
        self.paths["paca"].write_text(json.dumps({"autorites":[{
            "ark_pactols":"26678/pcrt-test-Aiglun","libelle_pactols":"Aiglun",
            "correspondances":[{
                "relation_editoriale":"correspondance_communale_validee",
                "code_insee":"06001","millesime_cog":2026,
                "validation":{"date":"2026-10-18"}
            }]
        }]}),encoding="utf8")

    def ecrire_csv(self,name,fields,rows):
        with self.paths[name].open("w",encoding="utf-8",newline="") as fh:
            writer=csv.writer(fh)
            writer.writerow(fields)
            writer.writerows(rows)

    def calculer(self,strict=False):
        return construire(**self.paths,sortie=self.sortie,verifier_sha=strict)

    def lire(self,slug):
        return json.loads((self.sortie/("cog-"+slug+".json")).read_text(encoding="utf8"))

    def test_quatre_regions_sans_ark_inferes(self):
        m=self.calculer()
        self.assertEqual(sorted(m["regions"]),["bfc","corse","paca","pdl"])
        self.assertEqual(m["regions"]["paca"]["validations_pactols_existantes"],1)
        for slug in ("bfc","pdl","corse"):
            self.assertEqual(self.lire(slug)["alignements_Pactols_COG_valides_2026"],[])
        self.assertEqual(self.lire("paca")["geometries_historiques"],[])
        self.assertEqual(self.lire("bfc")["periodes_com"][0]["libelle"],"Marchaux")

    def test_coma_comd_comparest_rattache_2026(self):
        self.calculer()
        d=self.lire("pdl")
        obs=d["observations_COMA_COMD_2026"]
        self.assertEqual(len(obs),1)
        self.assertEqual((obs[0]["code_insee"],obs[0]["comparent_2026"]),
                         ("49069","49126"))

    def test_mouvement_sans_conserver_ancienne_geometrie(self):
        self.calculer()
        d=self.lire("corse")
        self.assertTrue(any(x["code_avant"]=="20308" and x["code_apres"]=="2A308"
                            and x["date_effet"]=="1976-01-01"
                            for x in d["lignes_mouvements_cog"]))
        geo=json.loads((self.sortie/"contours-2026-corse.geojson").read_text())
        self.assertEqual(geo["features"][0]["properties"]["millesime"],2026)
        self.assertIsNone(geo["features"][0]["properties"]["ark_pactols_valide_2026"])
        self.assertEqual(d["geometries_historiques"],[])

    def test_bornes_fermees_ouvertes(self):
        self.assertTrue(periode_active({"debut_inclus":"1943-01-01",
                    "fin_exclue":"2018-01-01"},"2017-01-01"))
        self.assertFalse(periode_active({"debut_inclus":"1943-01-01",
                    "fin_exclue":"2018-01-01"},"2018-01-01"))
        self.assertFalse(periode_active({"debut_inclus":"2018-01-01",
                    "fin_exclue":"2018-01-01"},"2018-01-01"))

    def test_sources_non_officielles_refusees_en_production(self):
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            self.calculer(strict=True)


if __name__ == "__main__":
    unittest.main()
