#!/usr/bin/env python3
"""Consultation ponctuelle de Pactols vivant sur deux codes réutilisés (39137,71566).

Résultats purement observationnels : ne déduit jamais l'absence globale du
thésaurus d'une recherche négative. Aucun ARK n'est créé ou modifié.
"""
from __future__ import annotations
import argparse,datetime,json,re,urllib.request,urllib.error,urllib.parse
from pathlib import Path

BASE="https://pactols.frantiq.fr/opentheso/api/search"
SKOS="http://www.w3.org/2004/02/skos/core#"
QUERIES=("Saint-Hymetière-sur-Valouse","Saint-Hymetière","Chemilla",
         "Verdun-Ciel","Verdun-sur-le-Doubs")
TARGETS={
 "26678/pcrt80xbz0p4vht8kdd4mtdx":"Saint-Hymetière-sur-Valouse",
 "26678/pcrt2v0xk9OjyW":"Chemilla",
 "26678/pcrtoFlfDwt01N":"Verdun-sur-le-Doubs",
}
def extract_candidates(payload):
    if isinstance(payload,dict):nodes=[payload]
    elif isinstance(payload,list):nodes=[v for v in payload if isinstance(v,dict)]
    else:return []
    data=[]
    for el in nodes:
        uri=el.get("@id","")
        if not isinstance(uri,str):continue
        labs=el.get(SKOS+"prefLabel",[])
        matches=el.get(SKOS+"exactMatch",[])
        def parse_labels(seq):
            if not isinstance(seq,list):return []
            return sorted({x.get("@value","") for x in seq if isinstance(x,dict)
                           and x.get("@language","").lower()=="fr" and x.get("@value")})
        def parse_links(seq):
            if not isinstance(seq,list):return []
            return sorted({x.get("@id","") for x in seq if isinstance(x,dict) and x.get("@id")})
        if "/26678/" not in uri:continue
        data.append({"uri":uri,"pref_fr":parse_labels(labs),
                     "exactmatch":parse_links(matches)})
    return data

def verifier():
    results=[];seen={}
    for term in QUERIES:
        q=urllib.parse.urlencode(dict(q=term,theso="th17",lang="fr",format="jsonld"))
        url=BASE+"?"+q
        row={"requete":term,"url":url,"http_status":None,"json_valide":False,"concepts":[]}
        try:
            req=urllib.request.Request(url,headers={"Accept":"application/ld+json, application/json",
                                                      "User-Agent":"AdlFI-Pactols-P1-recette/1"})
            with urllib.request.urlopen(req,timeout=18) as resp:
                payload=json.loads(resp.read(3_000_000).decode("utf8"))
                row["http_status"]=resp.status
                row["json_valide"]=True
                row["concepts"]=extract_candidates(payload)
                for c in row["concepts"]:
                    if any(k in c["uri"] for k in TARGETS):
                        seen[c["uri"]]=c
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,OSError) as err:
            row["erreur"]=str(err)[:200]
        results.append(row)
    found={}
    for ark,label in TARGETS.items():
        obj=next((v for key,v in seen.items() if "/"+ark in key),None)
        found[ark]={"libelle_attendu":label,
                    "observe_recherche_api":obj is not None,
                    "pref_fr_observes":obj["pref_fr"] if obj else [],
                    "liens_exactmatch_observes":obj["exactmatch"] if obj else [],
                    "limite":"L'absence en réponse de recherche ne démontre pas l'absence de concept ou d'assertion."}
    return {"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source":"Pactols vivant / Opentheso API search th17",
            "requêtes":results,"ark_cibles":found,
            "absence_globale_deduite":False,
            "validation_nouvelle":0,"contours_historiques_attribues":0}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--sortie",type=Path,required=True)
    a=p.parse_args();result=verifier()
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"ark_cibles":result["ark_cibles"],
                      "recherches":[{k:r[k] for k in ("requete","http_status","json_valide")} for r in result["requêtes"]],
                      "validation_nouvelle":0},ensure_ascii=False,indent=2))
