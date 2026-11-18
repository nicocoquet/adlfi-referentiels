#!/usr/bin/env python3
"""Recette non validante des trois renommages communaux PACA et des concepts Pactols.

La date et le code COG sont prouvés séparément par l'Insee et par les décrets.
Un ARK Pactols n'est jamais promu sur la seule identité d'un code ou d'un nom.
Le RDF du 22 juillet 2026 est contrôlé et chaque assertion exacte est conservée.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from auditer_pactols_polynesie_2026 import (
    ARK, RDF, SKOS, OWL, DCT, XML, RDF_SHA, RDF_COMMIT, norm
)

SCHEMA="adlfi.lieux.paca.renommages.rdf2026.recette.v1"
SOURCES={
    "04045":{
        "ancien":"Céreste","nouveau":"Céreste-en-Luberon","date":"2024-01-01",
        "decret":"2023-959",
        "url_decret":"https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048226832"
    },
    "05127":{
        "ancien":"Rousset","nouveau":"Rousset-Serre-Ponçon","date":"2025-01-01",
        "decret":"2024-863",
        "url_decret":"https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000050085315"
    },
    "83052":{
        "ancien":"Esparron","nouveau":"Esparron-de-Pallières","date":"2026-01-01",
        "decret":"2025-815",
        "url_decret":"https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000052097266"
    }
}
CODES=set(SOURCES)
INSEE_URI=re.compile(r"^https?://id\.insee\.fr/geo/([^?#]+)/([^/?#]+)/?$",re.I)
INSEE_UUID=re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",re.I)
EXPECTED_RDF_CODES={"04045":[],"05127":["26678/pcrtla4EHGDgDd"],
                    "83052":["26678/pcrt7B7bs9P5g2"]}

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()

def verifier_cog(cog:dict)->list[dict]:
    if (cog.get("schema")!="adlfi.lieux.chronologie.4regions.public-recette.v1"
        or cog.get("millesime_cog")!=2026 or cog.get("region")!="paca"
        or len(cog.get("periodes_com",[]))!=1116
        or len(cog.get("alignements_Pactols_COG_valides_2026",[]))!=103
        or cog.get("geometries_historiques")!=[]):
        raise ValueError("Chronologie COG PACA altérée")
    records=[]
    for code,spec in SOURCES.items():
        periods=[p for p in cog["periodes_com"] if p["code_insee"]==code and p["typecom"]=="COM"]
        periods.sort(key=lambda x:x["debut_inclus"])
        if len(periods)!=2 or any(p["code_insee"]!=code for p in periods):
            raise ValueError("Épisodes COG incohérents : "+code)
        before,after=periods
        if (before["libelle"]!=spec["ancien"] or after["libelle"]!=spec["nouveau"]
            or before["fin_exclue"]!=spec["date"] or after["debut_inclus"]!=spec["date"]
            or after["fin_exclue"] is not None):
            raise ValueError("Historique de dénomination incohérent : "+code)
        events=[m for m in cog["lignes_mouvements_cog"]
                if m["code_avant"]==code and m["code_apres"]==code
                and m["date_effet"]==spec["date"] and m["mod"]=="10"
                and m["libelle_avant"]==spec["ancien"] and m["libelle_apres"]==spec["nouveau"]
                and m["typecom_avant"]=="COM" and m["typecom_apres"]=="COM"]
        if len(events)!=1:
            raise ValueError("Mouvement MOD10 absent ou ambigu : "+code)
        records.append({
            "code_COG":code,"nom_ancien":spec["ancien"],"nom_2026":spec["nouveau"],
            "date_effet":spec["date"],"nature_COG":"MOD10_RENOMMAGE_CODE_CONSERVE",
            "id_evenement_COG":events[0]["id"],"decret":spec["decret"],
            "decret_url":spec["url_decret"],"code_conserve":True
        })
    return records

def match_nom(label:str,spec:dict)->list[str]:
    name=norm(label)
    if not name:
        return []
    out=[]
    for target,key in ((spec["ancien"],"LIBELLE_ANCIEN"),(spec["nouveau"],"LIBELLE_NOUVEAU")):
        expected=norm(target)
        if name==expected:
            out.append(key+"_EXACT")
        elif name.startswith(expected+" "):
            out.append(key+"_AVEC_QUALIFICATIF_OU_HOMONYME")
    return out

def scan_rdf(rdf:Path)->dict:
    if sha256(rdf)!=RDF_SHA:
        raise ValueError("Instantané RDF Pactols non conforme")
    all_candidates={code:[] for code in SOURCES}
    direct={code:[] for code in SOURCES}
    count=0
    parser=ET.iterparse(rdf,events=("start","end"))
    _,root=next(parser)
    if root.tag!=RDF+"RDF":
        raise ValueError("RDF Pactols source absent")
    for event,el in parser:
        if event!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):
            continue
        match=ARK.fullmatch(el.get(RDF+"about",""))
        if not match:
            el.clear();root.clear();continue
        if el.tag==RDF+"Description" and not any(
            x.get(RDF+"resource")=="http://www.w3.org/2004/02/skos/core#Concept"
            for x in el.findall(RDF+"type")):
            el.clear();root.clear();continue
        count+=1
        ark=match.group(1)
        pref=[{"texte":(x.text or "").strip(),"lang":x.get(XML+"lang")}
              for x in el.findall(SKOS+"prefLabel") if (x.text or "").strip()]
        alt=[{"texte":(x.text or "").strip(),"lang":x.get(XML+"lang")}
             for x in el.findall(SKOS+"altLabel") if (x.text or "").strip()]
        exact=sorted({x.get(RDF+"resource","") for x in el.findall(SKOS+"exactMatch")
                      if x.get(RDF+"resource")})
        insee=[]
        for uri in exact:
            m=INSEE_URI.fullmatch(uri)
            if m:
                insee.append({"uri":uri,"famille":m.group(1),"identifiant":m.group(2),
                              "est_UUID":bool(INSEE_UUID.fullmatch(m.group(2)))})
        direct_targets={x["identifiant"] for x in insee
                        if x["famille"].lower()=="commune" and x["identifiant"] in CODES}
        matches={}
        for code,spec in SOURCES.items():
            reasons=[]
            if code in direct_targets:reasons.append("EXACTMATCH_INSEE_CODE_COURANT")
            for label in pref:
                if label["lang"] in ("fr","fr-FR",None):
                    reasons.extend("PREF_"+x for x in match_nom(label["texte"],spec))
            for label in alt:
                if label["lang"] in ("fr","fr-FR",None):
                    reasons.extend("ALT_"+x for x in match_nom(label["texte"],spec))
            if reasons:
                matches[code]=sorted(set(reasons))
        if matches:
            row={
                "ark":ark,"prefLabel":pref,"altLabel":alt,
                "exactMatch":exact,"exactMatch_INSEE":insee,
                "owl_deprecated":any((x.text or "").strip().lower() in ("true","1")
                                     for x in el.findall(OWL+"deprecated")),
                "dct_isReplacedBy":[x.get(RDF+"resource") or (x.text or "").strip()
                                     for x in el.findall(DCT+"isReplacedBy")],
                "dct_replaces":[x.get(RDF+"resource") or (x.text or "").strip()
                                for x in el.findall(DCT+"replaces")],
                "skos_broader":[x.get(RDF+"resource") for x in el.findall(SKOS+"broader")],
                "skos_related":[x.get(RDF+"resource") for x in el.findall(SKOS+"related")],
                "notes":[{"type":tag,"texte":(x.text or "").strip()[:650]}
                         for tag in ("historyNote","changeNote","scopeNote")
                         for x in el.findall(SKOS+tag) if (x.text or "").strip()]
            }
            for code,why in matches.items():
                all_candidates[code].append({**row,"motifs_de_recuperation":why,
                    "identification_commune_2026":"A_INSTRUIRE",
                    "decision_editoriale":"NON_PRISE"})
                if code in direct_targets:
                    direct[code].append(ark)
        el.clear();root.clear()
    for code in SOURCES:
        all_candidates[code].sort(key=lambda x:x["ark"])
        if sorted(set(direct[code]))!=EXPECTED_RDF_CODES[code]:
            raise ValueError("Assertions directes différentes du préflight PACA : "+code)
    return {"concepts_RDF_examines":count,"dossiers":all_candidates,
            "ARK_directement_assertes_COG_2026":direct}

def construire(cog:dict,scan:dict)->dict:
    events=verifier_cog(cog)
    dossiers=[]
    for e in events:
        code=e["code_COG"]
        candidates=scan["dossiers"][code]
        dossiers.append({**e,
            "ARK_directement_assertes_vers_code_2026":scan["ARK_directement_assertes_COG_2026"][code],
            "concepts_pactols_a_examiner":candidates,
            "nombre_candidats":len(candidates),
            "qualification":"COG_RENOMMAGE_CONFIRME_PACTOLS_A_INSTRUIRE",
            "nouvelle_validation_2026":False})
    return {
        "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
        "sources":{"pactols":{"commit":RDF_COMMIT,"sha256":RDF_SHA,
                   "fichier":"Pactols_Lieux_th17_20260722.rdf"},
                   "cog":{"millésime":"2026-01-01",
                   "fichier":"docs/data/lieux-chronologie/cog-paca.json"},
                   "decrets":"Légifrance, texte authentique indiqué dans chaque dossier"},
        "bilan":{"renommages_officiels_controles":3,
                 "concepts_RDF_examines":scan["concepts_RDF_examines"],
                 "ARK_directs_vers_codes_2026":sum(len(v) for v in
                     scan["ARK_directement_assertes_COG_2026"].values()),
                 "nouveaux_ARK_valides":0,"index_public_modifie":False,
                 "geometries_historiques_inferrees":0},
        "dossiers":dossiers,
        "limites":[
            "Un changement de dénomination avec code constant ne prouve pas l'identité ontologique d'un concept Pactols.",
            "Les correspondances lexicales et les éventuels exactMatch UUID sont des pistes, jamais des preuves de code COG 2026.",
            "Les homonymes sont conservés explicitement pour éviter une correspondance sur le seul nom.",
            "Le millésime 2026 est distinct des anciennes périodes COG, sans rétroprojection d'ARK.",
        ]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf",required=True,type=Path)
    p.add_argument("--cog",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Rapport nouveau hors docs/ uniquement")
    cog=json.loads(a.cog.read_text(encoding="utf-8"))
    verifier_cog(cog)
    scan=scan_rdf(a.rdf)
    report=construire(cog,scan)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                        encoding="utf-8")
    print("PACA_TROIS_RENOMMAGES_RDF_AUDIT",json.dumps({
        "bilan":report["bilan"],
        "candidats":{x["code_COG"]:x["nombre_candidats"] for x in report["dossiers"]},
        "sha256_rapport":sha256(a.sortie)
    },ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
