#!/usr/bin/env python3
"""Rives-du-Fougerais : audit non validant de l'UUID INSEE cité par Loterre.

Le concept Pactols ne contient aucun exactMatch INSEE. Sa variante code INSEE
85041 (Cezais) est contredite par le COG courant 85292. Loterre ajoute un
alignement vers un UUID INSEE : résoudre celui-ci auprès de l'INSEE, sans
supposer que le lien Loterre soit également asserté par Pactols.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import quote
from xml.etree import ElementTree as ET

SCHEMA="adlfi.lieux.pdl.rives_fougerais.insee_loterre.2026.audit.v1"
CODE="85292"
OLD="85041"
NEW_ARK="26678/pcrtjr01c5sg25ngf5hq8898"
OLD_ARK="26678/pcrtRm3hz8YCOM"
SOURCE_CONCEPT="http://data.loterre.fr/ark:/67375/D63-G704CG2Q-F"
WIKIDATA="https://www.wikidata.org/wiki/Q123475897"
UUID="ce20d8e4-bed6-4207-9f1e-ca4909a6bcbd"
URI="http://id.insee.fr/geo/commune/"+UUID
ENDPOINT="https://rdf.insee.fr/sparql?query="+quote("describe<"+URI+">",safe="")
INSEE="https://www.insee.fr/fr/metadonnees/geographie/commune/85292-rives-du-fougerais"
INSEE_CEZAIS="https://www.insee.fr/fr/metadonnees/geographie/commune-deleguee/85041-cezais"
ARRETE="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048728237"
LOTERRE="https://loterre.istex.fr/D63/fr/page/-G704CG2Q-F?clang=fr"
RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
OWL="http://www.w3.org/2002/07/owl#"
GEO="http://rdf.insee.fr/def/geo#"

def sha(b):return hashlib.sha256(b).hexdigest()
def collecter(destination:Path):
 if destination.exists():raise ValueError("La source officielle doit être acquise dans un fichier neuf")
 req=Request(ENDPOINT,headers={"Accept":"application/rdf+xml",
                               "User-Agent":"AdlFI-Referentiels/1.0 (academic RDF audit)",
                               "Cache-Control":"no-cache"})
 with urlopen(req,timeout=35) as response:
  data=response.read(1_000_001)
  url=response.geturl()
 if not url.startswith("https://rdf.insee.fr/"):
  raise ValueError("La source a quitté le domaine officiel INSEE")
 if len(data)>1_000_000:raise ValueError("Source RDF trop volumineuse")
 ET.fromstring(data)
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_bytes(data)
 print("RIVES_UUID_INSEE_RECUPERE",json.dumps({"uri":URI,"url":url,"sha256":sha(data),
  "octets":len(data)},ensure_ascii=False))
def analyser_rdf(data:bytes):
 root=ET.fromstring(data)
 if root.tag!=f"{{{RDF}}}RDF":raise ValueError("RDF/XML INSEE attendu")
 found=[n for n in root if n.attrib.get(f"{{{RDF}}}about")==URI]
 if len(found)!=1:raise ValueError("Sujet UUID INSEE introuvable ou ambigu")
 node=found[0]
 def lit(tag):
  return sorted(set(x.text.strip() for x in node.findall(f"{{{GEO}}}"+tag)
                    if x.text and x.text.strip()))
 def refs(ns,tag):
  return sorted(set(x.attrib[f"{{{RDF}}}resource"]
                    for x in node.findall(f"{{{ns}}}"+tag)
                    if f"{{{RDF}}}resource" in x.attrib))
 code=lit("codeINSEE")
 same=refs(OWL,"sameAs")
 nom=lit("nom")
 nature=refs(RDF,"type")
 return {
  "sujet_UUID":URI,
  "geo_codeINSEE":code,
  "owl_sameAs":same,
  "geo_nom":nom,
  "rdf_type":nature,
  "sha256_corps_RDF":sha(data),
  "octets":len(data),
  "identite_85292_confirmee_OFFICIELLEMENT":(
     code==[CODE] and same==["http://id.insee.fr/geo/commune/"+CODE] and
     nom==["Rives-du-Fougerais"] and nature==[GEO+"Commune"]),
  "code_85041_affirme_par_INSEE":OLD in code
 }
def instruction(cog:dict,ref:dict,published:dict,xml:bytes):
 if (cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026 or
     published.get("schema")!="adlfi.lieux.pactols.pdl.trois_uuid_resolus.2026.public.v1" or
     published.get("total_alignements_PDL_2026")!=1143 or
     published.get("communes_a_instruire")!=85):
  raise ValueError("Référentiel PDL publié altéré")
 if ref.get("schema")!="adlfi.lieux.pdl.quatre_sans_exactmatch.2026.audit.v1":
  raise ValueError("Recette Pactols initiale manquante")
 item=next(x for x in ref["dossiers"] if x["code_COG_2026"]==CODE)
 if (item["nom_COG_2026"]!="Rives-du-Fougerais" or item["date_effet"]!="2024-01-01"
     or item["type_transition"]!="CREATION_COMMUNE_NOUVELLE" or
     item["publication"]!="AUCUNE"):
  raise ValueError("Historique et décision éditoriale du lot précédent non conservés")
 new=next(x for x in item["candidats_Pactols"] if x["ark_pactols"]==NEW_ARK)
 old=next(x for x in item["candidats_Pactols"] if x["ark_pactols"]==OLD_ARK)
 if (new["exactMatch"]!=[] or new["exactMatch_INSEE"]!=[] or
     new["prefLabel"]!=[{"texte":"Rives-du-Fougerais","lang":"fr"}] or
     not any(x["texte"]=="85041 (code Insee)" for x in new["altLabel"]) or
     new["deprecated"] or old["prefLabel"][0]["texte"]!="Thouarsais-Bouildroux"):
  raise ValueError("Concept Pactols ou code parasitaire modifié")
 former={x["code_avant"] for x in cog["lignes_mouvements_cog"] if
         x["code_apres"]==CODE and x["date_effet"]=="2024-01-01" and x["mod"]=="32"
         and x["typecom_apres"]=="COM"}
 if former!={"85041","85271","85292"}:
  raise ValueError("Le COG ne confirme pas la création par trois communes")
 current=[p for p in cog["periodes_com"] if p["code_insee"]==CODE
          and p["debut_inclus"]=="2024-01-01" and p["typecom"]=="COM"]
 if len(current)!=1 or current[0]["libelle"]!="Rives-du-Fougerais":
  raise ValueError("Commune nouvelle COG 2026 non confirmée")
 old_cog=[p for p in cog["periodes_com"] if p["code_insee"]==OLD
          and p["typecom"]=="COM" and p["fin_exclue"]=="2024-01-01"]
 if len(old_cog)!=1 or old_cog[0]["libelle"]!="Cezais":
  raise ValueError("Code d'ancienne Cezais non confirmé")
 rdf=analyser_rdf(xml)
 return {
  "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
  "identite_COG":{"code_courant":CODE,"nom_courant":"Rives-du-Fougerais",
                 "date_effet":"2024-01-01","communes_origine":sorted(former),
                 "source_INSEE":INSEE,"source_arrete":ARRETE},
  "anomalie_source":{"code_chez_Pactols_et_Loterre":OLD,
                     "code_COG_officiel":CODE,
                     "ancien_lieu_85041":"Cezais",
                     "source_INSEE_Cezais":INSEE_CEZAIS,
                     "source_Loterre":LOTERRE,
                     "concept_Loterre":SOURCE_CONCEPT,
                     "concept_Pactols":NEW_ARK,
                     "exactMatch_Pactols_INSEE_absent":True,
                     "code_INSEE_85041_dans_variante_Pactols":True},
  "lien_Loterre_non_Pactols":{"predicat":"skos:exactMatch",
                           "sujet_Loterre":SOURCE_CONCEPT,
                           "objet_INSEE_UUID":URI,
                           "cible_Wikidata":WIKIDATA,
                           "lien_Pactols_vers_Loterre_atteste":False},
  "reponse_RDF_INSEE":rdf,
  "conclusion":{
   "code_COG_85292_resolu_par_UUID_Loterre":rdf["identite_85292_confirmee_OFFICIELLEMENT"],
   "code_source_85041_contre_preuve_officielle":rdf["identite_85292_confirmee_OFFICIELLEMENT"],
   "validation_editeur_Pactols_2026":"A_INSTRUIRE",
   "nouveaux_ARK_valides":0,"publications":0,"geometries":0,
   "relations_historiques_inferees":0},
  "limites":"Loterre ne fournit pas, par sa seule similitude de nom, un exactMatch pour le concept Pactols : ne pas fabriquer un alignement entre les deux thésaurus. La variante 85041 doit être corrigée à la source."
 }
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--collecter",type=Path)
 for name in ("source","cog","recette","publication","sortie"):
  p.add_argument("--"+name,type=Path)
 a=p.parse_args()
 if a.collecter:collecter(a.collecter)
 elif all((a.source,a.cog,a.recette,a.publication,a.sortie)):
  if a.sortie.exists() or "docs" in a.sortie.resolve().parts:raise ValueError("Rapport neuf hors docs")
  load=lambda p:json.loads(p.read_text(encoding="utf-8"))
  d=instruction(load(a.cog),load(a.recette),load(a.publication),a.source.read_bytes())
  a.sortie.parent.mkdir(parents=True,exist_ok=True)
  a.sortie.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
  print("PDL_RIVES_COG_LOTERRE_INSEE",json.dumps({"RDF":d["reponse_RDF_INSEE"],
         "conclusion":d["conclusion"]},ensure_ascii=False,sort_keys=True))
 else:p.error("--collecter SRC ou --source SRC --cog JSON --recette JSON --publication JSON --sortie JSON")
if __name__=="__main__":main()
