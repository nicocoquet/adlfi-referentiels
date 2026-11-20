"""Recette fail-closed du deuxième lot normand : 7 validations et 3 exceptions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import valider_normandie_lot02_pactols_2026 as m  # noqa: E402


def rapport_synthetique():
    dossiers=[]
    for code,spec in sorted(m.CASES.items()):
        candidates=[]
        for kind in ("actuel","ancien"):
            ark=spec[kind]
            lbl=spec["label_"+kind]
            current=kind=="actuel"
            exact=["http://id.insee.fr/geo/commune/"+code]
            definition=[]
            if code=="14342" and current:
                definition=[{"type":"definition","texte":"Isigny-sur-Mer est une ancienne commune"}]
                exact+=["http://fr.dbpedia.org/page/Isigny-sur-Mer_(commune_déléguée)"]
            if code=="27112":
                exact+=["https://www.wikidata.org/wiki/Q467162" if current
                        else "http://www.wikidata.org/entity/Q467162"]
            if code=="50546" and current:
                definition=[{"type":"historyNote","texte":"Création en 2016-01-01"}]
            notes=definition or ([{"type":"historyNote",
                          "texte":"Ancienne commune devenue commune déléguée au sein d'une commune nouvelle"}]
                                  if not current else [])
            candidates.append({
                "ark":ark,
                "role_preliminaire":("CANDIDAT_COMMUNE_ACTUELLE_A_INSTRUIRE"
                                    if current else
                                    "IDENTITE_ANTERIEURE_OU_DELEGUEE_A_INSTRUIRE"),
                "prefLabels_fr":[lbl],"exactMatch":exact,
                "owl_deprecated":False,"dct_isReplacedBy":[],
                "notes":notes,
            })
        dossiers.append({
            "code_COG_2026":code,"nom_COG_2026":spec["nom"],
            "decision_editoriale":"NON_PRISE","nouvelles_geometries":0,
            "liens_historiques_inferes":0,"candidats_Pactols":candidates,
        })
    return {
        "schema":"adlfi.lieux.normandie.lot02.candidats.2026.audit.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "source_rdf":{"sha256":m.RDF_SHA},
        "bilan":{"communes_COG_a_instruire":10,"ARK_candidats":20,"nouvelles_validations":0},
        "dossiers":dossiers,
    }


def notes_synthetiques():
    return {
        m.CASES[code]["actuel"]:{
            "ark":m.CASES[code]["actuel"],"code_COG_2026":code,
            "date_creation_RDF":date,"source":"skos:historyNote",
            "sha256_note_complete":hashlib.sha256((code+date).encode()).hexdigest(),
            "longueur_note_complete":300,
        }
        for code,date in m.VALIDATIONS.items()
    }


def registre_lot01():
    return {
        "schema":"adlfi.lieux.pactols.normandie.lot01.2026.public.v1",
        "source_rdf_sha256":m.RDF_SHA,"nombre_communes":9,
        "alignements_Pactols_COG_valides_2026":[
            {"code_insee":str(i+90000)} for i in range(9)
        ],
    }


class Lot02Validations(unittest.TestCase):
    def test_sept_validees_et_trois_suspendues(self):
        data=m.construire(rapport_synthetique(),notes_synthetiques(),registre_lot01())
        self.assertEqual(data["nombre_communes"],7)
        self.assertEqual(data["communes_lot02_suspendues"],3)
        self.assertEqual(data["cumule_avec_lot01"],16)
        self.assertEqual(data["nouvelles_geometries"],0)
        self.assertFalse(data["active_dans_interface"])
        self.assertEqual({e["code_insee"] for e in data["exceptions_non_validees"]},
                         {"14342","27112","50546"})
        self.assertNotIn("50546",[x["code_insee"] for x in data["alignements_Pactols_COG_valides_2026"]])
        self.assertTrue(all(r["ancien_ark_non_promu"]!=r["ark_pactols"]
                            for r in data["alignements_Pactols_COG_valides_2026"]))

    def test_exception_isigny_definition_ancienne_obligatoire(self):
        x=rapport_synthetique()
        d=next(c for c in x["dossiers"] if c["code_COG_2026"]=="14342")
        current=next(c for c in d["candidats_Pactols"] if c["ark"]==m.CASES["14342"]["actuel"])
        current["notes"]=[]
        with self.assertRaisesRegex(ValueError,"Isigny"):
            m.construire(x,notes_synthetiques(),registre_lot01())

    def test_exception_breteuil_wikidata_ancien_obligatoire(self):
        x=rapport_synthetique()
        d=next(c for c in x["dossiers"] if c["code_COG_2026"]=="27112")
        current=next(c for c in d["candidats_Pactols"] if c["ark"]==m.CASES["27112"]["actuel"])
        current["exactMatch"].remove("https://www.wikidata.org/wiki/Q467162")
        with self.assertRaisesRegex(ValueError,"Breteuil"):
            m.construire(x,notes_synthetiques(),registre_lot01())

    def test_exception_bourgvalles_2019_oblige_a_revoir(self):
        x=rapport_synthetique()
        d=next(c for c in x["dossiers"] if c["code_COG_2026"]=="50546")
        current=next(c for c in d["candidats_Pactols"] if c["ark"]==m.CASES["50546"]["actuel"])
        current["notes"][0]["texte"]+=" et 2019-01-01"
        with self.assertRaisesRegex(ValueError,"Bourgvallées"):
            m.construire(x,notes_synthetiques(),registre_lot01())

    def test_manque_de_note_complete_bloquant(self):
        notes=notes_synthetiques()
        del notes[m.CASES["14654"]["actuel"]]
        with self.assertRaisesRegex(ValueError,"non exhaustives"):
            m.construire(rapport_synthetique(),notes,registre_lot01())

    def test_ancien_ark_candidat_bloquant(self):
        x=rapport_synthetique()
        d=next(c for c in x["dossiers"] if c["code_COG_2026"]=="61341")
        d["candidats_Pactols"][0]["role_preliminaire"]="IDENTITE_ANTERIEURE_OU_DELEGUEE_A_INSTRUIRE"
        with self.assertRaisesRegex(ValueError,"Preuve Pactols"):
            m.construire(x,notes_synthetiques(),registre_lot01())

    def test_note_saint_pierre_longue_lue_integralement(self):
        ns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        skos="http://www.w3.org/2004/02/skos/core#"
        root=ET.Element("{"+ns+"}RDF")
        for code,date in m.VALIDATIONS.items():
            ark=m.CASES[code]["actuel"]
            el=ET.SubElement(root,"{"+skos+"}Concept")
            el.set("{"+ns+"}about","https://ark.frantiq.fr/ark:/"+ark)
            prefix=("Un autre mouvement. " * 95) if code=="14654" else ""
            phrase="Création de la commune nouvelle de "+m.CASES[code]["nom"]+\
                   " en lieu et place des anciennes communes [date d'effet : "+date+"]."
            if code=="61341":
                phrase=phrase.replace("nouvelle de ","nouvelle d'")
            ET.SubElement(el,"{"+skos+"}historyNote").text=prefix+phrase
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"test.rdf"
            ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)
            proof=m.preuves_creation_rdf(path)
        self.assertEqual(proof[m.CASES["14654"]["actuel"]]["date_creation_RDF"],"2017-01-01")
        self.assertGreater(proof[m.CASES["14654"]["actuel"]]["longueur_note_complete"],1600)


if __name__=="__main__":
    unittest.main()
