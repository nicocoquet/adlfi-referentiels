#!/usr/bin/env python3
"""Qualifier les listes de régions/départements Insee 2017 et 2020.

Seules les identités et relations COG au 1er janvier sont établies ici.
Ne dit rien des géométries et ne crée aucune correspondance Pactols.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

YEARS = (2017, 2020)
ARCHIVES_SHA256 = {
    "reg2017-txt.zip": "5683ada3aa4691c70b50cd337a1f64a50913ab8fdabe2f87ddd1ffe0dca612ae",
    "depts2017-txt.zip": "57feea872bd9e11be359e66430e79328123cb004a92195d9021daac749cdd18c",
    "cog_ensemble_2020_csv.zip": "d63ef3b1b258b479839d6883ecc37385c850b0c8319d1efa0e982365e08054bf",
}
SOURCES = {
    2017: {
        "region": "https://www.insee.fr/fr/statistiques/fichier/2666684/reg2017-txt.zip",
        "departement": "https://www.insee.fr/fr/statistiques/fichier/2666684/depts2017-txt.zip",
    },
    2020: {
        "ensemble": "https://www.insee.fr/fr/statistiques/fichier/4316069/cog_ensemble_2020_csv.zip",
    },
}

def lire(chemin: Path, year: int, level: str):
    raw = chemin.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARCHIVES_SHA256.get(chemin.name):
        raise ValueError("Archive Insee non conforme à l'empreinte de recette : " + chemin.name)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        expected = ("reg2017.txt" if level == "region" else "depts2017.txt") if year == 2017 \
          else ("region2020.csv" if level == "region" else "departement2020.csv")
        paths = [name for name in z.namelist() if Path(name).name.lower() == expected]
        if len(paths) != 1:
            raise ValueError(f"Archive {chemin.name} : {expected} absent/ambigu ; membres={z.namelist()[:40]}")
        orig = z.read(paths[0])
    data = orig.decode("latin-1" if year == 2017 else "utf-8-sig")
    reader = csv.DictReader(io.StringIO(data), delimiter="\t" if year == 2017 else ",")
    rows = [{str(k).upper(): v for k,v in row.items()} for row in reader]
    code_key = "REGION" if year == 2017 and level == "region" else "REG" if level == "region" else "DEP"
    expected_cols = {code_key, "NCCENR"}
    if level == "departement":
        expected_cols.add("REGION" if year == 2017 else "REG")
    if not rows or not expected_cols.issubset(rows[0]):
        raise ValueError(f"Colonnes {chemin.name}/{level} inattendues : {list(rows[0]) if rows else []}")
    features = {}
    for row in rows:
        code = row[code_key].strip()
        name = (row.get("LIBELLE") or row["NCCENR"]).strip()
        parent = row.get("REGION" if year == 2017 else "REG") if level == "departement" else None
        if not code or not name or code in features:
            raise ValueError("Identifiant ou libellé manquant/dupliqué : "+code)
        features[code] = {"nom":name, "region":parent.strip() if parent else None}
    if len(features) != (18 if level == "region" else 101):
        raise ValueError(f"Effectif {year}/{level} incohérent : {len(features)}")
    return features, {"url": SOURCES[year].get(level, SOURCES[year].get("ensemble")),
                      "fichier": chemin.name, "membre": paths[0],
                      "sha256_zip": hashlib.sha256(raw).hexdigest(),
                      "sha256_membre": hashlib.sha256(orig).hexdigest()}

def audit(dossier: Path, sortie: Path):
    if "docs" in sortie.resolve().parts or sortie.exists():
        raise ValueError("Sortie interdite ou existante")
    out = {"schema":"adlfi.lieux.cog-2017-2020.audit.v1",
           "statut":"RECETTE_COG_SANS_GEOMETRIE",
           "nouvelles_correspondances_pactols":0,"annees":{}}
    for year in YEARS:
        rpath=dossier / ("reg2017-txt.zip" if year==2017 else "cog_ensemble_2020_csv.zip")
        dpath=dossier / ("depts2017-txt.zip" if year==2017 else "cog_ensemble_2020_csv.zip")
        regs,rs=lire(rpath,year,"region")
        deps,ds=lire(dpath,year,"departement")
        orphans={code:dep["region"] for code,dep in deps.items() if dep["region"] not in regs}
        if orphans:
            raise ValueError("Rattachements COG manquants : "+str(orphans))
        out["annees"][str(year)]={"regions":regs,"departements":deps,"sources":{"regions":rs,"departements":ds},
                                  "effectif_regions":len(regs),"effectif_departements":len(deps)}
    a,b=(out["annees"][str(y)] for y in YEARS)
    for level in ("regions","departements"):
        if set(a[level])!=set(b[level]):
            raise ValueError(f"Ensemble de codes divergent 2017/2020 : {level}")
    diffs=[{"dep":code,"region_2017":v["region"],"region_2020":b["departements"][code]["region"]}
           for code,v in sorted(a["departements"].items())
           if v["region"]!=b["departements"][code]["region"]]
    out["rattachements_2017_2020_differents"]=diffs
    out["noms_regionaux_2017_2020_differents"]=[
        {"code":code,"nom_2017":v["nom"],"nom_2020":b["regions"][code]["nom"]}
        for code,v in sorted(a["regions"].items())
        if v["nom"]!=b["regions"][code]["nom"]]
    out["noms_departementaux_2017_2020_differents"]=[
        {"code":code,"nom_2017":v["nom"],"nom_2020":b["departements"][code]["nom"]}
        for code,v in sorted(a["departements"].items())
        if v["nom"]!=b["departements"][code]["nom"]]
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return {"codes_regions_2017":len(a["regions"]), "codes_departements_2020":len(b["departements"]),
            "rattachements_differents":diffs,
            "sha256_sources":{str(y):out["annees"][str(y)]["sources"] for y in YEARS}}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sources",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(audit(args.sources,args.sortie),ensure_ascii=False,indent=2))
