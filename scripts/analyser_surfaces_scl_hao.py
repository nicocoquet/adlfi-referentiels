#!/usr/bin/env python3
"""Recette locale : statistiques SCL sur les cinq polygones d'écart de Hao.

Géométries sources : GEO PF (Hao 20200) moins ISPF Ile 23, SHA officiels
épinglés. Raster : SCL_20m JP2 local vérifié par le manifeste de la PR 90.

Aucune classification écologique/juridique des objets, aucun raster publié.
La surface de cellule est une approximation de la couverture du polygone ;
ne pas la confondre avec l'aire géodésique.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from comparer_contours_geopf_ispf import GEO_PF_SHA, ISPF_GEO_SHA, lire_source_geopf, aire
from auditer_hao_ispf_geopf import polygones
from qualifier_jointures_geopf_ispf import code
from inventorier_assets_hao_sentinel2 import ITEM_ID
from diagnostiquer_pixels_hao_l2a import SCL

EXPECTED_IDGEO = "20200"
EXPECTED_IDILE = "23"
EXPECTED_CRS = "urn:ogc:def:crs:EPSG::4687"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_manifest(path, raster):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("produit") != ITEM_ID or manifest.get("mode") != "TELECHARGEMENT_S3_AUTHENTIFIE":
        raise ValueError("Manifeste d'acquisition local inattendu")
    entry = (manifest.get("fichiers") or {}).get("SCL_20m") or {}
    if entry.get("nom_local") != raster.name or not entry.get("sha256"):
        raise ValueError("Manifeste SCL absent ou incorrect")
    if entry.get("taille_octets") != raster.stat().st_size or entry["sha256"] != sha256_file(raster):
        raise ValueError("Intégrité du SCL local non confirmée")
    return entry["sha256"]

def top_five(geopf_archive, ispf_archive):
    from shapely.geometry import shape
    from pyproj import CRS

    if sha256_file(geopf_archive) != GEO_PF_SHA or sha256_file(ispf_archive) != ISPF_GEO_SHA:
        raise ValueError("Géométries sources non conformes aux SHA des PR 86–87")
    matches = [geom for props,geom in lire_source_geopf(geopf_archive)
               if code(props["code_geogr"], 5) == EXPECTED_IDGEO
               and code(props["id_ile"]) == EXPECTED_IDILE]
    if len(matches) != 1:
        raise ValueError("Source Hao GEO PF ambiguë")
    with ZipFile(ispf_archive) as z:
        layer = json.loads(z.read("Ile.GeoJSON"))
    if layer.get("crs", {}).get("properties", {}).get("name") != EXPECTED_CRS:
        raise ValueError("CRS des contours ISPF inattendu")
    ispf = [shape(f["geometry"]) for f in layer["features"]
            if code(f["properties"]["IDIle"]) == EXPECTED_IDILE]
    if len(ispf) != 1 or not matches[0].is_valid or not ispf[0].is_valid:
        raise ValueError("Géométries originales invalides ou non uniques")
    difference = matches[0].difference(ispf[0])
    geod = CRS.from_epsg(4687).get_geod()
    pieces = [(aire(p, geod), p) for p in polygones(difference) if aire(p, geod) > 0]
    pieces.sort(key=lambda pair: (-pair[0],pair[1].bounds))
    if len(pieces) < 5:
        raise ValueError("Moins de cinq polygones dans la différence Hao")
    return pieces[:5]

def compter_scl(ds, polygon):
    """Compter les centres de pixels compris dans polygon, hors NoData.

    Seule une fenêtre de quelques pixels autour de la géométrie est lue.
    Une classe SCL ne correspond pas à une catégorie de récif ou de motu.
    """
    import numpy as np
    from rasterio.features import geometry_window, rasterize
    from rasterio.warp import transform_geom
    from rasterio.errors import WindowError
    from shapely.geometry import mapping

    if ds.crs is None or not ds.crs.is_projected:
        raise ValueError("CRS projeté du SCL absent")
    if ds.count != 1:
        raise ValueError("SCL monobande attendu")
    geom = transform_geom("EPSG:4687", ds.crs, mapping(polygon), precision=-1)
    try:
        win = geometry_window(ds, [geom])
    except WindowError:
        return {"statut": "HORS_EMPRISE_RASTER", "pixels_centre_dans_polygone": 0,
                "pixels_valides": 0, "classes": {}, "pixel_nodata": 0}
    mask = rasterize(
        [(geom, 1)], out_shape=(int(win.height),int(win.width)),
        transform=ds.window_transform(win), fill=0, dtype="uint8",
        all_touched=False,
    ).astype(bool)
    selected = int(mask.sum())
    if selected == 0:
        return {"statut":"AUCUN_CENTRE_DE_PIXEL", "pixels_centre_dans_polygone":0,
                "pixels_valides":0, "classes":{}, "pixel_nodata":0}
    pixels = ds.read(1, window=win, masked=True)
    valid = mask & (~np.ma.getmaskarray(pixels))
    values = pixels.data[valid]
    counts = Counter(int(v) for v in values)
    return {
       "statut":"COMPTE_PIXEL_SEULEMENT",
       "pixels_centre_dans_polygone":selected,
       "pixels_valides":int(values.size),
       "pixel_nodata":selected-int(values.size),
       "classes":{str(k):{
           "libelle_SCL":SCL.get(k,"CLASSE_NON_DOCUMENTEE"),
           "pixels":n,
           "part_des_pixels_valides":round(n/int(values.size),6) if values.size else None,
       } for k,n in sorted(counts.items())},
    }

def audit(geopf, ispf, scl, manifest):
    import rasterio
    digest = verify_manifest(manifest,scl)
    pieces = top_five(geopf,ispf)
    with rasterio.open(scl) as ds:
        if ds.driver not in ("JP2OpenJPEG", "JP2KAK"):
            raise ValueError("Source raster locale non JP2")
        if any(abs(abs(v)-20)>0.001 for v in ds.res):
            raise ValueError("Résolution du SCL différente de 20 m")
        output = []
        for i,(area,polygon) in enumerate(pieces,1):
            output.append({
                "rang_pr87":i,
                "surface_geodesique_m2":round(area,3),
                "sha256_wkb_geometrie":hashlib.sha256(polygon.wkb).hexdigest(),
                "statistiques_scl":compter_scl(ds,polygon),
            })
        return {
            "schema":"adlfi.lieux.polynesie.hao.scl.surfaces.v1",
            "statut":"DIAGNOSTIC_RASTER_NON_VALIDANT",
            "produit":ITEM_ID,
            "raster_crs":str(ds.crs),
            "raster_resolution_unites_crs":[float(n) for n in ds.res],
            "raster_sha256":digest,
            "geo_pf_sha256":GEO_PF_SHA,"ispf_geojson_sha256":ISPF_GEO_SHA,
            "pieces":output,
            "limites":[
                "Centre de pixel dans polygone, aucune estimation sous-pixel de surface",
                "SCL : algorithme automatisé, pas une donnée de terrain",
                "NoData ignoré des proportions par classe mais comptabilisé",
                "Les cinq rangs ne constituent pas un inventaire complet de 654 polygones",
                "Les statistiques sur image 2022 ne valident aucune limite juridique ou historique",
            ],
            "publication":{"raster":0,"geometries":0,"autorites":0,"ark":0},
        }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("geopf","ispf_geojson","scl","manifest","sortie"):
        p.add_argument("--"+key.replace("_","-"),type=Path,required=True)
    a = p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie hors docs et sans écrasement")
    result = audit(a.geopf,a.ispf_geojson,a.scl,a.manifest)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("HAO_SCL_SURFACES",json.dumps([
        {"rang":r["rang_pr87"],"comptage":r["statistiques_scl"]}
        for r in result["pieces"]],ensure_ascii=False,sort_keys=True))

if __name__ == "__main__":
    main()
