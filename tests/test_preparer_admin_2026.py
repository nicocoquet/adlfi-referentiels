"""Tests sans réseau du contrat région/département 2026."""
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('adm2026',Path(__file__).resolve().parents[1]/'scripts/preparer_admin_2026.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

REG=('01','02','03','04','06','11','24','27','28','32','44','52','53','75','76','84','93','94')
DROM=('971','972','973','974','976')

def echantillon():
    reg={code:{'REG':code,'LIBELLE':'Région '+code} for code in REG}
    deps=list(DROM)+[f'{n:03d}' for n in range(1,97)]
    dep={code:{'DEP':code,'REG':REG[i%len(REG)],'LIBELLE':'Département '+code} for i,code in enumerate(deps)}
    for code,par in zip(DROM,REG[:5]):dep[code]['REG']=par
    poly={'type':'Polygon','coordinates':[[[2,47],[3,47],[3,48],[2,47]]]}
    gr={c:{'geometry':poly,'properties':{'code':c}} for c in reg}
    gd={c:{'geometry':poly,'properties':{'code':c}} for c in dep}
    return reg,dep,gr,gd

class Publication2026(unittest.TestCase):
    def test_rattachements_pactols_et_couches(self):
        r,d,rg,dg=echantillon()
        cols,index,rapport=mod.construire(r,d,rg,dg,{'source':'empreinte'})
        self.assertEqual(len(cols['regions-2026.geojson']['features']),18)
        self.assertEqual(len(cols['departements-2026.geojson']['features']),101)
        self.assertEqual(len(index['entries']),119)
        self.assertEqual(index['nouvelles_correspondances_pactols'],0)
        self.assertEqual(rapport['mayotte']['region'],'06')
        self.assertEqual(rapport['zones_ultramarines']['departements'],list(DROM))
        for fc in cols.values():
            self.assertFalse(fc['provenance']['pactols_valide'])
            for feature in fc['features']:
                self.assertFalse(feature['properties']['pactols_valide'])
                self.assertNotIn('ark_pactols',feature['properties'])
        self.assertIn('976',cols['regions-2026.geojson']['features'][4]['properties']['departements'])

    def test_refus_doublon_ou_departement_absent(self):
        r,d,gr,gd=echantillon()
        with self.assertRaisesRegex(ValueError,'sans géométrie'):
            mod.geo_par_codes({'features':list(gd.values())[1:]},d,'departement')
        with self.assertRaisesRegex(ValueError,'dupliqué'):
            mod.geo_par_codes({'features':list(gd.values())+[list(gd.values())[0]]},d,'departement')

    def test_refus_rattachement_non_qualifie(self):
        r,d,gr,gd=echantillon()
        d['976']['REG']='75'
        with self.assertRaisesRegex(ValueError,'Mayotte'):
            mod.construire(r,d,gr,gd,{})
        d['976']['REG']='00'
        with self.assertRaisesRegex(ValueError,'inconnue'):mod.construire(r,d,gr,gd,{})

    def test_refus_contour_inconnu(self):
        r,d,gr,gd=echantillon()
        gd['991']={'properties':{'code':'991'},'geometry':gd['976']['geometry']}
        with self.assertRaisesRegex(ValueError,'hors COG'):
            mod.geo_par_codes({'features':list(gd.values())},d,'departement')

    def test_refus_sortie_pages(self):
        with self.assertRaisesRegex(ValueError,'docs'):
            mod.produire('x','y','z','q','docs/data/lieux-historique')

if __name__=='__main__':unittest.main()
