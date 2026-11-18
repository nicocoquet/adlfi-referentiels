#!/usr/bin/env python3
"""Diagnostic non publiant : les anneaux intérieurs expliquent-ils les écarts ISPF/GEO PF ?

Les surfaces des trous sont de nature inconnue : elles ne sont PAS assimilées
automatiquement à des lagons. "Remplir" un anneau est une simulation numérique,
jamais une correction ni un fichier de géométrie produit.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union

from comparer_geometries_polynesie_2022_2026 import (
    records_zip, primary_code, digest, ISPF_HASH, GEOPF_HASH
)

SCHEMA = "adlfi.lieux.pf.diagnostic_trous_sources_2022.v1"
ETALAB_REFERENCE = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"

def polygones(g):
    if g is None:
        raise ValueError("Géométrie absente")
    if g.geom_type == "Polygon":
        return [g]
    if g.geom_type == "MultiPolygon":
        return list(g.geoms)
    raise ValueError("Type inattendu : " + g.geom_type)

def audit_anneaux(g):
    """Retourne l'aire des anneaux intérieurs, sans les interpréter comme eau."""
    pieces = polygones(g)
    count = sum(len(p.interiors) for p in pieces)
    area = sum(Polygon(ring).area for p in pieces for ring in p.interiors)
    return count, area / 1_000_000

def silhouette_sans_trous(g):
    """Construction éphémère pour diagnostic uniquement, sans export cartographique."""
    return unary_union([Polygon(p.exterior) for p in polygones(g)])

def iou(a, b):
    u = a.union(b).area
    if not u > 0:
        raise ValueError("Union vide")
    return a.intersection(b).area / u

def qualifier(report, ispf_rows, geopf_rows):
    if report.get("schema") != "adlfi.lieux.pf.comparaison_geometrique_2022_2026.v1":
        raise ValueError("Rapport précédent incorrect")
    sources = report.get("provenance", {})
    if (sources.get("ISPF_SHA256") != ISPF_HASH or
        sources.get("GEO_PF_SHA256") != GEOPF_HASH or
        sources.get("ETALAB_SHA256") != ETALAB_REFERENCE):
        raise ValueError("Empreintes de provenance incompatibles")
    expected = {x["code_COG"]: x for x in report["communes"]}
    if len(expected) != 48:
        raise ValueError("48 communes COG requises")
    a = {}
    for attrs, geo, error in ispf_rows:
        code = primary_code(attrs["IDCom"])
        if error or geo is None or code in a:
            raise ValueError("Géométrie ISPF invalide ou en double : " + code)
        a[code] = geo
    b_parts = defaultdict(list)
    for attrs, geo, error in geopf_rows:
        code = str(attrs["code_com_i"]).strip()
        if code not in expected or error or geo is None:
            raise ValueError("Unité GEO PF inconnue ou invalide : " + code)
        b_parts[code].append(geo)
    b = {code: unary_union(parts) for code, parts in b_parts.items()}
    if set(a) != set(expected) or set(b) != set(expected) or len(geopf_rows) != 179:
        raise ValueError("Couverture des 48 communes et 179 unités incompatible")
    rows = []
    for code in sorted(expected):
        x, y, previous = a[code], b[code], expected[code]
        raw = iou(x, y)
        prior = previous["geopf_vs_ispf"]["intersection_sur_union"]
        if abs(raw - prior) > 0.000002:
            raise ValueError("Reconstitution non reproductible pour " + code)
        n_x, hole_x = audit_anneaux(x)
        n_y, hole_y = audit_anneaux(y)
        xfilled, yfilled = silhouette_sans_trous(x), silhouette_sans_trous(y)
        fill_y = iou(x, yfilled)
        fill_both = iou(xfilled, yfilled)
        gain = fill_y - raw
        # Diagnostic, NON verdict : comparer avec les formes extérieures.
        if raw < 0.75 and gain >= 0.10:
            priority = "INVESTIGUER_ANNEAUX_INTERIEURS"
        elif raw < 0.75:
            priority = "DIVERGENCE_NON_EXPLIQUEE_PAR_ANNEAUX"
        elif raw < 0.95:
            priority = "ECART_MODERE_A_QUALIFIER"
        else:
            priority = "COHERENCE_GEOMETRIQUE_A_VERIFIER"
        rows.append({
            "code_COG": code,
            "libelle_COG": previous["libelle_COG"],
            "effectif_objets_GEO_PF":len(b_parts[code]),
            "anneaux_interieurs_ISPF":n_x,
            "aire_trous_ISPF_km2":round(hole_x,5),
            "anneaux_interieurs_GEO_PF":n_y,
            "aire_trous_GEO_PF_km2":round(hole_y,5),
            "iou_original_ISPF_GEO_PF":round(raw,6),
            "iou_ISPF_vs_GEO_PF_trous_simules_remplis":round(fill_y,6),
            "iou_silhouettes_sans_trous":round(fill_both,6),
            "gain_iou_simulation":round(gain,6),
            "priorite_examen":priority,
            "adoption_geometrie":"AUCUNE",
        })
    priorities = defaultdict(list)
    for row in rows:
        priorities[row["priorite_examen"]].append(row["code_COG"])
    return {
        "schema": SCHEMA,
        "statut": "RECETTE_NON_VALIDANTE_SANS_GEOMETRIE_PUBLIEE",
        "sources": {
            "ISPF_SHA256":ISPF_HASH, "GEO_PF_SHA256":GEOPF_HASH,
            "ETALAB_SOURCE_COMPOSITE_SHA256":ETALAB_REFERENCE,
            "relation_de_provenance":"Le fournisseur Etalab déclare réutiliser GEO PF pour les îles polynésiennes : comparaison non indépendante",
            "source_relation":"https://www.data.gouv.fr/datasets/contours-administratifs",
            "millésimes":"archives territoriales diffusées en 2022 ; validité juridique des limites non documentée ; édition Etalab 2026",
        },
        "limites":"La simulation de remplissage des anneaux intérieurs NE prouve pas qu'il s'agit de lagons ; les polygones simulés ne sont jamais exportés. Aucun changement de limites COG ou de droits territoriaux n'est inféré.",
        "classes_de_recette":{k:{"effectif":len(v),"codes":v} for k,v in sorted(priorities.items())},
        "communes":rows,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("ispf-zip","geopf-zip","comparaison","sortie"):
        p.add_argument("--"+key,type=Path,required=True)
    args=p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Sortie neuve hors docs/ seulement")
    if digest(args.ispf_zip)!=ISPF_HASH or digest(args.geopf_zip)!=GEOPF_HASH:
        raise ValueError("Archives territoriales modifiées")
    precedent=json.loads(args.comparaison.read_text(encoding="utf-8"))
    ispf,crs_ispf=records_zip(args.ispf_zip,"Com.shp")
    geopf,crs_geopf=records_zip(args.geopf_zip,"loc_commune_associee.shp")
    if crs_ispf!="EPSG:4687" or crs_geopf!="EPSG:4687":
        raise ValueError("CRS territorial inattendu")
    out=qualifier(precedent,ispf,geopf)
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("PF_ANNEAUX_DIAGNOSTIC",json.dumps({
        "classes":out["classes_de_recette"],
        "atolls":[x for x in out["communes"] if x["code_COG"] in ("98721","98726","98755","98720","98745")],
        "rapport_sha256":digest(args.sortie),
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
