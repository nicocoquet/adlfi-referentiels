#!/usr/bin/env python3
"""Comparer les limites BFC des départements IGN GEOFLA 2015 et 2016.

Région 2015 = union des huit départements (deux groupes de quatre) de l'édition 2015.
Région 2016 = union des huit départements (code régional 27) de l'édition 2016.
Les mêmes départements sont comparés séparément ; les différences numériques
mesurent les représentations, pas une modification juridique des limites.

GEOFLA est une source géographique départementale ; les régions créées ici
sont des dérivations déclarées, non des couches régionales originales IGN.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

BFC_2015={"26":{"21","58","71","89"},"43":{"25","39","70","90"}}
BFC_2016={"27":set().union(*BFC_2015.values())}
LIBELLES={"26":"Bourgogne","43":"Franche-Comté","27":"Bourgogne-Franche-Comté"}
SHA_2015="7831ad942f3c0646d7b9ebf9ba480dcf746d6f69d46834b38e36fa6681c1060e"
IGN_2015="https://data.geopf.fr/telechargement/download/GEOFLA/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04.7z"

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def charger_departements(path,annee):
    import geopandas as gpd
    x=gpd.read_file(path)
    if len(x)!=96 or x.crs is None or x.crs.to_epsg()!=2154:
        raise ValueError(f"GEOFLA {annee} : 96 départements en EPSG:2154 attendus")
    if not {"CODE_DEPT","CODE_REG","geometry"}.issubset(x.columns):
        raise ValueError("GEOFLA : attributs manquants")
    if x["CODE_DEPT"].duplicated().any() or not x.geometry.is_valid.all():
        raise ValueError("Départements non uniques ou géométries invalides")
    d={}
    for _,row in x.iterrows():
        d[str(row["CODE_DEPT"])]=(str(row["CODE_REG"]),row.geometry)
    return d

def verifier_hierarchie(source, attendu, annee):
    for reg,deps in attendu.items():
        for code in deps:
            if code not in source:
                raise ValueError(f"Département {code} absent du GEOFLA {annee}")
            if source[code][0] != reg:
                raise ValueError(f"Rattachement GEOFLA {annee} incorrect {code} -> {source[code][0]} ≠ {reg}")

def mesures(a,b):
    if not a.is_valid or not b.is_valid or a.is_empty or b.is_empty:
        raise ValueError("Géométries non valides ou vides")
    u=a.union(b)
    i=a.intersection(b)
    if not u.area:raise ValueError("Pas de zone commune")
    return {
        "aire_2015_km2":round(a.area/1e6,4),
        "aire_2016_km2":round(b.area/1e6,4),
        "difference_symetrique_km2":round(a.symmetric_difference(b).area/1e6,4),
        "intersection_sur_union_pct":round(100*i.area/u.area,6),
        "hausdorff_km":round(a.hausdorff_distance(b)/1000,5),
    }

def analyser(shp2015,shp2016,archive2015,archive2016,url2016):
    from shapely.ops import unary_union,transform
    from shapely.geometry import mapping
    from pyproj import Transformer
    if sha256(archive2015)!=SHA_2015:
        raise ValueError("Archive GEOFLA 2015 ne correspond pas à l'original contrôlé")
    if not (url2016.startswith("https://data.geopf.fr/telechargement/download/GEOFLA/") and
            "DEPARTEMENT" in url2016.upper() and "2016" in url2016 and url2016.endswith(".7z")):
        raise ValueError("Archive 2016 doit venir du catalogue officiel GEOFLA DEPARTEMENT")
    sha2016=sha256(archive2016)
    old=charger_departements(shp2015,"2015")
    new=charger_departements(shp2016,"2016")
    verifier_hierarchie(old,BFC_2015,"2015")
    verifier_hierarchie(new,BFC_2016,"2016")
    from shapely.ops import unary_union
    groups2015={reg:unary_union([old[d][1] for d in sorted(deps)]) for reg,deps in BFC_2015.items()}
    boundary2015=unary_union(list(groups2015.values()))
    boundary2016=unary_union([new[d][1] for d in sorted(BFC_2016["27"])])
    overall=mesures(boundary2015,boundary2016)
    by_dept=[]
    for dep in sorted(BFC_2016["27"]):
        m=mesures(old[dep][1],new[dep][1])
        by_dept.append({"code_departement":dep,"reg_2015":old[dep][0],
                        "reg_2016":new[dep][0],**m})
    to_wgs=Transformer.from_crs(2154,4326,always_xy=True).transform
    feat15=[{"type":"Feature",
             "geometry":mapping(transform(to_wgs,groups2015[reg])),
             "properties":{"code_region":reg,"nom":LIBELLES[reg],
                           "millesime_geometrie":2015,
                           "date_edition_archive":"2015-03-04",
                           "nature":"union_de_departements_GEOFLA_2015",
                           "departements_sources":sorted(deps),"pactols_valide":False}}
            for reg,deps in BFC_2015.items()]
    feat16=[{"type":"Feature",
             "geometry":mapping(transform(to_wgs,boundary2016)),
             "properties":{"code_region":"27","nom":LIBELLES["27"],
                           "millesime_geometrie":2016,
                           "date_edition_archive":url2016.split("/")[-2].rsplit("_",1)[-1],
                           "nature":"union_de_departements_GEOFLA_2016",
                           "departements_sources":sorted(BFC_2016["27"]),"pactols_valide":False}}]
    sources={
        "2015":{"annee":2015,"source_producteur":"IGN",
                "archive_url":IGN_2015,"archive_sha256":SHA_2015,
                "methode":"union des départements GEOFLA même édition",
                "contour_regional_natif":False},
        "2016":{"annee":2016,"source_producteur":"IGN",
                "archive_url":url2016,"archive_sha256":sha2016,
                "methode":"union des départements GEOFLA même édition",
                "contour_regional_natif":False},
    }
    collections={}
    for year,features in (("2015",feat15),("2016",feat16)):
        collections[year]={"type":"FeatureCollection",
            "provenance":{**sources[year],"absence_de_retroprojection":True},
            "features":features}
    rapport={
        "schema":"adlfi.lieux.bfc.comparaison_geofla_2015_2016.v1",
        "statut":"RECETTE_IGN_2_EDITIONS_SOURCE_PRIMAIRE_NON_PUBLIEE",
        "limites":["Différence de géométrie ne signifie pas changement juridique de frontières.",
                   "Le 4 mars 2015 et l'édition 2016 ne sont pas les 1er janvier de ces années.",
                   "Les régions sont des unions de départements, pas des couches natives de GEOFLA."],
        "nombre_departements_metropole_par_annee":96,
        "departements_bfc":sorted(BFC_2016["27"]),
        "groupes_2015":{k:sorted(v) for k,v in BFC_2015.items()},
        "groupe_2016":{k:sorted(v) for k,v in BFC_2016.items()},
        "sources":sources,
        "comparaison_totale":overall,
        "comparaison_par_departement":by_dept,
        "nombre_de_nouveaux_alignements_pactols":0,
        "nombre_de_contours_inferes_des_geometries_2026":0,
    }
    return collections,rapport

def exporter(collections,rapport,dossier):
    dest=Path(dossier)
    if "docs" in dest.resolve().parts:
        raise ValueError("Interdiction de publier les données de recette dans docs/")
    dest.mkdir(parents=True,exist_ok=True)
    for year,geo in collections.items():
        (dest/f"regions-bfc-{year}-IGN-geofla.geojson").write_text(
            json.dumps(geo,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
    r=dest/"rapport-comparaison-GEOFLA-2015-2016.json"
    r.write_text(json.dumps(rapport,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    with (dest/"comparaison-departements-BFC-GEOFLA-2015-2016.csv").open(
        "w",encoding="utf-8-sig",newline="") as f:
        fields=list(rapport["comparaison_par_departement"][0])
        writer=csv.DictWriter(f,fieldnames=fields,delimiter=";")
        writer.writeheader();writer.writerows(rapport["comparaison_par_departement"])

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ("shp2015","shp2016","archive2015","archive2016","sortie"):
        ap.add_argument("--"+key,type=Path,required=True)
    ap.add_argument("--url2016",required=True)
    a=vars(ap.parse_args())
    target=a.pop("sortie")
    data,report=analyser(**a)
    exporter(data,report,target)
    print(json.dumps(report,ensure_ascii=False,indent=2))
