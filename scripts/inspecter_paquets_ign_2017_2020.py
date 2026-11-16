#!/usr/bin/env python3
"""Inspecter l'arborescence des archives officielles IGN .7z 2017 et 2020.

Inventaire uniquement : pas de copie dans docs, pas de fausse certitude sur
l'historicité de la géométrie ni de changement de rattachement Pactols.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from py7zr import SevenZipFile

NAMES = {
    2017:"ADMIN-EXPRESS-COG_1-0__SHP__FRA_2017-06-19.7z",
    2020:"ADMIN-EXPRESS-COG_2-1__SHP__FRA_2020-11-20.7z",
}
BASE_URL="https://data.geopf.fr/telechargement/download/ADMIN-EXPRESS-COG/"

def inspecter(path: Path, year: int):
    with SevenZipFile(path,"r") as archive:
        info=archive.list()
        fichiers=[]
        for x in info:
            if x.is_directory:
                continue
            filename=x.filename
            basename=Path(filename).name
            ext=Path(filename).suffix.lower()
            f={
                "chemin": filename,
                "taille_non_compressee": x.uncompressed,
            }
            if x.compressed is not None:
                f["taille_compressee"] = x.compressed
            if ext in (".shp",".shx",".dbf",".prj",".cpg",".qpj"):
                fichiers.append(f)
        shp=[x for x in fichiers if x["chemin"].lower().endswith(".shp")]
        allnames=[x["chemin"] for x in fichiers]
        shp_candidates=[x for x in shp if any(s in Path(x["chemin"]).stem.lower()
            for s in ("region","departement"))]
        ext_counts=Counter(Path(x["chemin"]).suffix.lower() for x in fichiers)
    base=NAMES[year]
    folder=base[:-3]
    return {
        "annee_reference_supposee":year,
        "date_edition_ign":folder[-10:],
        "nom_paquet":base,
        "source_url":BASE_URL+folder+"/"+base,
        "source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "archive_octets":path.stat().st_size,
        "fichiers_geographiques":len(fichiers),
        "nombre_shp":len(shp),
        "extensions":dict(ext_counts),
        "candidats_regions_departements":shp_candidates,
        "tous_les_shp":shp,
        "fichiers_geographiques_inventorie":allnames[:200],
        "importation_realisee":False,
        "alignement_cog_realise":False,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--annee",type=int,choices=(2017,2020),required=True)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    args=p.parse_args()
    if args.archive.name != NAMES[args.annee]:
        raise ValueError("Nom du paquet officiel non attendu")
    if "docs" in args.sortie.resolve().parts or args.sortie.exists():
        raise ValueError("Ne pas écrire dans docs/ ni écraser le rapport")
    report=inspecter(args.archive,args.annee)
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print("ANNEE",args.annee,"PAQUET",report["archive_octets"],
          "FICHIERS",report["fichiers_geographiques"],
          "SHAPEFILES",report["nombre_shp"],flush=True)
    for file in report["candidats_regions_departements"]:
        print("COUCHE",file["chemin"],"TAILLE",file["taille_non_compressee"],flush=True)
