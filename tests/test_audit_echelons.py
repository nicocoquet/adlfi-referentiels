"""Tests d'audit des catégories sans mutation du maître éditorial."""
import unittest
from scripts.audit_echelons import audit_org_rows


def authority(ident,kind,level,name=None,visible='non'):
    return {'organisme_id':ident,'nom_normalise':name or ident,
            'type_organisme':kind,'echelon_territorial':level,
            'statut_validation':'valide','affichage_catalogue':visible}


class AuditEchelonsTests(unittest.TestCase):
    def test_museum_not_excluded_from_level(self):
        result=audit_org_rows([authority('ORG-0013','musee','communal',visible='oui')])
        self.assertEqual(result['summary']['levels_nonempty'],1)
        self.assertEqual(result['summary']['visible_with_level'],1)
        self.assertEqual(result['issues'],[])

    def test_alsace_identity_split_is_flagged(self):
        result=audit_org_rows([authority('ORG-0093','collectivite_territoriale','regional')])
        self.assertIn('identite_juridique_a_scinder',
                      [x['code_controle'] for x in result['issues']])
        self.assertEqual(result['summary']['focus'],1)

    def test_metropole_is_not_level(self):
        result=audit_org_rows([authority('ORG-0161','collectivite_territoriale','metropole')])
        codes={r['code_controle'] for r in result['issues']}
        self.assertEqual(codes,{'forme_vs_echelon','nature_collectivite_a_verifier'})

    def test_port_vendres_anomaly(self):
        result=audit_org_rows([authority('ORG-0429','collectivite_territoriale',
                                         'intercommunal','Commune de Port-Vendres')])
        codes={r['code_controle'] for r in result['issues']}
        self.assertEqual(codes,{'nature_collectivite_a_verifier','commune_non_communale'})

    def test_epci_intercommunal_is_coherent(self):
        result=audit_org_rows([authority('ORG-0652','epci','intercommunal')])
        self.assertEqual(result['summary']['focus'],1)
        self.assertEqual(result['issues'],[])

    def test_syndicat_mixte_stays_undetermined(self):
        result=audit_org_rows([authority('ORG-0093','syndicat_mixte','')])
        self.assertEqual(result['summary']['focus'],1)
        self.assertEqual(result['issues'],[])

    def test_national_private_activity_not_institutional(self):
        result=audit_org_rows([authority('ORG-0500','entreprise','national')])
        self.assertEqual([r['code_controle'] for r in result['issues']],['portee_vs_niveau'])


if __name__=='__main__':
    unittest.main()
