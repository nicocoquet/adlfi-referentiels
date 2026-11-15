#!/usr/bin/env python3
"""Recette de disponibilité GEOFLA historique IGN : aucun contenu n'est considéré validé par URL seule."""
from __future__ import annotations
import hashlib
import json
import urllib.request
import urllib.error
import argparse
from pathlib import Path

SOURCES = {
    "geoplateforme_GEOFLA": "https://data.geopf.fr/telechargement/resource/GEOFLA",
    "catalogue_IGN_GEOFLA": "https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_GEOFLA",
    "document_IGN_GEOFLA_2_2": "https://geoservices.ign.fr/sites/default/files/2021-07/DC_GEOFLA_2-2.pdf",
    "catalogue_open_data": "https://www.data.gouv.fr/api/1/datasets/geofla-r/",
    "geofla_communes_2015_schema": "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/geoflar-communes-2015",
}
def sonder(sortie:Path):
    data={}
    for name,url in SOURCES.items():
        req=urllib.request.Request(url,headers={"User-Agent":"AdlFI-Lieux-geofla-historique/1.0","Accept":"application/json, text/html, application/xml, */*"})
        try:
            with urllib.request.urlopen(req,timeout=35) as response:
                blob=response.read(800_000)
                data[name]={
                    "url":url,"url_finale":response.geturl(),"http":response.status,
                    "type_contenu":response.headers.get("Content-Type",""),
                    "taille_echantillon_octets":len(blob),
                    "sha256_echantillon":hashlib.sha256(blob).hexdigest(),
                    "extrait":blob[:16000].decode("utf-8","replace")
                }
        except (urllib.error.HTTPError, urllib.error.URLError,TimeoutError) as exc:
            data[name]={"url":url,"statut":"NON_ACCESSIBLE","erreur":str(exc)}
    sortie=Path(sortie)
    if "docs" in sortie.resolve().parts:raise ValueError("Recette interdite dans docs")
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({k:{f:v.get(f) for f in ("http","type_contenu","statut","erreur","url_finale")}
                      for k,v in data.items()},ensure_ascii=False,indent=2))
    return data
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sortie",type=Path,required=True)
    args=p.parse_args()
    sonder(args.sortie)
