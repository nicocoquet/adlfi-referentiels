"""Tests du pipeline Lieux : filtres, année d'opération, hiérarchie et non-publication."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.extraire_lieux_xml_adlfi import (
    extraire_fichier, extraire_ark, execution, inventaire, retenir_fichier,
)

XML = """<?xml version="1.0" encoding="utf-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
 <teiHeader><fileDesc><titleStmt><title>2019</title></titleStmt></fileDesc></teiHeader>
 <text><body>
  <div subtype="notice" type="section2" xml:id="n1">
   <head><index indexName="Index"><term type="orig">Aix-en-Provence</term>
    <index indexName="pactols:Lieux" source="26678/pcrtEurope">
     <term xml:lang="fr">Europe</term>
     <index source="26678/pcrtFrance"><term xml:lang="fr">France</term>
      <index source="26678/pcrtAix"><term xml:lang="fr">Aix-en-Provence</term></index>
     </index>
    </index>
   </index> – Quartier d'essai</head>
   <head type="sub">Diagnostic (2016)</head>
   <ab type="meta-archeo">Années des opérations : <date>2015</date>, <date>2017</date></ab>
   <p><index indexName="pactols:Lieux"
      source="https://ark.frantiq.fr/ark:/26678/pcrtSite">
      <term xml:lang="fr">Site d'essai</term>
   </index></p>
   <p><index indexName="pactols:Chronologie" source="26678/pcrtChrono"/></p>
  </div>
  <div subtype="notice" type="section2">
   <head>Deux lieux</head>
   <ab type="meta-archeo">Année de l’opération : <date from="2018" to="2020">2018–2020</date></ab>
   <p><index indexName="pactols:Lieux" source="26678/pcrtFrance">
     <term xml:lang="fr">France</term>
     <index source="26678/pcrtAix"><term xml:lang="fr">Aix-en-Provence</term></index>
     <index source="26678/pcrtNice"><term xml:lang="fr">Nice</term></index>
   </index></p>
  </div>
  <div subtype="notice"><head>Sans géographie</head><ab type="meta-archeo">Années des opérations : 2012, 2014</ab></div>
 </body></text>
</TEI>
"""


def pilote():
    return {
        "schema_version": "0.1.0",
        "statut_publication": "pilote_valide",
        "autorites": [
            {
                "ark_pactols": f"26678/pcrtPilote{i}",
                "correspondances": [{
                    "code_insee": f"04{i:03}",
                    "libelle_cog": "test",
                    "validation": {
                        "statut": "VALIDE_EDITEUR_2026_10_18", "source": "synthétique",
                    },
                }],
            }
            for i in range(103)
        ],
    }


class ExtractionLieuxTests(unittest.TestCase):
    def test_filtres_exactement_sur_noms(self):
        for nom in ("AdlFI_2025.xml", "adlfi-notices.XML", "AdlFI_Alsace_2015.xml"):
            self.assertTrue(retenir_fichier(Path(nom))[0], nom)
        for nom in ("BSR_2025.xml", "AdlFI_Edito.xml", "AdlFI_Édito.xml",
                    "AdlFI_Editos.xml", "AdlFI_2025.pdf"):
            self.assertFalse(retenir_fichier(Path(nom))[0], nom)

    def test_annees_terminales_et_contexte(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "AdlFI_exemple.xml"
            path.write_text(XML, encoding="utf-8")
            sha, notices, occurrences, anomalies = extraire_fichier(path, path.name)
            self.assertEqual(len(sha), 64)
            self.assertEqual(len(notices), 3)
            self.assertEqual(len(occurrences), 4)
            self.assertEqual(notices[0]["xml_id"], "n1")
            self.assertIn("Quartier d'essai", notices[0]["titre"])
            self.assertNotIn("Europe France", notices[0]["titre"])
            self.assertEqual(json.loads(notices[0]["annees_operation"]), [2015, 2017])
            self.assertEqual(notices[0]["nombre_ark_terminaux"], 2)
            self.assertEqual(json.loads(occurrences[0]["chaine_ark"]), [
                "26678/pcrtEurope", "26678/pcrtFrance", "26678/pcrtAix",
            ])
            self.assertEqual(occurrences[0]["zone_tei"], "head")
            self.assertEqual(occurrences[1]["zone_tei"], "p")
            self.assertEqual(json.loads(notices[1]["annees_operation"]), [2018, 2020])
            self.assertEqual(notices[1]["presence_intervalle"], "oui")
            self.assertEqual(json.loads(notices[2]["annees_operation"]), [2012, 2014])
            self.assertEqual({o["ark_terminal"] for o in occurrences}, {
                "26678/pcrtAix", "26678/pcrtSite", "26678/pcrtNice",
            })
            self.assertTrue(any(x["type"] == "aucun_index_pactols_lieux" for x in anomalies))
            self.assertTrue(any(x["type"] == "intervalle_annees_non_developpe" for x in anomalies))

    def test_inventaire_rejet_et_doublons_fichiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            racine = Path(tmp) / "AdlFI_NOTICES-FAITES"
            sous = racine / "region"
            sous.mkdir(parents=True)
            (sous / "AdlFI_Edito.xml").write_text(XML, encoding="utf-8")
            (sous / "BSR.xml").write_text(XML, encoding="utf-8")
            (sous / "AdlFI_1.xml").write_text(XML, encoding="utf-8")
            (racine / "AdlFI_2.xml").write_text(XML, encoding="utf-8")
            (racine / "AdlFI.pdf").write_text("PDF", encoding="utf-8")
            invent = inventaire(racine)
            self.assertEqual(len(invent), 4)
            self.assertEqual(sum(a["decision"] == "inclu" for a in invent), 2)
            source_pilote = Path(tmp) / "pilote.json"
            source_pilote.write_text(json.dumps(pilote()), encoding="utf-8")
            sortie = Path(tmp) / "sortie"
            execution(racine, sortie, pilote=source_pilote, inventaire_seul=True)
            self.assertTrue((sortie / "inventaire_xml.csv").exists())
            self.assertFalse((sortie / "notices.csv").exists())
            audit = execution(racine, sortie, pilote=source_pilote)
            self.assertEqual(audit["effectifs"]["notices"], 3)
            self.assertEqual(audit["effectifs"]["fichiers_doublons_exacts_exclus_des_statistiques"], 1)
            self.assertEqual(audit["effectifs"]["occurrences_terminales"], 4)
            self.assertEqual(audit["effectifs"]["autorites_distinctes"], 3)
            self.assertEqual(audit["effectifs"]["autorites_alignees_pilote_paca"], 0)
            with (sortie / "autorites_lieux.csv").open(encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f, delimiter=";"))
            aix = next(x for x in rows if x["ark_pactols"] == "26678/pcrtAix")
            self.assertEqual(int(aix["nombre_notices_distinctes"]), 2)

    def test_refus_ecriture_dans_le_corpus(self):
        with tempfile.TemporaryDirectory() as tmp:
            racine = Path(tmp)
            (racine / "AdlFI.xml").write_text(XML, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "EN DEHORS"):
                execution(racine, racine / "sortie", pilote=racine / "pilote.json")

    def test_ark_non_inventes(self):
        self.assertEqual(extraire_ark("26678/crtcTest"), "26678/crtcTest")
        self.assertEqual(extraire_ark("https://ark.frantiq.fr/ark:/26678/pcrtTest"), "26678/pcrtTest")
        self.assertIsNone(extraire_ark("26678/pcrtA,26678/pcrtB"))
        self.assertIsNone(extraire_ark("https://not-frantiq.org/ark:/26678/pcrtA"))


if __name__ == "__main__":
    unittest.main()
