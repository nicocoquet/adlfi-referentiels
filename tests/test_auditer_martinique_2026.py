"""Recette synthétique du lot Martinique : COG, exactMatch et garde-fous."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_martinique_2026 import (
    lire_reference,lire_pactols,normaliser,selectionner_exactmatch_eligibles,
    extraire_histoire, generer,
)

RDF_FIXTURE='''<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#">
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtA">
   <skos:prefLabel xml:lang="fr">Fort-de-France</skos:prefLabel>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97209"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtB">
   <skos:prefLabel xml:lang="fr">Le Lamentin</skos:prefLabel>
   <skos:closeMatch rdf:resource="http://id.insee.fr/geo/commune/97213"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtC">
   <skos:prefLabel xml:lang="fr">Fort-de-France</skos:prefLabel>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97209"/>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/75056"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtOLD">
   <skos:prefLabel xml:lang="fr">Ancienne commune</skos:prefLabel>
   <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97260"/>
 </skos:Concept>
</rdf:RDF>'''


def faire_rapport():
    names=dict(lire_reference(ROOT/"docs/data/lieux-outremer/recherche-2026.json"))
    items=[]
    for code,name in sorted(names.items()):
        links=[]
        if code=="97209":
            links=[{
                "ark":"26678/pcrtFORT","predicat":"exactMatch",
                "concept_deprecie":False,"concept_remplace":False,
                "codes_communes_INSEE_exactMatch":["97209"],
                "uri_insee":"http://id.insee.fr/geo/commune/97209",
                "libelles_fr":[{"propriete":"prefLabel","libelle":"Fort-de-France"}],
            }]
        if code=="97213":
            links=[{
                "ark":"26678/pcrtCLOSE","predicat":"closeMatch",
                "concept_deprecie":False,"concept_remplace":False,
                "codes_communes_INSEE_exactMatch":[],
                "uri_insee":"http://id.insee.fr/geo/commune/97213",
                "libelles_fr":[{"propriete":"prefLabel","libelle":"Le Lamentin"}],
            }]
        if code=="97234":
            links=[{
                "ark":"26678/pcrtBELLE","predicat":"exactMatch",
                "concept_deprecie":True,"concept_remplace":False,
                "codes_communes_INSEE_exactMatch":["97234"],
                "uri_insee":"http://id.insee.fr/geo/commune/97234",
                "libelles_fr":[{"propriete":"prefLabel","libelle":"Bellefontaine"}],
            }]
        items.append({
            "code_COG_2026":code,"libelle_COG_2026":name,
            "pactols_uri_insee_source":links,
        })
    return {"communes":items}


class MartiniqueTests(unittest.TestCase):
    def test_34_communes_officielles_de_l_index_public(self):
        names=lire_reference(ROOT/"docs/data/lieux-outremer/recherche-2026.json")
        self.assertEqual(len(names),34)
        self.assertEqual(names["97209"],"Fort-de-France")
        self.assertEqual(names["97229"],"Schœlcher")
        self.assertEqual(names["97234"],"Bellefontaine")
        self.assertEqual(normaliser("Schœlcher"),normaliser("Schœlcher"))

    def test_source_rdf_et_conflit_code_insee_hors_martinique(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"source.rdf"
            file.write_text(RDF_FIXTURE,encoding="utf8")
            concepts,meta=lire_pactols(file,{"97209":"Fort-de-France","97213":"Le Lamentin"})
        self.assertEqual(meta["concepts_examines"],4)
        self.assertEqual(meta["concepts_avec_code_insee_martinique"],4)
        self.assertEqual(meta["liens_insee_rejetes_hors_communes_2026"],1)
        self.assertEqual(len(concepts["97209"]["uri_insee_citees"]),2)
        self.assertEqual(concepts["97209"]["uri_insee_citees"][1]["codes_communes_INSEE_exactMatch"],
                         ["75056","97209"])
        self.assertEqual(concepts["97213"]["uri_insee_citees"][0]["predicat"],"closeMatch")

    def test_eligibilite_univoque_ne_traite_pas_closematch_et_deprecie(self):
        rows=selectionner_exactmatch_eligibles(faire_rapport())
        bycode={x["code_insee"]:x for x in rows}
        self.assertEqual(len(rows),34)
        self.assertEqual(bycode["97209"]["statut"],"ELIGIBLE_SELON_REGLE")
        self.assertEqual(bycode["97213"]["statut"],"A_INSTRUIRE")
        self.assertIn("PREDICAT_NON_EXACT",bycode["97213"]["motif"])
        self.assertEqual(bycode["97234"]["statut"],"A_INSTRUIRE")
        self.assertIn("CONCEPT_DEPRECIE",bycode["97234"]["motif"])
        self.assertEqual(bycode["97229"]["statut"],"A_INSTRUIRE")

    def test_ambiguite_de_concept_et_autre_exactmatch_exclus(self):
        report=faire_rapport()
        item=next(x for x in report["communes"] if x["code_COG_2026"]=="97209")
        item["pactols_uri_insee_source"][0]["codes_communes_INSEE_exactMatch"]=["75056","97209"]
        row=next(x for x in selectionner_exactmatch_eligibles(report)
                 if x["code_insee"]=="97209")
        self.assertEqual(row["statut"],"A_INSTRUIRE")
        self.assertIn("CONFLIT_EXACTMATCH",row["motif"])

    def test_historique_pas_de_succession_inferree(self):
        current=[
            {"COM":"97209","LIBELLE":"Fort-de-France","TYPECOM":"COM","REG":"02","DEP":"972"},
            {"COM":"97234","LIBELLE":"Bellefontaine","TYPECOM":"COM","REG":"02","DEP":"972"},
        ]
        hist=[
            {"COM":"97209","LIBELLE":"Fort-de-France","TYPECOM":"COM",
             "DATE_DEBUT":"1946-03-19","DATE_FIN":""},
            {"COM":"97234","LIBELLE":"Bellefontaine","TYPECOM":"COM",
             "DATE_DEBUT":"1950-01-01","DATE_FIN":""},
        ]
        movements=[
            {"MOD":"20","DATE_EFF":"1950-01-01","COM_AV":"97204",
             "COM_AP":"97234","TYPECOM_AV":"COM","TYPECOM_AP":"COM",
             "LIBELLE_AV":"Le Carbet","LIBELLE_AP":"Bellefontaine"}
        ]
        bycode,episodes,events=extraire_histoire(
            current,hist,movements,{"97209":"Fort-de-France","97234":"Bellefontaine"})
        self.assertEqual(len(episodes),2)
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]["COM_AV"],"97204")
        self.assertEqual(events[0]["COM_AP"],"97234")
        self.assertTrue(all(e["geometrie_historique"] is None for e in episodes))


if __name__=="__main__":
    unittest.main()
