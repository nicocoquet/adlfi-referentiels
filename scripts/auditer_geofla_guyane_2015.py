#!/usr/bin/env python3
"""Inspecter sans publication une archive GEOFLA Guyane 2015 issue d'un miroir tiers.

L'analyse inventorie les objets, identifiants et géométries, puis confronte
les contours à une couche nationale 2026 de référence. Aucune forme GEOFLA,
différence de polygones ou frontière reconstituée n'est exportée.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import re
from pathlib import Path

SCHEMA="adlfi.lieux.guyane.geofla2015.audit-source.v1"
ARCHIVE_NAME="GEOFLA_2-1_COMMUNE_SHP_UTM22RGFG95_D973_2015-12-01.rar"
SHA_NATIONAL="4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconnaitre_code(attributes:dict)->tuple[str|None,str|None]:
    """Ne jamais déduire un code depuis un nom ou une position géométrique."""
    possibilities=[]
    normalized={str(k).upper():str(v).strip() for k,v in attributes.items()}
    for field in ("CODE_INSEE","INSEE_COM","INSEE","INSEE_COM1","CODE_COM",
                  "INSEE_COMM","CODEINSEE","COD_INSEE","INSEE_C"):
        val=normalized.get(field)
        if val and re.fullmatch(r"973\d\d",val):
            possibilities.append((field,val))
    codes={code for _,code in possibilities}
    if len(codes)==1:
        return possibilities[0][1],possibilities[0][0]
    return None,None


def lire_geojson(path:Path,codes:set[str])->dict:
    from shapely.geometry import shape
    from shapely.ops import transform
    from pyproj import Transformer
    opener=gzip.open if path.suffix==".gz" else open
    with opener(path,"rt",encoding="utf-8") as fh:
        doc=json.load(fh)
    if doc.get("type")!="FeatureCollection":
        raise ValueError("Source nationale non GeoJSON FeatureCollection")
    proj=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True)
    bycode=collections.defaultdict(list)
    for f in doc.get("features",[]):
        code=str(f.get("properties",{}).get("code",""))
        if code in codes:
            g=shape(f.get("geometry"))
            bycode[code].append(transform(proj.transform,g))
    return bycode


def comparer_geometries(a,b)->dict:
    """Mesures sur copies dans la projection équivalente EPSG:6933."""
    if a.is_empty or b.is_empty or not a.is_valid or not b.is_valid:
        raise ValueError("Géométrie non valide pour une comparaison fiable")
    intersection=a.intersection(b).area
    union=a.union(b).area
    source_area=a.area
    reference_area=b.area
    return {
        "source2015_km2":round(source_area/1e6,6),
        "national2026_km2":round(reference_area/1e6,6),
        "difference_symetrique_km2":round(a.symmetric_difference(b).area/1e6,6),
        "source2015_hors_2026_km2":round(a.difference(b).area/1e6,6),
        "national2026_hors_2015_km2":round(b.difference(a).area/1e6,6),
        "jaccard_pct":round(intersection/union*100,6) if union else None,
    }


def inspecter(dossier:Path,rar:Path,national:Path,sortie:Path)->dict:
    import shapefile
    from shapely.geometry import shape
    from shapely.ops import transform
    from pyproj import CRS,Transformer
    if rar.name!=ARCHIVE_NAME:
        raise ValueError("Nom d'archive non conforme au produit attendu")
    if sha256(national)!=SHA_NATIONAL:
        raise ValueError("Le millésime national 2026 n'est pas celui de la recette")
    if "docs" in sortie.resolve().parts or sortie.resolve().is_relative_to(dossier.resolve()):
        raise ValueError("Rapport de recette interdit dans les sources ou le site")
    shapefiles=sorted(p for p in dossier.rglob("*") if p.is_file()
                      and p.suffix.lower()==".shp")
    if len(shapefiles)!=1:
        raise ValueError("Archive avec plusieurs shapefiles ou sans shapefile : "+
                         ", ".join(str(p.relative_to(dossier)) for p in shapefiles))
    shp=shapefiles[0]
    prj=shp.with_suffix(".prj")
    if not prj.exists():
        raise ValueError("Projection source absente : pas de géocodage par hypothèse")
    src_crs=CRS.from_wkt(prj.read_text(encoding="utf-8",errors="replace"))
    if not src_crs.is_projected:
        raise ValueError("Source GEOFLA sans système projeté vérifiable")
    to6933=Transformer.from_crs(src_crs,"EPSG:6933",always_xy=True)
    source=collections.defaultdict(list)
    code_fields=collections.Counter()
    records=[]
    with shapefile.Reader(str(shp),encoding="latin-1") as shpfile:
        fields=[x[0] for x in shpfile.fields[1:]]
        for sr in shpfile.iterShapeRecords():
            attr=dict(zip(fields,list(sr.record)))
            code,field=reconnaitre_code(attr)
            if field:code_fields[field]+=1
            if code:source[code].append(transform(to6933.transform,shape(sr.shape.__geo_interface__)))
            records.append({"code_identifie":code,"champs":sorted(attr.keys())})
    cogs={code for code in source if code.startswith("973")}
    if any(code not in cogs for code in source):raise ValueError("Commune non guyanaise dans la couche")
    comparison=[]
    target=lire_geojson(national,cogs)
    for code,gs in sorted(source.items()):
        refs=target.get(code,[])
        if len(gs)!=1 or len(refs)!=1:
            comparison.append({"code":code,"statut":"AMBIGU_OU_ABSENT",
                 "nb_source":len(gs),"nb_reference":len(refs)})
            continue
        a,b=gs[0],refs[0]
        row={"code":code,"statut":"COMPARAISON_NON_VALIDANTE",
             "source_valide":a.is_valid,"reference_valide":b.is_valid,
             "mesures":None}
        if a.is_valid and b.is_valid and not a.is_empty and not b.is_empty:
            row["mesures"]=comparer_geometries(a,b)
        comparison.append(row)
    stats={
        "fichiers_2015":len(records),
        "codes_reconnus":len(cogs),
        "codes_cog_2026_couverts":sum(bool(target.get(code)) for code in cogs),
        "codes_avec_comparaison_valide":sum(x.get("mesures") is not None for x in comparison),
        "geometries_2015_valides":sum(g.is_valid for shapes in source.values() for g in shapes),
        "codes_2015_non_uniques":sorted(c for c,gs in source.items() if len(gs)!=1),
        "principaux_ecarts_km2":sorted(
            [{"code":x["code"],"ecart_km2":x["mesures"]["difference_symetrique_km2"],
              "jaccard_pct":x["mesures"]["jaccard_pct"]}
              for x in comparison if x.get("mesures") is not None],
            key=lambda x:(-x["ecart_km2"],x["code"]))[:8],
    }
    report={
        "schema":SCHEMA,"statut":"AUDIT_SOURCE_TIERCE_NON_AUTHENTIFIEE",
        "source2015":{
            "fichier":rar.name,"source_externe":"miroir GitHub non officiel",
            "sha256":sha256(rar),
            "format":"shapefile archivé au format RAR",
            "shapefile_dans_archive":str(shp.relative_to(dossier)),
            "champs_attributaires":fields,
            "champ_code_detecte":dict(code_fields),
            "crs_wkt_sha256":hashlib.sha256(prj.read_bytes()).hexdigest(),
            "epsg_resolu":src_crs.to_epsg(),
            "identite_source_IGN_confirmee":False,
            "date_fichier_nom":"2015-12-01",
            "date_limites_administratives_attestee":None,
        },
        "source2026":{"sha256":sha256(national),
            "edition":"2026-05-04",
            "nature":"contours nationaux généralisés, distincts de GEOFLA"},
        "statistiques":stats,"comparaisons_par_code":comparison,
        "contours_historiques_adoptes":0,
        "geometries_publiees":0,
        "publication_possible":False,
        "avertissement":[
            "Une archive publiée par un tiers n'établit pas son identité ou intégrité vis-à-vis d'un paquet officiel IGN.",
            "La validité topologique d'un shapefile ne suffit pas à en garantir la validité juridique.",
            "Les différences de généralisation de GEOFLA et du fichier national 100 m rendent impossible la lecture des écarts comme seuls changements administratifs.",
            "La date d'édition du paquet 2015 ne prouve pas les limites en 1993 ou 1969.",
            "Aucune différence de polygones ni géométrie historique ne sont exportées.",
        ],
    }
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(json.dumps(report,ensure_ascii=False,
                      sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dossier",type=Path,required=True)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--national",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    a=p.parse_args()
    result=inspecter(a.dossier,a.archive,a.national,a.sortie)
    print(json.dumps({"source2015":result["source2015"],
          "statistiques":result["statistiques"],
          "publication_possible":False},ensure_ascii=False,indent=2))
