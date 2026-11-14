import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from auditer_statuts_delegues_associes import analyser

GRAPH=ROOT/'docs/lieux/recette/graphe-episodes-cog-lot001-dates.json'

class DeleguesAssocies(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.graphe=self.root/'dates.json'
        self.graphe.write_bytes(GRAPH.read_bytes())
        self.current=self.root/'communes.csv'
        self.movements=self.root/'mvt.csv'
        self.out=self.root/'out'
        self.data=json.loads(self.graphe.read_text(encoding='utf8'))
        self.byid={r['id']:r for r in self.data['etats_administratifs']}
        self.today=[]
        for s in self.data['etats_administratifs']:
            if s['typecom']=='COMD':
                self.today.append({'TYPECOM':'COMD','COM':s['code'],'LIBELLE':s['libelle'],'COMPARENT':'79185' if s['dossier']=='Aigondigné' else '28199'})
        self.events=[]
        for a in self.data['arcs_evenements']:
            before=self.byid[a['etat_avant_id']];after=self.byid[a['etat_apres_id']]
            self.events.append({'DATE_EFF':a['date_effet'],'MOD':a['mod'],
                'TYPECOM_AV':before['typecom'],'COM_AV':before['code'],'LIBELLE_AV':before['libelle'],
                'TYPECOM_AP':after['typecom'],'COM_AP':after['code'],'LIBELLE_AP':after['libelle']})
        self.write_files()

    def write_files(self):
        for path, rows, cols in [(self.current,self.today,['TYPECOM','COM','LIBELLE','COMPARENT']),
                                 (self.movements,self.events,['DATE_EFF','MOD','TYPECOM_AV','COM_AV','LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP'])]:
            with path.open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=cols,delimiter=';')
                writer.writeheader();writer.writerows(rows)

    def results(self):
        rep=analyser(self.graphe,self.current,self.movements,self.out)
        observed=json.loads((self.out/'audit-statut-delegue-associe-lot001.json').read_text())['observations']
        return rep,observed

    def test_six_delegues_presents_une_associee_terminee(self):
        rep,states=self.results()
        self.assertEqual(rep['nombre_etats'],7)
        self.assertEqual(rep['repartition'],{'absent_2026_sortie_attestee':1,'present_au_cog_2026':6})
        self.assertEqual(len(states),7)
        com_a=next(x for x in states if x['typecom']=='COMA')
        self.assertEqual(com_a['libelle'],'Mervilliers')
        self.assertEqual(com_a['date_derniere_sortie_attestee'],'2019-01-01')
        self.assertIsNone(com_a['comparent_2026'])
        for row in states:
            self.assertFalse(row['date_debut_complete_certifiee'])
            self.assertFalse(row['geometrie_historique_validee'])
            self.assertEqual(row['statut_lien_pactols_cog'],'non_valide')

    def test_parent_2026_et_date_entree_attestee(self):
        rep,states=self.results()
        allaines=next(x for x in states if x['libelle']=='Allaines-Mervilliers')
        self.assertEqual(allaines['comparent_2026'],'28199')
        self.assertEqual(allaines['date_premiere_entree_attestee'],'2019-01-01')
        mougon=next(x for x in states if x['libelle']=='Mougon')
        self.assertEqual(mougon['comparent_2026'],'79185')
        self.assertEqual(mougon['date_premiere_entree_attestee'],'2017-01-01')

    def test_absence_sans_sortie_alertee(self):
        self.today=[x for x in self.today if x['COM']!='28002']
        self.write_files()
        rep,states=self.results()
        x=next(x for x in states if x['code']=='28002')
        self.assertEqual(x['statut_au_millesime_2026'],'absent_2026_sans_sortie_identifiee')

    def test_sha_mouvements_bloquant(self):
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            analyser(self.graphe,self.current,self.movements,self.out,'0'*64)

    def test_doublon_de_statut_actif_bloquant(self):
        self.today.append(self.today[0].copy())
        self.write_files()
        with self.assertRaisesRegex(ValueError,'Doublon'):
            self.results()

if __name__=='__main__':unittest.main()
