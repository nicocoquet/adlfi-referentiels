"""Tests autonomes de la construction nationale : pas d'alignement lexical publié."""
from pathlib import Path
from tempfile import TemporaryDirectory
import csv
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from construire_referentiel_lieux_national import construire, normaliser, typer

ARK_A = '26678/pcrtAAAA001'
ARK_B = '26678/pcrtBBBB002'
ARK_C = '26678/pcrtCCCC003'
ARK_D = '26678/pcrtDDDD004'


def csv_source(path, headers, rows, sep=';'):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=headers, delimiter=sep)
        wr.writeheader()
        wr.writerows(rows)


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        d = Path(self.folder.name)
        self.a, self.o, self.l, self.h = [d / x for x in ('autorites.csv','occurrences.csv','alignements.csv','historique.csv')]
        self.out = d / 'resultats'
        rows = [
            (ARK_A, 'Ambérieu', '[1945]'),
            (ARK_B, 'Saint-Martin', '[2020]'),
            (ARK_C, 'Dauphiné', '[2001]'),
            (ARK_D, 'Saint-Germain', '[20232]'),
        ]
        csv_source(self.a, ['ark_pactols','libelle_fr_xml','annees_operation_relevees',
                            'alignement_pilote','code_insee_2026_valide'],
                   [dict(zip(['ark_pactols','libelle_fr_xml','annees_operation_relevees'],p),
                         alignement_pilote='valide_pilote_paca_2026' if p[0]==ARK_D else '',
                         code_insee_2026_valide='12345' if p[0]==ARK_D else '')
                    for p in rows])
        paths = [
            ['Europe','France','France métropolitaine','Auvergne-Rhône-Alpes',
             "Département de l'Ain",'Ambérieu'],
            ['Europe','France','France métropolitaine','Normandie',
             'Département du Calvados','Saint-Martin'],
            ['Europe physique','Alpes','Dauphiné'],
            ['Europe','France','France métropolitaine','Bourgogne',
             'Département de la Côte-d’Or','Saint-Germain'],
        ]
        headers=['ark_terminal','libelle_terminal_fr','chaine_ark',
                 'chaine_libelles_fr','notice_id','fichier_relatif']
        csv_source(self.o,headers,[
            {'ark_terminal': ark, 'libelle_terminal_fr': label,
             'chaine_ark':json.dumps(['26678/pcrtROOT']*(len(path)-1)+[ark]),
             'chaine_libelles_fr':json.dumps(path,ensure_ascii=False),
             'notice_id':'notice_'+str(i),'fichier_relatif':'xml_'+str(i)}
            for i,((ark,label,_),path) in enumerate(zip(rows,paths))])
        csv_source(self.l,['ark_pactols','statut','code_insee_2026'],
                   [{'ark_pactols':ARK_D,'statut':'valide_pilote_paca_2026',
                     'code_insee_2026':'12345'}])
        csv_source(self.h,['TYPECOM','COM','LIBELLE','DATE_DEBUT','DATE_FIN'],[
            {'TYPECOM':'COM','COM':'01004','LIBELLE':'Ambérieu',
             'DATE_DEBUT':'1943-01-01','DATE_FIN':'1955-03-31'},
            {'TYPECOM':'COM','COM':'01004','LIBELLE':'Ambérieu-en-Bugey',
             'DATE_DEBUT':'1955-03-31','DATE_FIN':''},
            {'TYPECOM':'COM','COM':'14099','LIBELLE':'Saint-Martin',
             'DATE_DEBUT':'1943-01-01','DATE_FIN':''},
            {'TYPECOM':'COM','COM':'50100','LIBELLE':'Saint-Martin',
             'DATE_DEBUT':'1943-01-01','DATE_FIN':''},
            {'TYPECOM':'ARM','COM':'75056','LIBELLE':'Dauphiné',
             'DATE_DEBUT':'1943-01-01','DATE_FIN':''},
        ],',')

    def donnees(self):
        return json.loads((self.out/'autorites_nationales.json').read_text())['autorites']

    def test_aucune_candidature_sans_fichier_cog(self):
        report = construire(self.a,self.o,self.l,self.out)
        self.assertEqual(report['nombre_autorites'],4)
        self.assertEqual(report['nombre_lignes_candidatures_historiques'],0)
        self.assertEqual(report['nombre_alignees_paca_2026'],1)
        self.assertTrue(all(not x['codes_cog_candidats'] for x in self.donnees()))

    def test_forme_historique_avec_dates_cog(self):
        report = construire(self.a,self.o,self.l,self.out,self.h)
        self.assertEqual(report['nombre_lignes_candidatures_historiques'],3)
        by = {r['ark_pactols']:r for r in self.donnees()}
        self.assertEqual(by[ARK_A]['codes_cog_candidats'],['01004'])
        self.assertEqual(by[ARK_A]['statut_raccordement'],
                         'candidature_lexicale_un_code_a_instruire')
        self.assertEqual(by[ARK_B]['codes_cog_candidats'],['14099','50100'])
        self.assertEqual(by[ARK_B]['statut_raccordement'],
                         'homonymie_plusieurs_codes_a_instruire')
        self.assertEqual(by[ARK_C]['codes_cog_candidats'],[])
        self.assertEqual(by[ARK_D]['validation_existante']['code_insee'],'12345')
        self.assertEqual(by[ARK_D]['annees_operation_invalides'],['20232'])
        self.assertEqual(report['nombre_annees_invalides_ark'],1)

    def test_sorties_reproductibles(self):
        construire(self.a,self.o,self.l,self.out,self.h)
        first={x.name:x.read_bytes() for x in self.out.iterdir()}
        construire(self.a,self.o,self.l,self.out,self.h)
        self.assertEqual(first,{x.name:x.read_bytes() for x in self.out.iterdir()})

    def test_interdiction_ecrasement_source(self):
        # Le nom de fichier source peut être celui d'une sortie, mais le dossier
        # de sortie n'est pas interdit par principe si les chemins sont distincts.
        forbidden = self.a.parent / 'autorites_nationales.json'
        forbidden.write_bytes(self.a.read_bytes())
        with self.assertRaises(ValueError):
            construire(forbidden,self.o,self.l,self.a.parent)

    def test_normalisation_ne_vaut_pas_preuve(self):
        self.assertEqual(normaliser('L’Île-d’Yeu'),normaliser("L'Ile d Yeu"))
        self.assertNotEqual(normaliser('Saint-Martin'),normaliser('Saint-Martin-de-Ré'))
        self.assertEqual(typer([{'libelles':['Europe physique','Alpes']}]),
                         'geographie_physique_hors_cog_communal')

    def test_objets_hors_champ_non_confondus_avec_sans_candidature(self):
        # Arks C (géographie physique) et nouveau profil hors champ doivent
        # être distingués des communes sans correspondance lexicale.
        construire(self.a,self.o,self.l,self.out,self.h)
        self.assertEqual(self.donnees()[2]['statut_raccordement'],
                         'hors_champ_communal_a_qualifier')
        from construire_referentiel_lieux_national import typer
        self.assertEqual(typer([{'libelles':['Monde antique','Gaule']}]),
                         'autre_hors_champ_cog_communal')


if __name__ == '__main__':
    unittest.main()
