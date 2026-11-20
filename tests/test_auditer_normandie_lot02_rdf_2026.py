"""Non-régression des vingt ARK normands (qualification sans validation)."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import auditer_normandie_lot02_rdf_2026 as m  # noqa: E402


def fake():
    explicit={}
    extras={}
    for code,c in m.CASES.items():
        explicit[code]=[]
        for kind in ('actuel','ancien'):
            ark=c[kind]
            label=c['label_'+kind]
            uri='http://id.insee.fr/geo/commune/'+code
            explicit[code].append({
                'ark':ark,'prefLabels_fr':[label],'altLabels_fr':[],
                'deprecie':False,
                'insee_exactMatch':[{'famille':'commune','code':code,'uri':uri}],
            })
            extras[ark]={
                'prefLabels_fr':[label], 'altLabels_fr':[],
                'owl_deprecated':False, 'dct_isReplacedBy':[],
                'dct_replaces':[], 'notes':[],
                'exactMatch':[uri],
            }
    return {'explicites':explicit,'concepts_RDF_examines':50556},extras


class NormandieLot02Tests(unittest.TestCase):
    def test_dix_codes_et_vingt_ark_sans_validation(self):
        self.assertEqual(len(m.CASES),10)
        self.assertEqual(len({a for c in m.CASES.values()
                              for a in (c['ancien'],c['actuel'])}),20)
        self.assertEqual(m.CASES['27112']['label_actuel'],'Breteuil (Eure)')
        self.assertEqual(m.CASES['14342']['label_ancien'],
                         'Isigny-sur-Mer (commune déléguée)')
        scan,meta=fake()
        with patch.object(m,'sha256',return_value=m.RDF_SHA), \
             patch.object(m,'analyser_rdf',return_value=scan), \
             patch.object(m,'rdf_complementaire',return_value=meta):
            report=m.produire(Path('epingle.rdf'))
        self.assertEqual(report['bilan']['ARK_candidats'],20)
        self.assertEqual(report['bilan']['nouvelles_validations'],0)
        self.assertEqual(report['bilan']['nouvelles_geometries'],0)
        self.assertEqual(report['bilan']['liens_historiques_inferes'],0)
        self.assertTrue(all(d['decision_editoriale']=='NON_PRISE' for d in report['dossiers']))
        self.assertNotIn('notice_id',json.dumps(report))

    def test_disparition_d_un_exactmatch_refusee(self):
        scan,meta=fake()
        scan['explicites']['61341'].pop()
        with patch.object(m,'sha256',return_value=m.RDF_SHA), \
             patch.object(m,'analyser_rdf',return_value=scan), \
             patch.object(m,'rdf_complementaire',return_value=meta):
            with self.assertRaisesRegex(ValueError,'modifiées'):
                m.produire(Path('epingle.rdf'))

    def test_changement_prefLabel_refuse(self):
        scan,meta=fake()
        meta[m.CASES['27112']['actuel']]['prefLabels_fr']=['Breteuil (Oise)']
        with patch.object(m,'sha256',return_value=m.RDF_SHA), \
             patch.object(m,'analyser_rdf',return_value=scan), \
             patch.object(m,'rdf_complementaire',return_value=meta):
            with self.assertRaisesRegex(ValueError,'Libellé'):
                m.produire(Path('epingle.rdf'))

    def test_empreinte_fausse_refusee(self):
        with patch.object(m,'sha256',return_value='invalid'):
            with self.assertRaisesRegex(ValueError,'source épinglée'):
                m.produire(Path('incorrect.rdf'))


if __name__=='__main__':
    unittest.main()
