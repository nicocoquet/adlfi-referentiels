"""Tests : conservation des sources communales existantes et limites d'une recette Leaflet."""
from __future__ import annotations
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'construire_vue_lieux_leaflet_integree.py'
spec = importlib.util.spec_from_file_location('integration_leaflet', SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False),encoding='utf-8')
    return path


class IntegrationReferentielTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / 'docs' / 'data' / 'lieux-chronologie'
        self.src.mkdir(parents=True)
        for zone in module.REGIONS:
            self.cog(zone)
            self.contours(zone)
        self.lieux = write(self.root / 'docs' / 'data' / 'lieux.json',
            {'schema_version':'0.1.0','totaux':{'autorites_pactols':103},
             'autorites':[{'ark_pactols':f'26678/pcrt{i:04d}'} for i in range(103)]})
        self.core = self.root/'assets/lieux-chronologie-core.js'
        self.core.parent.mkdir(parents=True)
        self.core.write_text('(function(){window.AdlfiLieuxChronologieCore={};})();',encoding='utf-8')
        self.old = self.root/'previous.html'
        data={'schema':'adlfi.lieux.interface_multiechelon_recette.v1',
              'alignements_Pactols_generes':0,
              'aucune_geometrie_2026_retroprojetee':True,
              'layers':{str(y):{
                  'region':[{'properties':{'annee':y,'pactols_valide':False}} for _ in range(n)],
                  'departement':[{'properties':{'annee':y,'pactols_valide':False}} for _ in range(96)]
              } for y,n in ((2015,22),(2016,13))}}
        self.old.write_text('<script id="data" type="application/json">'+json.dumps(data)+'</script>',encoding='utf-8')
        self.modele = self.root/'modele.html'
        self.modele.write_text('<script id="geo">__ADLFI_HISTORICAL_DATA__</script>\n'
            '<script id="comm">__ADLFI_COMMUNAL_DATA__</script>\n'
            '<script>__ADLFI_COMMUNAL_CORE__</script>',encoding='utf-8')
        self.output=self.root/'output'/'integration.html'

    def tearDown(self):
        self.tmp.cleanup()

    def cog(self,zone,liens=None):
        return write(self.src/f'cog-{zone}.json',
            {'schema':'adlfi.lieux.chronologie.4regions.public-recette.v1',
             'region':zone,'geometries_historiques':[],
             'periodes_com':[],'observations_COMA_COMD_2026':[],
             'lignes_mouvements_cog':[],
             'alignements_Pactols_COG_valides_2026':liens if liens is not None else []})

    def contours(self,zone,millesime=2026):
        return write(self.src/f'contours-2026-{zone}.geojson',
           {'type':'FeatureCollection','provenance':{'millesime':millesime},'features':[]})

    def run_generate(self):
        return module.generer(self.modele,self.old,self.src,self.lieux,self.core,self.output)

    def test_generation_reproductible_et_integrite(self):
        rapport=self.run_generate(); first=self.output.read_bytes()
        self.assertEqual(rapport['autorites_pactols_PACA_intactes'],103)
        self.assertEqual(rapport['nouvelles_correspondances_Pactols'],0)
        self.assertEqual(rapport['fichiers_publics_modifies'],0)
        self.assertEqual(len(rapport['sources_communales_SHA256']),9)
        self.assertEqual(self.run_generate(),rapport)
        self.assertEqual(self.output.read_bytes(),first)

    def test_lien_pactols_hors_paca_bloque(self):
        self.cog('bfc',[{'statut':'correspondance_PACA_preexistante_validee','millesime_validation':2026}])
        with self.assertRaisesRegex(ValueError,'hors PACA'):
            self.run_generate()

    def test_source_geometrie_2025_rejetee(self):
        self.contours('pdl',2025)
        with self.assertRaisesRegex(ValueError,'incohérents'):
            self.run_generate()

    def test_103_pactols_obligatoires(self):
        write(self.lieux,{'schema_version':'0.1.0','totaux':{'autorites_pactols':102},'autorites':[]})
        with self.assertRaisesRegex(ValueError,'103 identités'):
            self.run_generate()

    def test_inference_pactols_2015_rejetee(self):
        self.cog('paca',[{'statut':'correspondance_PACA_preexistante_validee','millesime_validation':2015}])
        with self.assertRaisesRegex(ValueError,'sans validation'):
            self.run_generate()

    def test_source_administrative_invalide(self):
        self.old.write_text('<script id="data" type="application/json">{}</script>',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Contrat du jeu'):
            self.run_generate()

    def test_publication_bloquee(self):
        with self.assertRaisesRegex(ValueError,'docs/'):
            module.generer(self.modele,self.old,self.src,self.lieux,self.core,
                self.root/'docs'/'recette.html')

    def test_les_sources_reste_identiques(self):
        before={p.name:module.sha(p) for p in self.src.glob('*')}
        self.run_generate()
        self.assertEqual(before,{p.name:module.sha(p) for p in self.src.glob('*')})


if __name__=='__main__':unittest.main()