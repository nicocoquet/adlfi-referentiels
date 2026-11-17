#!/usr/bin/env python3
"""Hao : confronter trois représentations attestées, sans correction.

1. GEO PF unité géographique code_geogr=20200 (polygone SHP)
2. ISPF unité fine Comas IDComas=202 (MultiPolygon GeoJSON)
3. ISPF île Ile IDIle=23 (MultiPolygon GeoJSON)

L'enjeu est de distinguer trous de polygones, emprise globale et localisation
des pièces d'écart. Les aires sont géodésiques (RGPF/GRS1980).
Aucun objet géométrique n'est versé dans le site.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from comparer_contours_geopf_ispf import (
    XLSX_SHA, ISPF_GEO_SHA, GEO_PF_SHA, aire, lire_source_geopf
)
from qualifier_jointures_geopf_ispf import code
from qualifier_communes_associees_ispf import rows
from inspecter_nomenclature_geographique_ispf import read_xlsx

ISPF_CRS = "urn:ogc:def:crs:EPSG::4687"
HAO_GEO = "20200"
HAO_COMAS = "202"
HAO_ILE = "23"

def polygones(geom):
    if geom.is_empty:
        return
    if geom.geom_type == "Polygon":
        yield geom
    elif geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        for child in geom.geoms:
            yield from polygones(child)

def statistiques_geometriques(geom, geod):
    """Examiner les trous, sans les confondre avec la surface légale d'un lagon."""
    from shapely.geometry import Polygon
    comps=list(polygones(geom))
    if not comps: raise ValueError("Géométrie sans polygone")
    rings=sum(len(p.interiors) for p in comps)
    shells_area=sum(aire(Polygon(p.exterior),geod) for p in comps)
    holes_area=sum(aire(Polygon(ring),geod) for p in comps for ring in p.interiors)
    return {
        "composantes_polygonales":len(comps),
        "anneaux_interieurs":rings,
        "surface_anneaux_exterieurs_m2":round(shells_area,3),
        "surface_trous_m2":round(holes_area,3),
        "surface_polygonale_nette_m2":round(aire(geom,geod),3),
        "emprise_lon_lat": [round(v,7) for v in geom.bounds],
        "centroide_approximatif_lon_lat":[round(geom.centroid.x,7),round(geom.centroid.y,7)],
    }

def differences(a,b,geod):
    """Surfaces hors source et composantes majeures des différences."""
    left=a.difference(b)
    right=b.difference(a)
    def top(geom):
        return sorted((round(aire(p,geod),3) for p in polygones(geom)),reverse=True)[:5]
    aa,bb=aire(a,geod),aire(b,geod)
    return {
        "aire_a_m2":round(aa,3),
        "aire_b_m2":round(bb,3),
        "surface_commune_m2":round(aire(a.intersection(b),geod),3),
        "a_hors_b_m2":round(aire(left,geod),3),
        "b_hors_a_m2":round(aire(right,geod),3),
        "fraction_a_hors_b":round(aire(left,geod)/aa,12),
        "fraction_b_hors_a":round(aire(right,geod)/bb,12),
        "nombre_composantes_a_hors_b":sum(1 for _ in polygones(left)),
        "nombre_composantes_b_hors_a":sum(1 for _ in polygones(right)),
        "cinq_plus_grandes_pieces_a_hors_b_m2":top(left),
        "cinq_plus_grandes_pieces_b_hors_a_m2":top(right),
    }

