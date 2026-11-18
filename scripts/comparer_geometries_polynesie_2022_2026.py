#!/usr/bin/env python3
"""Comparer sans publier les polygones Etalab 2026 aux références ISPF et GEO PF 2022.

Comparaison surfacique de diagnostic, non une équivalence juridique ou une
reconstitution historique. Les 179 unités GEO PF ne créent pas de communes COG.
"""
from __future__ import annotations
import argparse
import collections
import gzip
import hashlib
import io
import json
import zipfile
from pathlib import Path

ISPF_HASH = "8da21b8912a9df8db95036ce24f782a3172bf89698c11049e954a69a45dedc7e"
GEOPF_HASH = "29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b"
ETALAB_HASH = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def records_zip(path, name):
    import shapefile
    from pyproj import CRS, Transformer
    from shapely.geometry import shape
    from shapely.ops import transform
    from shapely.validation import explain_validity
    with zipfile.ZipFile(path) as z:
        names = {x.casefold(): x for x in z.namelist()}
        shp = next((x for x in z.namelist() if x.casefold().endswith("/"+name.casefold())
                    or x.casefold()==name.casefold()), None)
        if shp is None:
            raise ValueError("Couche absente de l'archive : "+name)
        stem = shp[:-4]
        get = lambda ext: z.read(names[(stem+ext).casefold()])
        kwargs = {"shp": io.BytesIO(get(".shp")), "shx": io.BytesIO(get(".shx")),
                  "dbf": io.BytesIO(get(".dbf"))}
        reader = shapefile.Reader(**kwargs)
        crs = CRS.from_wkt(get(".prj").decode("utf-8", "replace"))
        transformer = Transformer.from_crs(crs, CRS.from_epsg(6933), always_xy=True)
        rows = []
        for row in reader.iterShapeRecords():
            attrs = row.record.as_dict()
            g = shape(row.shape.__geo_interface__)
            valid = bool(g.is_valid and not g.is_empty and g.area > 0)
            projected = transform(transformer.transform, g) if valid else None
            rows.append((attrs, projected, None if valid else explain_validity(g)))
        return rows, crs.to_string()

def primary_code(value):
    text = str(value).strip()
    if not text.isdigit() or not (1 <= int(text) <= 99):
        raise ValueError("Identifiant de commune ISPF invalide : "+text)
    return f"987{int(text):02d}"

def summarise(g):
    return round(g.area / 1_000_000, 5) if g is not None else None

def compare(a, b):
    if a is None or b is None:
        return None
    union = a.union(b)
    if union.is_empty or union.area <= 0:
        return None
    inter = a.intersection(b)
    return {
        "intersection_sur_union": round(inter.area/union.area, 6),
        "difference_symetrique_km2": round(a.symmetric_difference(b).area/1e6, 5),
    }

