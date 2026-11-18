"""PACA : séparation du pilote et des candidats, URI INSEE UUID concurrentes."""
import sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from preparer_paca_exactmatch_832_2026 import (
    preparer_depuis_rapport,scanner_toutes_uris,qualifier,
)

def mock_report():
    rows=[]
    for i in range(946):
        code=f"{i+1:05d}"
        pilot=i<103
        eligible=(i<103 or i<935) and i!=0
        if i==0: status="A_INSTRUIRE_PLUSIEURS_ARK"
        elif i<935: status="ELIGIBLE_SELON_REGLE"
        else: status="SANS_EXACTMATCH"
        ark=f"26678/pcrtA{i:04d}"
        evidence=[{
            "ark":ark,"deprecie":False,"remplace":False,
            "prefLabels_fr":["Test"],
            "codes_communaux_cites":[code],
            "insee_exactMatch":[{"famille":"commune","code":code,
                                 "uri":"http://id.insee.fr/geo/commune/"+code}]
        }] if status=="ELIGIBLE_SELON_REGLE" else []
        rows.append({"code":code,"libelle":"Test","departement":"04",
            "pilote_103_valide":pilot,"ark_pilote":ark if pilot else None,
            "statut_rdf":status,"preuves_RDF_exactMatch":evidence,
            "arks_exactMatch_dans_rdf":[ark] if evidence else []})
    return {"schema":"adlfi.lieux.paca.cog-pactols.2026.audit.v1",
        "sources":{"pactols":{"sha256":"abc","commit":"def"},"cog":{"sha256":"ghi"}},
        "communes":rows}

class PacAPreflightTests(unittest.TestCase):
    def test_pilote_conserve_et_832_proposes(self):
        a,b,meta=preparer_depuis_rapport(mock_report())
        self.assertEqual(len(a),832)
        self.assertEqual(len(b),11)
        self.assertEqual(len(meta["pilote"]),103)
        self.assertNotIn("00001",{x["code_insee"] for x in a})
        self.assertEqual(len({x["ark_pactols"] for x in a}),832)
        self.assertTrue(all(x["publication_site"]=="EN_ATTENTE_RECETTE_PUBLICATION" for x in a))

    def test_uuid_concurrent_est_bloquee_et_non_ignoree(self):
        xml='''<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:skos="http://www.w3.org/2004/02/skos/core#">
          <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtAlpha">
            <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/04001"/>
            <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/12345678-abcd-4321-bcde-abcdef123456"/>
          </skos:Concept>
          <skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtBeta">
            <skos:exactMatch rdf:resource="http://id.insee.fr/geo/commune/04002"/>
          </skos:Concept>
        </rdf:RDF>'''
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"test.rdf"
            p.write_text(xml,encoding="utf-8")
            a=scanner_toutes_uris(p,[
                {"ark_pactols":"26678/pcrtAlpha","uri_insee":"http://id.insee.fr/geo/commune/04001"},
                {"ark_pactols":"26678/pcrtBeta","uri_insee":"http://id.insee.fr/geo/commune/04002"}])
        self.assertEqual(a["26678/pcrtAlpha"]["preflight_uris"],"URI_INSEE_SUPPLEMENTAIRE_OU_NON_RECONNUE")
        self.assertEqual(a["26678/pcrtBeta"]["preflight_uris"],"CONFORME_UNE_URI_COG_2026")

    def test_pas_de_suppression_implicite_du_pilote(self):
        from unittest.mock import patch
        a=mock_report()
        with patch("preparer_paca_exactmatch_832_2026.scanner_toutes_uris") as scan:
            # Si une URI nouvelle se signale, le candidat est placé en quarantaine.
            rows,_,_=preparer_depuis_rapport(a)
            scan.return_value={
                r["ark_pactols"]:{
                    "ark_pactols":r["ark_pactols"],
                    "uri_attendue":r["uri_insee"],
                    "toutes_uris_insee":[r["uri_insee"]],
                    "preflight_uris":"URI_INSEE_SUPPLEMENTAIRE_OU_NON_RECONNUE" if i==0 else "CONFORME_UNE_URI_COG_2026",
                } for i,r in enumerate(rows)
            }
            out,b=qualifier(Path("unused.rdf"),a)
        self.assertEqual(len(out),831)
        self.assertEqual(len(b["quarantaines_URI_INSEE"]),1)
        self.assertEqual(len(b["pilotage_valide_2026"]),103)
        self.assertEqual(b["bilan"]["nouvelles_relations_publiees"],0)

if __name__=="__main__":unittest.main()
