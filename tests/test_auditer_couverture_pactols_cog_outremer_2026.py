"""Invariants de couverture Pactols–COG et tests anti-promotions implicites."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from auditer_couverture_pactols_cog_outremer_2026 import audit

INDEX=ROOT/"docs/data/lieux-outremer/recherche-2026.json"
REGISTRES=ROOT/"recette/lieux"

class TestsCouvertureOutremer(unittest.TestCase):
    def test_situation_publiee_et_registres(self):
        r=audit(INDEX,REGISTRES)
        self.assertEqual(r["totaux"]["communes"],212)
        self.assertEqual(r["totaux"]["alignements_communaux"],176)
        self.assertEqual(r["totaux"]["sans_alignement_communal"],36)
        self.assertEqual(r["totaux"]["validations_registres_verifiees"],160)
        self.assertEqual(r["totaux"]["autres_validations_mayotte"],16)
        self.assertEqual(r["totaux"]["collectivites_distinctes"],4)
        for prefix,unvalidated in (("975",2),("976",1),("988",33)):
            row=next(t for t in r["territoires"] if t["territoire"]==prefix)
            self.assertEqual(row["sans_alignement_valide"],unvalidated)
        self.assertEqual(r["publication"]["nouveaux_alignements"],0)

    def test_refus_promotion_dem_beni(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=json.loads(INDEX.read_text(encoding="utf-8"))
            d["pactols_valides"]["97607"]=d["ark_confirmes_non_valides"]["97607"]
            p=Path(tmp)/"index.json"
            p.write_text(json.dumps(d),encoding="utf-8")
            with self.assertRaises(ValueError):
                audit(p,REGISTRES)

    def test_refus_ark_collectivite_reutilise_comme_commune(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=json.loads(INDEX.read_text(encoding="utf-8"))
            d["pactols_valides"]["98801"]=d["pactols_collectivites_valides"]["987"]
            p=Path(tmp)/"index.json"
            p.write_text(json.dumps(d),encoding="utf-8")
            with self.assertRaises(ValueError):
                audit(p,REGISTRES)

    def test_refus_une_decision_registre_perdue(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            for name in ("GUYANE","MARTINIQUE","GUADELOUPE","REUNION","POLYNESIE"):
                f=REGISTRES/(name+"-VALIDATIONS-PACTOLS-COG-2026.csv")
                s=f.read_text(encoding="utf-8")
                if name=="GUYANE":
                    s="\n".join(s.splitlines()[:-1])+"\n"
                (directory/f.name).write_text(s,encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Nombre de décisions"):
                audit(INDEX,directory)

if __name__=="__main__":
    unittest.main()
