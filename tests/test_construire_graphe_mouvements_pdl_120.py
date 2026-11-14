import csv,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from construire_graphe_mouvements_pdl_120 import construire,M,H

class GraphePdlTests(unittest.TestCase):
    def test_dedoublonner_sans_fusionner_etats(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            fields=list(M)
            item=dict(zip(fields,['32','2016-01-01','COM','49018','Baugé',
                'COMD','49018','Baugé']))
            def make(name,fields,rows):
                f=d/name
                with f.open('w',newline='',encoding='utf-8-sig') as out:
                    wr=csv.DictWriter(out,fieldnames=['code_cible',*fields],delimiter=';')
                    wr.writeheader();wr.writerows(rows)
                return f
            e1=make('a.csv',M,[{'code_cible':'49018',**item}])
            e2=make('b.csv',M,[{'code_cible':'49020',**item}])
            p=dict(zip(H,['49018','COM','Baugé','1943-01-01','2013-01-01']))
            h1=make('c.csv',H,[{'code_cible':'49018',**p}])
            h2=make('d.csv',H,[])
            rpt=construire(e1,e2,h1,h2,d/'out',strict=False)
            self.assertEqual(rpt['lignes_entree'],2)
            self.assertEqual(rpt['lignes_mouvement_distinctes'],1)
            self.assertEqual(rpt['lignes_dupliquees_eliminees'],1)
            self.assertEqual(rpt['periodes_code_libelle'],1)
            self.assertEqual(rpt['groupes_connexes_candidats'],1)
            graph=json.loads((d/'out/graphe-mouvements-pdl-120.json').read_text())
            self.assertEqual(len(graph['etats_observes']),2)
            self.assertEqual(graph['mouvements_lignes'][0]['codes_suivis'],['49018','49020'])
            self.assertEqual(graph['validations_adlfi'],[])
            self.assertEqual(graph['geometries_historiques'],[])

if __name__=='__main__':unittest.main()
