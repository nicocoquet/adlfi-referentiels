#!/usr/bin/env python3
"""Publication 2026 de trois communes nouvelles PDL à ARK historiques distincts."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import sha
from auditer_pactols_polynesie_2026 import RDF_SHA, analyser_rdf
from qualifier_pdl_ark_multiples_2026 import completer_rdf

SCHEMA="adlfi.lieux.pactols.pdl.trois-collisions.2026.public.v1"
SOURCE="recette/lieux/PDL-TROIS-COLLISIONS-2026.md"
URI="http://id.insee.fr/geo/commune/"
CASES={
 "49244":("Mauges-sur-Loire","La Pommeraye","2015-12-15",
           "26678/pcrtVBIl6UNl1S","26678/pcrtE0bVL7JsdM"),
 "53255":("Sainte-Suzanne-et-Chammes","Sainte-Suzanne","2016-01-01",
           "26678/pcrtwUykeFf31u","26678/pcrts0lDLWcVyJ"),
 "72137":("Villeneuve-en-Perseigne","La Fresnaye-sur-Chédouet","2015-01-01",
           "26678/pcrtoVf9Ovfyy7","26678/pcrtg6rwdnGM9r"),
}
PREVIOUS=[
 "pactols-pdl-2026.json",
 "pactols-pdl-uuid-resolus-2026.json",
 "pactols-pdl-communes-nouvelles-lot01-2026.json",
 "pactols-pdl-chemille-2026.json",
 "pactols-pdl-communes-nouvelles-lot02-2026.json",
 "pactols-pdl-oree-anjou-mod50-2026.json",
 "pactols-pdl-wikidata-p374-2026.json",
]
def publier(rdf:Path,cog:dict,publications:list[dict])->dict:
 if sha(rdf)!=RDF_SHA: raise ValueError("Pactols th17 : SHA-256 différent")
 prev=[x for p in publications for x in p["alignements_Pactols_COG_valides_2026"]]
 codes={x["code_insee"] for x in prev}; arks={x["ark_pactols"] for x in prev}
 if len(prev)!=1212 or len(codes)!=1212 or len(arks)!=1212:
  raise ValueError("La publication antérieure doit totaliser 1212 liens uniques")
 if cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026:
  raise ValueError("COG PDL incorrect")
 com=[p for p in cog["periodes_com"] if p["typecom"]=="COM" and
      p["debut_inclus"]<="2026-01-01" and
      (p["fin_exclue"] is None or p["fin_exclue"]>"2026-01-01")]
 if len(com)!=1228 or len({x["code_insee"] for x in com})!=1228:
  raise ValueError("COG courant PDL non unique")
 names={code:values[0] for code,values in CASES.items()}
 scan=analyser_rdf(rdf,names)
 all_arks={ark for name,old,date,ark,anc in CASES.values() for ark in (ark,anc)}
 evid=completer_rdf(rdf,all_arks)
 records=[]
 for code,(name,old,date,ark,anc) in sorted(CASES.items()):
  if code in codes or ark in arks or anc in arks or ark==anc:
   raise ValueError("Collision avec une publication antérieure : "+code)
  candidates=scan["explicites"][code]
  if len(candidates)!=2 or {p["ark"] for p in candidates}!={ark,anc}:
   raise ValueError("Deux ARK concurrents et seulement deux attendus : "+code)
  current=next(x for x in candidates if x["ark"]==ark)
  former=next(x for x in candidates if x["ark"]==anc)
  if (current["prefLabels_fr"]!=[name] or
      current["deprecie"] or current["remplace"] or
      former["deprecie"] or former["remplace"] or
      not former["prefLabels_fr"] or
      len(former["prefLabels_fr"])!=1):
   raise ValueError("Concepts historiques et contemporains non séparables : "+code)
  from auditer_pactols_polynesie_2026 import label_compatible
  if not (label_compatible(old,former["prefLabels_fr"][0]) or
          (code=="72137" and former["prefLabels_fr"]==["Fresnaye-sur-Chédouet"])):
   raise ValueError("Le libellé de l'ancienne commune n'est pas corroboré : "+code)
  for candidate in (current,former):
   if candidate["insee_exactMatch"]!=[{"uri":URI+code,"famille":"commune","code":code}]:
    raise ValueError("URI INSEE RDF contradictoire : "+code)
   e=evid[candidate["ark"]]
   links=[u for u in e["exactMatch_tous"] if u.startswith((
      "http://id.insee.fr/geo/","https://id.insee.fr/geo/"))]
   if links!=[URI+code] or e["remplacements_explicites"]:
    raise ValueError("URI INSEE supplémentaire ou remplacement : "+code)
  periods=[x for x in cog["periodes_com"]
           if x["typecom"]=="COM" and x["code_insee"]==code]
  periods.sort(key=lambda x:x["debut_inclus"])
  if ([(x["libelle"],x["fin_exclue"]) for x in periods] !=
      [(old,date),(name,None)] or periods[-1]["debut_inclus"]!=date):
   raise ValueError("Chronologie COG ancienne/nouvelle : "+code)
  moves=[x for x in cog["lignes_mouvements_cog"]
         if x["code_apres"]==code and x["date_effet"]==date and x["mod"]=="32"]
  if not any(m["code_avant"]==code and m["typecom_avant"]=="COM" and
             m["typecom_apres"]=="COM" and m["libelle_avant"]==old and
             m["libelle_apres"]==name for m in moves):
   raise ValueError("Création COM à code conservé absente : "+code)
  if not any(m["code_avant"]==code and m["typecom_avant"]=="COM" and
             m["typecom_apres"]=="COMD" and m["libelle_apres"]==old for m in moves):
   raise ValueError("Ancienne COMD non attestée : "+code)
  # Les notes du concept contemporain doivent mentionner la date de
  # création et le nom de la commune actuelle. Un texte RDF ne suffit
  # jamais seul à établir la relation.
  notes=evid[ark]["notes_histoire"]+evid[ark]["notes"]+evid[ark]["definitions"]
  if not any(date in n and name in n for n in notes):
   raise ValueError("Note RDF/Insee de création absente : "+code)
  records.append({
    "code_insee":code,"libelle_COG_2026":name,
    "ark_pactols":ark,"libelle_pactols":name,
    "ark_ancienne_commune_distinct":anc,"libelle_ancienne_commune":old,
    "uri_insee":URI+code,"predicat_source":"skos:exactMatch",
    "source_RDF_Pactols_sha256":RDF_SHA,"source_registre":SOURCE,
    "date_evenement_COG":date,
    "nature_evenement_COG":"MOD32_CREATION_COMMUNE_NOUVELLE",
    "type_ancienne_commune_apres":"COMD",
    "millesime_validation":2026,"date_validation":"2026-11-18",
    "statut":"correspondance_PDL_commune_nouvelle_validee_2026",
    "portee_chronologique":"2026_SEULEMENT",
    "relations_historiques_inferees":0
  })
 if len(records)!=3 or len({x["ark_pactols"] for x in records})!=3:
  raise ValueError("Trois identités uniques requises")
 return {"schema":SCHEMA,"region":"pdl","millesime_cog":"2026-01-01",
         "source_registre":SOURCE,"source_RDF_Pactols_sha256":RDF_SHA,
         "source_COG":"docs/data/lieux-chronologie/cog-pdl.json",
         "source_qualification":"recette/lieux/PDL-NEUF-COLLISIONS-HISTORIQUES-2026.md",
         "alignements_publies_precedemment":1212,"nouveaux_alignements":3,
         "total_alignements_PDL_2026":1215,"communes_PDL_COG_2026":1228,
         "communes_a_instruire":13,"nouvelles_geometries":0,
         "liens_historiques_inferes":0,
         "alignements_Pactols_COG_valides_2026":records}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ("rdf","cog","sortie"):
  p.add_argument("--"+name,type=Path,required=True)
 p.add_argument("--publications-dir",type=Path,required=True)
 a=p.parse_args()
 if a.sortie.exists():raise ValueError("Sortie déjà présente")
 read=lambda path:json.loads(path.read_text(encoding="utf-8"))
 d=publier(a.rdf,read(a.cog),[read(a.publications_dir/n) for n in PREVIOUS])
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(d,sort_keys=True,ensure_ascii=False,
                                  separators=(",",":"))+"\n",encoding="utf-8")
 print("PDL_TROIS_COLLISIONS_1215",len(d["alignements_Pactols_COG_valides_2026"]))
if __name__=="__main__":main()
