"""Tests sans réseau pour le criblage des 233 cibles COG ultramarines."""
import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_pactols_outremer_integral import (
    preparer_cibles,scanner_rdf,norm,
)

XML="""<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#" >
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrt-A1">
  <skos:prefLabel xml:lang="fr">Les Abymes</skos:prefLabel>
  <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/97101"/>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrt-KER">
  <skos:prefLabel xml:lang="fr">Archipel des Kerguelen</skos:prefLabel>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrt-TAAF">
  <skos:prefLabel xml:lang="fr">Terres australes et antarctiques françaises</skos:prefLabel>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrt-AB">
  <skos:prefLabel xml:lang="fr">Anse-Bertrand (Guadeloupe)</skos:prefLabel>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrt-PA">
  <skos:altLabel xml:lang="fr">Îles Saint-Paul et Amsterdam</skos:altLabel>
  <owl:deprecated>true</owl:deprecated>
 </skos:Concept>
 <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrt-OTHER">
  <skos:prefLabel xml:lang="fr">Inconnu</skos:prefLabel>
 </skos:Concept>
</rdf:RDF>
"""

class TestCriblagePactolsOutremer(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.rdf=Path(t.name)/"test.rdf"
        self.rdf.write_text(XML,encoding="utf8")
        communes=[
            {"TYPECOM":"COM","DEP":"971","COM":"97101",
             "LIBELLE":"Les Abymes","NCCENR":"Abymes"},
            {"TYPECOM":"COM","DEP":"971","COM":"97102",
             "LIBELLE":"Anse-Bertrand","NCCENR":"Anse-Bertrand"},
            {"TYPECOM":"COM","DEP":"75","COM":"75056",
             "LIBELLE":"Paris","NCCENR":"Paris"},
            {"TYPECOM":"COMD","DEP":"971","COM":"97199",
             "LIBELLE":"Hameau","NCCENR":"Hameau"},
        ]
        comer=[{"COMER":"984","LIBELLE":"Terres australes et antarctiques françaises",
                 "NCCENR":"Terres australes et antarctiques françaises"}]
        zones=[
            {"COM_COMER":"98411","COMER":"984","NATURE_ZONAGE":"DIS",
             "LIBELLE":"Îles Saint-Paul et Amsterdam",
             "NCCENR":"Îles Saint-Paul et Amsterdam"},
            {"COM_COMER":"98412","COMER":"984","NATURE_ZONAGE":"DIS",
             "LIBELLE":"Archipel des Kerguelen","NCCENR":"Archipel des Kerguelen"},
        ]
        self.targets=preparer_cibles(communes,comer,zones)

    def test_cibles_typage_et_exclusions(self):
        self.assertEqual(len(self.targets),5)
        ids={r["cible_id"] for r in self.targets}
        self.assertEqual(ids,{
            "DROM:COM:97101","DROM:COM:97102",
            "COMER:TERRITOIRE:984",
            "COMER:DIS:98411","COMER:DIS:98412"})
        self.assertEqual(norm("Îles Saint-Paul et Amsterdam"),
                         norm("Iles Saint Paul et Amsterdam"))

    def test_recherche_pref_alt_code_et_qualif_sans_validation(self):
        count,found=scanner_rdf(self.rdf,self.targets,{"26678/pcrt-A1"},
                               min_concepts=1)
        self.assertEqual(count,6)
        a=found["DROM:COM:97101"]["26678/pcrt-A1"]
        self.assertIn("pref_fr_exact",a["signaux"])
        self.assertIn("lien_insee_code_meme_valeur",a["signaux"])
        self.assertEqual(a["atteste_XML_AdlFI"],"oui")
        self.assertEqual(a["decision_editoriale"],"NON_VALIDE_A_INSTRUIRE")
        self.assertEqual(found["DROM:COM:97102"]["26678/pcrt-AB"]["signaux"],
                         "pref_fr_qualifie")
        self.assertIn("alt_fr_exact",found["COMER:DIS:98411"]["26678/pcrt-PA"]["signaux"])
        self.assertEqual(found["COMER:DIS:98411"]["26678/pcrt-PA"]["deprecie"],"oui")
        self.assertEqual(
            found["COMER:TERRITOIRE:984"]["26678/pcrt-TAAF"]["nature_zonage"],
            "TERRITOIRE")
        self.assertNotIn("DROM:COM:75056",found)

    def test_refus_fausse_archive_integrale(self):
        with self.assertRaisesRegex(ValueError,"RDF intégral non reconnu"):
            scanner_rdf(self.rdf,self.targets)

    def test_refus_de_code_zonage_hors_nomenclature(self):
        zones=[{"COM_COMER":"98411","COMER":"984","NATURE_ZONAGE":"FAUX",
                "LIBELLE":"Îles","NCCENR":"Îles"}]
        with self.assertRaisesRegex(ValueError,"sans nature"):
            preparer_cibles([],[
                {"COMER":"984","LIBELLE":"TAAF","NCCENR":"TAAF"}],zones)

if __name__=="__main__":
    unittest.main()
