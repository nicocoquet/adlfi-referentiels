"""Non-régression du lot 05 du référentiel Personnes AdlFI.
Les seuils sont des minima historiques, compatibles avec de futurs lots.
"""
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"docs/data/personnes.json"
MANIFEST=ROOT/"docs/data/manifest.json"
LOT05={'PER-000103': ('Claude Burnez', '034681760'), 'PER-000104': ('Carole Fritz', '050448862'), 'PER-000105': ('Annie Dumont', '071215301'), 'PER-000106': ('Arnaud Coutelas', '075903938'), 'PER-000107': ('Cécile Doulan', '083739475'), 'PER-000108': ('Mathieu Langlais', '121467570'), 'PER-000109': ('Fabien Pilon', '129583642'), 'PER-000110': ('Damien Pesesse', '136755690'), 'PER-000111': ('Christian Cribellier', '167797689'), 'PER-000112': ('Dominique Prost', '18389006X'), 'PER-000113': ('Jean-Philippe Sargiano', '243420420'), 'PER-000114': ('Jean-François Nauleau', '261598805'), 'PER-000115': ('Jean-Paul Guillaumet', '026908808'), 'PER-000116': ('Anne-Marie Pétrequin', '028256689'), 'PER-000117': ('Christian Sapin', '029806542'), 'PER-000118': ('Rémi Martineau', '060749563'), 'PER-000119': ('Jean-Luc Locht', '068658966'), 'PER-000120': ('Marie Soressi', '071520872'), 'PER-000121': ('Vivien Mathé', '077869818'), 'PER-000122': ('Jean-Marc Séguier', '11500789X'), 'PER-000123': ('Cécile Allinne', '104531835'), 'PER-000124': ('Michel Tessier', '151810214'), 'PER-000125': ('Bruno Aubry', '243730209'), 'PER-000126': ('Guy San Juan', '052302806'), 'PER-000127': ('Valérie Delattre', '057685673'), 'PER-000128': ('Christophe Cupillard', '070401845'), 'PER-000129': ('Pierre-Jérôme Rey', '177518545'), 'PER-000130': ('Sylvie Pluton-Kliesch', '221011803'), 'PER-000131': ('Vincent Krier', '243538375'), 'PER-000132': ('Pierre-Yves Nicod', '249927551')}

class TestPersonnesLot05(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(DATA.read_text(encoding="utf-8"))
        cls.manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_effectifs_et_manifeste(self):
        d=self.data
        a,c=d["authorities"],d["contributions"]
        self.assertGreaterEqual(len(a),132)
        self.assertGreaterEqual(len(c),1702)
        self.assertGreaterEqual(len({x["handle"] for x in c}),1590)
        self.assertEqual(d["totals"],{
            "authorities":len(a),
            "contributions":len(c),
            "notices":len({x["handle"] for x in c})
        })
        m=self.manifest["modules"]["personnes"]
        self.assertEqual(m["autorites_validees"],d["totals"]["authorities"])
        self.assertEqual(m["contributions_adlfi"],d["totals"]["contributions"])
        self.assertEqual(m["notices_adlfi"],d["totals"]["notices"])

    def test_per_uniques_et_identites_du_lot05(self):
        a=self.data["authorities"]
        by_id={x["id"]:x for x in a}
        self.assertEqual(len(by_id),len(a))
        self.assertTrue({f"PER-{i:06d}" for i in range(103,133)}.issubset(by_id))
        for per,(nom,ppn) in LOT05.items():
            self.assertEqual((by_id[per]["name"],by_id[per]["identifiers"]["idref"]),(nom,ppn))
        ppn=[x["identifiers"]["idref"] for x in a if x["identifiers"].get("idref")]
        self.assertEqual(len(set(ppn)),len(ppn))

    def test_contributions_et_roles(self):
        contributions=self.data["contributions"]
        keys=[(c["person_id"],c["handle"]) for c in contributions]
        self.assertEqual(len(keys),len(set(keys)))
        ids={a["id"] for a in self.data["authorities"]}
        self.assertTrue(all(c["person_id"] in ids for c in contributions))
        roles=Counter(" ".join(c["roles"]) for c in contributions)
        for role,minimum in (("aut fld",1371),("aut",316),("fld",15)):
            self.assertGreaterEqual(roles[role],minimum)

    def test_cecile_allinne(self):
        c=[x for x in self.data["contributions"] if
           x["person_id"]=="PER-000123" and x["handle"]=="20.500.13089/8yla"]
        self.assertEqual(len(c),1)
        self.assertEqual(c[0]["roles"],["fld"])

    def test_pas_de_registres_internes(self):
        s=DATA.read_text(encoding="utf-8")
        for forbidden in ("source_xml","reference_visa","validation_collective",
                          "MXML-","RESERVE-TEI-LOT05","ADLFI-PERSONNES-VISA-LOT05"):
            self.assertNotIn(forbidden,s)

if __name__=="__main__":
    unittest.main()
