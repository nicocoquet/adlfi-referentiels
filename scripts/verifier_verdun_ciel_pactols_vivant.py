#!/usr/bin/env python3
"""Vérification ponctuelle, non validante, de Verdun-Ciel dans Pactols vivant.

L'absence d'un résultat de moteur de recherche ne démontre jamais l'absence
d'un concept dans le thésaurus. Ne crée pas d'ARK ni de relation éditoriale.
"""
from __future__ import annotations
import argparse
import datetime
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://pactols.frantiq.fr/opentheso/api/search"
QUERIES = (
    ("Verdun-Ciel", "json"),
    ("Verdun-Ciel", "jsonld"),
    ("Verdun", "jsonld"),
    ("71566", "jsonld"),
)
ARK = re.compile(r"(?:ark:/|/ark:/|/)(26678/[A-Za-z0-9_\-]+)")
USER_AGENT = "AdlFI-historique-geographique/recette (consultation publique)"

def interprete(body: bytes, content_type: str):
    text = body.decode("utf-8", errors="replace")
    arks = sorted(set(ARK.findall(text)))
    try:
        payload = json.loads(text)
        valid_json = True
    except json.JSONDecodeError:
        payload = None
        valid_json = False
    return {
        "json_parseable": valid_json,
        "type_json": type(payload).__name__ if valid_json else None,
        "contient_verdun_ciel": bool(re.search(r"verdun[\-\s]+ciel", text, re.I)),
        "arks_reperes_dans_reponse": arks[:200],
        "reponse_debut": text[:3500],
        "type_reponse_http": content_type,
        "troncature_reponse": len(body) > 3500
    }

def verifier(timeout: int=18):
    checks=[]
    for term, fmt in QUERIES:
        url=BASE+"?"+urllib.parse.urlencode(dict(q=term,theso="th17",lang="fr",format=fmt))
        result={"requete":term,"format":fmt,"url":url}
        try:
            req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json, application/ld+json, */*"})
            with urllib.request.urlopen(req,timeout=timeout) as response:
                body=response.read(3_000_000)
                result["http_status"]=response.status
                result.update(interprete(body,response.headers.get("Content-Type","")))
        except urllib.error.HTTPError as exc:
            result.update(http_status=exc.code,erreur="erreur_http_"+str(exc.code))
        except (urllib.error.URLError,TimeoutError,OSError) as exc:
            result.update(http_status=None,erreur="inaccessible_ou_timeout",detail=str(exc)[:250])
        checks.append(result)
    valid=[x for x in checks if x.get("http_status")==200 and x.get("json_parseable")]
    if any(x.get("requete")=="Verdun-Ciel" and x.get("contient_verdun_ciel") for x in valid):
        statut="nom_trouve_dans_reponse_api_a_examiner"
    elif not valid:
        statut="verification_api_non_concluante"
    else:
        statut="aucun_nom_confirme_par_requetes_api_non_preuve_absence"
    return {
        "date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "site":"Pactols public / Opentheso",
        "thesaurus":"th17",
        "statut":statut,
        "controles":checks,
        "absence_pactols_confirmee":False,
        "nouvel_ark_valide":None,
        "commentaire":"Un terme peut ne pas être indexé par l'API ; ne jamais assimiler une réponse vide ou indisponible à une absence de concept.",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    result=verifier()
    a.sortie.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in result.items() if k!="controles"},ensure_ascii=False,indent=2))
