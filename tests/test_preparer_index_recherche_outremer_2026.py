"""Contrôles sans réseau du futur index national (recette ultramarine 2026)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from preparer_index_recherche_outremer_2026 import (
    SCHEMA, construire, instructions_editoriales, normaliser, rechercher,
    entree_commune, episodes_historique,
)


def donnees():
    return {
        "communes": [
            {"TYPECOM":"COM","COM":"97601","DEP":"976","REG":"06",
             "LIBELLE":"Acoua"},
            {"TYPECOM":"COM","COM":"97607","DEP":"976","REG":"06",
             "LIBELLE":"Dembeni"},
            {"TYPECOM":"COM","COM":"97407","DEP":"974","REG":"04",
             "LIBELLE":"Le Port"},
        ],
        "departements": [
            {"DEP":"976","REG":"06","LIBELLE":"Mayotte"},
            {"DEP":"974","REG":"04","LIBELLE":"La Réunion"},
        ],
        "zonages": [
            {"COMER":"987","COM_COMER":"98745","NATURE_ZONAGE":"COM",
             "LIBELLE":"Tahaa"},
            {"COMER":"975","COM_COMER":"97502","NATURE_ZONAGE":"COM",
             "LIBELLE":"Saint-Pierre"},
            {"COMER":"984","COM_COMER":"98412","NATURE_ZONAGE":"DIS",
             "LIBELLE":"Archipel des Kerguelen"},
            {"COMER":"981","COM_COMER":"98101","NATURE_ZONAGE":"CDM",
             "LIBELLE":"Île des Faisans"},
        ],
        "territoires": [
            {"COMER":"987","LIBELLE":"Polynésie française"},
            {"COMER":"975","LIBELLE":"Saint-Pierre-et-Miquelon"},
            {"COMER":"984","LIBELLE":"Terres australes et antarctiques françaises"},
            {"COMER":"981","LIBELLE":"Île des Faisans"},
        ],
        "hist_drom": [
            {"TYPECOM":"COM","COM":"97607","LIBELLE":"Dembeni",
             "DATE_DEBUT":"2011-03-31","DATE_FIN":""},
            {"TYPECOM":"COM","COM":"97601","LIBELLE":"Acoua",
             "DATE_DEBUT":"2011-03-31","DATE_FIN":""},
        ],
        "hist_comer": [
            {"NATURE_ZONAGE":"COM","COM_COMER":"97607",
             "LIBELLE":"Dembeni","DATE_DEBUT":"2007-02-23",
             "DATE_FIN":"2011-03-31"},
            {"NATURE_ZONAGE":"COM","COM_COMER":"98745",
             "LIBELLE":"Tahaa","DATE_DEBUT":"1943-01-01","DATE_FIN":""},
        ],
    }


def diagnostics(data):
    from auditer_contours_outremer_2026 import cibles
    cs = cibles(data["communes"], data["zonages"], data["territoires"], False)
    return [{**c, "statut": "PRESENTE_INVALIDE" if c["code"]=="98745"
             else "NON_EVALUE_TERRITOIRE_SANS_COUCHE_DEDIEE" if c["nature"]=="TERRITOIRE"
             else "ABSENTE_DU_FICHIER_COMMUNES" if c["nature"]=="CDM"
             else "PRESENTE_VALIDE_A_QUALIFIER"} for c in cs]


def decisions():
    return {
        "97601":{"statut":"VALIDE_2026","ark":"26678/pcrtZfYYjyoUIE",
                 "source":"MAYOTTE","libelle_source":"Acoua"},
        "97607":{"statut":"ARK_CONFIRME_CORRESPONDANCE_A_VALIDER",
                 "ark":"26678/crtZcuFSJVYZU","source":"MAYOTTE",
                 "libelle_source":"Dembeni"},
        "97407":{"statut":"ARK_CONFIRME_CORRESPONDANCE_A_VALIDER",
                 "ark":"26678/pcrtIKvRT9vwUl","source":"REUNION",
                 "libelle_source":"Le Port"},
    }


class IndexOutremerTests(unittest.TestCase):
    def test_separation_entre_les_autorites_et_les_zonages(self):
        c, other = construire(donnees(), diagnostics(donnees()),
                             decisions(), strict=False)
        self.assertEqual(c["schema"], SCHEMA)
        self.assertEqual(len(c["entrees"]), 5)
        self.assertEqual(len(other["entrees"]), 6)
        ids = {e["id"] for e in c["entrees"]}
        self.assertIn("COMER:COM:98745", ids)
        self.assertIn("DROM:COM:97601", ids)
        self.assertNotIn("COMER:DIS:98412", ids)
        self.assertNotIn("COMER:CDM:98101", ids)
        self.assertTrue(all(x["niveau_recherche"] is None
                            for x in other["entrees"]))
        self.assertEqual(other["manifest"]["geometries_publiees"], 0)

    def test_ark_valide_2026_et_ark_confirme_sont_distincts(self):
        c,_ = construire(donnees(), diagnostics(donnees()),
                         decisions(), strict=False)
        bycode = {x["code_insee"]:x for x in c["entrees"]}
        self.assertEqual(bycode["97601"]["pactols"]["ark_valide"],
                         "26678/pcrtZfYYjyoUIE")
        self.assertIn(normaliser("26678/pcrtZfYYjyoUIE"),
                      bycode["97601"]["champs_recherche"])
        self.assertIsNone(bycode["97607"]["pactols"]["ark_valide"])
        self.assertEqual(bycode["97607"]["pactols"]["ark_identifiant_confirme"],
                         "26678/crtZcuFSJVYZU")
        self.assertNotIn(normaliser("26678/crtZcuFSJVYZU"),
                         bycode["97607"]["champs_recherche"])
        self.assertIsNone(bycode["97407"]["pactols"]["ark_valide"])
        self.assertEqual(bycode["98745"]["pactols"]["relation_2026"], "A_INSTRUIRE")

    def test_historique_source_documentaire_non_rattachement_retroactif(self):
        c,_ = construire(donnees(), diagnostics(donnees()),
                         decisions(), strict=False)
        dembeni = next(x for x in c["entrees"] if x["code_insee"]=="97607")
        episodes = dembeni["historique_COG_observations"]
        self.assertEqual(len(episodes), 2)
        self.assertEqual([x["source_famille"] for x in episodes],
                         ["COG_COMER", "COG_DROM"])
        self.assertEqual([x["debut_inclus"] for x in episodes],
                         ["2007-02-23", "2011-03-31"])
        self.assertTrue(all(x["relation_identite_avec_2026"]=="NON_ETABLIE"
                            and x["geometrie_historique"] is None for x in episodes))
        self.assertEqual(dembeni["historique_validite_retroactive"], "NON_VALIDEE")
        self.assertEqual(dembeni["geom_2026"]["geometrie"], None)

    def test_noms_homonymes_et_codes_sont_recherchables_distinctement(self):
        c,_ = construire(donnees(), diagnostics(donnees()),
                         decisions(), strict=False)
        entries=c["entrees"]
        self.assertEqual([x["code_insee"] for x in rechercher(entries, "Tahaa")], ["98745"])
        self.assertEqual([x["code_insee"] for x in rechercher(entries, "Polynésie")], ["98745"])
        self.assertEqual([x["code_insee"] for x in rechercher(entries, "le port reunion")], ["97407"])
        self.assertEqual([x["code_insee"] for x in rechercher(entries, "97502")], ["97502"])
        self.assertEqual(rechercher(entries, "98101"), [])

    def test_blocage_si_decision_contradictoire(self):
        ds = decisions()
        ds["97601"]["libelle_source"] = "Une autre commune"
        with self.assertRaisesRegex(ValueError, "Libellé"):
            construire(donnees(), diagnostics(donnees()), ds, strict=False)

    def test_blocage_si_cible_diagnostic_dupliquee(self):
        source=donnees()
        with self.assertRaisesRegex(ValueError, "incomplets|différentes"):
            construire(source, diagnostics(source)[:-1],
                       decisions(), strict=False)

    def test_historique_conserve_le_code_sans_creer_de_succession(self):
        hist=episodes_historique(donnees())
        self.assertTrue(hist["97607"][0]["relation_identite_avec_2026"] == "NON_ETABLIE")
        self.assertEqual(hist["97607"][0]["fin_exclue"], "2011-03-31")


if __name__ == "__main__":
    unittest.main()
