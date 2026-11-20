#!/usr/bin/env python3
"""Contrôle géométrique GEOS de la recette normande 2026 sur la source Etalab.

Aucune correction automatique : la seule géométrie altérée doit être Cahagnes
(code 14120), par découpe non interpolante d'un anneau auto-tangent.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
from pathlib import Path

from shapely.geometry import shape
from shapely.validation import explain_validity

EXPECTED=2644
FIXED="14120"
GEO_SOURCE_SHA="4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"


def analyser(source:Path,sortie:Path)->dict:
    from preparer_lieux_normandie_2026 import sha
    if sha(source)!=GEO_SOURCE_SHA:
        raise ValueError("Source Etalab non conforme")
    with gzip.open(source,"rt",encoding="utf-8") as h:
        raw=json.load(h)
    final=json.loads(sortie.read_text(encoding="utf-8"))
    if final.get("type")!="FeatureCollection" or final.get("provenance",{}).get("millesime")!=2026:
        raise ValueError("Géométries 2026 non datées")
    features=final["features"]
    if len(features)!=EXPECTED:
        raise ValueError("Nombre de contours normands 2026 incorrect")
    codes=[f["properties"]["code"] for f in features]
    if len(set(codes))!=EXPECTED:
        raise ValueError("Code COG dupliqué")
    sources={f["properties"]["code"]:f for f in raw["features"]
             if f.get("properties",{}).get("code") in set(codes)}
    if len(sources)!=EXPECTED:
        raise ValueError("Source Etalab dépourvue de contours normands")
    repaired=final["provenance"].get("reparations_topologiques")
    if not isinstance(repaired,list) or len(repaired)!=1 or repaired[0].get("code")!=FIXED:
        raise ValueError("Une seule réparation autorisée : Cahagnes (14120)")
    invalid=[]
    types=collections.Counter()
    changed=[]
    for feature in features:
        code=feature["properties"]["code"]
        geom=shape(feature["geometry"])
        if geom.is_empty or not geom.is_valid or geom.area<=0:
            invalid.append((code,explain_validity(geom)))
        types[geom.geom_type]+=1
        original=sources[code]["geometry"]
        if original!=feature["geometry"]:
            changed.append(code)
    if invalid:
        raise ValueError("Géométries non valides : "+repr(invalid[:15]))
    if changed!=[FIXED]:
        raise ValueError("Plus d'une commune modifiée à la source : "+repr(changed))
    if types!={"Polygon":2629,"MultiPolygon":15}:
        raise ValueError("Typologie géométrique inattendue : "+repr(types))
    old=shape(sources[FIXED]["geometry"])
    new=shape(next(f["geometry"] for f in features if f["properties"]["code"]==FIXED))
    if old.is_valid or not new.is_valid:
        raise ValueError("Le cas Cahagnes n'est plus une auto-intersection réparable")
    diff=old.symmetric_difference(new).area
    if diff>1e-15 or abs(old.area-new.area)>1e-15 or old.bounds!=new.bounds:
        raise ValueError("Cahagnes : surface ou emprise modifiée")
    return {
        "communes":EXPECTED,"geometries_valides_GEOS":len(features),
        "reparations":[FIXED],"source_Cahagnes_initialement_invalide":True,
        "aire_difference_symetrique_Cahagnes":diff,
        "aire_avant":old.area,"aire_apres":new.area,
        "emprise_identique":old.bounds==new.bounds,
        "types":dict(sorted(types.items())),
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--geo",type=Path,required=True)
    args=parser.parse_args()
    result=analyser(args.source,args.geo)
    print("NORMANDIE_TOPOLOGIE_2026_OK",json.dumps(result,ensure_ascii=False,sort_keys=True))
