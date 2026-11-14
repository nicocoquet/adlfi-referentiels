import csv,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from qualifier_comparent_22_pdl import analyser

class Parentages22Tests(unittest.TestCase):
    def test_22_code_partage_com_comd_et_changement_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            p=d/'couples.csv'
            with p.open('w',encoding='utf-8-sig',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['code_insee','ark_enfant','libelle_enfant','ark_parent_pactols','libelle_parent_pactols'],delimiter=';')
                w.writeheader()
                w.writerows([{'code_insee':str(49000+i),'ark_enfant':'a'+str(i),'libelle_enfant':'E',
                    'ark_parent_pactols':'p'+str(i),'libelle_parent_pactols':'P'} for i in range(22)])
            c=d/'communes.csv'
            with c.open('w',encoding='utf-8-sig',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['COM','TYPECOM','LIBELLE','COMPARENT','REG','DEP'],delimiter=';')
                w.writeheader()
                w.writerows([{'COM':'49000','TYPECOM':'COM','LIBELLE':'Commune nouvelle',
                               'COMPARENT':'','REG':'52','DEP':'49'},
                             {'COM':'49000','TYPECOM':'COMD','LIBELLE':'Commune ancienne',
                               'COMPARENT':'49126','REG':'52','DEP':'49'},
                             {'COM':'49126','TYPECOM':'COM','LIBELLE':'Parent nouveau',
                               'COMPARENT':'','REG':'52','DEP':'49'},
                             {'COM':'49001','TYPECOM':'COMD','LIBELLE':'Autre ancienne',
                               'COMPARENT':'49001','REG':'52','DEP':'49'}])
            res=analyser(p,c)
            self.assertEqual(len(res),22)
            self.assertEqual(res[0]['comparent_2026'],'49126')
            self.assertEqual(res[0]['nom_commune_parente_2026'],'Parent nouveau')
            self.assertEqual(res[0]['type_de_relation'],'comparent_2026_different_code_historique')
            self.assertEqual(res[1]['type_de_relation'],'comparent_2026_egal_code_historique')
            self.assertEqual(res[2]['type_de_relation'],'pas_de_commune_deleguee_associee_2026')
            self.assertEqual(res[0]['validation_adlfi'],'non_valide')

if __name__=='__main__':unittest.main()
