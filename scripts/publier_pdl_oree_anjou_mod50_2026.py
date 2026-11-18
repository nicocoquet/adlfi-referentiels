#!/usr/bin/env python3
"""Valider Orée d'Anjou 2026 par transfert de chef-lieu COG MOD50 (49069→49126)."""
from __future__ import annotations
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import sha
from auditer_pactols_polynesie_2026 import (
    ARK,RDF,SKOS,OWL,DCT,XML,RDF_SHA,analyser_rdf
)
from qualifier_pdl_ark_multiples_2026 import completer_rdf

SCHEMA="adlfi.lieux.pactols.pdl.oree-anjou.mod50.2026.public.v1"
CODE="49126"
ANCIEN_CODE="49069"
NOM="Orée d'Anjou"
ARK_ACTUEL="26678/pcrtS50omR9Tb5"
ARK_DRAIN="26678/pcrtlzVsRTHJSP"
ARK_HAUTS_2016="26678/pcrtJmNskrfHiK"
SOURCE="recette/lieux/PDL-OREE-ANJOU-MOD50-2026.md"
URI="http://id.insee.fr/geo/commune/"

def concept_rdf(rdf:Path,ark:str)->dict:
    """Lecture du concept ciblé, avec dépréciation et remplacement complets."""
    parser=ET.iterparse(rdf,events=("start","end"))
    _,root=next(parser)
    found=[]
    for event,el in parser:
        if event!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):
            continue
        match=ARK.fullmatch(el.get(RDF+"about",""))
        if match and match.group(1)==ark:
            labels=sorted({x.text.strip() for x in el.findall(SKOS+"prefLabel")
                           if x.text and x.get(XML+"lang","").lower().startswith("fr")})
            deprecated=any((x.text or "").strip().lower() in ("true","1")
                           for x in el.findall(OWL+"deprecated"))
            replaced=bool(el.findall(DCT+"isReplacedBy"))
            found.append({"prefLabels_fr":labels,"deprecie":deprecated,"remplace":replaced})
        el.clear()
        root.clear()
    if len(found)!=1:
        raise ValueError("Un concept RDF exact doit être trouvé : "+ark)
    return found[0]

