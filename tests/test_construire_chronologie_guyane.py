"""Tests de chronologie COG Guyane et maintien des autorités historiques."""
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from construire_chronologie_guyane import (
    actif,etat,preparer,CODES_HISTORIQUES,SCHEMA,
)


def donnees():
    codes=([f"973{i:02d}" for i in range(1,15)]
           +["97352","97353","97356","97357","97358",
             "97360","97361","97362"])
    assert len(codes)==22
    codes_hist=sorted(CODES_HISTORIQUES)
    etats=[]
    current=[]
    for i,code in enumerate(codes):
        name=f"Commune {code}"
        current.append({"code_COG_2026":code,"libelle_COG_2026":name})
        if i<15:
            etats.extend([
                {"code":code,"libelle":name,
                 "debut_inclus":"1946-01-01","fin_exclue":"1953-01-01",
                 "fichier_source":"v_commune_depuis_1943.csv",
                 "geometrie_historique":None,
                 "identite_juridique_retroactive":"NON_ETABLIE"},
                {"code":code,"libelle":name,
                 "debut_inclus":"1953-01-01","fin_exclue":None,
                 "fichier_source":"v_commune_depuis_1943.csv",
                 "geometrie_historique":None,
                 "identite_juridique_retroactive":"NON_ETABLIE"},
            ])
        else:
            etats.append({"code":code,"libelle":name,
                 "debut_inclus":"1946-01-01","fin_exclue":None,
                 "fichier_source":"v_commune_depuis_1943.csv",
                 "geometrie_historique":None,
                 "identite_juridique_retroactive":"NON_ETABLIE"})
    non_current=[]
    historiques=[]
    for code in codes_hist:
        row={"code":code,"libelle":"Ancienne "+code,
             "debut_inclus":"1946-01-01","fin_exclue":"1969-03-27",
             "fichier_source":"v_commune_depuis_1943.csv",
             "geometrie_historique":None,
             "identite_juridique_retroactive":"NON_ETABLIE"}
        etats.append(row)
        ark="26678/pcrt"+code
        src={"code_insee_cite":code,"ark":ark,
             "uri_insee":"http://id.insee.fr/geo/commune/"+code,
             "predicat":"exactMatch","concept_deprecie":False,
             "concept_remplace":False,"codes_communes_INSEE_exactMatch":[code]}
        non_current.append(src)
        historiques.append({
             "code_insee_historique":code,"ark_pactols":ark,
             "uri_insee":src["uri_insee"],"predicat_source":"exactMatch",
             "statut_historique":"CONCEPT_PACTOLS_HISTORIQUE_A_INSTRUIRE"})
    assert len(etats)==41
    events=[{"DATE_EFF":"1969-03-27","MOD":"31",
             "COM_AV":"97351","TYPECOM_AV":"COM",
             "LIBELLE_AV":"Ancienne 97351",
             "COM_AP":"97301","TYPECOM_AP":"COM",
             "LIBELLE_AP":"Commune 97301"} for _ in range(52)]
    audit={
        "schema":"adlfi.lieux.guyane.audit.cog-pactols-geom.v1",
        "bilan":{"communes_COG_2026":22,"codes_distincts_historiques_973":26,
                 "periodes_historiques_973":41,
                 "mouvements_impliquant_code_973":52,
                 "source_Pactols_stats":{"liens_insee_non_courants":non_current}},
        "communes":current,"historique_codes_973":etats,
        "mouvements_source_avec_code_973":events,
    }
    validees=[{"code_insee":c["code_COG_2026"],"ark_pactols":"26678/pcrt"+c["code_COG_2026"],
              "libelle_COG_2026":c["libelle_COG_2026"],
              "statut_validation":"VALIDE_ADLFI_2026","portee_COG":"2026-01-01",
              "predicat_source":"exactMatch","concept_deprecie":"non"}
             for c in current]
    return audit,validees,historiques


