#!/usr/bin/env python3
"""Extraire et qualifier les régions/départements IGN ADMIN EXPRESS COG 2017/2020.

Les sources IGN sont lues directement (Shapefile), reprojectées en EPSG:4326,
puis généralisées à 100 mètres dans EPSG:3857. Le COG Insee au 1er janvier
de l'année reste l'autorité attributaire. Aucun ARK Pactols n'est attribué.
Sortie de recette seulement : jamais docs/ directement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
import unicodedata
from collections import defaultdict
from pathlib import Path

import shapefile
from py7zr import SevenZipFile
from pyproj import CRS, Transformer
from shapely import make_valid
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union
from shapely.validation import explain_validity

import auditer_cog_2017_2020 as cog
import inspecter_paquets_ign_2017_2020 as ign

ANNEES=(2017,2020)
IGN_SHA256={
    2017:"222c420c4edbbf6fac76a7426ff74f075feed337103794b5048ede92abcb0133",
    2020:"ff7a732872a069cbc31f426b613a751cf990e80f4a98e984ecd81d9adbf0fd08",
}
GENERALISATION_METRES=100
TO_MERCATOR=Transformer.from_crs("EPSG:4326","EPSG:3857",always_xy=True).transform
TO_WGS84=Transformer.from_crs("EPSG:3857","EPSG:4326",always_xy=True).transform
TO_AREA=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True).transform
MAX_REPARATION_AIRE_PCT=0.001
MAX_GENERALISATION_AIRE_PCT=1.0
LAYERS={"region":"REGION","departement":"DEPARTEMENT"}
PROPS={
    "region":{"code":("INSEE_REG","CODE_REG","REG"),"nom":("NOM_REG","NOM_REG_M","NOM_RE")},
    "departement":{"code":("INSEE_DEP","CODE_DEP","DEP"),"nom":("NOM_DEP","NOM_DEP_M"),
                   "region":("INSEE_REG","CODE_REG","REG")},
}
MISSING=object()

def norm(text):
    text=unicodedata.normalize("NFKD",str(text).casefold())
    return re.sub(r"[^a-z0-9]+"," ",
        "".join(c for c in text if not unicodedata.combining(c))).strip()

def champ(p,aliases,*,required=True):
    pp={str(k).upper(): v for k,v in p.items()}
    for key in aliases:
        val=pp.get(key)
        if val not in (None,""):
            return str(val).strip()
    if required:
        raise ValueError("Champ géographique absent "+str(aliases)+" : "+str(list(pp)))
    return None

def polygon_parts(g):
    if g.geom_type=="Polygon":return [g]
    if g.geom_type in ("MultiPolygon","GeometryCollection"):
        return [p for x in g.geoms for p in polygon_parts(x)]
    return []

def reparer(g, year, level, code, journal):
    if g.is_empty:raise ValueError("Source vide "+str((year,level,code)))
    if g.is_valid:return g
    fixed=make_valid(g)
    polygons=polygon_parts(fixed)
    if not polygons:raise ValueError("Réparation sans surface "+str((year,level,code)))
    repaired=unary_union(polygons)
    old_area=transform(TO_AREA,g).area
    new_area=transform(TO_AREA,repaired).area
    diff=abs(old_area-new_area)/old_area*100 if old_area else float("inf")
    event={"annee":year,"niveau":level,"code":code,
           "anomalie":explain_validity(g),"sortie_make_valid":fixed.geom_type,
           "difference_relative_aire_pct":round(diff,12),
           "methode":"shapely.make_valid et composants surfaciques seulement"}
    journal.append(event)
    if not repaired.is_valid or repaired.is_empty or diff>MAX_REPARATION_AIRE_PCT:
        raise ValueError("Réparation topologique non validable "+str(event))
    return repaired

def lire_shapefiles(source, year, out, journal):
    """Sélectionne seulement les 2 couches polygonales, métropole + 5 DROM."""
    out.mkdir(parents=True,exist_ok=False)
    with SevenZipFile(source,"r") as arc:
        names=arc.getnames()
        shps=[name for name in names if name.endswith(".shp") and
              Path(name).stem.upper() in LAYERS.values()]
        for level,stem in LAYERS.items():
            n=sum(Path(x).stem.upper()==stem for x in shps)
            if n!=(6 if year==2017 else 1):
                raise ValueError(f"Nombre de jeux SHP {year}/{level}: {n} (attendus 6 ou 1)")
        targets=[]
        for shp in shps:
            stem=shp[:-4]
            for ext in (".shp",".shx",".dbf",".prj",".cpg"):
                path=stem+ext
                if path in names:
                    targets.append(path)
            for ext in (".shp",".shx",".dbf",".prj"):
                if stem+ext not in targets:
                    raise ValueError("Composant obligatoire Shapefile absent : "+stem+ext)
        arc.extract(path=out, targets=targets)
    levels={"region":{}, "departement":{}}
    for s in sorted(shps):
        level=next(l for l,stem in LAYERS.items() if Path(s).stem.upper()==stem)
        path=out/s
        prj=path.with_suffix(".prj")
        crs=CRS.from_wkt(prj.read_text(encoding="utf-8"))
        to_wgs84=Transformer.from_crs(crs,"EPSG:4326",always_xy=True).transform
        cpg=path.with_suffix(".cpg")
        encoding=cpg.read_text(errors="replace").strip() if cpg.exists() else "utf-8"
        if encoding.upper()=="UTF8": encoding="utf-8"
        if encoding.upper()=="ANSI 1252": encoding="cp1252"
        reader=shapefile.Reader(str(path),encoding=encoding)
        fields=[f[0] for f in reader.fields[1:]]
        info={"chemin":s,"champs":fields,"crs":crs.to_string(),
              "encodage":encoding,"effectif":len(reader)}
        journal["couches"].append(info)
        for record in reader.iterShapeRecords():
            p={fields[i]:record.record[i] for i in range(len(fields))}
            code=champ(p,PROPS[level]["code"])
            if code in levels[level]:
                raise ValueError(f"Code doublon sur les Shapefiles {year}/{level}/{code}")
            nom=champ(p,PROPS[level]["nom"],required=False)
            parent=champ(p,PROPS[level]["region"]) if level=="departement" else None
            geom=transform(to_wgs84,shape(record.shape.__geo_interface__))
            geom=reparer(geom,year,level,code,journal["reparations"])
            mercator=transform(TO_MERCATOR,geom)
            geo_simplifiee=transform(TO_WGS84,
                   mercator.simplify(GENERALISATION_METRES,preserve_topology=True))
            if not geo_simplifiee.is_valid or geo_simplifiee.is_empty:
                raise ValueError("Géométrie généralisée invalide "+str((year,level,code)))
            area_initiale=transform(TO_AREA,geom).area
            area_simplifiee=transform(TO_AREA,geo_simplifiee).area
            diff=abs(area_initiale-area_simplifiee)/area_initiale*100 if area_initiale else float("inf")
            if diff>MAX_GENERALISATION_AIRE_PCT:
                raise ValueError(f"Simplification trop forte : {year}/{level}/{code} {diff:.7f}%")
            levels[level][code]={"nom_SIG":nom,"region_SIG":parent,
                   "geometry":mapping(geo_simplifiee),"generalisation_diff_pct":round(diff,8)}
    return levels

def produire(year, archive, cog_dir, sortie):
    if year not in ANNEES or archive.name!=ign.NAMES[year]:
        raise ValueError("Édition du paquet IGN inattendue")
    if "docs" in sortie.resolve().parts or sortie.exists():
        raise ValueError("Refus d'écraser la recette ou d'écrire dans docs/")
    archive_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
    if archive_hash!=IGN_SHA256[year]:
        raise ValueError("Empreinte d'origine IGN non conforme")
    region_archive=(cog_dir/("reg2017-txt.zip" if year==2017 else "cog_ensemble_2020_csv.zip"))
    depart_archive=(cog_dir/("depts2017-txt.zip" if year==2017 else "cog_ensemble_2020_csv.zip"))
    regs,meta_reg=cog.lire(region_archive,year,"region")
    depts,meta_dep=cog.lire(depart_archive,year,"departement")
    parent_regions=defaultdict(list)
    for code,row in depts.items():
        if row["region"] not in regs:
            raise ValueError("Département rattaché à une région non COG : "+code)
        parent_regions[row["region"]].append(code)
    journal={"annee":year,"source_IGN_SHA256":archive_hash,
             "date_edition_IGN":ign.NAMES[year][-13:-3],
             "couches":[],"reparations":[],"divergences_noms":[],"nouvelles_autorites_Pactols":0}
    # La structure source est diagnostiquée et conservée même si l'on bloque.
    with tempfile.TemporaryDirectory() as t:
        datas=lire_shapefiles(archive,year,Path(t)/"source",journal)
    outputs={}
    index=[]
    for level,leveldata in datas.items():
        annual=regs if level=="region" else depts
        if set(leveldata)!=set(annual):
            raise ValueError(f"Codes IGN ≠ COG pour {year}/{level} :"
              f" manque={sorted(set(annual)-set(leveldata))} "
              f"suppl={sorted(set(leveldata)-set(annual))}")
        features=[]
        for code,row in sorted(annual.items()):
            geom=leveldata[code]
            if level=="departement" and geom["region_SIG"]!=row["region"]:
                raise ValueError(f"Département {code} : IGN région {geom['region_SIG']} ≠ COG {row['region']}")
            if geom["nom_SIG"] and norm(geom["nom_SIG"])!=norm(row["nom"]):
                journal["divergences_noms"].append({
                  "niveau":level,"code":code,"nom_IGN":geom["nom_SIG"],"nom_COG":row["nom"]})
            p={"annee":year,"code":code,"nom":row["nom"],"niveau":level,
               "date_reference_COG":str(year)+"-01-01","annee_geometrie":year,
               "pactols_valide":False,"source_geometrie":"IGN ADMIN EXPRESS COG",
               "edition_geometrie":ign.NAMES[year][-13:-3]}
            if level=="departement":
                p["code_region_parent"]=row["region"]
                p["nom_region_parent"]=regs[row["region"]]["nom"]
            else:
                p["departements"]=sorted(parent_regions[code])
            features.append({"type":"Feature","properties":p,"geometry":geom["geometry"]})
            index.append({"kind":"admin","code":code,"year":year,"level":level,
                          "label":row["nom"],"champs":sorted({norm(row["nom"]),code.lower()})})
        source_meta=meta_reg if level=="region" else meta_dep
        source_url="https://data.geopf.fr/telechargement/download/ADMIN-EXPRESS-COG/"+\
                  ign.NAMES[year][:-3]+"/"+ign.NAMES[year]
        outputs[level+"s-"+str(year)+".geojson"]={
            "type":"FeatureCollection",
            "provenance":{
                "schema":"adlfi.lieux.contours.annuels.v1",
                "cog_au_premier_janvier":str(year),
                "annee_geometrie":year,"generalisation_m":GENERALISATION_METRES,
                "pactols_valide":False,
                "source_geometrie":"IGN ADMIN EXPRESS COG",
                "edition_IGN":ign.NAMES[year][-13:-3],
                "source_geometrie_url":source_url,
                "source_cog_url":cog.SOURCES[year].get("ensemble",
                    cog.SOURCES[year].get(level)),
                "source_archives_sha256":{archive.name:archive_hash,
                                         source_meta["fichier"]:source_meta["sha256_zip"]},
            },
            "features":features,
        }
    # Ne produire les couches que si tout le corpus a passé l'audit.
    sortie.mkdir(parents=True,exist_ok=False)
    for name,fc in outputs.items():
        (sortie/name).write_text(json.dumps(fc,ensure_ascii=False,
             separators=(",",":"),sort_keys=True)+"\n",encoding="utf-8")
    (sortie/f"index-{year}.json").write_text(json.dumps({
      "schema":"adlfi.lieux.admin.index_ponts.v1",
      "annee":year,"nouvelles_correspondances_pactols":0,
      "entries":index},ensure_ascii=False,separators=(",",":"),sort_keys=True)+"\n",encoding="utf-8")
    (sortie/f"rapport-{year}.json").write_text(json.dumps(journal,ensure_ascii=False,
      indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return {"annee":year,"codes_region":len(datas["region"]),
            "codes_departement":len(datas["departement"]),
            "reparations":journal["reparations"],
            "divergences_noms":journal["divergences_noms"],
            "fichiers":list(outputs)}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--annee",type=int,required=True,choices=ANNEES)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--sources-cog",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    args=p.parse_args()
    result=produire(args.annee,args.archive,args.sources_cog,args.sortie)
    print(json.dumps(result,ensure_ascii=False,indent=2))
