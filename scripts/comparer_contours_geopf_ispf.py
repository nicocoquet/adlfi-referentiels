#!/usr/bin/env python3
"""Comparer sans correction les contours ISPF Comas et GEO PF agrégé par code.

Appariement strict par IDGeo + hiérarchie ISPF, exclusion des divergences
(Maria, Maupihaa, Fangataufa). Aucun rapprochement par libellé.
Le rapport ne contient que des mesures et identifiants, pas de polygones.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
from zipfile import ZipFile

from inspecter_nomenclature_geographique_ispf import read_xlsx
from qualifier_communes_associees_ispf import SHA as XLSX_SHA, rows
from qualifier_jointures_geopf_ispf import GEO_PF_SHA, code
from auditer_geojson_ispf_polynesie import SOURCE_SHA as ISPF_GEO_SHA

EXCLUSIONS_DOCUMENTEES = ("28001", "43001", "44001", "55001")
SOURCE_URLS = {
    "xlsx": "https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx",
    "ispf_geojson": "https://www.data.gouv.fr/api/1/datasets/r/f5ec5fb2-c173-4a94-bbd9-c12ec876a4e6",
    "geopf": "https://www.data.gouv.fr/api/1/datasets/r/89d202c3-4f04-4168-842d-4c50036125c7",
}

def aire(geom, geod):
    if geom.is_empty: return 0.0
    if geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        return sum(aire(part, geod) for part in geom.geoms)
    if geom.geom_type != "Polygon": return 0.0
    from shapely.geometry.polygon import orient
    # GRS1980 : l’aire géodésique est signée ; les anneaux doivent être
    # réorientés (enveloppe antihoraire, trous horaires) avant mesure.
    value, _ = geod.geometry_area_perimeter(orient(geom, sign=1.0))
    if not math.isfinite(value): raise ValueError("Surface ellipsoïdale non finie")
    return abs(value)

def lire_source_geopf(path):
    import shapefile
    from shapely.geometry import shape
    with ZipFile(path) as z:
        names=z.namelist()
        shps=[n for n in names if n.lower().endswith(".shp")]
        if len(shps)!=1:raise ValueError("Une couche SHP GEO PF attendue")
        stem=shps[0][:-4]
        def part(ext):
            values=[n for n in names if n.lower()==(stem+ext).lower()]
            if len(values)!=1:raise ValueError("Composant "+ext+" absent ou dupliqué")
            return io.BytesIO(z.read(values[0]))
        with shapefile.Reader(shp=part(".shp"),shx=part(".shx"),dbf=part(".dbf"),
                              encoding="utf-8",encodingErrors="replace") as f:
            if len(f)!=179:raise ValueError("Cardinalité GEO PF différente de 179")
            return [(sr.record.as_dict(),shape(sr.shape.__geo_interface__))
                    for sr in f.iterShapeRecords()]

def comparer(xlsx, ispf_geojson, geopf):
    from shapely.geometry import shape
    from shapely.ops import unary_union
    from shapely.errors import GEOSException
    from pyproj import CRS
    sources={"xlsx":(xlsx,XLSX_SHA),"ispf_geojson":(ispf_geojson,ISPF_GEO_SHA),"geopf":(geopf,GEO_PF_SHA)}
    for name,(path,sha) in sources.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError("Source altérée : "+name)
    sheets={s["feuille"]:s for s in read_xlsx(xlsx)}
    georows=rows(sheets["Geo"])
    if len(georows)!=179:raise ValueError("179 unités ISPF attendues")
    xgeo={code(r["IDGeo"],5):r for r in georows}
    if len(xgeo)!=179:raise ValueError("Doublons IDGeo ISPF")
    geometry_rows=lire_source_geopf(geopf)
    with ZipFile(ispf_geojson) as z:
        comas=json.loads(z.read("Comas.GeoJSON"))
    if comas.get("crs",{}).get("properties",{}).get("name")!="urn:ogc:def:crs:EPSG::4687":
        raise ValueError("CRS ISPF inattendu")
    if len(comas["features"])!=116:raise ValueError("116 géométries ISPF attendues")
    official={}
    for feature in comas["features"]:
        props=feature["properties"]
        ident=code(props["IDComas"],3)
        if ident in official:raise ValueError("IDComas ISPF dupliqué")
        official[ident]=shape(feature["geometry"])
    geod=CRS.from_epsg(4687).get_geod()
    geofields={}
    anomalous=[]
    retained=defaultdict(list)
    seen=set()
    for props,geometry in geometry_rows:
        ident=code(props["code_geogr"],5)
        if ident in seen:raise ValueError("code_geogr GEO PF dupliqué")
        seen.add(ident)
        reference=xgeo.get(ident)
        if reference is None:
            anomalous.append({"code_geogr":ident,"raison":"CODE_ABSENT_ISPF",
                              "code_com_1":str(props.get("code_com_1"))})
            continue
        conflicts=[]
        for field,other,width in (("IDComas","code_com_1",3),
                                  ("IDCom","code_commu",2),
                                  ("IDSub","code_subdi",None),
                                  ("IDIle","id_ile",None)):
            try:
                if code(reference[field],width)!=code(props.get(other),width):
                    conflicts.append(field)
            except ValueError:
                conflicts.append(field)
        if conflicts or ident in EXCLUSIONS_DOCUMENTEES:
            anomalous.append({"IDGeo":ident,"raison":"HIERARCHIE_OU_EXCEPTION",
                              "champs":conflicts,"code_com_1":str(props.get("code_com_1"))})
            continue
        retained[code(reference["IDComas"],3)].append((ident,geometry))
    if len(seen)!=179:raise ValueError("179 codes GEO PF uniques attendus")
    if set(xgeo)-seen != {"43001","44001"}:
        raise ValueError("Écarts de codes GEO PF modifiés : revoir l'audit PR83")
    if len(anomalous)!=4:
        raise ValueError("Attendu 4 objets GEO PF exclus (deux Maria, Maupihaa, Fangataufa)")

    # Toutes les pièces géographiques de chaque unité fine doivent être
    # appariées ; sinon, exclure l'unité entière pour éviter un faux écart.
    expected_by_unit=defaultdict(set)
    for ident,rec in xgeo.items():
        expected_by_unit[code(rec["IDComas"],3)].add(ident)
    results={}
    excluded_units=[]
    for unit,reference in sorted(official.items()):
        parts=retained.get(unit,[])
        actual_ids={ident for ident,_ in parts}
        expected_ids=expected_by_unit.get(unit,set())
        if actual_ids!=expected_ids:
            excluded_units.append({"IDComas":unit,"raison":"COUVERTURE_INCOMPLETE",
                                   "codes_IDGeo_attendus":sorted(expected_ids),
                                   "codes_IDGeo_verifies":sorted(actual_ids)})
            continue
        if not reference.is_valid or reference.is_empty or any(g.is_empty or not g.is_valid for _,g in parts):
            excluded_units.append({"IDComas":unit,"raison":"GEOMETRIE_SOURCE_INVALIDE"})
            continue
        try:
            geom=unary_union([g for _,g in parts])
            if geom.is_empty or not geom.is_valid:
                excluded_units.append({"IDComas":unit,"raison":"UNION_GEO_PF_INVALIDE"})
                continue
            sym=reference.symmetric_difference(geom)
            inter=reference.intersection(geom)
            aa,bb=aire(reference,geod),aire(geom,geod)
            diff=aire(sym,geod)
            intersection=aire(inter,geod)
            results[unit]={
                "IDComas":unit,
                "codes_IDGeo":sorted(actual_ids),
                "nombre_polygones_geopf":len(parts),
                "aire_ISPF_m2":round(aa,3),
                "aire_GEO_PF_m2":round(bb,3),
                "aire_difference_symetrique_m2":round(diff,3),
                "aire_intersection_m2":round(intersection,3),
                "part_difference_sur_union":round(diff/(diff+intersection),12)
                   if diff+intersection>0 else None,
                "egalite_topologique":reference.equals(geom),
            }
        except (GEOSException, ValueError) as err:
            excluded_units.append({"IDComas":unit,"raison":"ERREUR_TOPOLOGIQUE",
                                   "erreur":str(err)[:180]})
    comparison=list(sorted(results.values(),key=lambda r:(-r["aire_difference_symetrique_m2"],r["IDComas"])))
    # Après exclusions, contrôler les mêmes paires qui recouvraient dans ISPF,
    # sans faire passer les absences de mesures pour des disparitions d'écarts.
    retained_shapes={}
    for unit in results:
        retained_shapes[unit]=unary_union([g for _,g in retained[unit]])
    pair_results=[]
    for ia,a in enumerate(sorted(retained_shapes)):
        for b in sorted(retained_shapes)[ia+1:]:
            g1,g2=retained_shapes[a],retained_shapes[b]
            if not g1.intersects(g2): continue
            try:
                inter=g1.intersection(g2)
                area=aire(inter,geod)
            except (GEOSException,ValueError):
                pair_results.append({"IDComas_a":a,"IDComas_b":b,"statut":"ERREUR_INTERSECTION"})
                continue
            if inter.area>0:
                pair_results.append({"IDComas_a":a,"IDComas_b":b,
                                     "aire_recouvrement_GEO_PF_m2":round(area,6),
                                     "statut":"RECOUVREMENT_GEO_PF"})
    return {
        "schema":"adlfi.lieux.polynesie.geopf.ispf.contours.comparaison.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "sources_sha256":{k:v[1] for k,v in sources.items()},
        "crs":"RGPF EPSG:4687","mesure":"GRS 1980, pyproj.Geod",
        "appariement":"IDGeo et IDComas/IDCom/IDSub/IDIle identiques, exhaustivité de toutes les pièces",
        "entites_geopf":len(geometry_rows),
        "objets_geographiques_ecartes":anomalous,
        "unites_fines_ISPF":len(official),
        "unites_comparees":len(results),
        "unites_exclues":excluded_units,
        "top_differences":comparison,
        "recouvrements_GEOPF_parmi_unites_comparees":pair_results,
        "limites":[
            "Sources institutionnelles mais indépendance géométrique non établie",
            "GEO PF date catalogue 2022, date de levé des contours non vérifiée",
            "Unités touchées par 4 écarts IDGeo/IDIle exclues sans ajustement",
            "Une différence de surfaces peut refléter une autre représentation du littoral",
            "Aucun contour corrigé, aucune publication automatisée"
        ],
        "publication":{"contours":0,"autorites":0,"ark":0},
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xlsx",required=True,type=Path)
    p.add_argument("--ispf-geojson",required=True,type=Path)
    p.add_argument("--geopf",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    args=p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Recette hors docs et sans écrasement")
    report=comparer(args.xlsx,args.ispf_geojson,args.geopf)
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("GEO_PF_CONTOURS_BILAN",json.dumps({
        "geopf":report["entites_geopf"],
        "unites_comparees":report["unites_comparees"],
        "unites_exclues":len(report["unites_exclues"]),
        "objets_ecartes":report["objets_geographiques_ecartes"],
        "recouvrements_geopf":len(report["recouvrements_GEOPF_parmi_unites_comparees"]),
        "top_differences":report["top_differences"][:5],
        "exclusions":report["unites_exclues"][:8],
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":main()
