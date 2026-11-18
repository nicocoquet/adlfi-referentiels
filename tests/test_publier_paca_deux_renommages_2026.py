"""PACA : deux renommages avec preuves RDF/COG/décrets, sans Céreste UUID."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_paca_deux_renommages_2026 import publier

def sources():
    files={
      "audit":"recette/lieux/PACA-TROIS-RENOMMAGES-RDF-2026.json",
      "pilote":"docs/data/lieux.json",
      "complet":"docs/data/lieux-chronologie/pactols-paca-2026.json",
      "cog":"docs/data/lieux-chronologie/cog-paca.json"
    }
    return {key:json.loads((ROOT/path).read_text(encoding="utf-8"))
            for key,path in files.items()}

class PACARenommagesTests(unittest.TestCase):
    def test_deux_preuves_et_neuf_reserves(self):
        a=sources()
        frozen=copy.deepcopy(a)
        pub=publier(**a)
        links=pub["alignements_Pactols_COG_valides_2026"]
        self.assertEqual([x["code_insee"] for x in links],["05127","83052"])
        self.assertEqual([x["ark_pactols"] for x in links],
                         ["26678/pcrtla4EHGDgDd","26678/pcrt7B7bs9P5g2"])
        self.assertEqual(pub["total_alignements_PACA_2026"],937)
        self.assertEqual(pub["communes_a_instruire"],9)
        self.assertEqual(pub["reserve_Cereste_UUID"],"04045")
        self.assertEqual(pub["geometries_modifiees"],0)
        self.assertEqual(pub["autres_renommages_historiques_inferes"],0)
        self.assertTrue(all(x["portee_chronologique"]=="2026_SEULEMENT" for x in links))
        self.assertTrue(all(x["predicat_source"]=="skos:exactMatch" for x in links))
        self.assertEqual(a,frozen)

    def test_exactmatch_supplementaire_est_bloquant(self):
        a=sources()
        row=next(x for x in a["audit"]["dossiers"] if x["code_COG"]=="05127")
        hit=next(x for x in row["concepts_pactols_a_examiner"]
                 if x["ark"]=="26678/pcrtla4EHGDgDd")
        hit["exactMatch"].append("http://id.insee.fr/geo/commune/abc-def")
        with self.assertRaisesRegex(ValueError,"Preuve RDF insuffisante"):
            publier(**a)

    def test_ajout_cereste_sans_resolution_interdit(self):
        a=sources()
        row=next(x for x in a["audit"]["dossiers"] if x["code_COG"]=="04045")
        row["ARK_directement_assertes_vers_code_2026"]=["26678/pcrtHxveTzUMik"]
        with self.assertRaisesRegex(ValueError,"Céreste"):
            publier(**a)

    def test_changement_de_decret_invalide(self):
        a=sources()
        row=next(x for x in a["audit"]["dossiers"] if x["code_COG"]=="83052")
        row["decret"]="2025-999"
        with self.assertRaisesRegex(ValueError,"événement"):
            publier(**a)

    def test_pilote_et_complement_ne_sont_pas_remplaces(self):
        a=sources()
        a["pilote"]["autorites"][0]["ark_pactols"]="26678/pcrtla4EHGDgDd"
        with self.assertRaisesRegex(ValueError,"index public|103|Un renommage"):
            publier(**a)

if __name__=="__main__":
    unittest.main()
