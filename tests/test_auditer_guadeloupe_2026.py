"""Tests synthétiques de l'audit Guadeloupe COG/Pactols et statuts distincts."""
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_guadeloupe_2026 import (
    lire_reference,lire_pactols,selectionner_exactmatch_eligibles,
    extraire_histoire,normaliser,
)

RDF='''<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#">
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtTEST1">
   <skos:prefLabel xml:lang="fr">Les Abymes</skos:prefLabel>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97101"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtTEST2">
   <skos:prefLabel xml:lang="fr">Basse-Terre</skos:prefLabel>
   <skos:closeMatch rdf:resource="http://id.insee.fr/geo/commune/97105"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtTEST3">
   <skos:prefLabel xml:lang="fr">Les Abymes</skos:prefLabel>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97101"/>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/75056"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtOLD971">
   <skos:prefLabel xml:lang="fr">Saint-Barthélemy</skos:prefLabel>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97123"/>
 </skos:Concept>
</rdf:RDF>'''


def mock_report():
    names=lire_reference(ROOT/"docs/data/lieux-outremer/recherche-2026.json")
    items=[]
    for code,name in sorted(names.items()):
        links=[]
        if code=="97101":
            links=[{"ark":"26678/pcrtA","predicat":"exactMatch",
                    "concept_deprecie":False,"concept_remplace":False,
                    "codes_communes_INSEE_exactMatch":[code],
                    "uri_insee":"http://id.insee.fr/geo/commune/"+code,
                    "libelles_fr":[{"propriete":"prefLabel","libelle":name}]}]
        if code=="97105":
            links=[{"ark":"26678/pcrtB","predicat":"closeMatch",
                    "concept_deprecie":False,"concept_remplace":False,
                    "codes_communes_INSEE_exactMatch":[],
                    "uri_insee":"http://id.insee.fr/geo/commune/"+code,
                    "libelles_fr":[{"propriete":"prefLabel","libelle":name}]}]
        if code=="97134":
            links=[{"ark":"26678/pcrtC","predicat":"exactMatch",
                    "concept_deprecie":True,"concept_remplace":False,
                    "codes_communes_INSEE_exactMatch":[code],
                    "uri_insee":"http://id.insee.fr/geo/commune/"+code,
                    "libelles_fr":[{"propriete":"prefLabel","libelle":name}]}]
        items.append({"code_COG_2026":code,"libelle_COG_2026":name,
                      "pactols_uri_insee_source":links})
    return {"communes":items}


class GuadeloupeAuditTests(unittest.TestCase):
    def test_cog_32_codes_non_contigus(self):
        noms=lire_reference(ROOT/"docs/data/lieux-outremer/recherche-2026.json")
        self.assertEqual(len(noms),32)
        self.assertEqual(noms["97101"],"Les Abymes")
        self.assertEqual(noms["97105"],"Basse-Terre")
        self.assertEqual(noms["97134"],"Vieux-Habitants")
        self.assertNotIn("97123",noms)
        self.assertNotIn("97127",noms)
        self.assertEqual(normaliser("Morne-à-l'Eau"),normaliser("Morne-à-l’Eau"))

    def test_rdf_exactclose_historique_et_conflit_externe(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"fixture.rdf";path.write_text(RDF,encoding="utf8")
            concepts,meta=lire_pactols(path,{"97101":"Les Abymes","97105":"Basse-Terre"})
        self.assertEqual(meta["concepts_examines"],4)
        self.assertEqual(meta["concepts_avec_code_insee_guadeloupe"],4)
        self.assertEqual(meta["liens_insee_rejetes_hors_communes_2026"],1)
        self.assertEqual(meta["liens_insee_non_courants"][0]["code_insee_cite"],"97123")
        self.assertEqual(len(concepts["97101"]["uri_insee_citees"]),2)
        self.assertEqual(concepts["97105"]["uri_insee_citees"][0]["predicat"],"closeMatch")
        self.assertEqual(concepts["97101"]["uri_insee_citees"][1]["codes_communes_INSEE_exactMatch"],
                         ["75056","97101"])

    def test_exactmatch_univoque_mais_pas_proximite(self):
        r={x["code_insee"]:x for x in selectionner_exactmatch_eligibles(mock_report())}
        self.assertEqual(len(r),32)
        self.assertEqual(r["97101"]["statut"],"ELIGIBLE_SELON_REGLE")
        self.assertEqual(r["97105"]["statut"],"A_INSTRUIRE")
        self.assertIn("PREDICAT_NON_EXACT",r["97105"]["motif"])
        self.assertEqual(r["97134"]["statut"],"A_INSTRUIRE")
        self.assertIn("CONCEPT_DEPRECIE",r["97134"]["motif"])
        self.assertEqual(r["97102"]["statut"],"A_INSTRUIRE")

    def test_conflits_d_autre_code_exclus(self):
        report=mock_report()
        item=next(x for x in report["communes"] if x["code_COG_2026"]=="97101")
        item["pactols_uri_insee_source"][0]["codes_communes_INSEE_exactMatch"]=["75056","97101"]
        r={x["code_insee"]:x for x in selectionner_exactmatch_eligibles(report)}
        self.assertEqual(r["97101"]["statut"],"A_INSTRUIRE")
        self.assertIn("CONFLIT_EXACTMATCH",r["97101"]["motif"])

    def test_l_historique_ne_remplace_pas_communes_actuelles(self):
        noms={"97101":"Les Abymes","97134":"Vieux-Habitants"}
        current=[{"COM":code,"LIBELLE":name,"TYPECOM":"COM",
                  "DEP":"971","REG":"01"} for code,name in noms.items()]
        periods=[
            {"COM":code,"LIBELLE":name,"TYPECOM":"COM",
             "DATE_DEBUT":"1946-03-21","DATE_FIN":""} for code,name in noms.items()]
        periods.append({"COM":"97123","LIBELLE":"Saint-Barthélemy","TYPECOM":"COM",
                        "DATE_DEBUT":"1946-03-21","DATE_FIN":"2007-07-15"})
        moves=[{"MOD":"99","DATE_EFF":"2007-07-15","TYPECOM_AV":"COM",
                "COM_AV":"97123","LIBELLE_AV":"Saint-Barthélemy",
                "TYPECOM_AP":"COM","COM_AP":"97701","LIBELLE_AP":"Saint-Barthélemy"}]
        bycode,episodes,events=extraire_histoire(current,periods,moves,noms)
        self.assertEqual(len(episodes),3)
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]["COM_AV"],"97123")
        self.assertIn("97123",bycode)
        self.assertEqual(len([e for e in episodes if e["fin_exclue"] is None]),2)
        self.assertTrue(all(x["geometrie_historique"] is None for x in episodes))


if __name__=="__main__":
    unittest.main()
