#!/usr/bin/env python3
"""PACA : qualifier les ARK des huit communes nouvelles sans les publier.

Sépare les communes nouvelles COG des anciennes communes fusionnées, y compris
quand le code est conservé. Les liens exactMatch identiques ne suffisent pas à
prouver l'identité ontologique d'un ARK historique et d'une commune nouvelle.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from auditer_pactols_polynesie_2026 import (
    RDF, SKOS, OWL, DCT, XML, ARK, RDF_SHA, RDF_COMMIT,
    analyser_rdf, norm
)
from auditer_paca_trois_renommages_rdf_2026 import sha256

SCHEMA="adlfi.lieux.paca.communes_nouvelles.8.exactmatch.2026.audit.v1"
CASES={
    "04033":{"nom":"Ubaye-Serre-Ponçon","date":"2017-01-01","arks":["26678/pcrtC1Vi7jqzBS","26678/pcrtDcVUj2Mdw9"]},
    "04120":{"nom":"Val d'Oronaye","date":"2016-01-01","arks":["26678/pcrtjDzQ2Y9N5o","26678/pcrtjMIYKdPaHG"]},
    "05001":{"nom":"Abriès-Ristolas","date":"2019-01-01","arks":["26678/pcrtGQ7nGPZN7K"]},
    "05024":{"nom":"Valdoule","date":"2017-07-01","arks":["26678/pcrtAUevxwngAh","26678/pcrteug78RKN9a"]},
    "05039":{"nom":"Aubessagne","date":"2018-01-01","arks":["26678/pcrtFGmyycRjcC","26678/pcrtp9Ljm1lvVd"]},
    "05053":{"nom":"Garde-Colombe","date":"2016-01-01","arks":["26678/pcrtKc33Ttmi9L","26678/pcrtYB42tOKsY7"]},
    "05101":{"nom":"Vallouise-Pelvoux","date":"2017-01-01","arks":["26678/pcrt2BsRDBxggr","26678/pcrt6KSOx6bX7u"]},
    "05118":{"nom":"Val Buëch-Méouge","date":"2016-01-01","arks":["26678/pcrth0vgSHba4G","26678/pcrtjKbaVOnEjn"]},
}
EXPECTED_NUM=8
TARGET_ARKS={ark for c in CASES.values() for ark in c["arks"]}
INSEE=re.compile(r"^https?://id\.insee\.fr/geo/([^/?#]+)/([^/?#]+)/?$",re.I)

def noms_compatibles(label:str,nom:str)->bool:
    x=norm(label);y=norm(nom)
    return x==y or x.startswith(y+" ")

def completer_concepts(rdf:Path)->dict:
    out={}
    p=ET.iterparse(rdf,events=("start","end"))
    _,root=next(p)
    if root.tag!=RDF+"RDF":raise ValueError("RDF source inattendu")
    for event,el in p:
        if event!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):continue
        m=ARK.fullmatch(el.get(RDF+"about",""))
        if not m or m.group(1) not in TARGET_ARKS:
            el.clear();root.clear();continue
        ark=m.group(1)
        if ark in out:raise ValueError("Concept dupliqué dans le RDF : "+ark)
        all_exact=sorted({x.get(RDF+"resource","") for x in el.findall(SKOS+"exactMatch")
                          if x.get(RDF+"resource","")})
        insee=[{"uri":u,"famille":match.group(1),"identifiant":match.group(2)}
               for u in all_exact if (match:=INSEE.fullmatch(u))]
        notes=[{"type":t,"texte":(x.text or "").strip()[:1300]}
               for t in ("historyNote","changeNote","scopeNote")
               for x in el.findall(SKOS+t) if (x.text or "").strip()]
        out[ark]={
            "prefLabels_fr":sorted({x.text.strip() for x in el.findall(SKOS+"prefLabel")
                                  if x.text and (x.get(XML+"lang") or "").lower().startswith("fr")}),
            "altLabels_fr":sorted({x.text.strip() for x in el.findall(SKOS+"altLabel")
                                 if x.text and (x.get(XML+"lang") or "").lower().startswith("fr")}),
            "insee_exactMatch":insee,
            "autres_exactMatch":[u for u in all_exact if not INSEE.fullmatch(u)],
            "owl_deprecated":any((x.text or "").strip().lower() in ("true","1")
                                 for x in el.findall(OWL+"deprecated")),
            "dct_isReplacedBy":[x.get(RDF+"resource") or (x.text or "").strip()
                                 for x in el.findall(DCT+"isReplacedBy")],
            "dct_replaces":[x.get(RDF+"resource") or (x.text or "").strip()
                             for x in el.findall(DCT+"replaces")],
            "skos_related":[x.get(RDF+"resource") for x in el.findall(SKOS+"related")],
            "notes":notes,
        }
        el.clear();root.clear()
    if set(out)!=TARGET_ARKS:raise ValueError("Candidats Pactols manquants : "+str(sorted(TARGET_ARKS-set(out))))
    return out

def reconstruire_cog(cog:dict)->dict:
    if (cog.get("region")!="paca" or cog.get("millesime_cog")!=2026
        or len(cog.get("periodes_com",[]))!=1116
        or len(cog.get("alignements_Pactols_COG_valides_2026",[]))!=103):
        raise ValueError("Historique COG PACA altéré")
    result={}
    for code,spec in CASES.items():
        periods=sorted(
            [x for x in cog["periodes_com"] if x["code_insee"]==code and x["typecom"]=="COM"],
            key=lambda x:x["debut_inclus"])
        if (len(periods)!=2 or periods[1]["libelle"]!=spec["nom"]
            or periods[1]["debut_inclus"]!=spec["date"]
            or periods[0]["fin_exclue"]!=spec["date"]
            or periods[1]["fin_exclue"] is not None):
            raise ValueError("Continuité du code de commune nouvelle différente : "+code)
        events=sorted(
            [m for m in cog["lignes_mouvements_cog"]
             if m["code_apres"]==code and m["date_effet"]==spec["date"]
             and m["mod"]=="32" and m["typecom_avant"]=="COM"
             and m["typecom_apres"]=="COM" and m["libelle_apres"]==spec["nom"]],
            key=lambda x:x["code_avant"])
        parentCodes={e["code_avant"] for e in events}
        if len(events)<2 or len(parentCodes)<2 or code not in parentCodes:
            raise ValueError("Fusion avec code conservé non prouvée : "+code)
        result[code]={
            "date_creation_commune_nouvelle":spec["date"],
            "code_INSEE_conserve":code,
            "ancienne_commune_porteuse_code":periods[0]["libelle"],
            "ancienne_periode":{"debut":periods[0]["debut_inclus"],"fin":periods[0]["fin_exclue"]},
            "commune_nouvelle":{"nom":spec["nom"],"debut":spec["date"]},
            "communes_sources":[{"code":m["code_avant"],"nom":m["libelle_avant"],
                                 "id_evenement":m["id"]} for m in events],
            "nature_evenement":"MOD32_FUSION_COMMUNE_NOUVELLE"
        }
    return result

def classer(ark:str,proof:dict,nom_actuel:str,anciens:list[str],code:str)->str:
    labels=proof["prefLabels_fr"]
    alt=proof["altLabels_fr"]
    nouveau=any(noms_compatibles(n,nom_actuel) for n in labels)
    ancien=any(noms_compatibles(n,old) for n in labels for old in anciens)
    if proof["owl_deprecated"] or proof["dct_isReplacedBy"]:
        return "CONCEPT_DEPRECIE_OU_REMPLACE_A_INSTRUIRE"
    if nouveau and not ancien:
        return "CANDIDAT_IDENTITE_COMMUNE_NOUVELLE_SELON_LIBELLE"
    if ancien and not nouveau:
        return "IDENTITE_ANCIENNE_COMMUNE_PORTEUSE_CODE"
    if nouveau and ancien:
        return "LIBELLE_MIXTE_A_INSTRUIRE"
    return "IDENTITE_NON_RESOLUE"

def produire(rdf:Path,cog:dict,preflight:dict)->dict:
    if sha256(rdf)!=RDF_SHA:raise ValueError("RDF Pactols-Lieux 2026 non conforme")
    if preflight.get("schema")!="adlfi.lieux.paca.exactmatch.preflight.2026.v1":
        raise ValueError("Préflight PACA inattendu")
    excluded={x["code_insee"]:x for x in preflight.get("exceptions_cog_pactols",[])}
    if not set(CASES).issubset(excluded) or preflight["bilan"]["candidats_conformes_apres_preflight"]!=832:
        raise ValueError("Huit fusions non comprises dans les exceptions PACA")
    histories=reconstruire_cog(cog)
    scanned=analyser_rdf(rdf,{k:v["nom"] for k,v in CASES.items()})
    meta=completer_concepts(rdf)
    if scanned["concepts_RDF_examines"]!=50556:
        raise ValueError("Nombre de concepts RDF différent de la recette PACA")
    out=[]
    for code,spec in CASES.items():
        expected=sorted(spec["arks"])
        ex=excluded[code]
        hits=scanned["explicites"][code]
        if (sorted(x["ark"] for x in hits)!=expected
            or sorted(ex["ark_candidats"])!=expected):
            raise ValueError("ARK concurrents du code modifiés : "+code)
        parents=histories[code]["communes_sources"]
        anciens=sorted({p["nom"] for p in parents})
        candidates=[]
        for item in hits:
            ark=item["ark"];details=meta[ark]
            if (details["prefLabels_fr"]!=item["prefLabels_fr"]
                or details["altLabels_fr"]!=item["altLabels_fr"]
                or details["owl_deprecated"]!=item["deprecie"]):
                raise ValueError("Preuves RDF incohérentes : "+ark)
            allcodes={x["identifiant"] for x in details["insee_exactMatch"] if x["famille"]=="commune"}
            if code not in allcodes:
                raise ValueError("Candidat sans exactMatch au code attendu : "+ark)
            candidates.append({
                "ark_pactols":ark,**details,
                "qualification_de_recette":classer(ark,details,spec["nom"],anciens,code),
                "code_COG_2026":code,
                "nouveau_lien_valide":False,
            })
        out.append({
            "code_COG_2026":code,"libelle_COG_2026":spec["nom"],
            "historique_COG":histories[code],
            "statut_preflight":ex["statut"],
            "candidats_Pactols":candidates,
            "concepts_lexicaux_non_validants":scanned["lexicaux_sans_exactMatch_987"].get(code,[]),
            "decision_editoriale":"NON_PRISE",
            "publication":"AUCUNE",
        })
    summary=Counter(p["qualification_de_recette"] for x in out for p in x["candidats_Pactols"])
    return {
        "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIANTE",
        "sources":{
            "pactols":{"repo":"frantiq/PACTOLS","commit":RDF_COMMIT,"sha256":RDF_SHA},
            "cog":{"fichier":"docs/data/lieux-chronologie/cog-paca.json","millésime":"2026-01-01"},
            "preflight":"recette/lieux/PACA-PREFLIGHT-EXACTMATCH-2026.json",
        },
        "bilan":{
            "communes_nouvelles_a_instruire":8,
            "ARK_vers_codes_contemporains":len(TARGET_ARKS),
            "concepts_RDF_examines":scanned["concepts_RDF_examines"],
            "classes_de_recette":dict(sorted(summary.items())),
            "nouvelles_validations_2026":0,
            "etats_historiques_inferes":0,
            "geometries_modifiees":0,
        },
        "dossiers":out,
        "limites":[
            "Un exactMatch Pactols vers un code de commune nouvelle partagé avec une ancienne commune ne prouve pas que le concept désigne la commune nouvelle.",
            "Les labels des concepts historiques et contemporains peuvent être contradictoires ; ils servent à trier les candidats, pas à valider les relations.",
            "Les mouvements COG MOD32 documentent la succession des communes mais ne fusionnent pas leurs ARK.",
            "La validité des liens est limitée au millésime de qualification, sauf relations historiques explicitement instruites.",
        ]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf",type=Path,required=True)
    p.add_argument("--cog",type=Path,required=True)
    p.add_argument("--preflight",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette neuve hors docs")
    r=produire(a.rdf,
        json.loads(a.cog.read_text(encoding="utf-8")),
        json.loads(a.preflight.read_text(encoding="utf-8")))
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("PACA_HUIT_COMMUNES_NOUVELLES_AUDIT",json.dumps({
        "bilan":r["bilan"],
        "candidats":[{"code":x["code_COG_2026"],"nom":x["libelle_COG_2026"],
            "ARK":[{"ark":p["ark_pactols"],"qualification":p["qualification_de_recette"],
                    "pref":p["prefLabels_fr"],"alt":p["altLabels_fr"]}
                  for p in x["candidats_Pactols"]]} for x in r["dossiers"]],
        "rapport_sha256":sha256(a.sortie)
    },ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
