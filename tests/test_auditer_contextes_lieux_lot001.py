"""Tests unitaires de l'analyse contextuelle Lieux, sans les XML privés."""
import importlib.util
import json
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/'scripts/auditer_contextes_lieux_lot001.py'
spec=importlib.util.spec_from_file_location('module_lieux_contextes',P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def occ(ark, labels, notice='xml::notice-1', path=None):
    arks=path or ['26678/root'+str(i) for i in range(len(labels)-1)]+[ark]
    return {'ark_terminal':ark,'chaine_libelles_fr':json.dumps(labels),
            'chaine_ark':json.dumps(arks),'notice_id':notice,
            'libelle_terminal_fr':labels[-1],
            'fichier_relatif':'jeu_essai.xml','zone_tei':'p'}

class ContextesTests(unittest.TestCase):
    def test_normaliser_les_accents_et_espaces(self):
        self.assertEqual(m.normalize('L’Île-d’Yeu'), 'l ile d yeu')
        self.assertEqual(m.normalize('ÉTREMBIÈRES'), 'etrembieres')

    def test_racine_facultative_ne_cree_pas_de_conflit(self):
        old=(['26678/root','26678/place'],['France','Lyon'])
        recent=(['26678/current']+old[0],['entités actuelles']+old[1])
        self.assertEqual(m.canon_path(*old),m.canon_path(*recent))

    def test_changement_de_departement_pas_cache(self):
        a=(['26678/root','26678/depA','26678/place'],['France','Département du Jura','Ville'])
        b=(['26678/current']+['26678/root','26678/depB','26678/place'],
            ['entités actuelles','France','Département du Doubs','Ville'])
        self.assertNotEqual(m.canon_path(*a),m.canon_path(*b))

    def test_transdepartemental_est_une_alerte_non_invalidante(self):
        ark='26678/place'
        master=occ(ark,['France','Département du Jura','Lieu'])
        others=[occ('26678/x'+str(i),['France','Département du Doubs','CommuneX'],path=['26678/root','26678/depB','26678/x'+str(i)]) for i in range(3)]
        context={master['notice_id']:[master]+others}
        meta={master['notice_id']:{'titre':'Prospections inter-départementales'}}
        r=m.contextual_flags(ark,[master],context,meta,'Lieu')
        self.assertEqual(len(r['outliers']),1)
        self.assertFalse(r['has_title'])
        self.assertEqual(r['num_notices'],1)

    def test_titre_interdepartemental_avec_commune_ne_doit_pas_etre_ecarte(self):
        ark='26678/place'
        master=occ(ark,['France','Département du Jura','Lieu'])
        context={master['notice_id']:[master]}
        meta={master['notice_id']:{'titre':'Lieu — Site archéologique'}}
        r=m.contextual_flags(ark,[master],context,meta,'Lieu')
        self.assertTrue(r['has_title'])
        self.assertFalse(r['outliers'])

    def test_index_ark_terminal_incoherent_declenche_une_erreur(self):
        ark='26678/correct'
        corrupt=occ('26678/incorrect',['France','Département du Jura','Lieu'])
        context={corrupt['notice_id']:[corrupt]}
        with self.assertRaisesRegex(ValueError,'Chaîne Pactols incohérente'):
            m.contextual_flags(ark,[corrupt],context,{corrupt['notice_id']:{'titre':'Lieu'}},'Lieu')

if __name__=='__main__':unittest.main()
