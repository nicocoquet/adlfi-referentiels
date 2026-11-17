#!/usr/bin/env python3
"""La Réunion : contrôler les 24 exactMatch Pactols–COG 2026 sans les publier.

Le registre de PR 30 est une préinstruction, non une preuve d'approbation.
La validation ne pourra être appliquée qu'après confrontation des RDF/COG épinglés.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

RDF="{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
SKOS="{http://www.w3.org/2004/02/skos/core#}"
OWL="{http://www.w3.org/2002/07/owl#}"
DCT="{http://purl.org/dc/terms/}"
XML="{http://www.w3.org/XML/1998/namespace}"
ARK=re.compile(r"^https?://ark\.frantiq\.fr/ark:/(26678/[A-Za-z0-9]+)$")
URI=re.compile(r"^https?://id\.insee\.fr/geo/commune/([0-9]{5})/?$")
EXPECTED={f"974{i:02d}" for i in range(1,25)}
SHAS={
    "v_commune_2026.csv":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
    "v_commune_depuis_1943.csv":"08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
    "v_mvt_commune_2026.csv":"8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
}
RDF_SHA="3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"

def empreinte(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()

def lire_csv(path:Path)->list[dict]:
    with path.open("r",encoding="utf-8-sig",newline="") as stream:
        r=csv.DictReader(stream,delimiter=";" if path.name.startswith("REUNION-") else ",")
        data=list(r)
    if not data or any(None in row or any(x is None for x in row.values()) for row in data):
        raise ValueError("CSV manquant ou incohérent : "+str(path))
    return data

def normaliser(v:str)->str:
    t=unicodedata.normalize("NFKD",v.casefold())
    return " ".join(re.findall(r"[a-z0-9]+","".join(c for c in t if not unicodedata.combining(c))))

def libelle_compatible(actual:str,pref:str)->bool:
    return normaliser(pref)==normaliser(actual) or (
        pref.startswith(actual+" (") and pref.endswith(")")
        and normaliser(pref[pref.rfind("(")+1:-1])=="la reunion"
    )

def candidats_rdf(path:Path)->dict[str,list[dict]]:
    found=collections.defaultdict(list)
    stream=ET.iterparse(path,events=("start","end"))
    _,root=next(stream)
    if root.tag!=RDF+"RDF":
        raise ValueError("Source Pactols non RDF/XML")
    for event,el in stream:
        if event!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):
            continue
        match=ARK.fullmatch(el.get(RDF+"about",""))
        if not match:
            el.clear();root.clear();continue
        if el.tag==RDF+"Description" and not any(
            x.get(RDF+"resource")==SKOS[1:-1]+"Concept"
            for x in el.findall(RDF+"type")
        ):
            el.clear();root.clear();continue
        exact=set()
        for item in el.findall(SKOS+"exactMatch"):
            m=URI.fullmatch(item.get(RDF+"resource",""))
            if m:exact.add(m.group(1))
        matches=sorted(exact&EXPECTED)
        if matches:
            labels=[x.text.strip() for x in el.findall(SKOS+"prefLabel")
                    if x.text and x.get(XML+"lang","").lower().startswith("fr")]
            dep=any((x.text or "").strip().lower() in ("true","1")
                    for x in el.findall(OWL+"deprecated"))
            info={"ark":match.group(1),"prefLabels_fr":sorted(labels),
                  "codes_exactmatch":sorted(exact),
                  "deprecie":dep,"remplace":bool(el.findall(DCT+"isReplacedBy"))}
            for code in matches:
                found[code].append(info)
        el.clear();root.clear()
    return {code:sorted(found.get(code,[]),key=lambda x:x["ark"]) for code in sorted(EXPECTED)}

def controler_cog(dossier:Path)->tuple[dict,dict]:
    for name,expected in SHAS.items():
        if empreinte(dossier/name)!=expected:
            raise ValueError("Empreinte officielle COG différente : "+name)
    current=lire_csv(dossier/"v_commune_2026.csv")
    now={r["COM"]:r["LIBELLE"] for r in current
         if r["TYPECOM"]=="COM" and r["DEP"]=="974"}
    if set(now)!=EXPECTED:
        raise ValueError("24 codes COG 974 attendus")
    periods=[r for r in lire_csv(dossier/"v_commune_depuis_1943.csv")
             if r["TYPECOM"]=="COM" and r["COM"].startswith("974")]
    moves=[r for r in lire_csv(dossier/"v_mvt_commune_2026.csv")
           if r["COM_AV"].startswith("974") or r["COM_AP"].startswith("974")]
    division=[r for r in moves if r["MOD"]=="20" and r["DATE_EFF"]=="1965-02-05"]
    if (len(periods),len(moves),len(division))!=(24,25,2):
        raise ValueError("Historique COG Réunion hors périmètre connu")
    if {r["COM_AP"] for r in division}!={"97414","97424"} or {
        r["COM_AV"] for r in division}!={"97414"}:
        raise ValueError("Division de Saint-Louis en 1965 non attestée")
    return now,{"periodes_COG":len(periods),"lignes_mouvements":len(moves),
                "lignes_division_1965":len(division)}

def auditer(dossier:Path,rdf:Path,registre:Path,sortie:Path)->dict:
    if empreinte(rdf)!=RDF_SHA:
        raise ValueError("Source RDF Pactols différente du commit épinglé")
    current,histoire=controler_cog(dossier)
    input_rows=lire_csv(registre)
    if len(input_rows)!=24 or {r["code_INSEE_2026"] for r in input_rows}!=EXPECTED:
        raise ValueError("Registre de revue Réunion non exhaustif")
    proofs=candidats_rdf(rdf)
    rows=[]
    for source in sorted(input_rows,key=lambda r:r["code_INSEE_2026"]):
        code=source["code_INSEE_2026"]
        if source["libelle_COG_2026"]!=current[code]:
            raise ValueError("Libellé COG incompatible pour "+code)
        if source["uri_INSEE_declaree_dans_Pactols"]!="http://id.insee.fr/geo/commune/"+code:
            raise ValueError("URI préinstruite non conforme : "+code)
        allp=proofs[code]
        matching=[x for x in allp if x["ark"]==source["ark_Pactols_candidat"]]
        valid=(len(allp)==1 and len(matching)==1 and
               matching[0]["codes_exactmatch"]==[code] and
               not matching[0]["deprecie"] and not matching[0]["remplace"] and
               matching[0]["prefLabels_fr"]==[source["prefLabel_fr_Pactols"]] and
               libelle_compatible(current[code],source["prefLabel_fr_Pactols"]))
        rows.append({"code_insee":code,"libelle_COG_2026":current[code],
                     "ark_pactols_candidat":source["ark_Pactols_candidat"],
                     "pactols_preuves":allp,
                     "statut":"ELIGIBLE_SELON_REGLE" if valid else "A_INSTRUIRE",
                     "evenement_1965":code in ("97414","97424"),
                     "geometrie_historique":None,
                     "statut_validation_public":"NON_PUBLIE"})
    result={"schema":"adlfi.lieux.reunion.audit.cog-pactols-2026.v1",
            "source_COG_SHA256":SHAS,"source_Pactols_SHA256":RDF_SHA,
            "annee_COG":"2026-01-01","historique":histoire,
            "bilan":{"communes":len(rows),
                     "eligibles":sum(x["statut"]=="ELIGIBLE_SELON_REGLE" for x in rows),
                     "a_instruire":sum(x["statut"]=="A_INSTRUIRE" for x in rows),
                     "validations_publiees_par_audit":0,
                     "geometries_historiques_publiees":0},
            "lignes":rows}
    if "docs" in sortie.resolve().parts or sortie.exists():
        raise ValueError("Interdiction d'écriture publique ou d'écrasement")
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cog-dir",type=Path,required=True)
    parser.add_argument("--pactols-rdf",type=Path,required=True)
    parser.add_argument("--registre",type=Path,required=True)
    parser.add_argument("--sortie",type=Path,required=True)
    args=parser.parse_args()
    r=auditer(args.cog_dir,args.pactols_rdf,args.registre,args.sortie)
    print(json.dumps(r["bilan"],ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
