import csv
import json
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from preparer_lots_lieux_regions import (REGIONS, PRESELECTION_ARK, skos_insee,
    classe_geo,classe_risque,prepare)

class QualificationRegionale(unittest.TestCase):
    def test_codes_region_et_departement(self):
        self.assertEqual({v['code'] for v in REGIONS.values()},{'94','52','27'})
        self.assertEqual(REGIONS['Corse']['departements']['Département de la Haute-Corse'],'2B')
        self.assertEqual(REGIONS['Bourgogne-Franche-Comté']['departements']['Territoire de Belfort'],'90')

    def test_skos_types_codes_et_uuid_separes(self):
        code,typ,other=skos_insee(json.dumps([
            'http://id.insee.fr/geo/commune/2B002',
            'http://id.insee.fr/geo/commune/39012',
            'http://id.insee.fr/geo/communeDeleguee/ef312e8c-b172-40ed-b169-8bf72e16ba8b',
            'http://id.insee.fr/geo/departement/25',
            'https://www.wikidata.org/wiki/Q123']))
        self.assertEqual(code,['2B002','39012'])
        self.assertIn('communeDeleguee',typ)
        self.assertIn('departement',typ)
        self.assertEqual(len(other),2)

    def test_typage_commune_lieu_imbrique_et_region(self):
        info=REGIONS['Pays de la Loire']
        self.assertEqual(classe_geo(['Europe','Pays de la Loire'],info),'region_administrative_ou_historique')
        self.assertEqual(classe_geo(['Europe','Pays de la Loire','Département de la Sarthe','Béthon'],info),'commune_candidate_directe')
        self.assertEqual(classe_geo(['Europe','Pays de la Loire','Département de la Sarthe','X','Y'],info),'lieu_imbrique_sous_departement')

    def test_code_different_departement_n_est_pas_corrige(self):
        d={'ark_pactols':'26678/pcrtANt29rHaDo','categorie_geographique':'lieu_imbrique_sous_departement',
           'departement_hierarchie':'70','codes_insee_skos':'["52210"]','autres_uris_insee':'[]',
           'concordance_code_departement':'code_hors_departement_de_hierarchie'}
        self.assertEqual(classe_risque(d),'H1_episode_historique_interdepartemental')
        d['ark_pactols']='26678/pcrtthzSDyCh4Z'
        self.assertEqual(classe_risque(d),'H1_episode_historique_interdepartemental')

    def test_anomalie_ark_et_objet_non_communal_prioritaires(self):
        r={'ark_pactols':'26678/pcrtXSoREPOwqU'}
        self.assertTrue(classe_risque(r).startswith('X1'))
        r={'ark_pactols':'26678/pcrt2jEAL85n1L'}
        self.assertTrue(classe_risque(r).startswith('T3'))

    def test_preselections_sans_doublons(self):
        for reg,arks in PRESELECTION_ARK.items():
            self.assertEqual(len(arks),len(set(arks)),reg)
            self.assertTrue(all(x.startswith('26678/') for x in arks))

    def test_donnees_reelles_si_disponibles(self):
        src=Path('/mnt/data/lieux_v2_work')
        output=ROOT/'resultats'
        if not (src/'autorites_lieux.csv').is_file() or not (ROOT/'controle_concepts_pactols.csv').is_file():
            self.skipTest('Sources XML locales absentes')
        summary=prepare(src/'autorites_lieux.csv',src/'occurrences_lieux.csv',
                        ROOT/'controle_concepts_pactols.csv',output,25)
        self.assertEqual(summary['synthese']['ark_regionaux_distincts'],1742)
        self.assertEqual(summary['synthese']['occurrences_region_hierarchie'],5898)
        self.assertEqual(summary['synthese']['ark_avec_lien_commune_insee_code_lisible'],1718)
        self.assertEqual(summary['synthese']['ark_code_hors_departement'],3)
        for reg,info in REGIONS.items():
            with (output/f'lot-01-{info["slug"]}.csv').open(encoding='utf-8-sig',newline='') as f:
                rows=list(csv.DictReader(f,delimiter=';'))
            self.assertEqual(len(rows),25)
            self.assertEqual(len({x['ark_pactols'] for x in rows}),25)
            self.assertTrue(set(PRESELECTION_ARK[reg]) <= {x['ark_pactols'] for x in rows})
            self.assertTrue(all(x['statut_validation_pactols_cog']=='non_nouvellement_valide' for x in rows))

if __name__=='__main__':unittest.main()
