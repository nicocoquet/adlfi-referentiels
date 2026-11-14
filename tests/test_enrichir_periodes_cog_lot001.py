import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from enrichir_periodes_cog_lot001 import enrichir,lire_historique

# Véritable graphe produit par les 23 mouvements transmis dans le lot 001 ;
# les couples Insee sont synthétiques dans ces tests, jamais publiés.
GRAPH=ROOT/'docs/lieux/recette/graphe-episodes-cog-lot001.json'

class PeriodesCOG(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.graph=self.root/'graphe.json'
        self.graph.write_text(GRAPH.read_text(encoding='utf8'),encoding='utf8')
        self.hist=self.root/'historique.csv'
        self.out=self.root/'resultat'
        self.states=json.loads(self.graph.read_text(encoding='utf8'))['etats_administratifs']
        self.rows=[]
        for x in self.states:
            if x['typecom']=='COM':
                a=x['entrees_aux_dates_evenements']
                b=x['sorties_aux_dates_evenements']
                begin=a[0] if a else '1943-01-01'
                end=b[0] if b else ''
                self.rows.append(dict(TYPECOM='COM',COM=x['code'],LIBELLE=x['libelle'],DATE_DEBUT=begin,DATE_FIN=end))
        # Cet état a réellement commencé en 1972 : le jeu synthétique
        # exerce le cas sans confondre période et année d'opération.
        for r in self.rows:
            if r['LIBELLE']=='Allaines-Mervilliers':r['DATE_DEBUT']='1972-12-28'
        self.write_hist()

    def write_hist(self):
        with self.hist.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,delimiter=';',fieldnames=['TYPECOM','COM','LIBELLE','DATE_DEBUT','DATE_FIN'])
            w.writeheader();w.writerows(self.rows)

    def report(self):
        return enrichir(self.graph,self.hist,self.out)

    def get(self,libelle,typ='COM'):
        doc=json.loads((self.out/'graphe-episodes-cog-lot001-dates.json').read_text())
        return next(x for x in doc['etats_administratifs'] if x['libelle']==libelle and x['typecom']==typ)

    def test_provenance_et_non_validation(self):
        report=self.report()
        self.assertEqual(report['nombre_etats_du_graphe'],33)
        self.assertEqual(report['operations'],11)
        self.assertEqual(report['arcs_evenements'],23)
        self.assertEqual(report['nouveaux_alignements_pactols_cog_valides'],0)
        self.assertEqual(report['geometries_historiques_validees'],0)
        self.assertTrue((self.out/'revue-periodes-cog-lot001.csv').is_file())
        with (self.out/'revue-periodes-cog-lot001.csv').open(encoding='utf-8-sig') as stream:
            self.assertTrue(all(x['validation_geometrie_historique']=='non_valide' for x in csv.DictReader(stream,delimiter=';')))

    def test_episodes_distincts_code_79185(self):
        self.report()
        a=self.get('Mougon'); b=self.get('Mougon-Thorigné'); c=self.get('Aigondigné')
        self.assertEqual({a['code'],b['code'],c['code']},{'79185'})
        self.assertEqual([x['periode_code_libelle_cog']['date_debut'] for x in (a,b,c)],['1943-01-01','2017-01-01','2019-01-01'])
        self.assertEqual(b['periode_code_libelle_cog']['date_fin_exclusive'],'2019-01-01')
        self.assertIsNone(c['periode_code_libelle_cog']['date_fin_exclusive'])
        self.assertFalse(c['periode_validite_officielle_complete'])

    def test_commune_deleguee_ne_recoit_pas_periode_com(self):
        self.report()
        comd=self.get('Allaines-Mervilliers','COMD')
        com=self.get('Allaines-Mervilliers')
        self.assertEqual(comd['statut_qualification_temporelle'],'aucun_couple_code_libelle_trouve')
        self.assertIsNone(comd['periode_code_libelle_cog'])
        self.assertEqual(com['periode_code_libelle_cog']['date_debut'],'1972-12-28')
        self.assertEqual(com['periode_code_libelle_cog']['date_fin_exclusive'],'2019-01-01')

    def test_codes_departement_mutation(self):
        self.report()
        old=next(x for x in json.loads((self.out/'graphe-episodes-cog-lot001-dates.json').read_text())['etats_administratifs'] if x['code']=='20001' and x['libelle']=='Afa')
        new=next(x for x in json.loads((self.out/'graphe-episodes-cog-lot001-dates.json').read_text())['etats_administratifs'] if x['code']=='2A001' and x['libelle']=='Afa')
        self.assertEqual(old['periode_code_libelle_cog']['date_fin_exclusive'],'1976-01-01')
        self.assertEqual(new['periode_code_libelle_cog']['date_debut'],'1976-01-01')

    def test_dates_incoherentes_ne_sont_pas_certifiees(self):
        for row in self.rows:
            if row['LIBELLE']=='Mougon-Thorigné':
                row['DATE_DEBUT']='2020-01-01';row['DATE_FIN']='2021-01-01'
        self.write_hist();self.report()
        state=self.get('Mougon-Thorigné')
        self.assertEqual(state['statut_qualification_temporelle'],'couples_trouves_mais_dates_incompatibles')
        self.assertIsNone(state['periode_code_libelle_cog'])

    def test_identite_homonyme_sur_plusieurs_intervalles_ne_peut_pas_etre_forcee(self):
        # Deux intervalles qui satisfont les bornes événementielles de l'état
        # Aigondigné : classification comme ambiguïté, sans choix arbitraire.
        self.rows.append(dict(TYPECOM='COM',COM='79185',LIBELLE='Aigondigné',DATE_DEBUT='2018-01-01',DATE_FIN=''))
        self.write_hist(); self.report()
        state=self.get('Aigondigné')
        self.assertEqual(state['statut_qualification_temporelle'],'plusieurs_periodes_compatibles_a_instruire')
        self.assertIsNone(state['periode_code_libelle_cog'])

    def test_intervalle_nul_insee_conserve_mais_non_attribuable(self):
        # Le véritable fichier Insee 2026 contient des lignes DATE_DEBUT=DATE_FIN.
        # Un intervalle vide est une preuve de source, pas une durée de vie.
        self.rows.append(dict(TYPECOM='COM',COM='2A001',LIBELLE='Afa',
                              DATE_DEBUT='1976-01-01',DATE_FIN='1976-01-01'))
        self.write_hist()
        out=self.report()
        self.assertEqual(out['lignes_historique_insee']['intervalles_de_duree_nulle'],1)
        records=json.loads((self.out/'graphe-episodes-cog-lot001-dates.json').read_text())['etats_administratifs']
        rec=next(x for x in records if x['code']=='2A001' and x['libelle']=='Afa')
        self.assertEqual(rec['statut_qualification_temporelle'],'couple_code_libelle_unique_compatible')
        self.assertEqual(rec['periode_code_libelle_cog']['date_debut'],'1976-01-01')

    def test_sha_incorrect_est_refuse(self):
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            enrichir(self.graph,self.hist,self.out,'0'*64)

    def test_dates_intervalles_invalides_sont_refusees(self):
        self.rows[0]['DATE_FIN']='1800-01-01'
        self.write_hist()
        with self.assertRaises(ValueError):lire_historique(self.hist)

if __name__=='__main__':unittest.main()
