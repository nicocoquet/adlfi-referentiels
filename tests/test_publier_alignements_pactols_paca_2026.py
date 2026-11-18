"""PACA : 832 correspondances complémentaires sans doublonner les 103 du pilote."""
import copy,csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from publier_alignements_pactols_paca_2026 import construire
from preparer_validations_pactols_corse_2026 import FIELDS

def sources():
    with (ROOT/"recette/lieux/PACA-CANDIDATS-EXACTMATCH-2026.csv").open(
        encoding="utf-8",newline="") as f:
        r=csv.DictReader(f,delimiter=";")
        assert tuple(r.fieldnames or ())==FIELDS
        rows=list(r)
    report=json.loads((ROOT/"recette/lieux/PACA-PREFLIGHT-EXACTMATCH-2026.json").read_text(encoding="utf-8"))
    pilote=json.loads((ROOT/"docs/data/lieux.json").read_text(encoding="utf-8"))
    cog=json.loads((ROOT/"docs/data/lieux-chronologie/cog-paca.json").read_text(encoding="utf-8"))
    return rows,report,pilote,cog

class PACAPublicationTests(unittest.TestCase):
    def test_832_complements_sans_eroder_le_pilote(self):
        a,b,c,d=sources()
        original_pilote=copy.deepcopy(c)
        original_cog=copy.deepcopy(d)
        publication=construire(a,b,c,d)
        entries=publication["alignements_Pactols_COG_valides_2026"]
        self.assertEqual(len(entries),832)
        self.assertEqual(publication["nombre_total_alignements_2026"],935)
        self.assertEqual(publication["communes_a_instruire"],11)
        self.assertEqual(len({x["code_insee"] for x in entries}),832)
        self.assertEqual(len({x["ark_pactols"] for x in entries}),832)
        pilot_codes={x["correspondances"][0]["code_insee"] for x in c["autorites"]}
        self.assertEqual(len(pilot_codes),103)
        self.assertFalse(pilot_codes&{x["code_insee"] for x in entries})
        self.assertEqual({x["code_insee"] for x in entries}&{"05139","04033","04045"},set())
        self.assertEqual(publication["nouvelles_geometries"],0)
        self.assertEqual(publication["liens_historiques_inferes"],0)
        self.assertEqual(c,original_pilote)
        self.assertEqual(d,original_cog)

    def test_ark_concurrent_ou_code_du_pilote_refuses(self):
        a,b,c,d=sources()
        a[1]["ark_pactols"]=a[0]["ark_pactols"]
        with self.assertRaisesRegex(ValueError,"non admissible|inadmissible|collision|dupliqué"):
            construire(a,b,c,d)
        a,b,c,d=sources()
        a[0]["code_insee"]="05139"
        with self.assertRaisesRegex(ValueError,"non admissible|collision|inadmissible"):
            construire(a,b,c,d)

    def test_quarantaine_ou_pilote_altere_bloque(self):
        a,b,c,d=sources()
        b["bilan"]["candidats_mis_en_quarantaine_URI"]=1
        with self.assertRaisesRegex(ValueError,"préflight"):
            construire(a,b,c,d)
        a,b,c,d=sources()
        c["autorites"][0]["correspondances"][0]["libelle_cog"]="Mauvaise commune"
        with self.assertRaisesRegex(ValueError,"invalidée"):
            construire(a,b,c,d)

    def test_conserve_devoluy_en_validation_du_pilote(self):
        a,b,c,d=sources()
        p=construire(a,b,c,d)
        self.assertNotIn("05139",{x["code_insee"] for x in p["alignements_Pactols_COG_valides_2026"]})
        row=next(x for x in c["autorites"] if x["correspondances"][0]["code_insee"]=="05139")
        self.assertEqual(row["ark_pactols"],"26678/pcrtSeD2WMEIYA")

if __name__=="__main__":
    unittest.main()
