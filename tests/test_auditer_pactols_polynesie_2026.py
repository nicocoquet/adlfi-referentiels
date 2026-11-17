"""Pactols Polynésie : URI explicite n'implique ni commune associée ni île."""
from __future__ import annotations
import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_pactols_polynesie_2026 as a

START='''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
 xmlns:owl="http://www.w3.org/2002/07/owl#">'''
BODY='''
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtAnaa">
 <skos:prefLabel xml:lang="fr">Anaa</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/98711"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtIleArue">
 <skos:prefLabel xml:lang="fr">île Arue</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/98712"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtPapeeteLex">
 <skos:prefLabel xml:lang="fr">Papeete</skos:prefLabel>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtClipperton">
 <skos:prefLabel xml:lang="fr">Clipperton</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/98799"/>
</skos:Concept>
<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtTerritoire">
 <skos:prefLabel xml:lang="fr">Polynésie française</skos:prefLabel>
 <skos:exactMatch rdf:resource="http://id.insee.fr/geo/collectiviteDOutreMer/987"/>
</skos:Concept>
'''
class PolynesieTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.rdf=Path(self.temp.name)/"rdf.xml"
  self.rdf.write_text(START+BODY+"</rdf:RDF>",encoding="utf-8")
  self.labels={f"987{i}":"Commune "+str(i) for i in range(11,59)}
  self.labels.update({"98711":"Anaa","98712":"Arue","98735":"Papeete"})
 def tearDown(self):self.temp.cleanup()
 def test_libelles_et_categories(self):
  self.assertTrue(a.label_compatible("Anaa","Anaa"))
  self.assertTrue(a.label_compatible("Arue","Arue (Tahiti)"))
  self.assertFalse(a.label_compatible("Arue","île Arue"))
  self.assertTrue(a.type_confusion(["île Arue"]))
  self.assertTrue(a.type_confusion(["atoll Anaa"]))
  self.assertFalse(a.type_confusion(["Papeete (Tahiti)"]))
 def test_rdf_exactmatch_et_homonymies(self):
  d=a.analyser_rdf(self.rdf,self.labels)
  self.assertEqual(d["concepts_RDF_examines"],5)
  self.assertEqual(d["explicites"]["98711"][0]["ark"],"26678/pcrtAnaa")
  self.assertEqual(d["explicites"]["98712"][0]["ark"],"26678/pcrtIleArue")
  self.assertTrue(d["explicites"]["98712"][0]["risque_ile_atoll_autre_type"])
  self.assertEqual(d["explicites"]["98735"],[])
  self.assertEqual(d["lexicaux_sans_exactMatch_987"]["98735"][0]["ark"],"26678/pcrtPapeeteLex")
  self.assertEqual(d["anciens_ou_territoriaux"]["98799"][0]["ark"],"26678/pcrtClipperton")
  self.assertEqual(d["anciens_ou_territoriaux"]["987"][0]["ark"],"26678/pcrtTerritoire")
 def report(self):
  with (patch.object(a,"sha",return_value=a.RDF_SHA),
        patch.object(a,"analyser_cog",return_value={
         "communes_2026":[{"code":c,"libelle":name}
                            for c,name in self.labels.items()]})):
   return a.rapport(self.rdf,Path(self.temp.name),Path(self.temp.name)/"index.json")
 def test_rapport_pas_de_validation_automatique(self):
  d=self.report()
  self.assertEqual(d["bilan"]["communes_COG"],48)
  self.assertEqual(d["bilan"]["codes_avec_exactMatch"],2)
  self.assertEqual(d["bilan"]["concepts_exactMatch_total"],2)
  self.assertEqual(d["bilan"]["statuts"]["ELIGIBLE_A_ARBITRAGE_COMMUNE_2026"],1)
  self.assertEqual(d["bilan"]["statuts"]["A_INSTRUIRE_ONTOLOGIE_LIBELLE_OU_MULTIPLICITE"],1)
  self.assertEqual(d["bilan"]["validations_automatiques"],0)
  self.assertEqual(d["bilan"]["nouveaux_alignements_publies"],0)
  self.assertEqual(d["bilan"]["comptage_communes_associees_ISPF_non_inferre"],98)
  self.assertTrue(all(not x["alignement_publie"] for x in d["codes_communes_2026"]))
 def test_candidat_multiple_refuse(self):
  self.rdf.write_text(self.rdf.read_text().replace("</rdf:RDF>",
   '''<skos:Concept rdf:about="http://ark.frantiq.fr/ark:/26678/pcrtAnaa2">
  <skos:prefLabel xml:lang="fr">Anaa</skos:prefLabel>
  <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/98711"/>
 </skos:Concept></rdf:RDF>'''),encoding="utf-8")
  d=self.report()
  self.assertEqual(d["codes_communes_2026"][0]["statut"],"A_INSTRUIRE_CANDIDATS_MULTIPLES")
  self.assertEqual(d["bilan"]["nouveaux_alignements_publies"],0)
 def test_rdf_invalide_refuse(self):
  self.rdf.write_text("<not-RDF/>",encoding="utf-8")
  with self.assertRaisesRegex(ValueError,"RDF/XML"):
   a.analyser_rdf(self.rdf,self.labels)
if __name__=="__main__":unittest.main()
