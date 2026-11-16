#!/usr/bin/env python3
"""Reconnaissance des paquets GEOFLA 2015 via l'API IGN Géoplateforme.

N'ESSAIE PAS de reconstituer un contour régional à partir des données 2026.
Le catalogue peut ne plus exposer une édition 2015 ; l'absence de résultat
dans cette API ne prouve pas l'inexistence d'archives historiques ailleurs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE="https://data.geopf.fr/telechargement"
ENDPOINTS={
  "geofla_2015":BASE+"/resource/GEOFLA?"+urllib.parse.urlencode({
    "editionDateFrom":"2015-01-01","editionDateTo":"2015-12-31",
    "format":"SHP","zone":"FRA","page":1,"limit":50}),
  "geofla_liste":BASE+"/resource/GEOFLA?page=1&limit=50",
  "capabilities":BASE+"/capabilities?page=1&limit=50&lang=fre&zone=FRA",
}
def sonder(timeout:int=35):
    report={
      "schema":"adlfi.lieux.ign.geofla2015.recherche_catalogue.v1",
      "statut":"RECONNAISSANCE_SOURCE_PRIMAIRE_NON_VALIDANTE",
      "reference_documentaire":"https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/telechargement/",
      "resultats":{},
      "archive_originale_2015_validee":False,
      "geometries_inferrees":0,
    }
    for name,url in ENDPOINTS.items():
        result={"url":url,"exploitable":False}
        try:
            req=urllib.request.Request(url,headers={"Accept":"application/atom+xml, application/xml, text/xml",
                                                     "User-Agent":"AdlFI-Lieux-recherche-GEOFLA-archives/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                blob=r.read(2_000_001)
                result["http_status"]=r.status
                result["content_type"]=r.headers.get("Content-Type","")
                result["octets_recus"]=len(blob)
            if len(blob)>2_000_000:
                result["erreur"]="Réponse trop grande pour le sondage"
            else:
                result["sha256_reponse"]=hashlib.sha256(blob).hexdigest()
                try:
                    root=ET.fromstring(blob)
                    result["xml_racine"]=root.tag
                    titles=[el.text.strip() for el in root.iter()
                        if el.tag.endswith("title") and el.text and el.text.strip()]
                    names=[el.attrib.get("href","") for el in root.iter()
                        if el.tag.endswith("link") and el.attrib.get("href")]
                    result["titres"] = titles[:80]
                    result["liens_contenant_GEOFLA_2015"]=[
                        href for href in names if "GEOFLA" in href.upper() and "2015" in href][:40]
                    result["liens_2015"]=[href for href in names if "2015" in href][:40]
                    result["exploitable"]=True
                except ET.ParseError:
                    result["erreur"]="Contenu distant non interprétable comme Atom/XML"
                    result["apercu"]=blob[:250].decode("utf8","replace")
        except urllib.error.HTTPError as e:
            result["http_status"]=e.code
            result["erreur"]="HTTP "+str(e.code)
        except Exception as e:
            result["erreur"]=type(e).__name__+": "+str(e)[:250]
        report["resultats"][name]=result
    return report

def ecrire(r,out):
    out=Path(out)
    if "docs" in out.resolve().parts:raise ValueError("Recette non autorisée sous docs")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sortie",type=Path,required=True)
    a=p.parse_args()
    r=sonder()
    ecrire(r,a.sortie)
    print(json.dumps(r,ensure_ascii=False,indent=2))
