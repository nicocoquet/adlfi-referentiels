"""Non-régression sur la comparaison des racines de Pactols et cas ambigus."""
import importlib.util,unittest
from pathlib import Path
mfile=Path(__file__).resolve().parents[1]/'scripts/auditer_variantes_hierarchiques.py'
spec=importlib.util.spec_from_file_location('audit_hierarchies_lieux',mfile)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class HierarchiesTests(unittest.TestCase):
    def test_prefixed_root_can_be_ignored_even_with_an_old_label(self):
        a=['26678/Europe','26678/France','26678/lieu']
        l=['Europe','France','Lieu']
        p=[m.ROOT_CURRENT]+a
        self.assertEqual(m.normaliser_racine(p,['_entités politiques et administratives actuelles']+l),(tuple(a),tuple(l)))
    def test_substantive_ancestor_must_stay(self):
        a=['26678/branch','26678/lieu'];l=['entités du passé','Lieu']
        self.assertEqual(m.normaliser_racine(a,l),(tuple(a),tuple(l)))
    def test_mismatched_chain_is_rejected(self):
        with self.assertRaises(ValueError):m.normaliser_racine(['1','2'],['A'])
    def test_label_only_classification(self):
        p={(('1','2'),('Europe','Ville')),(('1','2'),('Europe','Ville nouvelle'))}
        self.assertEqual(m.categoriser(p),'variantes_de_libelles_sans_changement_ark')
    def test_hydro_classification(self):
        p={(('1','2'),('Europe hydrographie','Lac')),(('1','4','2'),('_espaces géographiques aquatiques','Europe hydrographique','lac'))}
        self.assertEqual(m.categoriser(p),'hierarchies_hydrographiques_alternatives')
    def test_blank_ancestors_are_alerts(self):
        p={(('1','x','2'),('Europe','','Lieu')),(('1','2'),('Europe','Lieu'))}
        self.assertEqual(m.categoriser(p),'ancetre_sans_libelle_xml_a_reconstituer')

if __name__=='__main__':unittest.main()
