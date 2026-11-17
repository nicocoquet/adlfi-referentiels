#!/usr/bin/env python3
"""Échantillonnage diagnostique de 5 points Hao sur rasters JP2 L2A fournis.

Ce script ne télécharge aucun produit et n'affirme pas la provenance des
fichiers passés en argument. Les pixels SCL sont des classes automatiques
(20 m), non des observations de terrain, et ne décrivent pas tout le polygone.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from inventorier_assets_hao_sentinel2 import POINTS, ITEM_ID

SCL={
  0:"NO_DATA",1:"SATURATED_DEFECTIVE",2:"DARK_AREA",
  3:"CLOUD_SHADOW",4:"VEGETATION",5:"NOT_VEGETATED",
  6:"WATER",7:"UNCLASSIFIED",8:"CLOUD_MEDIUM_PROBABILITY",
  9:"CLOUD_HIGH_PROBABILITY",10:"THIN_CIRRUS",11:"SNOW_ICE",
}
BANDS=("B02_10m","B03_10m","B04_10m","B08_10m","SCL_20m")

def inspect_dataset(path, pts=POINTS):
    import rasterio
    from rasterio.warp import transform
    from rasterio.windows import Window
    records=[]
    with rasterio.open(path) as ds:
        if ds.crs is None or not ds.crs.is_projected:
            raise ValueError("CRS raster projeté non renseigné")
        if ds.count!=1:
            raise ValueError("Un asset monobande attendu")
        lon=[p["lon"] for p in pts]
        lat=[p["lat"] for p in pts]
        xs,ys=transform("EPSG:4326",ds.crs,lon,lat)
        for p,x,y in zip(pts,xs,ys):
            row,col=ds.index(x,y)
            if not(0<=row<ds.height and 0<=col<ds.width):
                records.append({"rang":p["rang"],"etat":"HORS_RASTER","valeur":None})
                continue
            pixel=ds.read(1,window=Window(col,row,1,1),masked=True)
            if pixel.mask is not False and bool(pixel.mask.any()):
                records.append({"rang":p["rang"],"etat":"NO_DATA","valeur":None})
            else:
                val=int(pixel[0,0])
                if ds.nodata is not None and val==ds.nodata:
                    records.append({"rang":p["rang"],"etat":"NO_DATA","valeur":None})
                else:
                    records.append({"rang":p["rang"],"etat":"PIXEL_PRESENT","valeur":val})
        return {
            "crs_raster":str(ds.crs),
            "resolution_pixels_unites_crs":[float(v) for v in ds.res],
            "width":ds.width,"height":ds.height,
            "nodata":ds.nodata,
            "driver":ds.driver,
            "points":records,
        }

def auditer(paths):
    if set(paths)!=set(BANDS):
        raise ValueError("Cinq bandes exactes requises, RGB + NIR + SCL")
    result={band:inspect_dataset(path) for band,path in paths.items()}
    crs_set={rec["crs_raster"] for rec in result.values()}
    if len(crs_set)!=1:
        raise ValueError("CRS divergents entre les cinq fichiers")
    for band in BANDS:
        expected=20 if band=="SCL_20m" else 10
        resolution=result[band]["resolution_pixels_unites_crs"]
        if not all(abs(v-expected)<1e-5 for v in resolution):
            raise ValueError("Résolution native inattendue : "+band)
    points=[]
    for p in POINTS:
        rank=p["rang"]
        items={band:next(x for x in result[band]["points"] if x["rang"]==rank)
               for band in BANDS}
        scl=items["SCL_20m"]["valeur"]
        points.append({
            "rang":rank,
            "longitude":p["lon"],"latitude":p["lat"],
            "pixels":items,
            "classe_SCL":SCL.get(scl,"INCONNUE") if scl is not None else None,
            "couverture_pixels_toutes_bandes":all(v["etat"]=="PIXEL_PRESENT" for v in items.values()),
            "qualification_objet":"NON_ETABLIE",
        })
    return {
       "schema":"adlfi.lieux.polynesie.hao.pixel.sample.v1",
       "statut":"DIAGNOSTIC_POINTS_SEULEMENT",
       "product_id_declare":ITEM_ID,
       "verification_appartenance_fichiers_au_produit":"NON_REALISEE",
       "source_fichiers":"FOURNIS_PAR_OPERATEUR",
       "bandes":result,
       "points":points,
       "limites":[
           "SCL est un masque automatique à 20 m, pas une preuve de récif ou motu",
           "Un point intérieur n'est pas représentatif du polygone entier",
           "Une image nécessite une chaîne de provenance de fichier, date, checksum et grid",
           "Ni analyse des autres pixels, ni vérification de nuages locaux sur toute la surface",
       ],
       "publication":{"images":0,"contours":0,"autorites":0,"ark":0},
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for band in BANDS:
        p.add_argument("--"+band.replace("_","-").lower(),required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    paths={band:getattr(a,band.lower()) for band in BANDS}
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Rapport hors docs, sans écrasement")
    record=auditer(paths)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    for point in record["points"]:
        print("HAO_PIXEL_POINT",json.dumps({
            "rang":point["rang"],"SCL":point["classe_SCL"],
            "pixels_presents":point["couverture_pixels_toutes_bandes"],
        },sort_keys=True))

if __name__=="__main__":
    main()
