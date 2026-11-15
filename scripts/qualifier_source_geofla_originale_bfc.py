#!/usr/bin/env python3
"""Qualifie les départements GEOFLA IGN 2015 et leur regroupement régional BFC.

Entrées : 4 fichiers du thème DEPARTEMENT, extraits depuis le PAQUET OFFICIEL
GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04 et GeoJSON ODS 2015.
L'union des 4 départements par région est une DÉRIVATION EXPLICITE,
pas un contour régional émis directement par l'IGN ni une rétroprojection de 2026.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import geopandas as gpd
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
from pyproj import Transformer
from shapely.ops import transform

DEP={
    "26":("Bourgogne",{"21","58","71","89"}),
    "43":("Franche-Comté",{"25","39","70","90"}),
}
SHA_ARCHIVE="7831ad942f3c0646d7b9ebf9ba480dcf746d6f69d46834b38e36fa6681c1060e"
URL_IGN="https://data.geopf.fr/telechargement/download/GEOFLA/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04.7z"
URL_ODS="https://public.opendatasoft.com/explore/dataset/georef-france-region-millesime/"
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def analyser(source_shp,source_ods, source_archive=None):
    shp=Path(source_shp)
    if source_archive is not None and digest(source_archive)!=SHA_ARCHIVE:
        raise ValueError("Archive GEOFLA originale non reconnue : SHA-256 différent")
    gdf=gpd.read_file(shp)
    if len(gdf)!=96:raise ValueError("Nombre de départements métropolitains GEOFLA inattendu")
    if gdf.crs is None or gdf.crs.to_epsg()!=2154:raise ValueError("Projection des départements : Lambert-93 requis")
    cols={"CODE_DEPT","CODE_REG","NOM_REG","NOM_DEPT","geometry"}
    if not cols<=set(gdf.columns):raise ValueError("Colonnes GEOFLA manquantes")
    if gdf["CODE_DEPT"].duplicated().any():raise ValueError("Codes de départements dupliqués")
    if not gdf.geometry.is_valid.all():raise ValueError("Géométries départementales invalides")
    ds=json.loads(Path(source_ods).read_text(encoding="utf8"))
    if ds.get("provenance",{}).get("annee")!=2015:raise ValueError("ODS 2015 attendu")
    if len(ds.get("features",[]))!=2:raise ValueError("Deux régions anciennes ODS attendues")
    wgs84=Transformer.from_crs(2154,4326,always_xy=True).transform
    l93=Transformer.from_crs(4326,2154,always_xy=True).transform
    feats=[];rows=[]
    for reg,(name,deps) in DEP.items():
        d=gdf.loc[gdf["CODE_DEPT"].isin(deps)]
        if len(d)!=4 or set(d["CODE_DEPT"])!=deps or set(d["CODE_REG"])!={reg}:
            raise ValueError("Appartenance régionale GEOFLA 2015 incompatible "+reg)
        ign=unary_union(list(d.geometry))
        if not ign.is_valid or ign.is_empty:
            raise ValueError("Union de départements géométriquement incorrecte "+reg)
        o=[f for f in ds["features"] if f["properties"].get("code_region")==reg]
        if len(o)!=1:raise ValueError("Région ODS manquante "+reg)
        ods=transform(l93,shape(o[0]["geometry"]))
        if not ods.is_valid:raise ValueError("Contour ODS invalide "+reg)
        intersection=ign.intersection(ods);combined=ign.union(ods)
        diff=ign.symmetric_difference(ods)
        rows.append({
            "code_region":reg,"region":name,
            "codes_departements":",".join(sorted(deps)),
            "surface_GE0FLA_origine_2015_km2":round(ign.area/1e6,4),
            "surface_ODS_2015_km2":round(ods.area/1e6,4),
            "difference_symetrique_km2":round(diff.area/1e6,4),
            "recouvrement_iou_pct":round(100*intersection.area/combined.area,6),
            "hausdorff_km":round(ign.hausdorff_distance(ods)/1e3,5),
            "type_comparaison":"ecart_de_representations_non_changement_de_frontiere",
        })
        feats.append({
            "type":"Feature",
            "geometry":mapping(transform(wgs84,ign)),
            "properties":{
                "code_region":reg,"nom":name,"millesime_geometrie":2015,
                "date_edition_archive":"2015-03-04",
                "nature":"contour_regional_reconstruit_par_union_de_departements_historiques",
                "source_geometrique":"IGN GEOFLA DEPARTEMENT 2015-03-04",
                "codes_departements":sorted(deps),
                "pactols_valide":False,
            }
        })
    feature_collection={
        "type":"FeatureCollection",
        "provenance":{
            "producteur":"IGN",
            "source":URL_IGN,
            "statut":"reconstitution_par_union_de_4_departements_geofla_originaux_par_region",
            "annee":2015,
            "edition_package":"2015-03-04",
            "date_du_COG_compare":"2015-01-01",
            "difference_entre_date_COG_et_edition_geometrie":True,
            "absence_de_retroprojection":True,
            "aucune_identite_Pactols_deduite":True,
        },
        "features":feats,
    }
    report={
        "schema":"adlfi.lieux.bfc.qualification_ign_geofla2015.v1",
        "statut":"RECETTE_GEO_DEPARTEMENTS_2015_SOURCE_IGN_ET_REGROUPEMENT_EXPLICITE",
        "source_geometries_ign":URL_IGN,
        "sha256_archive_ign":SHA_ARCHIVE if source_archive is not None else None,
        "SHA256_source_shp":digest(source_shp),
        "source_comparaison_ods":URL_ODS,
        "sha256_comparaison_ods":digest(source_ods),
        "departements_metropole_officiels":len(gdf),
        "departements_BFC_controles":8,
        "regions_BFC_2015_issues_de_departements_du_meme_millesime":2,
        "nombre_contours_regionaux_directement_produits_par_ign":0,
        "nombre_contours_regionaux_derived_de_departements_2015":2,
        "geometries_retroprojetees_depuis_2026":0,
        "alignements_Pactols_crees":0,
        "comparaisons":rows,
        "limites":[
            "GEOFLA DÉPARTEMENT ne fournit pas un niveau Région autonome.",
            "Les deux contours BFC sont les unions calculées de départements fournis dans le même paquet 2015.",
            "Les données GEOFLA portent une édition du 4 mars 2015, distincte du COG au 1er janvier 2015.",
            "La comparaison ODS quantifie des écarts de représentations, pas des changements juridiques de limites.",
            "Il faut contrôler séparément l'état régional au 1er janvier 2016.",
        ],
    }
    return feature_collection,report

def exporter(geo,report,out):
    out=Path(out)
    if "docs" in out.resolve().parts:raise ValueError("Refus d'écrire dans docs/")
    out.mkdir(parents=True,exist_ok=True)
    (out/"bfc-regions-reconstituees-departements-IGN-2015.geojson").write_text(
        json.dumps(geo,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
    (out/"rapport-comparaison-GEOFLA-ODS-2015.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    with (out/"comparaison-GEOFLA-ODS-BFC-2015.csv").open("w",encoding="utf-8-sig",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=list(report["comparaisons"][0]),delimiter=";")
        wr.writeheader();wr.writerows(report["comparaisons"])

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shp",type=Path,required=True)
    p.add_argument("--ods2015",type=Path,required=True)
    p.add_argument("--archive",type=Path)
    p.add_argument("--sortie",type=Path,required=True)
    a=p.parse_args()
    geo,report=analyser(a.shp,a.ods2015,a.archive)
    exporter(geo,report,a.sortie)
    print(json.dumps(report,ensure_ascii=False,indent=2))
