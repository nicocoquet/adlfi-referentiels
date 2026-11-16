#!/usr/bin/env python3
"""Localiser les écarts de dessin Guyane GEOFLA 2015 / Etalab 2026 à 100m et 50m.

Rapport de métriques uniquement : centres représentatifs et enveloppes
approximatives de composantes de différences, sans exporter de polygones.
Ne jamais en déduire littoral, hydrographie ou changement administratif.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

from auditer_geofla_guyane_2015 import (
    ARCHIVE_NAME, SOURCE_TIERS_SHA, SHA_NATIONAL, lire_geojson, sha256,
)

SCHEMA="adlfi.lieux.guyane.ecarts-localises-geofla15-etalab26.v1"
SHA_50M="6db43cd98a7211516da64e91761100504ba3feeddc986ebe0d50f84df624cd38"
FOCUS={"97301":"Régina","97312":"Sinnamary","97303":"Iracoubo"}
CODES={"97301","97302","97303","97304","97305","97306","97307",
       "97308","97309","97310","97311","97312","97313","97314",
       "97352","97353","97356","97357","97358","97360","97361","97362"}


def composantes(geometry):
    """Lister seulement les composantes surfaciques, sans fabriquer de formes."""
    if geometry.is_empty:
        return []
    if geometry.geom_type=="Polygon":
        return [geometry]
    if geometry.geom_type in ("MultiPolygon","GeometryCollection"):
        return [p for g in geometry.geoms for p in composantes(g)]
    return []


def localiser(geometry, vers_wgs84, seuil_km2:float=0.5,
             max_composantes:int=12)->dict:
    """Localisation descriptive : points internes, enveloppes, aires en EPSG:6933."""
    from shapely.ops import transform

    parts=sorted(composantes(geometry),key=lambda g:-g.area)
    total=sum(g.area for g in parts)
    if abs(total-geometry.area)>1:
        raise ValueError("La surface des composantes ne ferme pas")
    records=[]
    for g in parts:
        if g.area/1e6<seuil_km2 or len(records)>=max_composantes:
            break
        point=transform(vers_wgs84.transform,g.representative_point())
        envelope=transform(vers_wgs84.transform,g.envelope)
        records.append({
            "aire_km2":round(g.area/1e6,6),
            "longitude_point_interieur":round(point.x,6),
            "latitude_point_interieur":round(point.y,6),
            "enveloppe_wgs84_lonlat":[round(x,6) for x in envelope.bounds],
        })
    return {
        "surface_totale_km2":round(total/1e6,6),
        "composantes_detectees":len(parts),
        "composantes_au_dessus_du_seuil":sum(g.area/1e6>=seuil_km2 for g in parts),
        "composantes_exportees":len(records),
        "surface_composantes_exportees_km2":round(sum(x["aire_km2"] for x in records),6),
        "seuil_km2":seuil_km2,
        "composantes":[*records],
    }


def metriques(a,b)->dict:
    if a.is_empty or b.is_empty or not a.is_valid or not b.is_valid:
        raise ValueError("Géométries non exploitables")
    km=lambda x:round(x/1e6,6)
    inter=a.intersection(b).area
    union=a.union(b).area
    return {
        "symdiff_km2":km(a.symmetric_difference(b).area),
        "a_hors_b_km2":km(a.difference(b).area),
        "b_hors_a_km2":km(b.difference(a).area),
        "jaccard_pct":round(inter/union*100,6) if union else None,
    }


def charger_communes_2015(dossier:Path):
    import shapefile
    from pyproj import CRS,Transformer
    from shapely.geometry import shape
    from shapely.ops import transform

    shapes=sorted(p for p in dossier.rglob("*") if p.is_file()
                  and p.name.upper()=="COMMUNE.SHP")
    if len(shapes)!=1:raise ValueError("Une seule couche COMMUNE.shp attendue")
    shp=shapes[0]
    prj=shp.with_suffix(".prj")
    if not prj.exists():raise ValueError("Fichier PRJ non fourni")
    crs=CRS.from_wkt(prj.read_text(encoding="utf8",errors="replace"))
    if not crs.is_projected:raise ValueError("Source 2015 non projetée")
    to6933=Transformer.from_crs(crs,"EPSG:6933",always_xy=True)
    source={}
    with shapefile.Reader(str(shp),encoding="latin-1") as r:
        names=[x[0] for x in r.fields[1:]]
        for record in r.iterShapeRecords():
            info=dict(zip(names,list(record.record)))
            code=str(info.get("INSEE_COM","")).strip()
            if code not in CODES or code in source:
                raise ValueError("Code GEOFLA non conforme / répété : "+code)
            geom=transform(to6933.transform,shape(record.shape.__geo_interface__))
            if not geom.is_valid or geom.is_empty:
                raise ValueError("Géométrie 2015 invalide : "+code)
            source[code]=geom
    if set(source)!=CODES:
        raise ValueError("22 codes GEOFLA 2015 incomplets")
    return source


def charger_2026(path:Path)->dict:
    data=lire_geojson(path,CODES)
    if set(data)!=CODES or any(len(xs)!=1 for xs in data.values()):
        raise ValueError("Communes 2026 absentes ou répétées")
    result={code:xs[0] for code,xs in data.items()}
    if any(not g.is_valid or g.is_empty for g in result.values()):
        raise ValueError("Une géométrie 2026 est invalide")
    return result


def evaluer(source:dict,coarse:dict,fine:dict,vers_wgs84)->dict:
    from shapely.ops import unary_union
    if set(source)!=CODES or set(coarse)!=CODES or set(fine)!=CODES:
        raise ValueError("22 codes obligatoires et identiques entre les trois éditions")
    all_2015=unary_union(list(source.values()))
    all_100=unary_union(list(coarse.values()))
    all_50=unary_union(list(fine.values()))
    for label,shapes,full in (("GEOFLA_2015",source,all_2015),
                               ("Etalab_2026_100m",coarse,all_100),
                               ("Etalab_2026_50m",fine,all_50)):
        if not full.is_valid or full.is_empty:
            raise ValueError("Emprise totale invalide : "+label)
        sum_area=sum(g.area for g in shapes.values())
        if abs(sum_area-full.area)>100:
            raise ValueError("Communes du même jeu se recouvrent : "+label)

    global_stats={
        "2015_vers_2026_100m":metriques(all_2015,all_100),
        "2015_vers_2026_50m":metriques(all_2015,all_50),
        "2026_100m_vers_2026_50m":metriques(all_100,all_50),
        "aires_emprises_km2":{
            "geofla_2015":round(all_2015.area/1e6,6),
            "etalab_2026_100m":round(all_100.area/1e6,6),
            "etalab_2026_50m":round(all_50.area/1e6,6),
        },
    }
    if abs(global_stats["2015_vers_2026_100m"]["symdiff_km2"]-733.434981)>0.01:
        raise ValueError("Écart 2015/2026 100 m incompatible avec la recette publiée")

    local={}
    for code,name in FOCUS.items():
        a,b,c=source[code],coarse[code],fine[code]
        local[code]={
            "nom":name,
            "differences_cartographiques_2015_2026_par_commune":{
                "reference_100m":metriques(a,b),
                "reference_50m":metriques(a,c),
            },
            "difference_50m_100m_meme_millesime":metriques(b,c),
            "exterieur_guyane_100m":{
                "edition_2015_hors_emprise_2026":localiser(a.difference(all_100),vers_wgs84),
                "edition_2026_hors_emprise_2015":localiser(b.difference(all_2015),vers_wgs84),
            },
            "exterieur_guyane_50m":{
                "edition_2015_hors_emprise_2026":localiser(a.difference(all_50),vers_wgs84),
                "edition_2026_hors_emprise_2015":localiser(c.difference(all_2015),vers_wgs84),
            },
        }
    return {
        "comparaisons_globales":global_stats,
        "trois_communes_prioritaires":local,
        "recommandations_methodologiques":[
            "Aucune provenance canonique du fichier GEOFLA 2015 n'est authentifiée par ce calcul.",
            "50m et 100m sont deux généralisations du même millésime 2026, pas deux situations administratives.",
            "Les points sont des points intérieurs à des différences de dessins, jamais des lieux de mutation territoriale démontrée.",
            "Les coordonnées des enveloppes sont approximatives et ne constituent pas des géométries de limites.",
            "Une localisation près du littoral ou d'un fleuve nécessite une référence hydrographique ou de trait de côte indépendante.",
            "Aucun résultat ne valide de contours historiques ni de succession de communes.",
        ],
        "aucun_contour_exporte":True,
        "aucun_ark_pactols_cree":True,
    }


def produire(dossier:Path,archive:Path,geo100:Path,geo50:Path,sortie:Path)->dict:
    from pyproj import Transformer

    if archive.name!=ARCHIVE_NAME or sha256(archive)!=SOURCE_TIERS_SHA:
        raise ValueError("Archive GEOFLA 2015 non conforme à la copie épinglée")
    if sha256(geo100)!=SHA_NATIONAL:
        raise ValueError("Source 2026 100m non épinglée")
    if sha256(geo50)!=SHA_50M:
        raise ValueError("Source 2026 50m non épinglée")
    if "docs" in sortie.resolve().parts or sortie.exists():
        raise ValueError("Sortie vers site public ou écrasement interdit")
    a=charger_communes_2015(dossier)
    b=charger_2026(geo100)
    c=charger_2026(geo50)
    result=evaluer(a,b,c,Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True))
    result.update({
        "schema":SCHEMA,"statut":"RECETTE_CARTOGRAPHIQUE_NON_PUBLIEE",
        "provenance":{
            "2015_miroir_SHA256":sha256(archive),"original_IGN_authentifie":False,
            "2026_100m_SHA256":sha256(geo100),"2026_50m_SHA256":sha256(geo50),
            "edition_etalab_2026":"2026-05-04",
            "projection_mesures":"EPSG:6933, aires calculées sur géométries projetées",
            "coordonnees_points_et_enveloppes":"EPSG:4326",
        }
    })
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                      encoding="utf8")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("dossier","archive","geo100","geo50","sortie"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    r=produire(**vars(a))
    print(json.dumps({
        "provenance":r["provenance"],
        "comparaisons_globales":r["comparaisons_globales"],
        "trois_communes_prioritaires":{
            code:{
                "nom":v["nom"],
                "differences_cartographiques_2015_2026_par_commune":
                  v["differences_cartographiques_2015_2026_par_commune"],
                "difference_50m_100m_meme_millesime":
                  v["difference_50m_100m_meme_millesime"],
                "principaux_ecarts_externes_2015_hors_2026":{
                  year:
                    payload["edition_2015_hors_emprise_2026"]["composantes"][:6]
                  for year,payload in (
                    ("100m",v["exterieur_guyane_100m"]),
                    ("50m",v["exterieur_guyane_50m"])
                  )
                },
            } for code,v in r["trois_communes_prioritaires"].items()
        }
    },ensure_ascii=False,sort_keys=True,indent=2))
