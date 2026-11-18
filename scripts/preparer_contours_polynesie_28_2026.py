#!/usr/bin/env python3
"""Préparer, sans publication directe, 28 contours polynésiens cohérents au niveau communal.

La conformité aux critères de comparaison spatiale vaut recevabilité cartographique
pour la recette, PAS certification juridique ou restitution des états historiques.
Les seuils sont fixés à l'avance, et le jeu de 28 codes attendu est explicitement figé.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from shapely.geometry import shape
from shapely.validation import explain_validity

SOURCE_SHA256 = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
SOURCE_URL = "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-100m.geojson.gz"
COMPARAISON_SHA256 = "49724c979baa2cbedf0612b677b7c273757f8ba58749933e9b1a06a27398f52"
SCHEMA = "adlfi.lieux.contours.polynesie-2026.v1"
EXPECTED = ("98714","98715","98718","98722","98723","98724","98725","98729",
            "98731","98733","98734","98735","98736","98738","98739","98741",
            "98743","98744","98746","98747","98748","98750","98752","98753",
            "98754","98756","98757","98758")
EXCEPTION = "98745"
THRESHOLDS = {"etalab_ISPF":0.90,"etalab_GEO_PF":0.90,"ISPF_GEO_PF":0.95}

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as data:
        for block in iter(lambda: data.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def prepare(source, index, audit):
    if index.get("schema") != "adlfi.lieux.recherche.outremer.public.v1" or index.get("cog_ref") != "2026-01-01":
        raise ValueError("Index communal 2026 inattendu")
    names = {}
    for line in index["communes"]["987"].splitlines():
        code, sep, name = line.partition("|")
        if not sep or code in names or len(code) != 5 or not code.startswith("987"):
            raise ValueError("Identifiant COG 987 invalide ou dupliqué")
        names[code] = name
    if len(names) != 48 or EXCEPTION not in names:
        raise ValueError("48 communes COG attendues")
    if audit.get("schema") != "adlfi.lieux.pf.comparaison_geometrique_2022_2026.v1":
        raise ValueError("Audit des géométries incompatible")
    a = {x["code_COG"]: x for x in audit.get("communes",[])}
    if set(a) != set(names):
        raise ValueError("Audit incomplet ou redondant")
    admissibles = sorted(code for code,x in a.items()
        if x["etalab_topologie"] == "VALIDE" and
           x["etalab_vs_ispf"] is not None and
           x["etalab_vs_geopf"] is not None and
           x["geopf_vs_ispf"] is not None and
           x["etalab_vs_ispf"]["intersection_sur_union"] >= THRESHOLDS["etalab_ISPF"] and
           x["etalab_vs_geopf"]["intersection_sur_union"] >= THRESHOLDS["etalab_GEO_PF"] and
           x["geopf_vs_ispf"]["intersection_sur_union"] >= THRESHOLDS["ISPF_GEO_PF"])
    if admissibles != list(EXPECTED):
        raise ValueError("Critères géométriques modifiés : lot éditorial non réévalué")
    if a[EXCEPTION]["etalab_topologie"] == "VALIDE":
        raise ValueError("Tahaa n'est plus diagnostiquée invalide : réévaluation obligatoire")
    if source.get("type") != "FeatureCollection":
        raise ValueError("GeoJSON source non conforme")
    geometries = {}
    for item in source.get("features",[]):
        code = str((item.get("properties") or {}).get("code") or "")
        if code in names:
            if code in geometries:
                raise ValueError("Géométrie source dupliquée : " + code)
            geometries[code] = item.get("geometry")
    if set(geometries) != set(names):
        raise ValueError("Couverture de la source Etalab incomplète")
    features = []
    for code in EXPECTED:
        geometry = geometries[code]
        g = shape(geometry)
        if g.geom_type not in ("Polygon","MultiPolygon") or g.is_empty or not g.is_valid or g.area <= 0:
            raise ValueError("Contour invalide : " + code + " / " + explain_validity(g))
        minx,miny,maxx,maxy = g.bounds
        if not (-160 < minx < maxx < -130 and -30 < miny < maxy < -6):
            raise ValueError("Emprise géographique incohérente : " + code)
        features.append({"type":"Feature", "properties":{
            "code":code, "nom":names[code], "zone":"polynesie", "ref_cog":"COMER:COM:"+code,
            "niveau":"commune", "annee":2026, "millesime_cog":"2026-01-01",
            "edition_geometrie":"2026-05-04","qualification_geometrie":"audit_comparatif_et_topologique",
            "limite_juridique_homologuee":False, "ark_pactols":None
        }, "geometry":geometry})
    if len(features)!=28:
        raise ValueError("Effectif de contours inexact")
    return {"type":"FeatureCollection","features":features,"provenance":{
        "schema":SCHEMA,"statut":"contours_cartographiques_reference_2026",
        "cog_ref":"2026-01-01","edition_geometrie":"2026-05-04","generalisation_m":100,
        "sha256_source_geometrique":SOURCE_SHA256,"source_geometrique":SOURCE_URL,
        "sha256_audit_comparatif":COMPARAISON_SHA256,
        "criteres_recette_iou":THRESHOLDS,"nombre_contours":28,
        "communes_COG_2026":48,"exclues_a_instruire":sorted(set(names)-set(EXPECTED)),
        "tahaa_code":EXCEPTION,"tahaa_motif":"auto_intersection_et_alab",
        "contours_sans_ARK":True,"limites_juridiques_homologuees":False,
        "restitutions_historiques":0,
        "source_filiation":"Les contours Etalab des îles polynésiennes dérivent en partie des sources GEO PF : pas de validation indépendante.",
        "portee":"Repère de l'édition Etalab 2026, fond territorial antérieur ; pas de preuve de limites juridiques au 1er janvier 2026",
    }}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("geometries","index-cog","comparaison","sortie"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette neuve, hors docs/")
    if sha256(a.geometries)!=SOURCE_SHA256:
        raise ValueError("Archive Etalab : SHA-256 différent : "+sha256(a.geometries))
    if sha256(a.comparaison)!=COMPARAISON_SHA256:
        raise ValueError("Rapport comparatif : SHA-256 différent : "+sha256(a.comparaison))
    raw=a.geometries.read_bytes()
    source=json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    index=json.loads(a.index_cog.read_text(encoding="utf-8"))
    audit=json.loads(a.comparaison.read_text(encoding="utf-8"))
    output=prepare(source,index,audit)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(output,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print("PF28_PREPARE",json.dumps({
      "contours":28,"a_instruire":20,"tahaa_exclue":True,"sha256":sha256(a.sortie),
      "octets":a.sortie.stat().st_size},sort_keys=True))

if __name__ == "__main__":
    main()
