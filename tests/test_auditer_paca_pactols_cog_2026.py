"""PACA : croisement du pilote sans décision nouvelle ni invalidation implicite."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_paca_pactols_cog_2026 import croiser

class TestPACA(unittest.TestCase):
    def test_pilote_absent_rdf_non_supprime(self):
        cog={"06001":{"code":"06001","libelle":"Aiglun","departement":"06"}}
        pil={"06001":{"ark":"26678/pcrtTest","libelle":"Aiglun","date_validation":"2026-10-18"}}
        rdf={"explicites":{"06001":[]},"lexicaux_sans_exactMatch_987":{},
             "concepts_RDF_examines":50556}
        report=croiser(cog,pil,rdf)
        self.assertEqual(report["bilan"]["pilote_valide_preexistant"],1)
        self.assertEqual(report["bilan"]["pilote_non_retrouve_dans_RDF"],1)
        self.assertEqual(report["communes"][0]["ark_pilote"],"26678/pcrtTest")
        self.assertEqual(report["bilan"]["nouveaux_ARK_publies"],0)
        self.assertEqual(report["bilan"]["geometries_ajoutees"],0)

    def test_exactmatch_hors_pilote_reste_candidat(self):
        cog={"06001":{"code":"06001","libelle":"Aiglun","departement":"06"}}
        hit={"ark":"26678/pcrtTest","insee_exactMatch":[{"famille":"commune","code":"06001","uri":"http://id.insee.fr/geo/commune/06001"}],
             "deprecie":False,"remplace":False,
             "codes_communaux_cites":["06001"],"prefLabels_fr":["Aiglun"]}
        scan={"explicites":{"06001":[hit]},"lexicaux_sans_exactMatch_987":{},
              "concepts_RDF_examines":50556}
        report=croiser(cog,{},scan)
        self.assertEqual(report["communes"][0]["statut_rdf"],"ELIGIBLE_SELON_REGLE")
        self.assertEqual(report["bilan"]["eligibles_hors_pilote"],1)
        self.assertEqual(report["communes"][0]["nouvelle_decision_editoriale"],"NON_PRISE")
        self.assertEqual(report["communes"][0]["publication_cette_recette"],"NON_PUBLIEE")

if __name__=="__main__":unittest.main()