def auditer(xlsx:Path,geojson:Path,geopf:Path):
    from pyproj import CRS
    from shapely.geometry import shape
    inputs={"xlsx":(xlsx,XLSX_SHA),"ispf_geojson":(geojson,ISPF_GEO_SHA),
            "geopf":(geopf,GEO_PF_SHA)}
    for nom,(path,digest) in inputs.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError("Empreinte de source altérée: "+nom)
    sheet={s["feuille"]:s for s in read_xlsx(xlsx)}
    lines={code(r["IDGeo"],5):r for r in rows(sheet["Geo"])}
    target=lines.get(HAO_GEO)
    if not target or code(target["IDComas"],3)!=HAO_COMAS or code(target["IDIle"])!=HAO_ILE:
        raise ValueError("Rattachement Hao ISPF inattendu")
    observed=[(properties,g) for properties,g in lire_source_geopf(geopf)
              if code(properties["code_geogr"],5)==HAO_GEO]
    if len(observed)!=1: raise ValueError("Une seule géométrie Hao GEO PF attendue")
    props,gpf=observed[0]
    for key,name,width in (("IDComas","code_com_1",3),("IDCom","code_commu",2),
                           ("IDSub","code_subdi",None),("IDIle","id_ile",None)):
        if code(target[key],width)!=code(props.get(name),width):
            raise ValueError("Discordance hiérarchique Hao : "+key)
    with ZipFile(geojson) as z:
        sources={}
        for layer,key,value in (("Comas.GeoJSON","IDComas",HAO_COMAS),
                                ("Ile.GeoJSON","IDIle",HAO_ILE)):
            data=json.loads(z.read(layer))
            if data.get("crs",{}).get("properties",{}).get("name")!=ISPF_CRS:
                raise ValueError("CRS ISPF non attesté")
            matches=[shape(f["geometry"]) for f in data["features"]
                     if code(f["properties"][key],3 if key=="IDComas" else None)==value]
            if len(matches)!=1: raise ValueError("Géométrie non unique dans "+layer)
            sources[layer]=matches[0]
    geometries={"GEO_PF_IDGeo_20200":gpf,"ISPF_Comas_202":sources["Comas.GeoJSON"],
                "ISPF_Ile_23":sources["Ile.GeoJSON"]}
    if any(g.is_empty or not g.is_valid for g in geometries.values()):
        raise ValueError("L'une des géométries de Hao est invalide")
    geod=CRS.from_epsg(4687).get_geod()
    return {
        "schema":"adlfi.lieux.polynesie.hao.geometries.audit.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "sources_sha256":{key:val[1] for key,val in inputs.items()},
        "identifiants":{"IDGeo":HAO_GEO,"IDComas":HAO_COMAS,"IDIle":HAO_ILE},
        "metadonnees_geopf":{
            "nom_geographique":str(props.get("nom_geogra")),
            "mode_acquisition":str(props.get("mode_acq")),
            "organisme_acquisition":str(props.get("org_acq")),
        },
        "statistiques":{key:statistiques_geometriques(g,geod)
                        for key,g in geometries.items()},
        "comparaisons":{
            "GEO_PF_20200__ISPF_Comas_202":differences(gpf,sources["Comas.GeoJSON"],geod),
            "GEO_PF_20200__ISPF_Ile_23":differences(gpf,sources["Ile.GeoJSON"],geod),
            "ISPF_Ile_23__ISPF_Comas_202":differences(sources["Ile.GeoJSON"],sources["Comas.GeoJSON"],geod),
        },
        "limites":[
            "Le nombre de trous et leur surface ne prouve pas un tracé légal du lagon.",
            "Le centroïde en coordonnées géographiques est indicatif, non métrique.",
            "La différence d'emprise peut être insulaire, temporelle ou géométrique.",
            "La généalogie des deux producteurs reste non démontrée.",
        ],
        "publication":{"nouveaux_contours":0,"ark":0,"autorites":0},
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xlsx",required=True,type=Path)
    p.add_argument("--ispf-geojson",required=True,type=Path)
    p.add_argument("--geopf",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Rapport hors docs et sans écrasement")
    r=auditer(a.xlsx,a.ispf_geojson,a.geopf)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("HAO_GEOMETRIES",json.dumps({
        "statistiques":r["statistiques"],"comparaisons":r["comparaisons"],
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