def construire(ispf_zip, geopf_zip, etalab_file, cog_file):
    from shapely.geometry import shape
    from shapely.ops import unary_union, transform
    from shapely.validation import explain_validity
    from pyproj import Transformer
    for path, hash_ in ((ispf_zip, ISPF_HASH),(geopf_zip,GEOPF_HASH),(etalab_file,ETALAB_HASH)):
        if digest(path) != hash_:
            raise ValueError("SHA-256 de la source non conforme : "+str(path))
    index = json.loads(cog_file.read_text(encoding="utf-8"))
    if index.get("cog_ref") != "2026-01-01":
        raise ValueError("Millésime COG non conforme")
    expected = dict(line.split("|",1) for line in index["communes"]["987"].splitlines())
    if len(expected) != 48:
        raise ValueError("48 codes COG attendus")
    ispf_rows, ispf_crs = records_zip(ispf_zip, "Com.shp")
    geopf_rows, geopf_crs = records_zip(geopf_zip, "loc_commune_associee.shp")
    ispf = {}
    ispf_invalid = {}
    for attrs, g, diagnostic in ispf_rows:
        code = primary_code(attrs["IDCom"])
        if code in ispf:
            raise ValueError("Commune ISPF en double : "+code)
        ispf[code] = g
        if diagnostic:
            ispf_invalid[code] = diagnostic
    if set(ispf) != set(expected):
        raise ValueError("Les 48 codes communaux ISPF ne correspondent pas au COG")
    groups = collections.defaultdict(list)
    geofp_invalid = collections.defaultdict(list)
    outside = []
    for attrs, g, diagnostic in geopf_rows:
        code = str(attrs.get("code_com_i") or "").strip()
        if code not in expected:
            outside.append(code)
        else:
            groups[code].append(g)
            if diagnostic:
                geofp_invalid[code].append(diagnostic)
    # Une invalidité dans une unité empêche de former son union, sans make_valid implicite.
    geopf = {
        c: unary_union(parts) if parts and all(p is not None for p in parts) else None
        for c, parts in groups.items()
    }
    raw = etalab_file.read_bytes()
    fcoll = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    to_equal_area = Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True)
    etalab = {}
    etalab_invalid = {}
    for f in fcoll["features"]:
        code = str(f.get("properties",{}).get("code") or "")
        if code not in expected: continue
        if code in etalab: raise ValueError("Géométrie Etalab en double : "+code)
        g = shape(f["geometry"])
        valid = g.is_valid and not g.is_empty and g.area > 0
        etalab[code] = transform(to_equal_area.transform,g) if valid else None
        if not valid:
            etalab_invalid[code] = explain_validity(g)
    if set(etalab) != set(expected) or set(etalab_invalid) != {"98745"}:
        raise ValueError("Couverture/anomalies Etalab 2026 modifiées")
    results = []
    for code,label in sorted(expected.items()):
        gi,ge,gt = ispf.get(code),geopf.get(code),etalab.get(code)
        results.append({
            "code_COG": code, "libelle_COG": label,
            "surface_ispf_2022_km2": summarise(gi),
            "surface_geopf_2022_km2": summarise(ge),
            "surface_etalab_2026_km2": summarise(gt),
            "nb_unites_GEO_PF": len(groups.get(code,[])),
            "ispf_topologie": ispf_invalid.get(code,"VALIDE"),
            "geopf_topologie": geofp_invalid.get(code,[]) or "VALIDE" if code in groups else "ABSENT",
            "etalab_topologie": etalab_invalid.get(code,"VALIDE"),
            "etalab_vs_ispf": compare(gt,gi),
            "etalab_vs_geopf": compare(gt,ge),
            "geopf_vs_ispf": compare(ge,gi),
            "qualification_juridique": "NON_EFFECTUEE",
            "publication": "NON_PUBLIE",
        })
    return {
        "schema": "adlfi.lieux.pf.comparaison_geometrique_2022_2026.v1",
        "statut": "RECETTE_SPATIALE_NON_VALIDANTE",
        "provenance": {
            "ISPF_SHA256":ISPF_HASH,"GEO_PF_SHA256":GEOPF_HASH,
            "ETALAB_SHA256":ETALAB_HASH,"ISPF_CRS":ispf_crs,"GEO_PF_CRS":geopf_crs,
            "calcul_surface": "EPSG:6933, km2 ; diagnostic uniquement",
        },
        "bilan": {
            "communes_COG":48,"communes_ISPF":len(ispf),
            "unites_GEO_PF":len(geopf_rows),"parents_GEO_PF":len(groups),
            "parents_GEO_PF_absents":sorted(set(expected)-set(groups)),
            "codes_GEO_PF_hors_COG":sorted(set(outside)),
            "ISPF_invalides":ispf_invalid,"GEO_PF_invalides":dict(geofp_invalid),
            "Etalab_invalides":etalab_invalid,
            "nouveaux_ARK":0,"nouvelles_geometries_publiees":0,
        },
        "communes":results,
        "limites":"Écarts 2022-2026 et généralisations, non preuve d'un changement administratif ni d'un tracé juridiquement homologué. Les communes associées et îles rattachées restent des unités distinctes.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("ispf-zip","geopf-zip","etalab","index-cog","sortie"):
        parser.add_argument("--"+name,type=Path,required=True)
    a = parser.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie neuve hors docs/")
    report = construire(a.ispf_zip,a.geopf_zip,a.etalab,a.index_cog)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    ranked = sorted((x for x in report["communes"] if x["etalab_vs_ispf"]),
                    key=lambda x:x["etalab_vs_ispf"]["intersection_sur_union"])
    print("PF_COMPARAISON_SOURCES",json.dumps({
        "bilan":report["bilan"], "10_plus_faibles_iou":
        [{"code":x["code_COG"],"libelle":x["libelle_COG"],"iou":x["etalab_vs_ispf"]["intersection_sur_union"]}
         for x in ranked[:10]],
        "rapport_sha256":digest(a.sortie),
    },ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
