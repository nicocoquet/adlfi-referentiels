import csv,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from auditer_lieux_bfc_cog import classer,identite,jlist,sha,SHAS

def row(code='39012',dept='25'):
    return {'ark_pactols':'26678/fixture','codes_insee_skos':json.dumps([code]),'departement_hierarchie':dept}

class BourgogneFrancheComte(unittest.TestCase):
    def test_types_admin_and_code_historique_non_corrige(self):
        self.assertEqual(classer(row(),[{'TYPECOM':'COMA'}]),'commune_associee_2026')
        self.assertEqual(classer(row(),[]),'code_historique_absent_cog2026')
        self.assertEqual(classer(row('25368'),[{'TYPECOM':'COM'},{'TYPECOM':'COMD'}]),'code_partage_COM_COMD_2026')
        self.assertEqual(classer(row('25368'),[{'TYPECOM':'COM','DEP':'25','REG':'27'}]),'commune_COM_2026_code_departement_concordant')
        self.assertEqual(classer(row('25368'),[{'TYPECOM':'COM','DEP':'39','REG':'27'}]),'commune_COM_2026_territoire_a_verifier')
        self.assertEqual(classer({'codes_insee_skos':'[]'},[]),'hors_code_communal_numerique')
    def test_pactols_json_codes_pas_de_supposition(self):
        self.assertEqual(jlist('[]'),[])
        with self.assertRaises(ValueError):jlist('"39012"')
        with self.assertRaises(ValueError):jlist('[39012]')
    def test_identifiants_etats_distincts(self):
        a=identite({'code':'25368','typecom':'COM','libelle':'Marchaux'},'etat:')
        b=identite({'code':'25368','typecom':'COMD','libelle':'Marchaux'},'etat:')
        self.assertNotEqual(a,b)
        self.assertEqual(a,identite({'libelle':'Marchaux','typecom':'COM','code':'25368'},'etat:'))
    def test_inventaire_pilote_regional(self):
        root=Path(__file__).resolve().parents[1]/'docs/lieux/recette'
        full=root/'inventaire-bourgogne-franche-comte.csv'
        self.assertEqual(sha(full),SHAS['inventaire'])
        def read(path):
            with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=';'))
        allrows=read(full);pilot=read(root/'lot-01-bourgogne-franche-comte.csv')
        self.assertEqual((len(allrows),len(pilot)),(736,25))
        indexes={x['ark_pactols']:x for x in allrows}
        self.assertEqual(len(indexes),736)
        for r in pilot:self.assertEqual(indexes[r['ark_pactols']],r)

if __name__=='__main__':unittest.main()
