#!/usr/bin/env python3
"""Construire un HTML autonome BFC : union IGN GEOFLA 2015 / polygone ODS 2016.

Les sources de contours restent distinguées et conservées dans les GeoJSON ;
aucune géométrie 2026 ni alignement Pactols n'est ajouté.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED={"2015":{"26","43"},"2016":{"27"}}
IGN_NATURE="reconstitution_par_union_de_departements_geofla2015"

def verifier(geo,year):
    if geo.get("type")!="FeatureCollection" or geo.get("provenance",{}).get("annee")!=int(year):
        raise ValueError("Année / GeoJSON incompatible : "+year)
    bycode={f.get("properties",{}).get("code_region"):f for f in geo.get("features",[])}
    if set(bycode)!=EXPECTED[year] or len(geo["features"])!=len(bycode):
        raise ValueError("Nombre de régions ou codes erronés : "+year)
    if any(f["properties"].get("millesime_geometrie")!=int(year) for f in bycode.values()):
        raise ValueError("Contours non attribués au bon millésime")
    if any(f["properties"].get("pactols_valide") is not False for f in bycode.values()):
        raise ValueError("Alignement Pactols non autorisé")
    if year=="2015":
        p=geo["provenance"]
        if p.get("edition_package")!="2015-03-04" or "reconstitution_par_union" not in p.get("statut",""):
            raise ValueError("GEOFLA 2015 doit être une union déclarée de départements")
        if any(f["properties"].get("nature")!="contour_regional_reconstruit_par_union_de_departements_historiques" for f in bycode.values()):
            raise ValueError("Les deux régions doivent provenir de la même méthode IGN")
    else:
        if "opendatasoft" not in geo["provenance"].get("jeu","").casefold():
            raise ValueError("La géométrie 2016 doit annoncer sa provenance ODS")
    return geo

def construire(modele,ign2015,ods2016,sortie):
    destination=Path(sortie)
    if "docs" in destination.resolve().parts:
        raise ValueError("Interdit : publication hors validation sous docs")
    data={
        "2015":verifier(json.loads(Path(ign2015).read_text(encoding="utf8")),"2015"),
        "2016":verifier(json.loads(Path(ods2016).read_text(encoding="utf8")),"2016"),
    }
    h=Path(modele).read_text(encoding="utf8")
    if h.count("__BFC_INLINE_DATA__")!=1:
        raise ValueError("Il faut un modèle avec un emplacement de données unique")
    h=h.replace("__BFC_INLINE_DATA__",json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c"))
    h,n1=re.subn(
        r"Les contours proviennent de deux\s+millésimes distincts d'un référentiel géographique réutilisant des données IGN",
        "Les contours de 2015 sont reconstitués par union des départements du paquet IGN GEOFLA daté du 4 mars 2015 ; le contour de 2016 est tiré du référentiel Opendatasoft millésimé et simplifié",
        h,count=1)
    h,n2=re.subn(r'Carte vectorielle de recette · source : Opendatasoft, géométries millésimées 2015/2016\s+\(réutilisation IGN GEOFLA / ADMIN EXPRESS\) · Licence Ouverte v2\.0 ·\s+les coordonnées n.ont pas été fabriquées à partir de frontières de 2026\.',
        "2015 : IGN GEOFLA original, union contrôlée de départements de la même édition · 2016 : Opendatasoft millésimé, simplifié. Aucune géométrie de 2026 n'est utilisée.",
        h,count=1)
    h,n3=re.subn(r'<div class="provenance"><strong>Provenance et limites de la recette\.</strong>.*?</div>',
        '''<div class="provenance"><strong>Provenance et limites de la recette.</strong>
        <strong>2015 :</strong> source primaire IGN GEOFLA, édition du 4 mars 2015 ;
        les régions sont <strong>reconstituées</strong> par union de leurs quatre départements
        de cette même édition, et ne sont pas des contours régionaux natifs IGN.
        <strong>2016 :</strong> contour provenant d’Opendatasoft, simplifié et attribué au millésime 2016.
        Le code administratif est vérifié séparément dans les COG Insee 2015 et 2016.
        Un écart entre ces représentations ne prouve aucun changement de frontière ;
        une archive de mars 2015 n’atteste pas nécessairement les limites précises au 1er janvier.
        Aucun alignement Pactols n’est inféré, et aucun contour de 2026 n’est rétroprojeté.
        </div>''',h,count=1,flags=re.S)
    before="'<dt>Source géométrique</dt><dd>Opendatasoft · réutilisation de données IGN</dd>'+"
    after="'<dt>Source géométrique</dt><dd>'+(current==='2015'?'IGN GEOFLA 2015 · union de départements':'Opendatasoft · contour simplifié 2016')+'</dd>'+"
    if h.count(before)!=1:raise ValueError("Fiche source non retrouvée")
    h=h.replace(before,after)
    if (n1,n2,n3)!=(1,1,1):raise ValueError(f"Le modèle a changé : {(n1,n2,n3)}")
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(h,encoding="utf8")
    return {"fichier":str(destination),"taille_octets":destination.stat().st_size,
            "sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
            "millesime_2015":"GEOFLA_IGN_union_departements",
            "millesime_2016":"ODS_geometrie_simplifiee",
            "nouvelles_validations_pactols":0}

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ("modele","ign2015","ods2016","sortie"):
        ap.add_argument("--"+key,type=Path,required=True)
    print(json.dumps(construire(**vars(ap.parse_args())),ensure_ascii=False,indent=2))
