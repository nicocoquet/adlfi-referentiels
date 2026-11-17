"""Tests des invariants de l'audit géographique ISPF, sans téléchargement réseau."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from auditer_iles_ispf_polynesie import analyser

class TestAuditIlesISPF(unittest.TestCase):
    def test_refuse_rapport_non_qualifie(self):
        with self.assertRaisesRegex(ValueError, "non qualifié"):
            analyser({"schema": "autre", "statut": "RECETTE_ISPF_NON_VALIDANTE"})

    def test_refuse_cardinalites_non_confirmees(self):
        with self.assertRaisesRegex(ValueError, "cardinalité"):
            analyser({"schema": "adlfi.lieux.polynesie.ispf.associees.audit.v1",
                     "statut": "RECETTE_ISPF_NON_VALIDANTE",
                     "bilan": {"communes_COG": 0, "communes_associees_ISPF": 98,
                               "communes_ISPF_sans_associees": 18,
                               "iles_ISPF_dans_classeur": 119,
                               "codes_geographiques_ISPF": 179}})

    def test_une_ile_partagee_ne_cree_pas_de_geom(self):
        units = [{"id_comas_ISPF": f"{i:03d}", "id_commune_ISPF": f"{i//10:02d}",
                  "code_commune_COG": f"987{i//10:02d}"} for i in range(110, 226)]
        row = lambda code, fine, ile: {
            "IDGeo": code, "IDComas": fine, "IDCom": fine[:2],
            "IDIle": ile, "Ile": "Ile témoin", "IDSub": "1", "Geo": "Ile témoin",
            "isCom": "0", "isComas": "1", "isIleRattachee": "0"}
        geo = [row("11000", "110", "1"), row("11100", "111", "1")]
        # Un rapport artificiel peut déclencher l'audit des relations sans
        # dépendre de l'accès réseau ; 177 lignes distinctes supplémentaires.
        geo += [row(f"{i:05d}", "110", str(i)) for i in range(10000, 10177)]
        geo[2]["IDGeo"] = "43001"
        geo[2]["IDComas"] = "431"
        # Une telle source synthétique doit être refusée avant d'inférer
        # quoi que ce soit, car l'unité 431 n'est pas présente.
        audit = {"schema": "adlfi.lieux.polynesie.ispf.associees.audit.v1",
                 "statut": "RECETTE_ISPF_NON_VALIDANTE",
                 "bilan": {"communes_COG": 48, "communes_associees_ISPF": 98,
                           "communes_ISPF_sans_associees": 18,
                           "iles_ISPF_dans_classeur": 119,
                           "codes_geographiques_ISPF": 179},
                 "communes_associees": units[:98],
                 "unites_conventionnelles_non_associees": units[98:],
                 "codes_geographiques": geo}
        with self.assertRaisesRegex(ValueError, "sans unité"):
            analyser(audit)

if __name__ == "__main__":
    unittest.main()
