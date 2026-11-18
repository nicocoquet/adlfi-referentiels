#!/usr/bin/env python3
"""Publier 49160 (MOD32) et 85084 (MOD21) en préservant leurs histoires distinctes."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import sha
from auditer_pactols_polynesie_2026 import RDF_SHA,analyser_rdf
from qualifier_pdl_ark_multiples_2026 import completer_rdf
from auditer_pdl_ingrandes_essarts_2024 import PUBS

SCHEMA="adlfi.lieux.pactols.pdl.2024-ingrandes-essarts.2026.public.v1"
SOURCE="recette/lieux/PDL-INGRANDES-ESSARTS-PUBLICATION-2026.md"
QUALIF="recette/lieux/PDL-INGRANDES-ESSARTS-2024.md"
WDREG="recette/lieux/PDL-INGRANDES-WIKIDATA-2024.json"
CODE_ING="49160"
CODE_ESS="85084"
ARK_ING="26678/pcrtj64zr6gnns4mnfd2828b"
ARK_ING_OLD="26678/pcrtQBSwT6fBDW"
ARK_ESS="26678/pcrt0PrU3oVWxo"
ARK_ESS_OLD="26678/pcrtFmygG5m3QZ"
URI="http://id.insee.fr/geo/commune/"
UUID_INSEE="2cdbc96f-9287-4279-80c9-b3c169bb1fed"
QID="Q123475717"
OLDID=2309862185
def publier(rdf:Path,cog:dict,pubs:list[dict],wiki:dict)->dict:
 if sha(rdf)!=RDF_SHA:raise ValueError("RDF Frantiq th17 non conforme")
 if cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026:
  raise ValueError("COG PDL 2026 incorrect")
 existing=[x for p in pubs for x in p["alignements_Pactols_COG_valides_2026"]]
 used_codes={x["code_insee"] for x in existing}
 used_arks={x["ark_pactols"] for x in existing}
 if len(existing)!=1215 or len(used_codes)!=1215 or len(used_arks)!=1215:
  raise ValueError("Les 1215 liens précédents doivent être intacts et uniques")
 if {CODE_ING,CODE_ESS}&used_codes or {ARK_ING,ARK_ESS,ARK_ING_OLD,ARK_ESS_OLD}&used_arks:
  raise ValueError("Collision ARK ou code")
 latest=[p for p in cog["periodes_com"] if p["typecom"]=="COM" and
         p["debut_inclus"]<="2026-01-01" and
         (p["fin_exclue"] is None or p["fin_exclue"]>"2026-01-01")]
 if len(latest)!=1228 or len({p["code_insee"] for p in latest})!=1228:
  raise ValueError("COG PDL courant incomplet")
 names={CODE_ING:"Ingrandes-le-Fresne-sur-Loire",CODE_ESS:"Essarts-en-Bocage"}
 cur={p["code_insee"]:p for p in latest}
 if any(cur.get(c,{}).get("libelle")!=v or
        cur[c]["debut_inclus"]!="2024-01-01" for c,v in names.items()):
  raise ValueError("Libellés ou débuts d'épisode 2024 non conformes")
 scan=analyser_rdf(rdf,names)
 targets={p["ark"] for c in names for p in
          scan["explicites"][c]+scan["lexicaux_sans_exactMatch_987"].get(c,[])}
 extra=completer_rdf(rdf,targets)
 ing_lex=scan["lexicaux_sans_exactMatch_987"].get(CODE_ING,[])
 ing_exp=scan["explicites"][CODE_ING]
 ess_exp=scan["explicites"][CODE_ESS]
 if (len(ing_lex)!=1 or ing_lex[0]["ark"]!=ARK_ING or
     len(ing_exp)!=2 or ARK_ING_OLD not in {x["ark"] for x in ing_exp} or
     len(ess_exp)!=2 or {x["ark"] for x in ess_exp}!={ARK_ESS,ARK_ESS_OLD} or
     scan["lexicaux_sans_exactMatch_987"].get(CODE_ESS)):
  raise ValueError("Les anciens et nouveaux concepts Pactols ont changé")
 current_ing=ing_lex[0]
 current_ess=next(x for x in ess_exp if x["ark"]==ARK_ESS)
 for x,expected in ((current_ing,names[CODE_ING]),(current_ess,names[CODE_ESS])):
  if (x["prefLabels_fr"]!=[expected] or x.get("deprecie",False) or x.get("remplace",False) or
      extra[x["ark"]]["remplacements_explicites"]):
   raise ValueError("Concept 2026 remplacé ou libellé incertain : "+x["ark"])
 def insee(ark):
  return sorted(u for u in extra[ark]["exactMatch_tous"] if
                u.startswith(("http://id.insee.fr/geo/","https://id.insee.fr/geo/")))
 def wikidata(ark):
  return sorted(u for u in extra[ark]["exactMatch_tous"] if "wikidata.org/" in u)
 if (insee(ARK_ING)!=[URI+UUID_INSEE] or
     wikidata(ARK_ING)!=["https://www.wikidata.org/wiki/"+QID] or
     insee(ARK_ING_OLD)!=[URI+CODE_ING] or
     insee(ARK_ESS)!=[URI+CODE_ESS] or
     insee(ARK_ESS_OLD)!=[URI+CODE_ESS]):
  raise ValueError("Chaînes de preuves INSEE et Wikidata non conformes")
 if (not any("2024" in d and "Saint-Sigismond" in d for d in extra[ARK_ING]["definitions"]) or
     not any("2024-05-31" in n for n in extra[ARK_ING]["notes_histoire"])):
  raise ValueError("Concept contemporain Ingrandes non daté de 2024")
 if (not any("2024" in d and "Sainte-Florence" in d and "L'Oie" in d
             for d in extra[ARK_ESS]["definitions"]) or
     not any("2024-06-03" in n for n in extra[ARK_ESS]["notes_histoire"])):
  raise ValueError("Concept Essarts non mis à jour après la scission")
 if (wiki.get("schema")!="adlfi.lieux.pdl.ingrandes.wikidata-p374.frozen.v1" or
     wiki.get("qid")!=QID or wiki.get("lastrevid")!=OLDID or
     wiki.get("P31")!=["Q484170"] or wiki.get("P374")!=[CODE_ING] or
     wiki.get("P571")!=["2024-01-01"] or
     wiki.get("revision_url")!=
      "https://www.wikidata.org/w/index.php?title="+QID+"&oldid="+str(OLDID) or
     wiki.get("source_pactols_ARK")!=ARK_ING):
  raise ValueError("Snapshot Wikidata de l'identité 2024 non admissible")
 movement=cog["lignes_mouvements_cog"]
 def require_cog(code,old,mod):
  if not any(m["code_avant"]==code and m["code_apres"]==code and
             m["date_effet"]=="2024-01-01" and m["mod"]==mod and
             m["libelle_avant"]==old and m["libelle_apres"]==names[code] and
             m["typecom_avant"]=="COM" and m["typecom_apres"]=="COM"
             for m in movement):
   raise ValueError("Mouvement COG 2024 non corroboré : "+code)
  periods=sorted((p for p in cog["periodes_com"] if
       p["typecom"]=="COM" and p["code_insee"]==code),
       key=lambda p:p["debut_inclus"])
  if (len(periods)!=3 or periods[-2]["libelle"]!=old or
      periods[-2]["fin_exclue"]!="2024-01-01" or
      periods[-1]["libelle"]!=names[code]):
   raise ValueError("Périodes COG 2024 non corroborées : "+code)
 require_cog(CODE_ING,"Ingrandes-Le Fresne sur Loire","32")
 require_cog(CODE_ESS,"Essarts en Bocage","21")
 if not any(m["date_effet"]=="2024-01-01" and m["mod"]=="32" and
             m["code_avant"]=="49321" and m["code_apres"]==CODE_ING and
             m["typecom_apres"]=="COM" for m in movement):
  raise ValueError("Fusion de Saint-Sigismond absente")
 if not all(any(m["date_effet"]=="2024-01-01" and m["mod"]=="21" and
                 m["code_avant"]==CODE_ESS and m["code_apres"]==c and
                 m["typecom_apres"]=="COM" for m in movement)
            for c in ("85165","85212")):
  raise ValueError("Rétablissement de L'Oie et Sainte-Florence absent")
 result=[
   {"code_insee":CODE_ING,"libelle_COG_2026":names[CODE_ING],
    "libelle_pactols":names[CODE_ING],"ark_pactols":ARK_ING,
    "ark_concept_2016_non_promu":ARK_ING_OLD,
    "uri_insee_uuid_RDF_Pactols":URI+UUID_INSEE,
    "uri_insee_uuid_resolue":False,
    "uri_insee_courante_COG":URI+CODE_ING,
    "qid_Wikidata":QID,
    "URI_Wikidata_exactMatch":"https://www.wikidata.org/wiki/"+QID,
    "revision_Wikidata":OLDID,"revision_Wikidata_url":wiki["revision_url"],
    "code_INSEE_Wikidata_P374":CODE_ING,
    "predicat_Pactols_Wikidata":"skos:exactMatch",
    "predicat_Wikidata_INSEE":"P374",
    "source_registre":SOURCE,"source_qualification":QUALIF,
    "source_RDF_Pactols_sha256":RDF_SHA,
    "date_evenement_COG":"2024-01-01",
    "nature_evenement_COG":"MOD32_CREATION_COMMUNE_NOUVELLE",
    "millesime_validation":2026,"date_validation":"2026-11-18",
    "statut":"correspondance_PDL_2024_via_Wikidata_validee_2026",
    "portee_chronologique":"2026_SEULEMENT",
    "relations_historiques_inferees":0},
   {"code_insee":CODE_ESS,"libelle_COG_2026":names[CODE_ESS],
    "libelle_pactols":names[CODE_ESS],"ark_pactols":ARK_ESS,
    "ark_ancienne_commune_distinct":ARK_ESS_OLD,
    "uri_insee_RDF_Pactols":URI+CODE_ESS,
    "predicat_Pactols_INSEE":"skos:exactMatch",
    "source_registre":SOURCE,"source_qualification":QUALIF,
    "source_RDF_Pactols_sha256":RDF_SHA,
    "date_evenement_COG":"2024-01-01",
    "nature_evenement_COG":"MOD21_RETABLISSEMENT_COMMUNES",
    "codes_communes_retablies":["85165","85212"],
    "millesime_validation":2026,"date_validation":"2026-11-18",
    "statut":"correspondance_PDL_2024_MOD21_validee_2026",
    "portee_chronologique":"2026_SEULEMENT",
    "relations_historiques_inferees":0},
 ]
 return {"schema":SCHEMA,"region":"pdl","millesime_cog":"2026-01-01",
         "source_registre":SOURCE,"source_qualification":QUALIF,
         "source_RDF_Pactols_sha256":RDF_SHA,
         "source_COG":"docs/data/lieux-chronologie/cog-pdl.json",
         "source_Wikidata_2024":WDREG,
         "alignements_publies_precedemment":1215,"nouveaux_alignements":2,
         "total_alignements_PDL_2026":1217,"communes_PDL_COG_2026":1228,
         "communes_a_instruire":11,
         "geometries_nouvelles":0,"liens_historiques_inferes":0,
         "alignements_Pactols_COG_valides_2026":result}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ("rdf","cog","publications-dir","wikidata","sortie"):
  p.add_argument("--"+key,required=True,type=Path)
 a=p.parse_args()
 if a.sortie.exists():raise ValueError("Refus d'écraser le fichier de sortie")
 read=lambda path:json.loads(path.read_text(encoding="utf8"))
 pub=publier(a.rdf,read(a.cog),[
   read(a.publications_dir/x) for x in PUBS],read(a.wikidata))
 a.sortie.parent.mkdir(parents=True,exist_ok=True)
 a.sortie.write_text(json.dumps(pub,ensure_ascii=False,sort_keys=True,
     separators=(",",":"))+"\n",encoding="utf8")
 print("PDL_DEUX_2024_1217",json.dumps({"ajoutes":2,"total":1217,"exceptions":11,
    "uuid_insee_resolue":False,"geometries_nouvelles":0,
    "liens_historiques_inferes":0},sort_keys=True))
if __name__=="__main__":main()
