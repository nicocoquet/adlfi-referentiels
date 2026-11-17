#!/usr/bin/env python3
"""Préflight des assets du produit Sentinel-2A Hao du 26 décembre 2022.

Inventaire de métadonnées STAC et de modalités d'accès, sans téléchargement
de rasters ni classification radiométrique improvisée. Ne jamais exposer de
jetons ou URLs signées dans le rapport.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ITEM_ID="S2A_MSIL2A_20221226T193851_N0510_R056_T07KEV_20240715T211924"
ITEM_URL="https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a/items/"+ITEM_ID
CIBLES={"B02_10m","B03_10m","B04_10m","B08_10m","SCL_20m","CLD_20m","TCI_10m","thumbnail"}
POINTS=[
    {"rang":1,"lon":-140.7412651,"lat":-18.3624007},
    {"rang":2,"lon":-140.7531718,"lat":-18.4187267},
    {"rang":3,"lon":-140.8136959,"lat":-18.3995869},
    {"rang":4,"lon":-140.8287866,"lat":-18.2859358},
    {"rang":5,"lon":-140.9301156,"lat":-18.2668435},
]
def safe_host(url):
    if not isinstance(url,str):return None
    p=urlparse(url)
    return {"scheme":p.scheme,"host":p.hostname,"path_suffix":Path(p.path).suffix.lower()}
def get_json(url):
    with urlopen(Request(url,headers={"Accept":"application/json",
          "User-Agent":"AdlFI-Lieux-Hao-assets-audit/1.0"}),timeout=35) as r:
        if int(r.headers.get("content-length","0") or 0)>3_000_000:
            raise ValueError("Métadonnées STAC trop volumineuses")
        return json.load(r)

def describe_asset(name,asset):
    href=asset.get("href")
    return {
        "asset_key":name,
        "title":asset.get("title"),
        "media_type":asset.get("type"),
        "roles":asset.get("roles"),
        "host_et_extension":safe_host(href),
        "bandes_eo":asset.get("eo:bands"),
        "bandes_raster":asset.get("raster:bands"),
        "projection_epsg":asset.get("proj:epsg"),
        "projection_shape":asset.get("proj:shape"),
        "projection_transform":asset.get("proj:transform"),
        "spatial_resolution_m":asset.get("gsd"),
        "href_existe":bool(href),
        "verification_des_pixels":"NON_REALISEE",
        "acces_aux_pixels":"NON_TESTE",
    }

def audit(item):
    if item.get("id")!=ITEM_ID or item.get("collection")!="sentinel-2-l2a":
        raise ValueError("Identité ou collection STAC inattendue")
    timestamp=(item.get("properties") or {}).get("datetime")
    if not isinstance(timestamp,str) or not timestamp.startswith("2022-12-26T19:38:51"):
        raise ValueError("Date de la scène non conforme")
    from shapely.geometry import Point,shape
    footprint=shape(item["geometry"])
    if not footprint.is_valid or footprint.is_empty:
        raise ValueError("Footprint invalide")
    covered=[p["rang"] for p in POINTS if footprint.covers(Point(p["lon"],p["lat"]))]
    if covered!=[1,2,3,4,5]:
        raise ValueError("Le footprint STAC ne contient plus les cinq points")
    assets=item.get("assets") or {}
    if not isinstance(assets,dict):raise ValueError("Assets STAC non structurés")
    descriptors={name:describe_asset(name,asset) for name,asset in sorted(assets.items())
                 if isinstance(asset,dict)}
    return {
       "schema":"adlfi.lieux.polynesie.hao.sentinel2.assets.preflight.v1",
       "statut":"RECETTE_NON_VALIDANTE",
       "source_item_stac":ITEM_URL,
       "item_id":ITEM_ID,
       "acquisition_utc":timestamp,
       "plateforme":item.get("properties",{}).get("platform"),
       "cloud_cover_tuile_pourcent":item.get("properties",{}).get("eo:cloud_cover"),
       "points_couverts_par_empreinte":covered,
       "nombre_assets":len(descriptors),
       "asset_keys":sorted(descriptors),
       "assets":descriptors,
       "cibles_raster_presumee_par_nom":sorted(set(descriptors).intersection(CIBLES)),
       "perimetre_expertise":"METADONNEES_SEULEMENT",
       "niveau_certitude":"Footprint et catalogue, non couverture des pixels",
       "classification_geographique":"NON_ETABLIE",
       "publication":{"raster":0,"geometrie":0,"autorite":0,"ark":0},
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sortie",required=True,type=Path)
    args=p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Sortie hors docs et sans écrasement")
    result=audit(get_json(ITEM_URL))
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("HAO_STAC_ASSETS",json.dumps({
        "nombre":result["nombre_assets"],
        "keys":result["asset_keys"],
        "cibles":result["cibles_raster_presumee_par_nom"],
        "sources":{name:{"host":a["host_et_extension"],"type":a["media_type"],
                           "projection_epsg":a["projection_epsg"],
                           "roles":a["roles"]}
                   for name,a in result["assets"].items()},
    },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":main()
