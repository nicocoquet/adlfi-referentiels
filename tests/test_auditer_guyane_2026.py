"""Tests sans réseau de l'audit Guyane COG / Pactols / géométries."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_guyane_2026 import (
    normaliser, lire_reference, lire_pactols, extraire_histoire, generer, revue_26_candidats,
)

RDF_FIXTURE='''<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#">
  <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtEXACT">
    <skos:prefLabel xml:lang="fr">Cayenne</skos:prefLabel>
    <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97302"/>
    <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/75056"/>
  </skos:Concept>
  <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtHOMONYME">
    <skos:prefLabel xml:lang="fr">Cayenne</skos:prefLabel>
  </skos:Concept>
  <rdf:Description rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtMANA">
    <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
    <skos:altLabel xml:lang="fr">Mana</skos:altLabel>
    <skos:closeMatch rdf:resource="https://id.insee.fr/geo/commune/97306"/>
  </rdf:Description>
  <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtOUTSIDE">
    <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97370"/>
  </skos:Concept>
  <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtUNRELATED">
    <skos:prefLabel xml:lang="fr">Paris</skos:prefLabel>
  </skos:Concept>
</rdf:RDF>'''


class AuditerGuyaneTests(unittest.TestCase):
    def test_index_public_contient_22_communes_exactes(self):
        rows=lire_reference(ROOT/"docs/data/lieux-outremer/recherche-2026.json")
        self.assertEqual(len(rows),22)
        self.assertEqual(rows["97302"],"Cayenne")
        self.assertEqual(rows["97361"],"Awala-Yalimapo")
        self.assertEqual(rows["97362"],"Papaichton")
        self.assertEqual(rows["97357"],"Grand-Santi")
        self.assertEqual(normaliser("Rémire-Montjoly"),normaliser("Remire-Montjoly"))

    def test_pactols_citation_insee_est_differente_homonymie(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"pactols.rdf"
            p.write_text(RDF_FIXTURE,encoding="utf8")
            c,stats=lire_pactols(p,{"97302":"Cayenne","97306":"Mana"})
        self.assertEqual(stats["concepts_examines"],5)
        self.assertEqual(stats["concepts_avec_code_insee_guyane"],3)
        self.assertEqual(stats["liens_insee_rejetes_hors_communes_2026"],1)
        self.assertEqual(stats["liens_insee_non_courants"][0]["code_insee_cite"],"97370")
        self.assertEqual(stats["liens_insee_non_courants"][0]["statut"],"IDENTITE_HISTORIQUE_A_INSTRUIRE")
        self.assertEqual(len(c["97302"]["uri_insee_citees"]),1)
        self.assertEqual(
            c["97302"]["uri_insee_citees"][0]["codes_communes_INSEE_exactMatch"],
            ["75056","97302"])
        self.assertFalse(c["97302"]["uri_insee_citees"][0]["concept_remplace"])
        self.assertEqual(len(c["97302"]["candidatures_lexicales"]),2)
        self.assertEqual(len(c["97306"]["uri_insee_citees"]),1)
        self.assertEqual(c["97306"]["uri_insee_citees"][0]["predicat"],"closeMatch")
        self.assertEqual(c["97306"]["candidatures_lexicales"][0]["labels_concordants"][0]["propriete"],"altLabel")
        self.assertTrue(all(e["statut"]=="LIEN_SOURCE_NON_VALIDE_PAR_EDITORIAL"
                            for rows in c.values() for e in rows["uri_insee_citees"]))

    def test_histoire_deux_cotes_du_mouvement_sans_succession_automatique(self):
        curr=[
            {"COM":"97302","LIBELLE":"Cayenne","TYPECOM":"COM","REG":"03","DEP":"973"},
            {"COM":"97361","LIBELLE":"Awala-Yalimapo","TYPECOM":"COM","REG":"03","DEP":"973"},
        ]
        hist=[
            {"COM":"97302","TYPECOM":"COM","LIBELLE":"Cayenne",
             "DATE_DEBUT":"1943-01-01","DATE_FIN":""},
            {"COM":"97361","TYPECOM":"COM","LIBELLE":"Awala-Yalimapo",
             "DATE_DEBUT":"1989-01-01","DATE_FIN":""},
            {"COM":"97306","TYPECOM":"COM","LIBELLE":"Mana",
             "DATE_DEBUT":"1943-01-01","DATE_FIN":"1989-01-01"},
        ]
        moves=[{"MOD":"20","DATE_EFF":"1989-01-01",
                "COM_AV":"97306","COM_AP":"97361","TYPECOM_AV":"COM",
                "TYPECOM_AP":"COM","LIBELLE_AV":"Mana","LIBELLE_AP":"Awala-Yalimapo"}]
        percode, episodes, events=extraire_histoire(
            curr,hist,moves,{"97302":"Cayenne","97361":"Awala-Yalimapo"})
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]["COM_AV"],"97306")
        self.assertEqual(events[0]["COM_AP"],"97361")
        self.assertEqual(len(episodes),3)
        self.assertEqual(percode["97361"][0]["debut_inclus"],"1989-01-01")
        self.assertTrue(all(x["geometrie_historique"] is None for x in episodes))
        self.assertTrue(all(x["identite_juridique_retroactive"]=="NON_ETABLIE"
                            for x in episodes))

    def test_registre_editorial_conserve_les_codes_historiques_distincts(self):
        report={
            "communes":[{"code_COG_2026":"97302","libelle_COG_2026":"Cayenne",
                "pactols_uri_insee_source":[{
                    "ark":"26678/pcrtCAY","libelles_fr":[{"libelle":"Cayenne","propriete":"prefLabel"}],
                    "predicat":"exactMatch","uri_insee":"http://id.insee.fr/geo/commune/97302",
                    "concept_deprecie":False}]}],
            "bilan":{"source_Pactols_stats":{"liens_insee_non_courants":[{
                "code_insee_cite":"97351","ark":"26678/pcrtOLD",
                "libelles_fr":[{"libelle":"Approuague (chef-lieu Régina)","propriete":"prefLabel"}],
                "predicat":"exactMatch","uri_insee":"http://id.insee.fr/geo/commune/97351",
                "concept_deprecie":False}]}}
        }
        percode={"97351":[{"libelle":"Approuague (chef-lieu Régina)",
                           "debut_inclus":"1953-01-01"}]}
        rows=revue_26_candidats(report,percode)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0][2],"COMMUNE_COG_2026")
        self.assertEqual(rows[0][9],"A_INSTRUIRE")
        self.assertEqual(rows[1][2],"CODE_COG_HISTORIQUE_NON_COURANT")
        self.assertEqual(rows[1][9],"A_INSTRUIRE_HISTORIQUE")
        self.assertEqual(rows[1][8],"non")

    def test_refus_contradiction_entre_cog_courant_et_export(self):
        with self.assertRaisesRegex(ValueError,"non conforme"):
            extraire_histoire(
                [{"COM":"97302","LIBELLE":"Cayenne","TYPECOM":"COM",
                  "DEP":"973","REG":"03"}],
                [],[],{"97302":"Régina"})

    def test_rapport_ne_valide_ni_ark_ni_contour(self):
        c={"97302":"Cayenne"}
        rows=generer(c,{"97302":[]},[],[],
           {"97302":{"statut":"PRESENTE_VALIDE_A_QUALIFIER",
                     "contour_adopte":False,"geometrie_historique":None}},
           {"97302":{"uri_insee_citees":[{"ark":"26678/pcrtTEST"}],
                    "candidatures_lexicales":[]}},
           {"concepts_examines":1})
        self.assertEqual(rows["bilan"]["communes_COG_2026"],1)
        self.assertEqual(rows["bilan"]["candidatures_avec_uri_source"],1)
        self.assertEqual(rows["bilan"]["correspondances_Pactols_validees_par_cet_audit"],0)
        self.assertEqual(rows["bilan"]["contours_adoptes_par_cet_audit"],0)
        self.assertEqual(rows["communes"][0]["statut_alignement_Pactols"],"A_INSTRUIRE")


if __name__=="__main__":
    unittest.main()
