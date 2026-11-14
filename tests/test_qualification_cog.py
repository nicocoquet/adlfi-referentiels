"""Tests du tri non validant des candidatures géographiques historiques."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json, csv, sys, unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from qualifier_candidatures_cog import construire, extraire_departements, code_departement


def enregistrer_csv(path, headers,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=headers,delimiter=';');w.writeheader();w.writerows(rows)


def autorite(ark,nom,chemin,profil='sous_departement_candidat_communal',valide=False):
    return {'ark_pactols':ark,'libelle_documentaire':nom,
        'profil_geographique_provisoire':profil,'statut_raccordement':'candidature_lexicale_un_code_a_instruire',
        'hierarchies_pactols_attestees':[{'libelles':chemin,'arks':[]}],
        'annees_operation_attestees':[2022],
        'attestation_temoin':{'notice_id':'notice-1'},
        'validation_existante':{'code_insee':'13055'} if valide else None}


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        d=Path(self.tmp.name)
        self.a,self.c,self.d=[d/x for x in ['autorites.json','candidatures.csv','departements.csv']]
        self.out=d/'out'
        ars=[
            autorite('26678/pcrtA','Ambérieu',['France',"Département de l'Ain",'Ambérieu']),
            autorite('26678/pcrtB','Saint-Martin',['France','Département du Calvados','Saint-Martin']),
            autorite('26678/pcrtC','Dauphiné',['Europe physique','Alpes','Dauphiné'],'geographie_physique_hors_cog_communal'),
            autorite('26678/pcrtD','Arandon',['France',"Département de l'Isère",'Arandon-Passins','Arandon'],'sous_commune_ou_lieu_imbrique_a_qualifier'),
            autorite('26678/pcrtE','Marseille',['France','Département des Bouches-du-Rhône','Marseille'],valide=True),
            autorite('26678/pcrtF','Bourgs',['France','Département du Cher','Bourgs']),
        ]
        self.a.write_text(json.dumps({'unite':'concept_pactols_atteste_dans_XML','autorites':ars},ensure_ascii=False))
        codes={
            '26678/pcrtA':['01004'],
            '26678/pcrtB':['14099','50100'],
            '26678/pcrtD':['38001'],
            '26678/pcrtE':['13055'],
            '26678/pcrtF':['99999'],
        }
        entries=[]
        for a in ars:
            for code in codes.get(a['ark_pactols'],[]):
                entries.append({'ark_pactols':a['ark_pactols'],'code_insee_historique':code,
                    'libelle_cog':a['libelle_documentaire'],'date_debut':'1943-01-01','date_fin':''})
        enregistrer_csv(self.c,['ark_pactols','code_insee_historique','libelle_cog','date_debut','date_fin'],entries)
        enregistrer_csv(self.d,['DEP','LIBELLE'],[
            {'DEP':a,'LIBELLE':b} for a,b in [('01','Ain'),('14','Calvados'),('50','Manche'),('38','Isère'),('13','Bouches-du-Rhône'),('18','Cher')]])

    def lire(self,f):
        with (self.out/f).open(encoding='utf-8-sig',newline='') as h:
            return list(csv.DictReader(h,delimiter=';'))

    def test_categories_ne_creent_aucune_validation(self):
        report=construire(self.a,self.c,self.d,self.out,taille_lot=2)
        self.assertEqual(report['autorites'],6)
        self.assertEqual(report['candidatures_lignes'],6)
        rows={x['ark_pactols']:x for x in self.lire('audit_candidatures_par_ark.csv')}
        self.assertEqual(rows['26678/pcrtA']['categorie_audit'],'un_code_corrobore_par_departement')
        self.assertEqual(rows['26678/pcrtB']['categorie_audit'],'homonymie_nationale_reduite_a_un_code_par_departement')
        self.assertEqual(json.loads(rows['26678/pcrtB']['codes_cog_departement_concordants']),['14099'])
        self.assertEqual(rows['26678/pcrtC']['categorie_audit'],'hors_perimetre_cog_communal')
        self.assertEqual(rows['26678/pcrtD']['categorie_audit'],'lieu_imbrique_ou_ancienne_commune_a_instruire')
        self.assertEqual(rows['26678/pcrtE']['categorie_audit'],'alignement_editorial_preexistant')
        self.assertEqual(rows['26678/pcrtF']['categorie_audit'],'conflit_departement_cog_vs_pactols')
        lot=self.lire('lot_editorial_prioritaire_001.csv')
        self.assertEqual(len(lot),2)
        self.assertEqual({x['ark_pactols'] for x in lot},{'26678/pcrtA','26678/pcrtB'})
        self.assertTrue(all(x['statut_validation']=='non_valide' for x in lot))

    def test_prefixe_cog_et_articles_departement(self):
        self.assertEqual(code_departement('97105'),'971')
        self.assertEqual(code_departement('2A004'),'2A')
        self.assertEqual(code_departement('01004'),'01')
        self.assertEqual(extraire_departements([{'libelles':["Département de l'Ain",'test']},
                         {'libelles':['Département des Bouches-du-Rhône','test']}]),
                         ['Ain','Bouches-du-Rhône'])

    def test_reproductibilite(self):
        construire(self.a,self.c,self.d,self.out,taille_lot=2)
        a={p.name:p.read_bytes() for p in self.out.iterdir()}
        construire(self.a,self.c,self.d,self.out,taille_lot=2)
        self.assertEqual(a,{p.name:p.read_bytes() for p in self.out.iterdir()})


if __name__=='__main__':unittest.main()
