#!/usr/bin/env python3
"""Audit et extraction des géométries 2015/2016 du pilote BFC (source millésimée ODS).

Preuves indépendantes : les codes/noms COG ont été vérifiés dans l'audit Insee.
L'export ODS est une RÉUTILISATION multi-sources (IGN GEOFLA/ADMIN EXPRESS),
pas une archive IGN primaire. Chaque géométrie conserve sa provenance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path
from collections import Counter

API="https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/georef-france-region-millesime/records"
DATASET="https://public.opendatasoft.com/explore/dataset/georef-france-region-millesime/"
CONTROLES={
    ("2015","26"): "Bourgogne",
    ("2015","43"): "Franche-Comté",
    ("2016","27"): "Bourgogne-Franche-Comté",
}
# Les noms et codes annuels proviennent du COG 2015/2016 (source indépendante).
# ODS (réutilisation) sert uniquement à restituer le contour au millésime indiqué.

def telecharger(timeout=60):
    records=[]
    offset=0; total=None; h=hashlib.sha256()
    while total is None or offset<total:
        url=API+"?"+urllib.parse.urlencode({"limit":100,"offset":offset})
        req=urllib.request.Request(url,headers={
            "Accept":"application/json",
            "User-Agent":"AdlFI-Lieux-COG-historique-recherche/1.0",
        })
        with urllib.request.urlopen(req,timeout=timeout) as r:
            if r.status != 200:raise ValueError("Réponse ODS "+str(r.status))
            data=r.read(25_000_000)
        h.update(data)
        body=json.loads(data)
        this_total=body.get("total_count")
        batch=body.get("results")
        if not isinstance(this_total,int) or not isinstance(batch,list) or not batch:
            raise ValueError("Pagination ODS non reconnue")
        if total is not None and total!=this_total:
            raise ValueError("Le total change pendant la pagination")
        total=this_total
        records.extend(batch); offset+=len(batch)
        if offset>2000:raise ValueError("Pagination ODS inattendue")
    if len(records)!=total:raise ValueError("Pagination incomplète")
    return records,h.hexdigest(),total

def val_reg(r,code):
    v=r.get("reg_code")
    return isinstance(v,list) and code in v

def ctrl_geom(g):
    if not isinstance(g,dict) or g.get("type")!="Feature":raise ValueError("Géométrie ODS non GeoJSON Feature")
    geo=g.get("geometry")
    if not isinstance(geo,dict) or geo.get("type") not in ("Polygon","MultiPolygon"):
        raise ValueError("Pas de géométrie surfacique GeoJSON")
    coords=geo.get("coordinates")
    if not coords:raise ValueError("Géométrie vide")
    n=0
    def walk(v):
        nonlocal n
        if isinstance(v,list) and len(v)>=2 and all(isinstance(x,(int,float)) for x in v[:2]):
            x,y=v[:2]
            if not (-180<=x<=180 and -90<=y<=90):raise ValueError("Coordonnées hors WGS84")
            n+=1
        elif isinstance(v,list):
            for x in v:walk(x)
    walk(coords)
    if n<20:raise ValueError("Géométrie trop grossière")
    return n

def analyser(records,sha,total):
    by_key={}
    for (year,code),name in CONTROLES.items():
        selected=[r for r in records if str(r.get("year"))==year and val_reg(r,code)]
        if len(selected)!=1:
            raise ValueError("Il faut 1 entrée géométrique "+year+" "+code+" ; trouvé "+str(len(selected))+
                " ; détails="+json.dumps([
                    {k:v for k,v in r.items() if k in ("year","reg_code","reg_name","reg_type","reg_status","reg_iso3","reg_current_code")}
                    | {"geo_sha256":hashlib.sha256(json.dumps(r.get("geo_shape"),sort_keys=True).encode()).hexdigest()}
                    for r in selected
                ],ensure_ascii=False))
        row=selected[0]
        labels=row.get("reg_name")
        if not isinstance(labels,list) or len(labels)!=1 or labels[0]!=name:
            raise ValueError("Nom ODS différent du COG "+year+" "+code+": "+repr(labels))
        geometry=row.get("geo_shape")
        n=ctrl_geom(geometry)
        by_key[(year,code)]={"record":row,"vertices":n}
    # Ne jamais mettre la couche 2015 sous le libellé 2016.
    geo={}
    for year in ("2015","2016"):
        feats=[]
        for (y,code),obj in sorted(by_key.items()):
            if y!=year:continue
            row=obj["record"]
            feats.append({
                "type":"Feature",
                "geometry":row["geo_shape"]["geometry"],
                "properties":{
                    "code_region":code,"nom":CONTROLES[(year,code)],
                    "millesime_geometrie":int(year),
                    "date_reference":year+"-01-01",
                    "source_fournisseur":"Opendatasoft",
                    "source_producteur":"IGN GEOFLA / ADMIN EXPRESS (données réutilisées, non isolées)",
                    "statut_geometrie":"geometrie_millesimee_reutilisation_a_qualifier",
                    "pactols_valide":False,
                }
            })
        geo[year]={
            "type":"FeatureCollection",
            "provenance":{
                "jeu":DATASET,"annee":int(year),
                "statut":"geometries_millesimees_reutilisation_non_source_primaire",
                "absence_de_retroprojection":True,
            },
            "features":feats,
        }
    stat={
        "schema":"adlfi.lieux.bfc.geometries_millesimees.recette.v1",
        "source_ODS":DATASET,
        "nb_records_total_ODS":total,
        "pagination_sha256_sur_reponses":sha,
        "cibles_par_annee":{y:[f["properties"]["code_region"] for f in geo[y]["features"]] for y in geo},
        "vertices":{f"{y}:{code}":obj["vertices"] for (y,code),obj in sorted(by_key.items())},
        "statut":"RECETTE_SOURCE_DERIVEE_A_QUALIFIER_NON_PUBLIEE",
        "millesimes":[2015,2016],
        "nombre_nouveaux_alignements_pactols":0,
        "nombre_geometries_historiques_inferrees":0,
        "avertissement":"La date du jeu ODS ne prouve pas à elle seule la précision des sources géométriques ; comparaison nécessaire avec GEOFLA IGN original.",
    }
    return geo,stat

def publier(geo,rapport,dest):
    dest=Path(dest)
    if "docs" in dest.resolve().parts:
        raise ValueError("Publication Pages interdite pour la recette")
    dest.mkdir(parents=True,exist_ok=True)
    for y,g in geo.items():
        (dest/f"regions-{y}-bfc.geojson").write_text(
            json.dumps(g,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf8")
    (dest/"rapport-geometries-bfc.json").write_text(
        json.dumps(rapport,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sortie",type=Path,required=True)
    a=p.parse_args()
    records,sha,total=telecharger()
    geo,rapport=analyser(records,sha,total)
    publier(geo,rapport,a.sortie)
    print(json.dumps(rapport,ensure_ascii=False,indent=2))
