#!/usr/bin/env python3
"""Lister les sous-ressources de GEOFLA en interrogeant toutes les pages IGN.

La date dans un nom de paquet ne suffit PAS à qualifier sa couche (CANTON,
DÉPARTEMENT ou COMMUNE). Ne présuppose ni URL ni contenu des archives.
"""
from __future__ import annotations
import argparse
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE="https://data.geopf.fr/telechargement/resource/GEOFLA"
NS="{http://www.w3.org/2005/Atom}"
def liste(maxpages=20,limit=50):
    found={}
    pages=[]
    for n in range(1,maxpages+1):
        url=f"{BASE}?page={n}&limit={limit}"
        with urllib.request.urlopen(urllib.request.Request(url,headers={
            "User-Agent":"AdlFI-Lieux-Archives-IGN-2015/1.0",
        }),timeout=45) as response:
            root=ET.fromstring(response.read(2_000_000))
        entries=root.findall(NS+"entry")
        this=[]
        for entry in entries:
            title=entry.findtext(NS+"title",default="")
            links=[l.get("href","") for l in entry.findall(NS+"link")]
            for link in links:
                if "/resource/GEOFLA/" in link and link.split("?")[0]!=BASE:
                    code=link.split("?")[0].rsplit("/",1)[-1]
                    if code:
                        found[code]={"code":code,"titre":title,
                                      "fiche":link.split("?")[0]}
                        this.append(code)
                        break
        pages.append({"page":n,"url":url,"entrees":len(entries),
                       "sous_ressources_trouvees":len(this)})
        if len(entries)<limit:break
    depts=sorted((v for v in found.values()
                 if "DEPARTEMENT" in v["code"].upper() and "2015" in v["code"]),
                key=lambda r:r["code"])
    metro=sorted((v for v in depts
                  if "LAMB93" in v["code"].upper() and "FXX" in v["code"].upper()),
                 key=lambda r:r["code"])
    return {
        "schema":"adlfi.lieux.geofla_paquets_disponibles.v1",
        "source":BASE,"statut":"INVENTAIRE_ARCHIVES_IGN_SANS_EXTRACTION",
        "pagination":pages,
        "nombre_paquets":len(found),
        "paquets_departements_2015":depts,
        "paquets_departements_2015_metropole":metro,
        "tous_les_paquets_2015":[v for k,v in sorted(found.items()) if "2015" in k],
        "note":"Il faut ouvrir et vérifier les fichiers du paquet choisi avant tout usage cartographique",
    }
def enregistrer(r,path):
    path=Path(path)
    if "docs" in path.resolve().parts:raise ValueError("Ne pas publier l'inventaire sous docs")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
if __name__=="__main__":
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--sortie",required=True,type=Path)
    args=a.parse_args()
    report=liste()
    enregistrer(report,args.sortie)
    print(json.dumps({
        "nombre_paquets":report["nombre_paquets"],
        "pagination":report["pagination"],
        "paquets_departements_2015_metropole":report["paquets_departements_2015_metropole"]
    },ensure_ascii=False,indent=2))