def publier(rdf:Path,cog:dict,publications:list[dict])->dict:
    if sha(rdf)!=RDF_SHA:
        raise ValueError("Source RDF Pactols non épinglée")
    if cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026:
        raise ValueError("COG PDL non conforme")
    already=[r for p in publications for r in p["alignements_Pactols_COG_valides_2026"]]
    used_codes={x["code_insee"] for x in already}
    used_arks={x["ark_pactols"] for x in already}
    if len(already)!=1194 or len(used_codes)!=1194 or len(used_arks)!=1194:
        raise ValueError("1149 + 45 = 1194 précédents alignements requis")
    if CODE in used_codes or ARK_ACTUEL in used_arks or ARK_DRAIN in used_arks or ARK_HAUTS_2016 in used_arks:
        raise ValueError("Collision d'ARK ou de code avec les liens précédents")
    current=[x for x in cog["periodes_com"] if x["typecom"]=="COM" and
             x["debut_inclus"]<="2026-01-01" and
             (x["fin_exclue"] is None or x["fin_exclue"]>"2026-01-01")]
    if len(current)!=1228 or len({x["code_insee"] for x in current})!=1228:
        raise ValueError("COG PDL 2026 incomplet")
    episodes=sorted((x for x in cog["periodes_com"]
                     if x["typecom"]=="COM" and x["libelle"]==NOM and
                     x["code_insee"] in (CODE,ANCIEN_CODE)),
                    key=lambda x:x["debut_inclus"])
    if [(x["code_insee"],x["debut_inclus"],x["fin_exclue"])
         for x in episodes]!=[
          ("49069","2015-12-15","2025-01-01"),
          ("49126","2025-01-01",None)]:
        raise ValueError("Deux périodes du code Orée d'Anjou incorrectes")
    transfers=[x for x in cog["lignes_mouvements_cog"]
               if x["date_effet"]=="2025-01-01" and
               x["code_avant"]==ANCIEN_CODE and x["code_apres"]==CODE]
    if (len(transfers)!=1 or transfers[0]["mod"]!="50" or
        transfers[0]["libelle_avant"]!=NOM or transfers[0]["libelle_apres"]!=NOM or
        transfers[0]["typecom_avant"]!="COM" or transfers[0]["typecom_apres"]!="COM"):
        raise ValueError("Le COG ne prouve pas un transfert MOD50 de chef-lieu")
    if not any(x["code_insee"]==CODE and x["libelle"]==NOM for x in current):
        raise ValueError("La commune actuelle n'est pas attestée")
    # Vérifier également les deux concepts sous ce code : Orée est absent
    # de ses exactMatch au code actuel ; Drain y apparaît comme ancienne COM.
    scans=analyser_rdf(rdf,{CODE:NOM})
    lex=scans["lexicaux_sans_exactMatch_987"].get(CODE,[])
    hits=scans["explicites"][CODE]
    if (len(lex)!=1 or lex[0]["ark"]!=ARK_ACTUEL or
        lex[0]["prefLabels_fr"]!=[NOM] or
        len(hits)!=1 or hits[0]["ark"]!=ARK_DRAIN):
        raise ValueError("Les deux ARK Pactols candidats ont changé")
    evidence=completer_rdf(rdf,{ARK_ACTUEL,ARK_DRAIN,ARK_HAUTS_2016})
    def insee(ark):
        return sorted(u for u in evidence[ark]["exactMatch_tous"] if
                      u.startswith(("http://id.insee.fr/geo/","https://id.insee.fr/geo/")))
    if (insee(ARK_ACTUEL)!=[URI+ANCIEN_CODE] or insee(ARK_DRAIN)!=[URI+CODE] or
        insee(ARK_HAUTS_2016)!=[URI+"49065"]):
        raise ValueError("URI INSEE RDF changée ou contradictoire")
    c=concept_rdf(rdf,ARK_ACTUEL)
    if (c["prefLabels_fr"]!=[NOM] or c["deprecie"] or c["remplace"] or
        evidence[ARK_ACTUEL]["remplacements_explicites"]):
        raise ValueError("Concept Orée d'Anjou non courant ou remplacé")
    return {
        "schema":SCHEMA,"region":"pdl","millesime_cog":"2026-01-01",
        "source_registre":SOURCE,"source_RDF_Pactols_sha256":RDF_SHA,
        "source_COG":"docs/data/lieux-chronologie/cog-pdl.json",
        "source_insee_modalites":"https://www.insee.fr/fr/information/8377252",
        "alignements_publies_precedemment":1194,
        "nouveaux_alignements":1,"total_alignements_PDL_2026":1195,
        "communes_PDL_COG_2026":1228,"communes_a_instruire":33,
        "nouvelles_geometries":0,"liens_historiques_inferes":0,
        "alignements_Pactols_COG_valides_2026":[{
           "code_insee":CODE,"libelle_COG_2026":NOM,"libelle_pactols":NOM,
           "ark_pactols":ARK_ACTUEL,
           "ark_ancienne_commune_distinct":ARK_DRAIN,
           "uri_insee_RDF_Pactols":URI+ANCIEN_CODE,
           "uri_insee_courante":URI+CODE,
           "predicat_RDF_Pactols":"skos:exactMatch",
           "source_RDF_Pactols_sha256":RDF_SHA,"source_registre":SOURCE,
           "date_evenement_COG":"2025-01-01",
           "nature_evenement_COG":"MOD50_TRANSFERT_CHEF_LIEU",
           "code_COG_avant":ANCIEN_CODE,
           "code_COG_apres":CODE,
           "millesime_validation":2026,"date_validation":"2026-11-18",
           "statut":"correspondance_PDL_validee_COG_MOD50_2026",
           "portee_chronologique":"2026_SEULEMENT",
           "relations_historiques_inferees":0
        }]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("rdf","cog","base","uuid","lot01","chemille","lot02","sortie"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists():
        raise ValueError("Ne pas écraser le résultat")
    read=lambda f:json.loads(f.read_text(encoding="utf-8"))
    d=publier(a.rdf,read(a.cog),
              [read(a.base),read(a.uuid),read(a.lot01),
               read(a.chemille),read(a.lot02)])
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,
                                  separators=(",",":"))+"\n",encoding="utf-8")
    print("PDL_OREE_MOD50_1195",json.dumps({"ajouts":1,"total":1195,
          "exceptions":33,"source_RDF_49069":True,"mod50_COG_2025":True,
          "geometry_nouvelle":0,"retroprojection":0},sort_keys=True))
if __name__=="__main__":
    main()
