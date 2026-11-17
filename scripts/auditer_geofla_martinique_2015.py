#!/usr/bin/env python3
"""Martinique : audit non validant GEOFLA 2015 contre Etalab 2026 100 m / 50 m.

La validité juridique, la date des limites et l'authenticité IGN de la copie
tiers ne sont PAS déduites des comparaisons. Aucun polygone n'est exporté.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path


from auditer_geofla_guyane_2015 import lire_geojson

SCHEMA="adlfi.lieux.martinique.audit.geofla2015-etalab2026.v1"
ARCHIVE_NAME="GEOFLA_2-1_COMMUNE_SHP_UTM20W84MART_D972_2015-12-01.rar"
# Empreinte à fixer à partir de la première acquisition contrôlée.
SHA_2015=""
SHA_2026_100="4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
SHA_2026_50="6db43cd98a7211516da64e91761100504ba3feeddc986ebe0d50f84df624cd38"
CODES={f"972{n:02d}" for n in range(1,35)}
SOURCE_URL=("https://raw.githubusercontent.com/justinelliotmeyers/"
 "official_france_administrative_boundary_shapefile/master/"+ARCHIVE_NAME)
KM=lambda area:round(area/1e6,6)


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def code_insee(attributs:dict)->tuple[str|None,str|None]:
    """Lire uniquement les codes attestés dans des champs attributaires."""
    fields={str(k).upper():str(v).strip() for k,v in attributs.items()}
    choices=[(fields[field],field) for field in (
        "INSEE_COM","CODE_INSEE","CODE_COM","INSEE","INSEE_COM1",
        "INSEE_COMM","CODEINSEE","COD_INSEE","INSEE_C"
    ) if field in fields and re.fullmatch(r"972\d\d",fields[field])]
    distinct={code for code,_ in choices}
    if len(distinct)==1:
        code=next(iter(distinct))
        return code,choices[0][1]
    return None,None


def loader_2015(dossier:Path)->tuple[dict,dict]:
    import shapefile
    from pyproj import CRS, Transformer
    from shapely.geometry import shape
    from shapely.ops import transform
    shps=sorted(p for p in dossier.rglob("*") if p.is_file()
                and p.suffix.lower()==".shp")
    communes=[p for p in shps if p.stem.upper()=="COMMUNE"]
    if len(communes)!=1:
        raise ValueError("Une unique couche COMMUNE.shp est attendue")
    shp=communes[0]
    prj=shp.with_suffix(".prj")
    if not prj.is_file():
        raise ValueError("Projection source .prj manquante")
    crs=CRS.from_wkt(prj.read_text(encoding="utf-8",errors="replace"))
    if not crs.is_projected:
        raise ValueError("GEOFLA 2015 sans CRS projeté reconnu")
    transformer=Transformer.from_crs(crs,"EPSG:6933",always_xy=True)
    points=Transformer.from_crs(crs,"EPSG:4326",always_xy=True)
    bycode={}
    source_fields=collections.Counter()
    with shapefile.Reader(str(shp),encoding="latin-1") as reader:
        names=[x[0] for x in reader.fields[1:]]
        for entry in reader.iterShapeRecords():
            attrs=dict(zip(names,list(entry.record)))
            code,field=code_insee(attrs)
            if not code or code not in CODES or code in bycode:
                raise ValueError("Code commune GEOFLA absent, non 972 ou en doublon : "+str(code))
            source_fields[field]+=1
            original=shape(entry.shape.__geo_interface__)
            if original.is_empty or not original.is_valid or original.geom_type not in ("Polygon","MultiPolygon"):
                raise ValueError("Géométrie source non valide "+code)
            pt=original.representative_point()
            lon,lat=points.transform(pt.x,pt.y)
            if not(-62.0<lon<-60.0 and 14.0<lat<16.0):
                raise ValueError("Transformation CRS produit des coordonnées hors Martinique : "+code)
            bycode[code]=transform(transformer.transform,original)
    if set(bycode)!=CODES:
        raise ValueError("La couche GEOFLA 2015 ne couvre pas les 34 communes")
    details={
        "archive_shapefile":str(shp.relative_to(dossier)),
        "couches_shapefile":sorted(str(p.relative_to(dossier)) for p in shps),
        "codes_champ":dict(source_fields),
        "crs_wkt_sha256":sha256(prj),
        "crs_epsg_reconnu":crs.to_epsg(),
        "crs_equivalent_epsg32620":crs.equals(CRS.from_epsg(32620),ignore_axis_order=True),
        "crs_datum":crs.datum.name if crs.datum else None,
        "projection_parametres":[{
            "nom":p.name,"valeur":p.value,"unite":p.unit_name
        } for p in crs.coordinate_operation.params] if crs.coordinate_operation else [],
    }
    return bycode,details


def loader_2026(path:Path)->dict:
    result=lire_geojson(path,CODES)
    if set(result)!=CODES or any(len(rows)!=1 for rows in result.values()):
        raise ValueError("Contours Etalab : 34 codes absents ou dupliqués")
    d={code:rows[0] for code,rows in result.items()}
    if any(g.is_empty or not g.is_valid or g.geom_type not in ("Polygon","MultiPolygon") for g in d.values()):
        raise ValueError("Géométrie 2026 invalide")
    return d


def controler_partition(d:dict,edition:str):
    from shapely.ops import unary_union
    if set(d)!=CODES:raise ValueError(edition+" : codes 972 incomplets")
    if any(g.is_empty or not g.is_valid or g.area<=0 for g in d.values()):
        raise ValueError(edition+" : géométrie invalide")
    u=unary_union(list(d.values()))
    if not u.is_valid:raise ValueError(edition+" : union invalide")
    # Surfaces en mètres carrés, tolérance de 100 m² pour imprécisions numériques.
    surcomptage=sum(x.area for x in d.values())-u.area
    if abs(surcomptage)>100:
        raise ValueError(edition+" : recouvrement géométrique interne "+str(surcomptage))
    return u


def principales_composantes(g,vers_geo,seuil_km2:float=0.01,max_n:int=7)->dict:
    from shapely.ops import transform
    """Points intérieurs et emprises approximatives, jamais les polygones."""
    def polygons(a):
        if a.is_empty:return []
        if a.geom_type=="Polygon":return [a]
        if a.geom_type in ("MultiPolygon","GeometryCollection"):
            return [p for piece in a.geoms for p in polygons(piece)]
        return []
    parts=sorted(polygons(g),key=lambda x:-x.area)
    if abs(sum(x.area for x in parts)-g.area)>0.1:
        raise ValueError("Composantes non surfaciques inattendues")
    out=[]
    for part in parts:
        if part.area/1e6<seuil_km2 or len(out)>=max_n:break
        point=transform(vers_geo.transform,part.representative_point())
        extent=transform(vers_geo.transform,part.envelope)
        out.append({
            "aire_km2":KM(part.area),
            "point_interieur_wgs84_lonlat":[round(point.x,6),round(point.y,6)],
            "enveloppe_approximative_wgs84_lonlat":[round(z,6) for z in extent.bounds],
        })
    return {"surface_km2":KM(g.area),"composantes":len(parts),
            "composantes_exportees":len(out),"plus_grandes":out,
            "precision":"point représentatif et rectangle d'emprise, non géométrie administrative"}


def comparaison(a:dict,b:dict,edition:str,vers_geo)->dict:
    ua=controler_partition(a,"GEOFLA 2015")
    ub=controler_partition(b,edition)
    external1=ua.difference(ub)
    external2=ub.difference(ua)
    total=0.0
    intern=0.0
    rows=[]
    for code in sorted(CODES):
        x,y=a[code],b[code]
        d=x.symmetric_difference(y).area
        out1=x.difference(ub).area
        out2=y.difference(ua).area
        inner=x.intersection(ub).difference(y).area
        inner_rev=y.intersection(ua).difference(x).area
        if abs(d-(out1+out2+inner+inner_rev))>100:
            raise ValueError("Décomposition de la commune "+code+" incohérente")
        total+=d
        intern+=inner
        inter=x.intersection(y).area
        union=x.union(y).area
        rows.append({
            "code":code,"diff_symetrique_km2":KM(d),
            "exterieur_2015_hors_2026_km2":KM(out1),
            "exterieur_2026_hors_2015_km2":KM(out2),
            "interieur_code_different_km2":KM(inner+inner_rev),
            "part_ecart_exterieur_pct":round((out1+out2)/d*100,3) if d else 0,
            "jaccard_pct":round(inter/union*100,6) if union else None,
        })
    rev=sum(b[code].intersection(ua).difference(a[code]).area for code in CODES)
    external=external1.area+external2.area
    if (abs(intern-rev)>100
        or abs(total-(external+intern+rev))>100):
        raise ValueError("La partition externe / interne ne ferme pas")
    return {
        "edition_reference":edition,
        "communes":34,"aire_2015_km2":KM(ua.area),
        "aire_2026_km2":KM(ub.area),
        "ecart_emprise_exterieure_km2":KM(external),
        "emprise_2015_hors_2026_km2":KM(external1.area),
        "emprise_2026_hors_2015_km2":KM(external2.area),
        "ecart_entre_codes_interieur_unique_km2":KM(intern),
        "cumul_ecarts_communaux_km2":KM(total),
        "equation":"cumul = écart extérieur + 2 × écart interne",
        "principaux_ecarts_communaux":sorted(rows,key=lambda x:(-x["diff_symetrique_km2"],x["code"]))[:12],
        "toutes_communes":rows,
        "composantes_exterieures":{
            "2015_hors_2026":principales_composantes(external1,vers_geo),
            "2026_hors_2015":principales_composantes(external2,vers_geo),
        },
    }


def evaluer(dossier:Path,archive:Path,reference100:Path,reference50:Path,sortie:Path)->dict:
    from pyproj import Transformer
    if archive.name!=ARCHIVE_NAME:
        raise ValueError("Archive GEOFLA inattendue")
    if not archive.is_file() or not reference100.is_file() or not reference50.is_file():
        raise ValueError("Source manquante")
    hashes={"copie_GEOFLA_2015":sha256(archive),
            "contours_2026_100m":sha256(reference100),
            "contours_2026_50m":sha256(reference50)}
    if SHA_2015 and hashes["copie_GEOFLA_2015"]!=SHA_2015:
        raise ValueError("Archive GEOFLA 2015 changée")
    if hashes["contours_2026_100m"]!=SHA_2026_100 or hashes["contours_2026_50m"]!=SHA_2026_50:
        raise ValueError("Contours 2026 différents des sources épinglées")
    if "docs" in sortie.resolve().parts or sortie.exists():
        raise ValueError("Écriture interdite sous docs/ ou écrasement de la recette")
    g,meta=loader_2015(dossier)
    h=loader_2026(reference100)
    k=loader_2026(reference50)
    vers_geo=Transformer.from_crs("EPSG:6933","EPSG:4326",always_xy=True)
    c100=comparaison(g,h,"Etalab2026_100m",vers_geo)
    c50=comparaison(g,k,"Etalab2026_50m",vers_geo)
    u100=controler_partition(h,"Etalab2026_100m")
    u50=controler_partition(k,"Etalab2026_50m")
    generalization=KM(u100.symmetric_difference(u50).area)
    result={
        "schema":SCHEMA,
        "statut":"AUDIT_NON_VALIDANT_SOURCE_TIERCE_NON_AUTHENTIFIEE",
        "sources":{
            "copie_2015":{"nom":ARCHIVE_NAME,"url_tiers":SOURCE_URL,
                "empreinte_sha256":hashes["copie_GEOFLA_2015"],
                "empreinte_epinglee":bool(SHA_2015),
                "identite_originale_IGN_authentifiee":False,
                "date_limite_administrative_attestee":None,"metadonnees":meta},
            "contours2026":{
                "edition":"2026-05-04","100m_sha256":hashes["contours_2026_100m"],
                "50m_sha256":hashes["contours_2026_50m"],
                "origines":"Etalab/IGN, produits de généralisations distinctes"},
        },
        "etats_2026_100m":c100,
        "etats_2026_50m":c50,
        "difference_emprise_2026_100m_50m_km2":generalization,
        "communes_COG_2026":34,
        "nouvelles_relations_Pactols":0,
        "geometries_historiques_adoptees":0,
        "publication_docs":False,
        "limites_interpretation":[
            "La date 2015 du fichier n'atteste pas la date d'effet des limites.",
            "La source tierce n'est pas authentifiée par le producteur IGN.",
            "Les différences géométriques ne prouvent aucun changement juridique.",
            "Aucune représentation 2015 n'est projetée sur 1946-2014 ni sur le présent.",
            "Points et enveloppes des composantes ne sont pas des frontières.",
        ]
    }
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for option in ("dossier","archive","reference100","reference50","sortie"):
        p.add_argument("--"+option,type=Path,required=True)
    args=p.parse_args()
    result=evaluer(**vars(args))
    summary={
        "sources":result["sources"],
        "100m":{k:v for k,v in result["etats_2026_100m"].items()
                if k not in ("toutes_communes","composantes_exterieures")},
        "50m":{k:v for k,v in result["etats_2026_50m"].items()
                if k not in ("toutes_communes","composantes_exterieures")},
        "generalisation2026_km2":result["difference_emprise_2026_100m_50m_km2"]
    }
    print(json.dumps(summary,sort_keys=True,ensure_ascii=False,indent=2))
