"""Tests non-régression du contrôle COG pour le lot national Lieux."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from auditer_evenements_cog_lot import auditer, transitions_probables

def row(nom="Afa", code_old="20001", code_new="2A001", date="1976-01-01"):
    return {
        "ark_pactols":"26678/pcrtgs2LLPYow2",
        "libelle_documentaire":nom,
        "codes_cog_departement_concordants":json.dumps([code_new]),
        "details_cog_candidats":json.dumps([
            {"code_insee_historique":code_old,"libelle_cog":nom,
             "date_debut":"1943-01-01","date_fin":date},
            {"code_insee_historique":code_new,"libelle_cog":nom,
             "date_debut":date,"date_fin":""},
        ]),
    }

class AuditEvenements(unittest.TestCase):
    def test_dates_jointives_signalent_simple_hypothese(self):
        ts=transitions_probables([row()])
        self.assertEqual(len(ts),1)
        self.assertEqual(ts[0]["code_avant"],"20001")

    def test_dates_non_jointives_exclues(self):
        r=row()
        h=json.loads(r["details_cog_candidats"])
        h[0]["date_fin"]="1975-01-01"
        r["details_cog_candidats"]=json.dumps(h)
        self.assertEqual(transitions_probables([r]),[])

    def test_homonymes_differents_ne_sont_pas_successeurs(self):
        r=row()
        h=json.loads(r["details_cog_candidats"])
        h[0]["libelle_cog"]="Crouy"
        r["details_cog_candidats"]=json.dumps(h)
        self.assertEqual(transitions_probables([r]),[])

    def test_evenement_direct_mod41_ne_valide_pas_pactols(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            lot=root/"lot.csv";mvt=root/"v_mvt_commune_2026.csv"
            r=row()
            with lot.open("w",encoding="utf-8-sig",newline="") as fh:
                w=csv.DictWriter(fh,fieldnames=r.keys(),delimiter=";")
                w.writeheader();w.writerow(r)
            ev={
                "MOD":"41","DATE_EFF":"1976-01-01",
                "TYPECOM_AV":"COM","COM_AV":"20001","LIBELLE_AV":"Afa",
                "TYPECOM_AP":"COM","COM_AP":"2A001","LIBELLE_AP":"Afa",
            }
            with mvt.open("w",encoding="utf-8",newline="") as fh:
                w=csv.DictWriter(fh,fieldnames=ev.keys(),delimiter=",")
                w.writeheader();w.writerow(ev)
            rapport=auditer(lot,mvt,root/"sortie")
            self.assertEqual(rapport["transitions_avec_evenement_direct_exact"],1)
            self.assertEqual(rapport["repartition_MOD_transitions"],{"41":1})
            with (root/"sortie/transitions_code_a_verifier.csv").open(encoding="utf-8-sig",newline="") as fh:
                relations=list(csv.DictReader(fh,delimiter=";"))
            self.assertEqual(relations[0]["statut_validation_pactols"],"non_valide")

    def test_sans_evenement_on_conserve_incertitude(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); lot=root/"lot.csv";mvt=root/"events.csv"
            r=row()
            with lot.open("w",encoding="utf-8",newline="") as fh:
                w=csv.DictWriter(fh,fieldnames=r.keys(),delimiter=";")
                w.writeheader();w.writerow(r)
            with mvt.open("w",encoding="utf-8",newline="") as fh:
                w=csv.writer(fh);w.writerow([
                    "MOD","DATE_EFF","TYPECOM_AV","COM_AV","LIBELLE_AV",
                    "TYPECOM_AP","COM_AP","LIBELLE_AP"])
            report=auditer(lot,mvt,root/"sortie")
            self.assertEqual(report["transitions_sans_evenement_direct_exact"],1)
            self.assertEqual(report["transitions_avec_evenement_direct_exact"],0)

if __name__=="__main__":
    unittest.main()
