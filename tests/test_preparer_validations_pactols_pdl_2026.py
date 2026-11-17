"""Pays de la Loire 2026 : les cas ambigus restent non publiés."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from preparer_validations_pactols_pdl_2026 import (
    preparer_depuis_rapport,STATUTS_ATTENDUS
)

def row(code,name,status,ark="26678/pcrtEssai"):
    item={
        "ark":ark,
        "prefLabels_fr":[name],
        "insee_exactMatch":[{"famille":"commune","code":code,
                             "uri":"http://id.insee.fr/geo/commune/"+code}]
    }
    return {"region":"52","departement":code[:2],"code":code,"nom":name,
            "etat":status,"preuves_RDF_exactMatch":
                [] if status=="SANS_EXACTMATCH" else [item]}

class TestPaysDeLaLoire(unittest.TestCase):
    def test_cardinalites_attendues(self):
        self.assertEqual(STATUTS_ATTENDUS,{
            "ELIGIBLE_SELON_REGLE":1140,
            "A_INSTRUIRE_PLUSIEURS_ARK":60,
            "A_INSTRUIRE_LIBELLE_STATUT_OU_URI":24,
            "SANS_EXACTMATCH":4,
        })
    def test_registre_et_exception_disjoints(self):
        r={"pactols":{"sha256":"source"},"communes":[
            row("44001","Aigrefeuille-sur-Maine","ELIGIBLE_SELON_REGLE"),
            row("44066","Grandchamp-des-Fontaines","SANS_EXACTMATCH")
        ]}
        selected,exceptions,_=preparer_depuis_rapport(
            r,{"ELIGIBLE_SELON_REGLE":1,"SANS_EXACTMATCH":1})
        self.assertEqual(len(selected),1)
        self.assertEqual(selected[0]["code_insee"],"44001")
        self.assertEqual(selected[0]["statut_validation"],"VALIDE_ADLFI_2026")
        self.assertEqual(selected[0]["publication_site"],"EN_ATTENTE_RECETTE_PUBLICATION")
        self.assertEqual(exceptions[0]["code_insee"],"44066")
        self.assertEqual(exceptions[0]["decision_editoriale"],"NON_PRISE")
    def test_ark_concurrent_bloque(self):
        r={"pactols":{"sha256":"source"},"communes":[
            row("44001","Aigrefeuille-sur-Maine","ELIGIBLE_SELON_REGLE"),
            row("44002","Ancenis-Saint-Géréon","ELIGIBLE_SELON_REGLE")
        ]}
        with self.assertRaisesRegex(ValueError,"dupliqués"):
            preparer_depuis_rapport(r,{"ELIGIBLE_SELON_REGLE":2})
    def test_statuts_inattendus_bloquent(self):
        r={"pactols":{"sha256":"source"},"communes":[
            row("44001","Aigrefeuille-sur-Maine","ELIGIBLE_SELON_REGLE"),
        ]}
        with self.assertRaisesRegex(ValueError,"Cardinalités"):
            preparer_depuis_rapport(r,{"SANS_EXACTMATCH":1})

if __name__=="__main__":unittest.main()
