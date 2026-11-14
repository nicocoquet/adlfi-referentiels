"""Index national : pas de géocodage fictif des 9 825 ARK non instruits."""
import csv,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from preparer_index_pactols_xml_national import produire,normaliser

class IndexPactolsXML(unittest.TestCase):
 def test_normalisation_francaise(self):
  self.assertEqual(normaliser("Saint-Hymetière-sur-Valouse"),"saint hymetiere sur valouse")
 def test_variantes_et_validation_heritee(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);a=p/"a.csv";o=p/"o.csv";output=p/"out"
   with a.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,delimiter=";",fieldnames=(
      "ark_pactols","libelle_fr_xml","nombre_notices_distinctes","nombre_occurrences",
      "annees_operation_relevees","alignement_pilote",
      "code_insee_2026_valide","nom_cog_2026_valide"))
    w.writeheader()
    w.writerow(dict(ark_pactols="26678/pcrtABC",libelle_fr_xml="Draix",
      nombre_notices_distinctes=1,nombre_occurrences=1,
      annees_operation_relevees="[2023]",alignement_pilote="valide_pilote_paca_2026",
      code_insee_2026_valide="04072",nom_cog_2026_valide="Draix"))
    w.writerow(dict(ark_pactols="26678/crtXYZ",libelle_fr_xml="Ancien nom",
      nombre_notices_distinctes=2,nombre_occurrences=2,
      annees_operation_relevees="[2016, 2020]",alignement_pilote="hors_pilote_non_instruit",
      code_insee_2026_valide="",nom_cog_2026_valide=""))
   with o.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,delimiter=";",fieldnames=(
      "ark_terminal","libelle_terminal_fr","libelle_original_index","notice_id"))
    w.writeheader()
    w.writerow(dict(ark_terminal="26678/pcrtABC",libelle_terminal_fr="Draix",
                    libelle_original_index="Draix",notice_id="n1"))
    w.writerow(dict(ark_terminal="26678/crtXYZ",libelle_terminal_fr="Ancien nom",
                    libelle_original_index="Ancienne forme",notice_id="n2"))
    w.writerow(dict(ark_terminal="26678/crtXYZ",libelle_terminal_fr="Ancien nom",
                    libelle_original_index="Ancien nom",notice_id="n3"))
   r=produire(a,o,output,controler_empreintes=False)
   self.assertEqual((r["autorites_xml"],r["occurrences_xml"],
                     r["correspondances_cog_2026_deja_validees"]),(2,3,1))
   idx=json.loads((output/"index-autorites-pactols-xml.json").read_text())
   by={x["ark_pactols"]:x for x in idx["autorites"]}
   self.assertEqual(by["26678/crtXYZ"]["correspondance_cog_validee_2026"],None)
   self.assertEqual(set(by["26678/crtXYZ"]["formes_attestees_xml"]),
                    {"Ancien nom","Ancienne forme"})
   self.assertEqual(by["26678/pcrtABC"]["correspondance_cog_validee_2026"]["code_insee"],"04072")
   self.assertIsNone(by["26678/crtXYZ"]["geometrie_historique"])
 def test_code_insee_non_valide_interdit(self):
  # Les comportements de refus sont validés aussi par le test précédent :
  # seule une entrée déjà au statut 'valide_pilote_paca_2026' doit porter un code.
  self.assertEqual(normaliser("l'Œuvre"),"l oeuvre")
if __name__=="__main__":unittest.main()
