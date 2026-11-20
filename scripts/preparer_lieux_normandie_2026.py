#!/usr/bin/env python3
"""Normandie : construire les états COG et contours 2026 sans les activer en ligne.

Réutilise strictement le constructeur homologué des 4 premières régions,
avec UNE région supplémentaire paramétrée seulement pour ce processus.
Les sources COG 2026 et l'archive 100 m d'Etalab sont épinglées SHA-256.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from unittest.mock import patch

import preparer_lieux_chronologie_4regions as base

SCHEMA="adlfi.lieux.normandie.contours-cog.2026.recette.v1"
REGION={"normandie":{
    "titre":"Normandie","reg":"28","departements":("14","27","50","61","76"),
}}
# SHA réelle de la source Etalab 2026/100m déjà certifiée dans le pilote
# PACA–Corse–Pays de la Loire–BFC (PR #29).
SOURCE_SHA="4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
CODES_ATTENDUS=2644
SOURCE_COG="https://www.insee.fr/fr/information/8740222"
SOURCE_GEO=base.GEO_URL


def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda:handle.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


def courant_normand(path:Path)->dict:
    if sha(path)!=base.COG_SHA256["communes"]:
        raise ValueError("COG courant 2026 non épinglé")
    rows={}
    with path.open(encoding="utf-8-sig",newline="") as f:
        dr=csv.DictReader(f)
        if not {"TYPECOM","COM","REG","DEP","LIBELLE"}.issubset(dr.fieldnames or []):
            raise ValueError("Table COG 2026 incompatible")
        for r in dr:
            if r["REG"]!="28" or r["TYPECOM"]!="COM":
                continue
            code=r["COM"]
            if (code in rows or r["DEP"] not in REGION["normandie"]["departements"]
                    or not r["LIBELLE"]):
                raise ValueError("Doublon, département ou libellé normand incohérent : "+code)
            rows[code]=r["LIBELLE"]
    if len(rows)!=CODES_ATTENDUS:
        raise ValueError("Effectif COG 2026 Normandie inattendu : "+str(len(rows)))
    return rows


def anneaux(geometry:dict):
    if not isinstance(geometry,dict):
        raise ValueError("Géométrie manquante")
    t=geometry.get("type")
    if t=="Polygon":
        return geometry.get("coordinates")
    if t=="MultiPolygon":
        polys=geometry.get("coordinates")
        if not isinstance(polys,list) or not polys:
            raise ValueError("Multipolygone vide")
        return [ring for polygon in polys for ring in polygon]
    raise ValueError("Géométrie non polygonale : "+str(t))


def verifier_geometrie(geometry:dict):
    rings=anneaux(geometry)
    if not isinstance(rings,list) or not rings:
        raise ValueError("Aucun anneau géométrique")
    points=0
    for ring in rings:
        if not isinstance(ring,list) or len(ring)<4 or ring[0]!=ring[-1]:
            raise ValueError("Anneau GeoJSON ouvert ou trop court")
        for coord in ring:
            if (not isinstance(coord,list) or len(coord)<2
                    or not all(isinstance(x,(int,float)) and math.isfinite(x)
                               for x in coord[:2])):
                raise ValueError("Coordonnée non finie")
            lon,lat=coord[:2]
            if not (-5<lon<5 and 47<lat<52):
                raise ValueError("Coordonnée hors emprise normande plausible")
        points+=len(ring)
    return points


def construire(communes:Path,historique:Path,mouvements:Path,
               contours:Path,paca:Path,sortie:Path)->dict:
    if sha(contours)!=SOURCE_SHA:
        raise ValueError("Contours Etalab 2026/100 m différents de la source vérifiée")
    codes=courant_normand(communes)
    output=Path(sortie)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Répertoire de recette existant non vide")
    with patch.dict(base.REGIONS,REGION,clear=True):
        original=base.construire(
            communes=communes,historique=historique,mouvements=mouvements,
            contours=contours,paca=paca,sortie=output,verifier_sha=True)
    if set(original["regions"])!={"normandie"}:
        raise ValueError("Génération régionale contaminée")
    result=original["regions"]["normandie"]
    if (result["contours_2026"]!=CODES_ATTENDUS
            or result["contours_manquants"] or result["validations_pactols_existantes"]!=0):
        raise ValueError("Contours normands incomplets ou alignements non souhaités")

    path_cog=output/"cog-normandie.json"
    path_geo=output/"contours-2026-normandie.geojson"
    cog=json.loads(path_cog.read_text(encoding="utf-8"))
    geo=json.loads(path_geo.read_text(encoding="utf-8"))
    if (cog["schema"]!=base.SCHEMA or cog["region"]!="normandie"
            or cog["alignements_Pactols_COG_valides_2026"] or cog["geometries_historiques"]
            or len(geo["features"])!=CODES_ATTENDUS):
        raise ValueError("COG temporel ou géométries incompatibles avec le moteur Lieux")
    if geo["provenance"].get("sha256_fichier_geo_source")!=SOURCE_SHA:
        raise ValueError("Chaîne de provenance cartographique rompue")
    seen=set()
    points=0
    types={}
    for f in geo["features"]:
        p=f["properties"]
        code=p.get("code")
        if (code not in codes or code in seen or
                p.get("millesime")!=2026 or p.get("ark_pactols_valide_2026") is not None):
            raise ValueError("Géométrie hors COG 2026 ou ARK inféré : "+str(code))
        seen.add(code)
        p["nom"]=codes[code] # libellé officiel du COG ; non la graphie d'Etalab
        p["statut"]="contour_COG_2026_sans_validation_ARK_inferree"
        points+=verifier_geometrie(f["geometry"])
        t=f["geometry"]["type"]
        types[t]=types.get(t,0)+1
    if seen!=set(codes):
        raise ValueError("Couverture géométrique normande non exhaustive")
    geo["provenance"]["libelles"]="Insee COG 2026, TYPECOM=COM, REG=28"
    geo["provenance"]["sha256_COG_communes"]=base.COG_SHA256["communes"]
    path_geo.write_text(
        json.dumps(geo,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",
        encoding="utf-8")

    rapport={
        "schema":SCHEMA,"statut":"RECETTE_NON_ACTIVEE",
        "region":"normandie","code_region_COG":"28",
        "cog_millesime":2026,"geometry_millesime":2026,
        "nombre_communes_cog":len(codes),"nombre_contours":len(seen),
        "nombre_periodes":len(cog["periodes_com"]),
        "nombre_lignes_mouvements":len(cog["lignes_mouvements_cog"]),
        "nombre_observations_COMA_COMD":len(cog["observations_COMA_COMD_2026"]),
        "points_geojson":points,
        "types_geometriques":dict(sorted(types.items())),
        "correspondances_Pactols_ajoutees":0,
        "geometries_historiques":0,
        "active_dans_interface":False,
        "sources":{
            "COG_2026":SOURCE_COG,"sha256_cog_communes":base.COG_SHA256["communes"],
            "sha256_cog_historique":base.COG_SHA256["historique"],
            "sha256_cog_mouvements":base.COG_SHA256["mouvements"],
            "contours":SOURCE_GEO,"sha256_contours_100m_gz":SOURCE_SHA,
            "edition_geometries":"2026-05-04","generalisation":"100m",
            "licence_couche":"ODbL",
        },
        "sorties":{
            "cog_nominatif":"cog-normandie.json",
            "contours":"contours-2026-normandie.geojson",
            "sha256_cog":sha(path_cog),
            "sha256_geojson":sha(path_geo),
        },
        "limitations":[
            "Le COG historique décrit des codes et libellés, pas des géométries historiques.",
            "Les contours 2026 ne sont pas des limites juridiquement homologuées.",
            "Les régions historiques ne sont pas reconstituées par préfixe de département.",
            "Les seize alignements Pactols normands validés restent dans deux registres séparés.",
            "L'interface cartographique n'est pas activée par ce générateur.",
        ],
    }
    (output/"manifest.json").unlink()
    (output/"rapport-normandie-recette.json").write_text(
        json.dumps(rapport,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        encoding="utf-8")
    return rapport


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ("communes","historique","mouvements","contours","paca","sortie"):
        ap.add_argument("--"+key,required=True,type=Path)
    args=ap.parse_args()
    d=construire(**vars(args))
    print("NORMANDIE_COG_CONTOURS_2026",
          json.dumps({k:d[k] for k in ("nombre_communes_cog","nombre_contours",
                                       "nombre_periodes","nombre_lignes_mouvements",
                                       "points_geojson","types_geometriques","active_dans_interface")},
                     ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()
