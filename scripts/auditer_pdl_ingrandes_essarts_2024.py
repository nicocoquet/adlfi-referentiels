#!/usr/bin/env python3
"""Instruction non validante des deux mouvements communaux de 2024 : 49160/85084."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import sha
from auditer_pactols_polynesie_2026 import RDF_SHA, analyser_rdf
from qualifier_pdl_ark_multiples_2026 import completer_rdf

SCHEMA="adlfi.lieux.pdl.2024.ingrandes-essarts.audit.v1"
CODES={
  "49160":{"nom":"Ingrandes-le-Fresne-sur-Loire","mod":"32",
           "ancien_nom":"Ingrandes-Le Fresne sur Loire",
           "autre_code":"49321","autre_nom":"Saint-Sigismond",
           "date":"2024-01-01",
           "ark_ancienne":"26678/pcrtQBSwT6fBDW",
           "ark_candidat":"26678/pcrtj64zr6gnns4mnfd2828b"},
  "85084":{"nom":"Essarts-en-Bocage","mod":"21",
           "ancien_nom":"Essarts en Bocage",
           "autres_codes":["85165","85212"],
           "autres_noms":["L'Oie","Sainte-Florence"],
           "date":"2024-01-01",
           "ark_ancienne":"26678/pcrt0PrU3oVWxo",
           "ark_candidat":"26678/pcrt0PrU3oVWxo"},
}
PUBS=(
 "pactols-pdl-2026.json","pactols-pdl-uuid-resolus-2026.json",
 "pactols-pdl-communes-nouvelles-lot01-2026.json",
 "pactols-pdl-chemille-2026.json",
 "pactols-pdl-communes-nouvelles-lot02-2026.json",
 "pactols-pdl-oree-anjou-mod50-2026.json",
 "pactols-pdl-wikidata-p374-2026.json",
 "pactols-pdl-trois-collisions-2026.json",
)
def instruire(rdf:Path,cog:dict,pubs:list[dict])->dict:
 if sha(rdf)!=RDF_SHA:
  raise ValueError("RDF Pactols : SHA-256 inattendu")
 if cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026:
  raise ValueError("COG PDL versionné non conforme")
 all_old=[a for p in pubs for a in p["alignements_Pactols_COG_valides_2026"]]
 codes={a["code_insee"] for a in all_old}
 arks={a["ark_pactols"] for a in all_old}
 if len(all_old)!=1215 or len(codes)!=1215 or len(arks)!=1215 or set(CODES)&codes:
  raise ValueError("La publication 1215/1228 doit être intacte")
 cur=[p for p in cog["periodes_com"] if p["typecom"]=="COM" and
      p["debut_inclus"]<="2026-01-01" and
      (p["fin_exclue"] is None or p["fin_exclue"]>"2026-01-01")]
 if len(cur)!=1228 or len({p["code_insee"] for p in cur})!=1228:
  raise ValueError("COG PDL 2026 incomplet")
 scan=analyser_rdf(rdf,{c:d["nom"] for c,d in CODES.items()})
 targets={x["ark"] for code in CODES for x in (
     scan["explicites"][code]+scan["lexicaux_sans_exactMatch_987"].get(code,[]))}
 full=completer_rdf(rdf,targets)
 dossiers=[]
 for code,c in sorted(CODES.items()):
  periods=sorted((p for p in cog["periodes_com"] if
      p["code_insee"]==code and p["typecom"]=="COM"),
      key=lambda p:p["debut_inclus"])
  expected=[
    ("Ingrandes","1943-01-01","2016-01-01"),
    ("Ingrandes-Le Fresne sur Loire","2016-01-01","2024-01-01"),
    ("Ingrandes-le-Fresne-sur-Loire","2024-01-01",None),
  ] if code=="49160" else [
    ("Les Essarts","1943-01-01","2016-01-01"),
    ("Essarts en Bocage","2016-01-01","2024-01-01"),
    ("Essarts-en-Bocage","2024-01-01",None),
  ]
  if [(p["libelle"],p["debut_inclus"],p["fin_exclue"]) for p in periods]!=expected:
   raise ValueError("Épisodes COG altérés : "+code)
  changes=[x for x in cog["lignes_mouvements_cog"] if
      x["date_effet"]=="2024-01-01" and
      (x["code_avant"]==code or x["code_apres"]==code or
       x["code_apres"] in c.get("autres_codes",[]) or
       x["code_avant"]==c.get("autre_code"))]
  if not any(x["mod"]==c["mod"] and x["code_avant"]==code and
             x["code_apres"]==code and x["typecom_apres"]=="COM" and
             x["libelle_apres"]==c["nom"] for x in changes):
   raise ValueError("Mouvement COG actuel manquant : "+code)
  if code=="49160":
   if not any(x["mod"]=="32" and x["code_avant"]=="49321" and
              x["code_apres"]=="49160" and x["typecom_apres"]=="COM" for x in changes):
    raise ValueError("Fusion avec Saint-Sigismond non prouvée")
  else:
   if not all(any(x["mod"]=="21" and x["code_avant"]==code and
                x["code_apres"]==dest and x["typecom_apres"]=="COM" for x in changes)
              for dest in c["autres_codes"]):
    raise ValueError("Rétablissement des communes L'Oie/Sainte-Florence non prouvé")
  hits=scan["explicites"][code]
  lexical=scan["lexicaux_sans_exactMatch_987"].get(code,[])
  if code=="49160":
   if len(hits)!=2 or len(lexical)!=1 or lexical[0]["ark"]!=c["ark_candidat"]:
    raise ValueError("Candidat 2024 d'Ingrandes non unique")
  else:
   if len(hits)!=2 or lexical:
    raise ValueError("Concept Essarts inconnu ou lexical concurrent")
  if c["ark_ancienne"] not in {p["ark"] for p in hits}:
   raise ValueError("ARK existant absent : "+code)
  candidates=[]
  for h in hits+lexical:
   ext=full[h["ark"]]
   insee=[u for u in ext["exactMatch_tous"] if u.startswith((
       "http://id.insee.fr/geo/","https://id.insee.fr/geo/"))]
   candidates.append({
    "ark":h["ark"],"prefLabels_fr":h["prefLabels_fr"],
    "altLabels_fr":h.get("altLabels_fr",[]),
    "lien_INSEE_courant":("http://id.insee.fr/geo/commune/"+code) in insee,
    "exactMatch_INSEE":insee,
    "exactMatch_Wikidata":[u for u in ext["exactMatch_tous"] if "wikidata.org/" in u],
    "autres_exactMatch":[u for u in ext["exactMatch_tous"] if
                          "wikidata.org/" not in u and u not in insee],
    "closeMatch":ext["closeMatch_tous"],
    "definitions":ext["definitions"],
    "notes_histoire":ext["notes_histoire"],
    "notes_portee":ext["notes_portee"],
    "remplacements_explicites":ext["remplacements_explicites"],
    "deprecie":h.get("deprecie",False),
    "remplace":h.get("remplace",False),
    "candidat_lexical_sans_INSEE":h in lexical,
    "decision_editoriale":"NON_PRISE",
   })
  candidates.sort(key=lambda x:x["ark"])
  dossiers.append({
    "code":code,"nom_COG_2026":c["nom"],
    "date":"2024-01-01","mod_cog":c["mod"],
    "statut_evenement":("NOUVELLE_COMMUNE_MOD32" if code=="49160"
                       else "RETABLISSEMENT_COM_MOD21"),
    "episodes_COM":periods,"mouvements_COG":changes,
    "ark_candidat":c["ark_candidat"],"ark_anterieur":c["ark_ancienne"],
    "candidats_Pactols":candidates,
    "decision_editoriale":"NON_PRISE","publication":"NON_PUBLIE",
   })
 return {
  "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
  "source_RDF_Pactols_sha256":RDF_SHA,
  "source_COG":"docs/data/lieux-chronologie/cog-pdl.json",
  "source_COG_mode":"DERIVE_2026_VERSIONNE",
  "nombre_dossiers":2,"couverture_PDL_publique":1215,
  "exceptions_PDL":13,"nouvelles_validations":0,
  "geometries_nouvelles":0,"liens_historiques_inferes":0,
  "dossiers":dossiers,
 }
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ("rdf","cog","publications-dir","sortie"):
  p.add_argument("--"+key,required=True,type=Path)
 a=p.parse_args()
 if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
  raise ValueError("Rapport uniquement dans la recette, hors docs")
 rd=lambda f:json.loads(f.read_text(encoding="utf8"))
 d=instruire(a.rdf,rd(a.cog),[
   rd(a.publications_dir/f) for f in PUBS])
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
 print("PDL_2024_DOUBLE_MOUVEMENT_BILAN",json.dumps({
  "comptes":len(d["dossiers"]),"validation":d["nouvelles_validations"],
  "source_COG":d["source_COG_mode"]},sort_keys=True))
 for x in d["dossiers"]:
  print("PDL_2024_DOSSIER",json.dumps({
   "code":x["code"],"evenement":x["statut_evenement"],
   "ark_candidat":x["ark_candidat"],
   "concepts":[{"ark":q["ark"],"pref":q["prefLabels_fr"],
     "insee":q["exactMatch_INSEE"],"wikidata":q["exactMatch_Wikidata"],
     "definitions":q["definitions"],"notes_portee":q["notes_portee"],
     "notes_histoire":q["notes_histoire"]} for q in x["candidats_Pactols"]]
  },sort_keys=True,ensure_ascii=False))
if __name__=="__main__":main()
