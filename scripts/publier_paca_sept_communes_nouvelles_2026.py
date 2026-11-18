#!/usr/bin/env python3
"""Sept communes nouvelles PACA au COG 2026, avec preuve RDF + MOD32 daté.

Ne remplace pas les identités des anciennes communes porteuses du même code.
Aucune rétroprojection des ARK n'est faite pour les années précédant la fusion.
"""
from __future__ import annotations
import argparse,json,re,hashlib
from pathlib import Path
from auditer_paca_huit_communes_nouvelles_2026 import SCHEMA as AUDIT_SCHEMA,CASES,reconstruire_cog,RDF_SHA

SCHEMA="adlfi.lieux.pactols.paca.sept_communes_nouvelles.2026.public.v1"
EXPECTED=("04033","04120","05024","05039","05053","05101","05118")
ARKS={
 "04033":"26678/pcrtDcVUj2Mdw9",
 "04120":"26678/pcrtjDzQ2Y9N5o",
 "05024":"26678/pcrtAUevxwngAh",
 "05039":"26678/pcrtFGmyycRjcC",
 "05053":"26678/pcrtKc33Ttmi9L",
 "05101":"26678/pcrt2BsRDBxggr",
 "05118":"26678/pcrtjKbaVOnEjn",
}
RESERVES=("04045","05001")
def produire(audit,pilote,complement,renommages,cog):
 if (audit.get("schema")!=AUDIT_SCHEMA or audit.get("bilan",{}).get("communes_nouvelles_a_instruire")!=8
   or audit.get("bilan",{}).get("ARK_vers_codes_contemporains")!=15
   or audit.get("bilan",{}).get("nouvelles_validations_2026")!=0
   or audit.get("sources",{}).get("pactols",{}).get("sha256")!=RDF_SHA):
  raise ValueError("Audit des huit communes nouvelles différent")
 history=reconstruire_cog(cog)
 if set(history)!=set(CASES):raise ValueError("État historique différent")
 if (len(pilote.get("autorites",[]))!=103 or
  complement.get("schema")!="adlfi.lieux.pactols.paca.complement.2026.public.v1" or
  len(complement.get("alignements_Pactols_COG_valides_2026",[]))!=832 or
  renommages.get("schema")!="adlfi.lieux.pactols.paca.renommages.2026.public.v1" or
  len(renommages.get("alignements_Pactols_COG_valides_2026",[]))!=2 or
  renommages.get("total_alignements_PACA_2026")!=937):
  raise ValueError("937 liens PACA précédents différents")
 previous={}
 arks=set()
 for row in pilote["autorites"]:
  code=row["correspondances"][0]["code_insee"];ark=row["ark_pactols"]
  if code in previous or ark in arks:raise ValueError("Doublon historique pilote")
  previous[code]=ark;arks.add(ark)
 for data in (complement,renommages):
  for row in data["alignements_Pactols_COG_valides_2026"]:
   code=row["code_insee"];ark=row["ark_pactols"]
   if code in previous or ark in arks:raise ValueError("Doublon avec un alignement publié")
   previous[code]=ark;arks.add(ark)
 if len(previous)!=937 or any(c in previous for c in (*EXPECTED,*RESERVES)):
  raise ValueError("Réserves ou alignements précédents modifiés")
 dossiers={x["code_COG_2026"]:x for x in audit["dossiers"]}
 if set(dossiers)!=set(CASES):raise ValueError("Huit dossiers incomplets")
 new=[]
 old_arks=[]
 for code in CASES:
  dossier=dossiers[code];ctx=history[code]
  if (dossier["historique_COG"]!=ctx or dossier["publication"]!="AUCUNE"
    or dossier["decision_editoriale"]!="NON_PRISE"):
   raise ValueError("Historique ou arbitrage changé : "+code)
  allconcepts=dossier["candidats_Pactols"]
  if len(allconcepts)!=(1 if code=="05001" else 2):
   raise ValueError("Concepts RDF en nombre inattendu : "+code)
  ancient=[p for p in allconcepts if p["qualification_de_recette"]=="IDENTITE_ANCIENNE_COMMUNE_PORTEUSE_CODE"]
  candidates=[p for p in allconcepts if p["qualification_de_recette"]=="CANDIDAT_IDENTITE_COMMUNE_NOUVELLE_SELON_LIBELLE"]
  if len(ancient)!=1 or len(candidates)!=(0 if code=="05001" else 1):
   raise ValueError("Identités actuelles/anciennes non séparées : "+code)
  pold=ancient[0]
  if (pold["prefLabels_fr"]!=[ctx["ancienne_commune_porteuse_code"]]
      or pold["owl_deprecated"] or pold["dct_isReplacedBy"]):
   raise ValueError("Concept ancien incorrect : "+code)
  old_arks.append(pold["ark_pactols"])
  if code=="05001":continue
  current=candidates[0]
  ark=ARKS[code]
  name=CASES[code]["nom"];date=ctx["date_creation_commune_nouvelle"]
  uri="http://id.insee.fr/geo/commune/"+code
  notes=[x["texte"] for x in current["notes"] if x["type"]=="historyNote"]
  history_text=" ".join(notes)
  if (current["ark_pactols"]!=ark or current["prefLabels_fr"]!=[name]
      or current["owl_deprecated"] or current["dct_isReplacedBy"]
      or len(current["insee_exactMatch"])!=1
      or current["insee_exactMatch"][0]!={"famille":"commune","identifiant":code,"uri":uri}
      or not ("Création de la commune nouvelle" in history_text or
              "Création de la commune" in history_text and "commune nouvelle" in history_text)
      or date not in history_text or name not in history_text
      or ark in arks or ark==pold["ark_pactols"]):
   raise ValueError("Preuve de commune nouvelle insuffisante : "+code)
  new.append({
   "code_insee":code,"libelle_COG_2026":name,"ark_pactols":ark,
   "libelle_pactols":name,"uri_insee":uri,"predicat_source":"skos:exactMatch",
   "date_creation_commune_nouvelle":date,
   "code_ancienne_commune_porgant":code,
   "libelle_ancienne_commune_porteuse":ctx["ancienne_commune_porteuse_code"],
   "ark_ancienne_commune_distinct":pold["ark_pactols"],
   "sources_anciennes_communes":ctx["communes_sources"],
   "preuve_historique_Pactols":notes,
   "source_RDF_sha256":RDF_SHA,"millesime_validation":2026,
   "date_validation":"2026-11-18",
   "statut":"correspondance_commune_nouvelle_validee_RDF_COG_2026",
   "type_validation":"prefLabel_commune_nouvelle_exactMatch_INSEE_unique_historyNote_COG_MOD32",
   "portee_chronologique":"2026_SEULEMENT",
  })
 if len(new)!=7 or len(old_arks)!=8 or len(set(old_arks))!=8 or
    any(a in arks for a in old_arks):
  raise ValueError("Nombre d'identités anciennes / nouvelles erroné")
 if set(x["code_insee"] for x in new)!=set(EXPECTED):
  raise ValueError("Les sept communes ne sont pas celles du lot validé")
 return {
  "schema":SCHEMA,"region":"paca","millesime_cog":"2026-01-01",
  "source_rdf_sha256":RDF_SHA,
  "source_audit":"recette/lieux/PACA-HUIT-COMMUNES-NOUVELLES-RDF-2026.json",
  "liens_communes_nouvelles_ajoutes":7,
  "pilote_valide_conserve":103,"complements_conserves":832,
  "renommages_conserves":2,"alignements_total_PACA_2026":944,
  "communes_a_instruire":2,"exceptions_restantes":["04045","05001"],
  "ARK_anciens_concepts_non_promus":sorted(old_arks),
  "nouvelles_geometries":0,"identites_historiques_inferees":0,
  "alignements_Pactols_COG_valides_2026":sorted(new,key=lambda x:x["code_insee"])
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for arg in ("audit","pilote","complement","renommages","cog","sortie"):
  p.add_argument("--"+arg,type=Path,required=True)
 a=p.parse_args()
 if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
  raise ValueError("Sortie neuve hors docs")
 def load(x):return json.loads(x.read_text(encoding="utf-8"))
 result=produire(load(a.audit),load(a.pilote),load(a.complement),load(a.renommages),load(a.cog))
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
 print("PACA_SEPT_COMMUNES_NOUVELLES_PREPAREES",json.dumps({
  "nouvelles_validations":7,"total":944,"exceptions":result["exceptions_restantes"],
  "SHA256":hashlib.sha256(a.sortie.read_bytes()).hexdigest()},ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
