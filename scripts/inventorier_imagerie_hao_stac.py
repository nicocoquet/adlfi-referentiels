#!/usr/bin/env python3
"""Hao : inventorier les acquisitions Sentinel-2 L2A du catalogue STAC CDSE.

Audit des métadonnées : ne télécharge aucune image, ne qualifie pas la nature
des cinq composantes et ne déduit pas la nébulosité locale d'un taux par tuile.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API="https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a/items"
COLLECTION="sentinel-2-l2a"
# Points intérieurs calculés à la PR 87 ; l'ordre et les coordonnées sont figés.
POINTS=[
    {"rang":1,"lon":-140.7412651,"lat":-18.3624007,"surface_m2":2415216.230},
    {"rang":2,"lon":-140.7531718,"lat":-18.4187267,"surface_m2":1890678.303},
    {"rang":3,"lon":-140.8136959,"lat":-18.3995869,"surface_m2":1277374.555},
    {"rang":4,"lon":-140.8287866,"lat":-18.2859358,"surface_m2":474780.394},
    {"rang":5,"lon":-140.9301156,"lat":-18.2668435,"surface_m2":404471.058},
]
# Périmètre commun sur toute l'emprise source de la différence (PR 87).
BBOX=[-141.0721,-18.4306,-140.6630,-18.0612]
FENETRES=[
    ("annee_catalogue_geopf_2022","2022-01-01T00:00:00Z","2022-12-31T23:59:59Z"),
    ("periode_recente_2025","2025-01-01T00:00:00Z","2025-12-31T23:59:59Z"),
]
LIMITE_PAR_REQUETE=100

def make_url(start,end):
    if start>=end:raise ValueError("Fenêtre temporelle incorrecte")
    query=urlencode({
        "bbox":",".join(str(v) for v in BBOX),
        "datetime":start+"/"+end,
        "limit":str(LIMITE_PAR_REQUETE),
    })
    return API+"?"+query

def point_dans_emprise(bbox,lon,lat):
    if bbox is None or len(bbox)<4:return False
    return bbox[0]<=lon<=bbox[2] and bbox[1]<=lat<=bbox[3]

def footprint_points(feature):
    """Exiger la géométrie réelle d'emprise et pas seulement la boîte STAC."""
    from shapely.geometry import Point,shape
    geom=feature.get("geometry")
    if not isinstance(geom,dict):
        return []
    poly=shape(geom)
    if poly.is_empty or not poly.is_valid:return []
    return [p["rang"] for p in POINTS
            if point_dans_emprise(feature.get("bbox"),p["lon"],p["lat"])
            and poly.covers(Point(p["lon"],p["lat"]))]

def summarise_feature(feature):
    properties=feature.get("properties") or {}
    timestamp=properties.get("datetime") or properties.get("start_datetime")
    if not timestamp:raise ValueError("Acquisition sans date STAC")
    # Vérifier la syntaxe temporelle, aucune invention à partir du nom d'objet.
    dt=datetime.fromisoformat(timestamp.replace("Z","+00:00"))
    if dt.tzinfo is None:raise ValueError("Date d'acquisition sans fuseau")
    cloud=properties.get("eo:cloud_cover")
    return {
        "id":feature.get("id"),
        "acquisition_utc":dt.astimezone(timezone.utc).isoformat(),
        "cloud_cover_tuile_pourcent":cloud,
        "collection":feature.get("collection"),
        "points_couverts_par_empreinte":footprint_points(feature),
        "bbox":feature.get("bbox"),
        "plateforme":properties.get("platform"),
        "niveau_traitement":properties.get("processing:level"),
        "url_metadonnees":next((link.get("href") for link in feature.get("links",[])
                                  if link.get("rel")=="self"),None),
    }

def interroger(start,end,fetch):
    url=make_url(start,end)
    data=fetch(url)
    if data.get("type")!="FeatureCollection" or not isinstance(data.get("features"),list):
        raise ValueError("Réponse STAC inattendue")
    features=data["features"]
    if len(features)>LIMITE_PAR_REQUETE:raise ValueError("Dépassement limite STAC")
    summaries=[]
    for f in features:
        r=summarise_feature(f)
        if r["points_couverts_par_empreinte"]:
            summaries.append(r)
    summaries.sort(key=lambda s:(s["acquisition_utc"],s["id"] or ""),reverse=True)
    next_links=[l for l in data.get("links",[]) if l.get("rel")=="next"]
    return {
        "url_requete":url,
        "nombre_retournes":len(features),
        "nombre_couvrant_au_moins_un_point":len(summaries),
        "pagination_supplementaire":bool(next_links),
        "consultation_exhaustive":not next_links and len(features)<LIMITE_PAR_REQUETE,
        "scenes":summaries,
        "points_sans_scene":[p["rang"] for p in POINTS
              if not any(p["rang"] in s["points_couverts_par_empreinte"] for s in summaries)],
    }

def online_fetch(url):
    request=Request(url,headers={"Accept":"application/geo+json, application/json",
                                "User-Agent":"AdlFI-GEO-PF-recette/1.0"})
    with urlopen(request,timeout=70) as response:
        return json.load(response)

def auditer(fetch=online_fetch):
    windows=[]
    for label,start,end in FENETRES:
        try:
            result=interroger(start,end,fetch)
            windows.append({"periode":label,"statut":"CATALOGUE_CONSULTE",**result})
        except Exception as exc:
            windows.append({
                "periode":label,
                "statut":"CATALOGUE_INACCESSIBLE_OU_INEXPLOITABLE",
                "type_erreur":type(exc).__name__,
                "erreur":str(exc)[:400],
                "url_requete":make_url(start,end),
                "consultation_exhaustive":False,
                "scenes":[],
                "points_sans_scene":None,
            })
    return {
        "schema":"adlfi.lieux.polynesie.hao.imagerie.catalogue.stac.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "catalogue":API,
        "collection":COLLECTION,
        "fenetres":windows,
        "points_interieurs_PR87":POINTS,
        "emprise_recherche_lon_lat":BBOX,
        "resol_spatiale_nominale_m":"10 m pour quatre bandes Sentinel-2 MSI, à vérifier par asset et produit",
        "limitations":[
            "Un footprint contient le point sans garantir des pixels exploitables à cet emplacement",
            "Le taux de nuages eo:cloud_cover s'applique au produit, pas à la composante",
            "Les dates listées sont celles des produits retournés et pas celles des fonds GEO PF",
            "Une réponse paginée ne prouve pas l'exhaustivité des acquisitions",
            "Aucune classification motu/récif/lagon par le catalogue seul",
            "Aucune acquisition ne peut être déclarée validée sans examen des bandes et métadonnées",
        ],
        "publication":{"imagery":0,"geometries":0,"autorites":0,"ark":0},
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sortie",type=Path,required=True)
    opts=p.parse_args()
    if opts.sortie.exists() or "docs" in opts.sortie.resolve().parts:
        raise ValueError("Écrire hors docs et sans écrasement")
    result=auditer()
    opts.sortie.parent.mkdir(parents=True,exist_ok=True)
    opts.sortie.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    for r in result["fenetres"]:
        print("HAO_STAC",json.dumps({
            "periode":r["periode"],"statut":r["statut"],
            "retournes":r.get("nombre_retournes"),
            "couvrent":r.get("nombre_couvrant_au_moins_un_point"),
            "pagination":r.get("pagination_supplementaire"),
            "scenes":r["scenes"][:4],
            "erreur":r.get("erreur"),
        },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