class ChronologieGuyaneTests(unittest.TestCase):
    def test_fin_exclue_et_date_effet(self):
        p={"debut_inclus":"1953-01-01","fin_exclue":"1969-03-27"}
        self.assertFalse(actif(p,"1952-12-31"))
        self.assertTrue(actif(p,"1953-01-01"))
        self.assertTrue(actif(p,"1969-03-26"))
        self.assertFalse(actif(p,"1969-03-27"))

    def test_etat_refuse_identites_simultanees(self):
        p={"code":"97301","libelle":"Régina",
           "debut_inclus":"1946-01-01","fin_exclue":None}
        with self.assertRaisesRegex(ValueError,"Deux identités"):
            etat([p,p],"2026-01-01")

    def test_1943_non_documente_et_1969_avant_reorganisation(self):
        a,v,h=donnees()
        r=preparer(a,v,h)
        self.assertEqual(r["schema"],SCHEMA)
        years={v["annee"]:v for v in r["etats_1er_janvier"]}
        self.assertEqual(len(years),84)
        self.assertEqual(years[1943]["total"],0)
        self.assertEqual(years[1943]["couverture"],"NON_DOCUMENTEE_DANS_LE_FICHIER")
        self.assertEqual(years[1946]["total"],26)
        self.assertEqual(years[1969]["total"],26)
        self.assertEqual(years[1970]["total"],22)
        self.assertEqual(years[2026]["total"],22)
        self.assertTrue(all(x["geometrie"] is None for y in years.values()
                            for x in y["communes"]))
        self.assertTrue(all(y["interpretation_identite_Pactols"]=="NON_RETROPROJETEE"
                            for y in years.values()))

    def test_quatre_codes_historiques_non_fusionnes(self):
        a,v,h=donnees()
        r=preparer(a,v,h)
        old=r["autorites_historiques_candidats"]
        self.assertEqual({x["code_insee_historique"] for x in old},
                         CODES_HISTORIQUES)
        self.assertTrue(all(x["successeur_COG"]=="A_INSTRUIRE_A_PARTIR_DES_MOUVEMENTS"
                            for x in old))
        self.assertTrue(all(x["correspondance_avec_commune_2026"] is None for x in old))
        self.assertEqual(r["statistiques"]["liens_Pactols_historiques_valides"],0)
        self.assertEqual(r["statistiques"]["geometries_historiques_validees"],0)

    def test_provenance_et_regroupement_dates(self):
        a,v,h=donnees()
        r=preparer(a,v,h)
        self.assertEqual(len(r["mouvements_COG_sans_succession_inferree"]),52)
        self.assertEqual(len(r["bilans_par_date_effet"]),1)
        day=r["bilans_par_date_effet"][0]
        self.assertEqual(day["date_effet_COG"],"1969-03-27")
        self.assertEqual(day["etat_COG_avant"],26)
        self.assertEqual(day["etat_COG_apres"],22)
        self.assertEqual(day["delta_nombre_communes"],-4)
        self.assertTrue(all(x["relation_historique_reciproque_validee"] is False
                            for x in r["mouvements_COG_sans_succession_inferree"]))

    def test_refus_autorite_historique_conflit(self):
        a,v,h=donnees()
        h[0]["ark_pactols"]="26678/pcrtWRONG"
        with self.assertRaisesRegex(ValueError,"non justifiée"):
            preparer(a,v,h)

    def test_refus_validation_actuelle_avec_code_disparu(self):
        a,v,h=donnees()
        v[0]["code_insee"]="97351"
        with self.assertRaisesRegex(ValueError,"incompatible"):
            preparer(a,v,h)

    def test_refus_source_succession_prevalidatee(self):
        a,v,h=donnees()
        a["historique_codes_973"][0]["identite_juridique_retroactive"]="VALIDE"
        with self.assertRaisesRegex(ValueError,"non conforme"):
            preparer(a,v,h)


if __name__=="__main__":
    unittest.main()
