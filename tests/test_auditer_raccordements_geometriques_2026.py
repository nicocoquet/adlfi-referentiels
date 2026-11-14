import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from auditer_raccordements_geometriques_2026 import construire

COLS=['n','libelle_pactols','ark_pactols','departement_pactols','code_cog_2026_candidat','statut_alignement_pactols_cog']

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.lot=self.root/'lot.csv';self.geo=self.root/'geo.json';self.out=self.root/'out'
        self.rows=[dict(zip(COLS,['1','Abrest','26678/pcrtTEST01','03','03001','non_valide'])),
                   dict(zip(COLS,['2','Aucun','26678/pcrtTEST02','03','03002','non_valide']))]
        self.features=[{'type':'Feature','properties':{'code':'03001','nom':'Abrest'},
                       'geometry':{'type':'Polygon','coordinates':[[[0,0],[1,0],[1,1],[0,0]]]}}]
        self.write()
    def write(self):
        with self.lot.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=COLS,delimiter=';');w.writeheader();w.writerows(self.rows)
        self.geo.write_text(json.dumps({'type':'FeatureCollection','features':self.features}),encoding='utf-8')
    def test_present_absent_conserve_non_validation(self):
        report=construire([self.lot],self.geo,self.out)
        self.assertEqual(report['candidatures'],2)
        self.assertEqual(report['repartition'],{'code_present_nom_concordant':1,'code_sans_contour_dans_source':1})
        payload=json.loads((self.out/'raccordements-candidats-cog2026.json').read_text())
        self.assertTrue(all(x['statut_validation_lien_pactols_cog']=='non_valide' for x in payload['candidatures']))
        self.assertTrue(all(x['geometrie_historique_validee'] is False for x in payload['candidatures']))
        self.assertEqual(len(json.loads((self.out/'contours-candidats-cog2026.geojson').read_text())['features']),1)
    def test_nom_divergent_alerte(self):
        self.features[0]['properties']['nom']='Autre commune';self.write()
        r=construire([self.lot],self.geo,self.out)
        self.assertEqual(r['repartition']['code_present_nom_a_verifier'],1)
    def test_refus_doublon_code_geo(self):
        self.features.append(self.features[0]);self.write()
        with self.assertRaisesRegex(ValueError,'dupliqués'):construire([self.lot],self.geo,self.out)
    def test_refus_requalification_publiee(self):
        self.rows[0]['statut_alignement_pactols_cog']='valide';self.write()
        with self.assertRaisesRegex(ValueError,'validation'):construire([self.lot],self.geo,self.out)
    def test_verrou_millesime_et_generalisation(self):
        with self.assertRaisesRegex(ValueError,'verrouillé'):
            construire([self.lot],self.geo,self.out,millesime=2025)

if __name__=='__main__':unittest.main()
