#!/usr/bin/env python3
"""Audit national des rattachements régionaux 2015/2016 IGN GEOFLA–Insee COG.

Vérifier les 96 départements métropolitains et les 22/13 codes régionaux,
sans produire de géométries ni de nouvelles relations Pactols.
Les états COG sont datés au 1er janvier ; les archives IGN de mars/juin.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from auditer_cog_regions_millesimes import HASHES,FUSIONS_2016,csv_lire,sha256

def charger_geofla(path,annee):
    import geopandas as gpd
    g=gpd.read_file(path)
    if len(g)!=96 or g.crs is None or g.crs.to_epsg()!=2154:
        raise ValueError(f"GEOFLA {annee}: 96 départements métropolitains en Lambert-93 attendus")
    required={"CODE_DEPT","CODE_REG","geometry"}
    if not required.issubset(g.columns):
        raise ValueError("GEOFLA: colonnes département/région absentes")
    if g.CODE_DEPT.duplicated().any() or not g.geometry.is_valid.all():
        raise ValueError("GEOFLA : codes dupliqués ou géométries invalides")
    return {str(r.CODE_DEPT):str(r.CODE_REG) for r in g.itertuples()}

def analyser(shp2015,shp2016,dep2015,dep2016):
    for name,path in (("dep2015",dep2015),("dep2016",dep2016)):
        if sha256(path)!=HASHES[name]:
            raise ValueError(f"COG officiel modifié ou erreur de millésime : {name}")
    geo15=charger_geofla(shp2015,2015); geo16=charger_geofla(shp2016,2016)
    cog15={r["DEP"]:r for r in csv_lire(dep2015,"dep",2015)}
    cog16={r["DEP"]:r for r in csv_lire(dep2016,"dep",2016)}
    for y,cog,geo in ((2015,cog15,geo15),(2016,cog16,geo16)):
        if not set(geo).issubset(cog):
            raise ValueError("COG : des départements IGN sont inconnus")
        for code,reg in geo.items():
            if cog[code]["REGION"]!=reg:
                raise ValueError(f"Discordance IGN/COG {y}: {code} -> {reg} != {cog[code]['REGION']}")
    if set(geo15)!=set(geo16):
        raise ValueError("Les deux IGN métropolitains ne couvrent pas les mêmes départements")
    regs15=set(geo15.values()); regs16=set(geo16.values())
    if len(regs15)!=22 or len(regs16)!=13:
        raise ValueError(f"Nombre de codes régionaux inattendu : {len(regs15)} / {len(regs16)}")
    old_to_new={old:new for new,parts in FUSIONS_2016.items() for old in parts}
    if len(old_to_new)!=16 or len(FUSIONS_2016)!=7:
        raise ValueError("Les sept fusions régionales ne sont pas correctement définies")
    rows=[];nchanged=0
    for dep in sorted(geo15):
        old,new=geo15[dep],geo16[dep]
        expected=old_to_new.get(old,old)
        if expected!=new:
            raise ValueError(f"Succession de région incohérente pour le département {dep}: {old}→{new}")
        changed=old!=new
        nchanged+=changed
        rows.append({
            "code_departement":dep,
            "libelle_departement_COG2015":cog15[dep]["NCCENR"],
            "libelle_departement_COG2016":cog16[dep]["NCCENR"],
            "code_region_COG2015":old,"code_region_COG2016":new,
            "nature_succession":"fusion_regionale_2016" if changed else "continuite_code_region",
            "date_reference_avant":"2015-01-01",
            "date_effet_reforme":"2016-01-01",
            "date_edition_IGN_2015":"2015-03-04",
            "date_edition_IGN_2016":"2016-06-28",
        })
    if nchanged!=65:
        raise ValueError(f"Nombre de départements changeant de région : {nchanged} != 65")
    report={
        "schema":"adlfi.lieux.regions.geofla_cog_national_2015_2016.v1",
        "statut":"RECETTE_HORS_PAGES_NON_VALIDANTE",
        "departements_metropole_2015":len(geo15),
        "departements_metropole_2016":len(geo16),
        "regions_metropole_2015":len(regs15),
        "regions_metropole_2016":len(regs16),
        "rattachements_IGN_COG_concordants":{2015:96,2016:96},
        "fusions":7,"anciennes_regions_fusionnees":16,
        "departements_dont_code_regional_change":nchanged,
        "source_IGN_shapefile_sha256":{"2015":sha256(shp2015),"2016":sha256(shp2016)},
        "source_COG_SHA256":{"2015":sha256(dep2015),"2016":sha256(dep2016)},
        "nouvelles_geometries_historiques_generees":0,
        "nouveaux_alignements_Pactols":0,
        "reserves":[
            "Les dates administratives au 1er janvier sont distinctes des dates d'édition des archives GEOFLA.",
            "La stabilité du code départemental n'est pas une preuve de limites géométriques constantes.",
            "Aucun code 2026 n'est utilisé pour remplacer un code régional historique.",
        ]
    }
    return rows,report

def exporter(rows,report,sortie):
    out=Path(sortie)
    if "docs" in out.resolve().parts:
        raise ValueError("Recette ne doit pas être publiée dans docs/")
    out.mkdir(parents=True,exist_ok=True)
    with (out/"rattachements-IGN-COG-2015-2016.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=";")
        w.writeheader();w.writerows(rows)
    (out/"rapport-national-geofla-cog-2015-2016.json").write_text(
        json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("shp2015","shp2016","dep2015","dep2016","sortie"):
        p.add_argument("--"+k,type=Path,required=True)
    args=vars(p.parse_args())
    output=args.pop("sortie")
    rows,report=analyser(**args)
    exporter(rows,report,output)
    print(json.dumps(report,ensure_ascii=False,indent=2))
