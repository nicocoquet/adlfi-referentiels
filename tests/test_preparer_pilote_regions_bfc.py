"""Non-régression du pilote cartographique BFC sans réseau."""
import sys, unittest, tempfile, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from preparer_pilote_regions_bfc import analyser,publier,ctrl_geom

def geom():
    ring=[[4.0+i*0.11,45.5+(i%2)*0.1] for i in range(22)]
    ring.append(ring[0])
    return {"type":"Feature","geometry":{"type":"Polygon","coordinates":[ring]},"properties":{}}
def row(year, code, nom):
    return {"year":year,"reg_code":[code],"reg_name":[nom],"geo_shape":geom()}

class RegionsBFCTests(unittest.TestCase):
    def setUp(self):
        self.rows=[row("2015","26","Bourgogne"),
                   row("2015","43","Franche-Comté"),
                   row("2016","27","Bourgogne-Franche-Comté")]
    def test_trois_polygones_mais_seulement_deux_millesimes(self):
        geo,rapport=analyser(self.rows,"sha",3)
        self.assertEqual([f["properties"]["code_region"] for f in geo["2015"]["features"]],["26","43"])
        self.assertEqual([f["properties"]["code_region"] for f in geo["2016"]["features"]],["27"])
        self.assertEqual(rapport["nombre_geometries_historiques_inferrees"],0)
        self.assertEqual(rapport["nombre_nouveaux_alignements_pactols"],0)
        for y in geo:
            self.assertEqual(geo[y]["provenance"]["annee"],int(y))
            self.assertTrue(geo[y]["provenance"]["absence_de_retroprojection"])
    def test_refuse_couche_2015_remplacee_par_geometrie_2016(self):
        rows=[r for r in self.rows if not (r["year"]=="2015" and r["reg_code"]==["43"])]
        with self.assertRaisesRegex(ValueError,"Il faut 1 entrée"):
            analyser(rows,"sha",2)
    def test_refuse_nom_incorrect(self):
        self.rows[0]["reg_name"]=["Bourgogne-Franche-Comté"]
        with self.assertRaisesRegex(ValueError,"Nom ODS différent du COG"):
            analyser(self.rows,"sha",3)
    def test_interdit_écriture_dans_pages(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"docs"):
                publier({}, {}, Path(d)/"docs"/"lieux")
    def test_coordinates_valides(self):
        self.assertEqual(ctrl_geom(geom()),23)
if __name__=="__main__":
    unittest.main()
