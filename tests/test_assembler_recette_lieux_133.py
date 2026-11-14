import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from assembler_recette_lieux_133 import verifier_entrees,assembler

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.dir=Path(self.tmp.name);self.pilote=self.dir/'pilot.json';self.aud=self.dir/'audit.json';self.geo=self.dir/'geo.json';self.out=self.dir/'out'
        self.valid=[dict(ark_pactols=f'26678/pcrtPACA{i:03}',correspondances=[dict(code_insee=f'83{i:03}',libelle_cog=f'Paca {i}',validation=dict(statut='VALIDE_EDITEUR_2026_10_18'))]) for i in range(103)]
        self.cand=[dict(ark_pactols=f'26678/pcrtTEST{i:03}',code_cog_2026_candidat=f'33{i:03}',nom_geojson_2026=f'Candidate {i}',
            statut_geometrie_2026='code_present_nom_concordant',statut_validation_lien_pactols_cog='non_valide',geometrie_historique_validee=False) for i in range(30)]
        self.write()
    def write(self):
        self.pilote.write_text(json.dumps({'totaux':{'autorites_pactols':103},'provenance':{'millesime_cog':2026},'autorites':self.valid}))
        self.aud.write_text(json.dumps({'statut':'audit_non_validant','candidatures':self.cand}))
        all_rows=[(f'83{i:03}',f'Paca {i}') for i in range(103)]+[(f'33{i:03}',f'Candidate {i}') for i in range(30)]
        geo={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'code':c,'nom':n},
               'geometry':{'type':'Polygon','coordinates':[[[0,0],[1,0],[1,1],[0,0]]]}} for c,n in all_rows]}
        self.geo.write_text(json.dumps(geo))
    def test_assemblage_avec_validations_distinguees(self):
        report=assembler(self.pilote,self.aud,self.geo,self.out,sha_attendu=None)
        self.assertEqual((report['validations_preexistantes'],report['candidatures_non_validees'],report['communes_distinctes']),(103,30,133))
        result=json.loads((self.out/'carte-lieux-recette-133-communes-2026-100m.geojson').read_text())
        statuses=[x['properties']['statut_lien_pactols_cog'] for x in result['features']]
        self.assertEqual(statuses.count('valide_pilote_paca_2026'),103)
        self.assertEqual(statuses.count('candidat_non_valide'),30)
        self.assertTrue(all(x['properties']['validation_geometrie_historique']=='non' for x in result['features']))
    def test_collision_code_interdite(self):
        self.cand[0]['code_cog_2026_candidat']='83000';self.write()
        with self.assertRaisesRegex(ValueError,'Collision'):verifier_entrees(self.pilote,self.aud)
    def test_statut_non_valide_obligatoire(self):
        self.cand[0]['statut_validation_lien_pactols_cog']='valide';self.write()
        with self.assertRaisesRegex(ValueError,'sans arbitrage'):verifier_entrees(self.pilote,self.aud)
    def test_source_epreuve(self):
        with self.assertRaisesRegex(ValueError,'empreinte incorrecte'):
            assembler(self.pilote,self.aud,self.geo,self.out,sha_attendu='0'*64)
    def test_contour_manquant_bloquant(self):
        d=json.loads(self.geo.read_text());d['features']=d['features'][:-1];self.geo.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'absents'):assembler(self.pilote,self.aud,self.geo,self.out,sha_attendu=None)

if __name__=='__main__':unittest.main()
