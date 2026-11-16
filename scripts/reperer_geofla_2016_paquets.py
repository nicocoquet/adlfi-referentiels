#!/usr/bin/env python3
"""Repérer et caractériser les paquets officiels GEOFLA DEPARTEMENT 2016.

Le catalogue Atom IGN est paginé. Ne pas présumer qu'un intitulé de paquet
garantit les couches contenues ou la situation au 1er janvier 2016.
Ne télécharge aucune géométrie ; ne publie rien dans docs/.
"""
from __future__ import annotations
import argparse
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE="https://data.geopf.fr/telechargement/resource/GEOFLA"
NS="{http://www.w3.org/2005/Atom}"
HEADERS={"User-Agent":"AdlFI-referentiels-lieux-IGN-2016/1.0"}

def get_atom(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=65) as response:
        if response.status!=200: raise ValueError("HTTP "+str(response.status))
        return ET.fromstring(response.read(4_000_000))

def indexer(maxpages=20,limit=50):
    records={}
    pages=[]
    for n in range(1,maxpages+1):
        url=f"{BASE}?page={n}&limit={limit}"
        root=get_atom(url)
        entries=root.findall(NS+"entry")
        pages.append({"page":n,"nombre_entrees":len(entries)})
        for entry in entries:
            title=entry.findtext(NS+"title",default="")
            for link in entry.findall(NS+"link"):
                href=link.get("href","").split("?")[0]
                if href.startswith(BASE+"/"):
                    code=href.rsplit("/",1)[-1]
                    records[code]={"code":code,"title":title,"fiche":href}
                    break
        if len(entries)<limit:break
    else:
        raise ValueError("Pagination potentiellement incomplète")
    tous_2016=[r for r in records.values() if "2016" in r["code"]]
    dep_2016=[r for r in tous_2016 if "DEPARTEMENT" in r["code"].upper()]
    metro_2016=[r for r in dep_2016 if "LAMB93" in r["code"].upper() and "FXX" in r["code"].upper()]
    if not metro_2016:raise ValueError("Aucun paquet départemental métropolitain GEOFLA 2016 découvert")
    return {
        "schema":"adlfi.lieux.geofla_candidats_2016.v1",
        "statut":"INVENTAIRE_NON_VALIDANT_DES_PAQUETS",
        "source":BASE,"pages":pages,
        "nb_references_catalogue":len(records),
        "paquets_metropolitains_departements_2016":sorted(metro_2016,key=lambda x:x["code"]),
        "paquets_departements_2016":sorted(dep_2016,key=lambda x:x["code"]),
        "autres_paquets_2016":sorted(
            [r for r in tous_2016 if r not in dep_2016],key=lambda x:x["code"]),
        "nb_contours_valides":0,
        "limites":[
            "Le nom d'un paquet ne suffit pas pour identifier sa couche réelle.",
            "L'année d'édition ne prouve pas le découpage exact au premier janvier.",
            "Une future archive sera comparée au COG officiel 2016 et à l'édition IGN 2015.",
        ],
    }

def enregistrer(d,out:Path):
    if "docs" in out.resolve().parts:raise ValueError("Sortie de recette interdite dans docs/")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sortie",required=True,type=Path)
    args=ap.parse_args()
    d=indexer()
    enregistrer(d,args.sortie)
    print(json.dumps({key:d[key] for key in (
        "nb_references_catalogue","paquets_metropolitains_departements_2016",
        "paquets_departements_2016")},ensure_ascii=False,indent=2))
