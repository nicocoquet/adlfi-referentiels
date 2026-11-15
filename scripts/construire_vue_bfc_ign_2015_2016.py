#!/usr/bin/env python3
"""Assembler la carte BFC 2015/2016 à partir des deux archives IGN GEOFLA.

La représentation est composée d'unions de départements de la même
édition géographique, non de contours régionaux natifs de l'IGN.
Ne pas présumer que les éditions 2015-03-04 / 2016-06-28 décrivent
respectivement les limites exactement au 1er janvier de ces années.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED={"2015":{"26","43"},"2016":{"27"}}
EDITIONS={"2015":"2015-03-04","2016":"2016-06-28"}

def verifier(geo,year):
    if geo.get("type")!="FeatureCollection":
        raise ValueError("FeatureCollection attendue")
    p=geo.get("provenance",{})
    if p.get("annee")!=int(year) or p.get("source_producteur")!="IGN":
        raise ValueError("Mauvaise année ou source géographique")
    if p.get("contour_regional_natif") is not False or p.get("absence_de_retroprojection") is not True:
        raise ValueError("Les régions doivent être des unions d'archives de la bonne date")
    if EDITIONS[year] not in p.get("archive_url",""):
        raise ValueError("Edition IGN incompatible : "+year)
    if not re.fullmatch(r"[a-f0-9]{64}",p.get("archive_sha256","")):
        raise ValueError("SHA-256 source manquant")
    features=geo.get("features",[])
    codes=[f.get("properties",{}).get("code_region") for f in features]
    if set(codes)!=EXPECTED[year] or len(features)!=len(EXPECTED[year]):
        raise ValueError("Codes régionaux incorrects pour "+year)
    for f in features:
        attr=f.get("properties",{})
        if (attr.get("millesime_geometrie")!=int(year)
            or attr.get("nature")!=f"union_de_departements_GEOFLA_{year}"
            or attr.get("date_edition_archive")!=EDITIONS[year]
            or attr.get("pactols_valide") is not False):
            raise ValueError("Contour ou provenance incohérents pour "+year)
    return geo

def construire(modele:Path,geom2015:Path,geom2016:Path,sortie:Path):
    sortie=Path(sortie)
    if "docs" in sortie.resolve().parts:
        raise ValueError("Le pilote ne doit pas être écrit sous docs/")
    all_geo={
        year:verifier(json.loads(Path(src).read_text(encoding="utf8")),year)
        for year,src in (("2015",geom2015),("2016",geom2016))
    }
    src=Path(modele).read_text(encoding="utf8")
    if src.count("__BFC_INLINE_DATA__")!=1:
        raise ValueError("L'emplacement de données est absent ou ambigu")
    payload=json.dumps(all_geo,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    src=src.replace("__BFC_INLINE_DATA__",payload)
    replacements=[
        (r"Les contours proviennent de deux\s+millésimes distincts d'un référentiel géographique réutilisant des données IGN",
         "Les régions sont reconstruites par union de départements de deux archives originales IGN GEOFLA distinctes, datées du 4 mars 2015 et du 28 juin 2016"),
        (r"Carte vectorielle de recette · source : Opendatasoft, géométries millésimées 2015/2016\s+\(réutilisation IGN GEOFLA / ADMIN EXPRESS\) · Licence Ouverte v2\.0 ·\s+les coordonnées n.ont pas été fabriquées à partir de frontières de 2026\.",
         "Sources géométriques : IGN GEOFLA DÉPARTEMENT, éditions 2015-03-04 et 2016-06-28. Chaque contour régional est l'union explicite des départements de la même édition. Aucune géométrie de 2026 n'est utilisée."),
        (r'<div class="provenance"><strong>Provenance et limites de la recette\.</strong>.*?</div>',
         '''<div class="provenance"><strong>Provenance et limites de la recette.</strong>
         La représentation 2015 associe les départements de l'édition IGN GEOFLA du
         <strong>4 mars 2015</strong> ; celle de 2016 associe les départements de l'édition du
         <strong>28 juin 2016</strong>. GEOFLA n'a pas fourni ici de couches régionales
         natives : les contours sont obtenus par union documentée des huit départements
         du millésime concerné. Les codes des régions et rattachements départementaux
         sont contrôlés indépendamment dans les COG Insee 2015 et 2016.
         Les dates des deux éditions géographiques sont distinctes des dates administratives
         au 1er janvier. Un écart entre les deux éditions IGN peut résulter d'une révision
         géométrique et ne prouve pas un changement de frontière.
         Aucun ARK Pactols n'est attribué automatiquement et aucun contour 2026
         n'est rétroprojeté.
         </div>'''),
    ]
    for pattern,replacement in replacements:
        src,count=re.subn(pattern,replacement,src,count=1,flags=re.S)
        if count!=1:raise ValueError("Structure du modèle HTML modifiée : "+pattern[:70])
    before="'<dt>Source géométrique</dt><dd>Opendatasoft · réutilisation de données IGN</dd>'+"
    after="'<dt>Source géométrique</dt><dd>IGN GEOFLA DÉPARTEMENT, édition '+(current==='2015'?'04/03/2015':'28/06/2016')+' · contour régional reconstruit</dd>'+"
    if src.count(before)!=1:raise ValueError("Fiche de source géométrique introuvable")
    src=src.replace(before,after)
    sortie.parent.mkdir(parents=True,exist_ok=True)
    sortie.write_text(src,encoding="utf8")
    return {
        "fichier":str(sortie),
        "taille_octets":sortie.stat().st_size,
        "sha256":hashlib.sha256(sortie.read_bytes()).hexdigest(),
        "contours_regions_2015":2,
        "contours_regions_2016":1,
        "sources":"IGN_GEOFLA_2015_03_04_et_2016_06_28",
        "nombre_nouvelles_relations_pactols":0,
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ("modele","geom2015","geom2016","sortie"):
        ap.add_argument("--"+key,required=True,type=Path)
    print(json.dumps(construire(**vars(ap.parse_args())),ensure_ascii=False,indent=2))
