"""Trois changements de nom PACA : preuve COG distincte des concepts Pactols."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_paca_trois_renommages_rdf_2026 import (
    RDF_SHA, verifier_cog, scan_rdf, construire, match_nom
)

class TestsRenommagesPACA(unittest.TestCase):
    def test_les_trois_dossiers_cog_officiels(self):
        source=json.loads((ROOT/"docs/data/lieux-chronologie/cog-paca.json").read_text(encoding="utf-8"))
        rows=verifier_cog(source)
        self.assertEqual([x["code_COG"] for x in rows],["04045","05127","83052"])
        self.assertEqual([x["date_effet"] for x in rows],
                         ["2024-01-01","2025-01-01","2026-01-01"])
        self.assertTrue(all(x["nature_COG"]=="MOD10_RENOMMAGE_CODE_CONSERVE" for x in rows))
        self.assertEqual(len(source["alignements_Pactols_COG_valides_2026"]),103)

    def test_changement_nom_cog_ne_signifie_pas_identite_pactols(self):
        source=json.loads((ROOT/"docs/data/lieux-chronologie/cog-paca.json").read_text(encoding="utf-8"))
        data=construire(source,{
            "concepts_RDF_examines":3,
            "dossiers":{"04045":[{"ark":"26678/pcrtTest","motifs_de_recuperation":["PREF_LIBELLE_ANCIEN_EXACT"]}],
                       "05127":[],"83052":[]},
            "ARK_directement_assertes_COG_2026":{"04045":[],"05127":[],"83052":[]}
        })
        self.assertEqual(data["bilan"]["nouveaux_ARK_valides"],0)
        self.assertFalse(data["bilan"]["index_public_modifie"])
        self.assertTrue(all(x["nouvelle_validation_2026"] is False for x in data["dossiers"]))

    def test_homonymes_ne_sont_pas_assimiles(self):
        spec={"ancien":"Rousset","nouveau":"Rousset-Serre-Ponçon"}
        self.assertIn("LIBELLE_ANCIEN_AVEC_QUALIFICATIF_OU_HOMONYME",
                      match_nom("Rousset (Bouches-du-Rhône)",spec))
        self.assertEqual(match_nom("Roussillon",spec),[])
        self.assertIn("LIBELLE_NOUVEAU_EXACT",
                      match_nom("Rousset-Serre-Ponçon",spec))

    def test_scan_conserve_les_preuves_et_ne_valide_rien(self):
        xml='''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#"
 xmlns:dct="http://purl.org/dc/terms/" xmlns:xml="http://www.w3.org/XML/1998/namespace">
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtCereste">
  <skos:prefLabel xml:lang="fr">Céreste (Alpes-de-Haute-Provence)</skos:prefLabel>
  <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/12345678-abcd-4321-bcde-abcdef123456"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtla4EHGDgDd">
  <skos:prefLabel xml:lang="fr">Rousset (Hautes-Alpes)</skos:prefLabel>
  <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/05127"/>
  <owl:deprecated>true</owl:deprecated>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrt7B7bs9P5g2">
  <skos:prefLabel xml:lang="fr">Esparron (Var)</skos:prefLabel>
  <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/83052"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtRoussetHomonyme">
  <skos:prefLabel xml:lang="fr">Rousset (Bouches-du-Rhône)</skos:prefLabel>
  <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/13087"/>
 </skos:Concept>
</rdf:RDF>'''
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"fragment.rdf"
            p.write_text(xml,encoding="utf-8")
            with patch("auditer_paca_trois_renommages_rdf_2026.sha256",return_value=RDF_SHA):
                result=scan_rdf(p)
        self.assertEqual(result["ARK_directement_assertes_COG_2026"],
                         {"04045":[],"05127":["26678/pcrtla4EHGDgDd"],
                          "83052":["26678/pcrt7B7bs9P5g2"]})
        cereste=result["dossiers"]["04045"]
        self.assertEqual(len(cereste),1)
        self.assertTrue(cereste[0]["exactMatch_INSEE"][0]["est_UUID"])
        self.assertEqual(cereste[0]["decision_editoriale"],"NON_PRISE")
        rousset=result["dossiers"]["05127"]
        self.assertEqual(len(rousset),2)
        self.assertTrue(any(x["owl_deprecated"] for x in rousset))
        self.assertTrue(any(x["ark"]=="26678/pcrtRoussetHomonyme" for x in rousset))

if __name__=="__main__":
    unittest.main()
