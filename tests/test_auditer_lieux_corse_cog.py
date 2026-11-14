import csv
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from auditer_lieux_corse_cog import produire,statut_nom

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'docs'/'lieux'/'recette'
if not (SRC/'inventaire-corse.csv').exists():
    SRC=Path('/mnt/data/lieux_regions_2026/resultats')

class AuditCorse(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.inv=SRC/'inventaire-corse.csv';self.lot=SRC/'lot-01-corse.csv'
        if not self.inv.exists() or not self.lot.exists():self.skipTest('Corpus source local non disponible')
        with self.inv.open(encoding='utf-8-sig',newline='') as f:self.auts=list(csv.DictReader(f,delimiter=';'))
        self.com=self.root/'v_commune_2026.csv'
        self.hist=self.root/'v_commune_depuis_1943.csv'
        self.mvt=self.root/'v_mvt_commune_2026.csv'
        self.out=self.root/'out'
        # Jeu officiel simulé et déclaré synthétique : 194 codes présents.
        self.rows=[];self.history=[]
        for a in self.auts:
            codes=json.loads(a['codes_insee_skos'])
            if not codes:continue
            c=codes[0];name=a['pref_fr_pactols']
            if name.endswith(' (Haute-Corse)'):name=name[:-len(' (Haute-Corse)')]
            if name.endswith(' (Corse-du-Sud)'):name=name[:-len(' (Corse-du-Sud)')]
            self.rows.append({'TYPECOM':'COM','COM':c,'REG':'94','DEP':a['departement_hierarchie'],'LIBELLE':name})
            self.history.append({'TYPECOM':'COM','COM':c,'LIBELLE':name,'DATE_DEBUT':'1976-01-01','DATE_FIN':''})
        self.history += [
            {'TYPECOM':'COM','COM':'20001','LIBELLE':'Afa','DATE_DEBUT':'1943-01-01','DATE_FIN':'1976-01-01'},
            {'TYPECOM':'COM','COM':'20002','LIBELLE':'Aghione','DATE_DEBUT':'1943-01-01','DATE_FIN':'1976-01-01'},
        ]
        self.events=[
            {'MOD':'41','DATE_EFF':'1976-01-01','TYPECOM_AV':'COM','COM_AV':'20001','LIBELLE_AV':'Afa',
             'TYPECOM_AP':'COM','COM_AP':'2A001','LIBELLE_AP':'Afa'},
            {'MOD':'41','DATE_EFF':'1976-01-01','TYPECOM_AV':'COM','COM_AV':'20002','LIBELLE_AV':'Aghione',
             'TYPECOM_AP':'COM','COM_AP':'2B002','LIBELLE_AP':'Aghione'},
        ]
        self.write_all()
    def tearDown(self):self.temp.cleanup()
    def write(self,path,rows):
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=rows[0],delimiter=',');w.writeheader();w.writerows(rows)
    def write_all(self):
        self.write(self.com,self.rows);self.write(self.hist,self.history);self.write(self.mvt,self.events)
    def audit(self):return produire(self.inv,self.lot,self.com,self.hist,self.mvt,self.out)
    def test_nombre_et_non_validation(self):
        r=self.audit()
        self.assertEqual((r['autorites'],r['candidatures_skos_code_commune'],r['autres_autorites'],r['premier_lot']),(200,194,6,25))
        self.assertEqual(r['nouvelles_validations_pactols_cog'],0)
        with (self.out/'corse-200-candidatures-cog.csv').open(encoding='utf-8-sig') as f:
            x=list(csv.DictReader(f,delimiter=';'))
        self.assertEqual(len(x),200)
        self.assertTrue(all(a['statut_alignement_adlfi']=='non_valide' for a in x))
        self.assertEqual(sum(a['statut_cog_2026']=='hors_champ_communal' for a in x),6)
    def test_code_corse_1943_et_mouvements(self):
        self.audit()
        with (self.out/'corse-25-prioritaires-cog.csv').open(encoding='utf-8-sig') as f:
            rows=list(csv.DictReader(f,delimiter=';'))
        for name,old in [('Afa','20001'),('Aghione','20002')]:
            a=next(x for x in rows if x['libelle_xml']==name)
            self.assertEqual(a['code_historique_predecessur_mod41'],old)
            self.assertEqual(a['categorie_audit'],'commune_avec_predecesseur_code_mod41')
            self.assertEqual(a['nombre_periodes_historiques_pour_codes'],'2')
    def test_refuser_suppression_preuve(self):
        self.events.pop();self.write_all()
        with self.assertRaisesRegex(ValueError,'Aghione'):self.audit()
    def test_rejet_source_changee(self):
        self.rows[0]['DEP']='99';self.write_all()
        r=self.audit()
        self.assertEqual(r['repartition']['conflit_territorial_cog_2026'],1)
    def test_distinguer_qualification_pactols(self):
        self.assertEqual(statut_nom('Saint-Florent (Haute-Corse)','Saint-Florent'),'qualificatif_departement_documentaire')
        self.assertEqual(statut_nom('Saint-Florent','Saint-Florent'),'identique_normalise')
        self.assertEqual(statut_nom('Saint-Florent','Saint-Etienne'),'divergence_nom_a_instruire')
    def test_hors_cog_pas_geometry(self):
        self.audit();records=json.loads((self.out/'corse-200-historique-detail.json').read_text())['autorites']
        no={r['ark_pactols'] for r in self.auts if not json.loads(r['codes_insee_skos'])}
        self.assertTrue(all(not r['couples_code_libelle_historiques'] for r in records if r['ark_pactols'] in no))

if __name__=='__main__':unittest.main()
