"""PACA : passage de 937 à 938 codes sans substitution ni rétroprojection."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_paca_trois_renommages_2026 import publier,verifier_preuve_insee
from publier_paca_deux_renommages_2026 import publier as publier_deux

FILES=[
 "recette/lieux/PACA-TROIS-RENOMMAGES-RDF-2026.json",
 "recette/lieux/PACA-CERESTE-UUID-INSEE-AUDIT-2026.json",
 "docs/data/lieux.json",
 "docs/data/lieux-chronologie/pactols-paca-2026.json",
 "docs/data/lieux-chronologie/cog-paca.json"
]
def sources():
    return [json.loads((ROOT/p).read_text(encoding="utf-8")) for p in FILES]

class TroisRenommagesTests(unittest.TestCase):
    def test_ajout_une_seule_identite_uuid(self):
        a=sources()
        freeze=copy.deepcopy(a)
        out=publier(*a)
        self.assertEqual(a,freeze)
        self.assertEqual(out["schema"],"adlfi.lieux.pactols.paca.renommages.2026.public.v2")
        self.assertEqual(out["liens_renommages_ajoutes"],3)
        self.assertEqual(out["total_alignements_PACA_2026"],938)
        self.assertEqual(out["communes_a_instruire"],8)
        self.assertEqual(out["geometries_modifiees"],0)
        self.assertEqual(out["autres_renommages_historiques_inferes"],0)
        links=out["alignements_Pactols_COG_valides_2026"]
        self.assertEqual([x["code_insee"] for x in links],["04045","05127","83052"])
        self.assertEqual(links[0]["ark_pactols"],"26678/pcrtHxveTzUMik")
        self.assertEqual(links[0]["code_insee_resolu"],"04045")
        self.assertEqual(links[0]["portee_chronologique"],"2026_SEULEMENT")
        self.assertEqual(links[0]["predicat_resolution"],"http://rdf.insee.fr/def/geo#codeINSEE")
        old=publier_deux(a[0],a[2],a[3],a[4])
        self.assertEqual(links[1:],old["alignements_Pactols_COG_valides_2026"])
        self.assertEqual(len({x["ark_pactols"] for x in links}),3)

    def test_spoof_sparql_autre_sujet_refuse(self):
        a=sources()
        proof=a[1]
        result=next(x for x in proof["appels_sparql"] if x.get("preuve",{}).get("preuve_directe_code_04045"))
        result["preuve"]["triples"]=[
          {"s":"http://id.insee.fr/geo/commune/04045",
           "p":"http://rdf.insee.fr/def/geo#codeINSEE","o":"04045","type":"literal"}]
        with self.assertRaisesRegex(ValueError,"double preuve"):
            publier(*a)

    def test_code_uuid_falsifie_refuse(self):
        a=sources()
        a[1]["appels_dereferencement"][0]["codeINSEE_du_sujet_UUID"]=["05045"]
        with self.assertRaisesRegex(ValueError,"double preuve"):
            publier(*a)

    def test_autre_uri_insee_pactols_refuse(self):
        a=sources()
        c=next(x for x in a[0]["dossiers"] if x["code_COG"]=="04045")
        c["concepts_pactols_a_examiner"][0]["exactMatch"].append(
            "http://id.insee.fr/geo/commune/04045")
        with self.assertRaisesRegex(ValueError,"concept Pactols"):
            publier(*a)

    def test_103_et_832_intacts(self):
        a=sources()
        a[2]["autorites"][0]["ark_pactols"]="26678/pcrtHxveTzUMik"
        with self.assertRaises(ValueError):
            publier(*a)

    def test_annee_historique_ne_peut_devenir_2024(self):
        a=sources()
        out=publier(*a)
        self.assertTrue(all(x["millesime_validation"]==2026 for x in out["alignements_Pactols_COG_valides_2026"]))
        self.assertTrue(all(x["portee_chronologique"]=="2026_SEULEMENT" for x in out["alignements_Pactols_COG_valides_2026"]))

if __name__=="__main__":
    unittest.main()
