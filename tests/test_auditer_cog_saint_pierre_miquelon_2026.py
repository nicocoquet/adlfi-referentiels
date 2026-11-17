"""Tests de préinstruction COG des deux communes de Saint-Pierre-et-Miquelon."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import auditer_cog_saint_pierre_miquelon_2026 as aud

class TestSaintPierreMiquelon(unittest.TestCase):
 def test_sources_identifiants_et_schema(self):
  self.assertEqual(set(aud.SHAS),{
   "v_comer_2026.csv","v_commune_comer_2026.csv",
   "v_tom_depuis_1943.csv","v_commune_outremer_depuis_1943.csv",
   "v_commune_depuis_1943.csv","v_commune_2026.csv"})
  self.assertEqual(aud.CODES,{"97501","97502"})
  self.assertEqual(aud.CIBLE,"975")
  self.assertTrue(all(len(x)==64 for x in aud.SHAS.values()))
 def test_episode(self):
  row={"LIBELLE":"Miquelon-Langlade","DATE_DEBUT":"1985-06-11","DATE_FIN":""}
  self.assertEqual(aud.episode(row,"COMER","97501","COM"),
   {"code":"97501","libelle":"Miquelon-Langlade","famille":"COMER",
    "nature":"COM","debut_inclus":"1985-06-11","fin_exclue":None})
  for end in ("1985-06-11","1980-01-01","XX"):
   with self.assertRaises(ValueError):
    aud.episode({**row,"DATE_FIN":end},"COMER","97501","COM")
 def fixture(self):
  return {
   "v_comer_2026.csv":[{"COMER":"975","LIBELLE":"Saint-Pierre-et-Miquelon"}],
   "v_commune_comer_2026.csv":[
     {"COMER":"975","NATURE_ZONAGE":"COM","COM_COMER":"97501",
      "LIBELLE":"Miquelon-Langlade"},
     {"COMER":"975","NATURE_ZONAGE":"COM","COM_COMER":"97502",
      "LIBELLE":"Saint-Pierre"}],
   "v_tom_depuis_1943.csv":[{"COMER":"975","LIBELLE":"Saint-Pierre-et-Miquelon",
                             "DATE_DEBUT":"1985-06-11","DATE_FIN":""}],
   "v_commune_outremer_depuis_1943.csv":[
     {"NATURE_ZONAGE":"COM","COM_COMER":code,"LIBELLE":label,
      "DATE_DEBUT":"1985-06-11","DATE_FIN":""}
     for code,label in (("97501","Miquelon-Langlade"),("97502","Saint-Pierre"))],
   "v_commune_depuis_1943.csv":[],
   "v_commune_2026.csv":[],
  }
 def audit(self,fixture):
  with patch.object(aud,"sha",side_effect=lambda p:aud.SHAS[p.name]), \
       patch.object(aud,"lire",side_effect=lambda p:fixture[p.name]):
   return aud.analyser(Path("/temporary/cog"))
 def test_audit_ne_confond_pas_statut_et_commune(self):
  a=self.audit(self.fixture())
  self.assertEqual(a["schema"],"adlfi.lieux.spm.audit.cog2026.v1")
  self.assertEqual(len(a["communes_2026"]),2)
  self.assertEqual(a["collectivite_actuelle"]["code_communal"],False)
  self.assertEqual(len(a["episodes_communes_COMER_COG"]),2)
  self.assertEqual(a["episodes_communes_DROM_COG"],[])
  self.assertEqual(len(a["periodes_juridiques_a_ne_pas_confondre"]),3)
  self.assertTrue(all(x["transition_communes_inferree"] is False
                      for x in a["periodes_juridiques_a_ne_pas_confondre"]))
  self.assertFalse(a["publication_docs"])
  self.assertEqual(a["nouveaux_alignements_pactols"],0)
  self.assertEqual(a["nouvelles_relations_successions_inferrees"],0)
  self.assertEqual(a["geometries_historiques_adoptees"],0)
 def test_refuser_code_territoire_confondu_avec_commune(self):
  f=self.fixture()
  f["v_commune_comer_2026.csv"].append({
   "COMER":"975","NATURE_ZONAGE":"COM","COM_COMER":"975",
   "LIBELLE":"Saint-Pierre-et-Miquelon"})
  with self.assertRaises(ValueError):self.audit(f)
 def test_conserver_periode_dom_sans_inference(self):
  f=self.fixture()
  f["v_commune_depuis_1943.csv"]=[
   {"COM":"97501","LIBELLE":"Miquelon-Langlade","TYPECOM":"COM",
     "DATE_DEBUT":"1976-07-19","DATE_FIN":"1985-06-11"}]
  a=self.audit(f)
  self.assertEqual(len(a["episodes_communes_DROM_COG"]),1)
  self.assertEqual(a["episodes_communes_DROM_COG"][0]["famille"],"DROM")
 def test_refuser_historique_comer_incomplet(self):
  f=self.fixture()
  f["v_commune_outremer_depuis_1943.csv"]=f[
   "v_commune_outremer_depuis_1943.csv"][:1]
  with self.assertRaises(ValueError):self.audit(f)
if __name__=="__main__":unittest.main()
