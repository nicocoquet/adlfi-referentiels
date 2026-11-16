#!/usr/bin/env python3
"""Reconstruction expérimentale de Tahaa depuis huit communes associées de 2022.

Cette union géométrique ne constitue NI un contour officiel de commune NI une
preuve de limites administratives 2026. Aucun GeoJSON de géométrie produit.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import zipfile
from pathlib import Path

try:
    from pyproj import CRS, Transformer
    from shapely import make_valid
    from shapely.geometry import shape, mapping
    from shapely.ops import transform, unary_union
    COMPARAISON_DISPONIBLE = True
except ImportError:
    CRS = Transformer = make_valid = shape = mapping = transform = unary_union = None
    COMPARAISON_DISPONIBLE = False

from comparer_sources_geometrie_outremer import stats_comparaison
from inventorier_source_polynesie_2022 import normaliser

SOURCE_SHA = "29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b"
NATIONAL_SHA = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
CODES_ASSOCIES = {str(x) for x in range(451, 459)}


def source_shapefile(archive: Path):
    import shapefile
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Empreinte archive polynésienne 2022 inattendue")
    with zipfile.ZipFile(archive) as z:
        names = {name.lower(): name for name in z.namelist()}
        base = next((x[:-4] for x in names if x.endswith("loc_commune_associee.shp")), None)
        if not base or any(base + ext not in names for ext in (".shp",".shx",".dbf",".prj")):
            raise ValueError("Shapefile Tahaa incomplet")
        files = {ext: z.read(names[base + ext]) for ext in (".shp",".shx",".dbf",".prj")}
    crs = CRS.from_wkt(files[".prj"].decode("utf-8",errors="replace"))
    reader = shapefile.Reader(
        shp=io.BytesIO(files[".shp"]), shx=io.BytesIO(files[".shx"]),
        dbf=io.BytesIO(files[".dbf"]),
        encoding="cp1252", encodingErrors="replace",
    )
    props_names = [f[0] for f in reader.fields[1:]]
    found = []
    for sr in reader.iterShapeRecords():
        props = dict(zip(props_names,sr.record))
        if str(props.get("code_com_i","")).strip() != "98745":
            continue
        if normaliser(props.get("nom","")) != "tahaa":
            raise ValueError("Code 98745 rattaché à un nom autre que Tahaa")
        found.append((props, sr.shape.__geo_interface__))
    codes = {str(p.get("code_com_1","")).strip() for p,_ in found}
    if len(found) != 8 or codes != CODES_ASSOCIES:
        raise ValueError("Huit unités associées de Tahaa non exhaustives")
    return crs, found


def examiner_source(archive: Path):
    if not COMPARAISON_DISPONIBLE:
        raise RuntimeError("Shapely et pyproj nécessaires au contrôle géométrique")
    crs, found = source_shapefile(archive)
    transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    geoms = []
    diagnostics = []
    for props, raw in found:
        initial = shape(raw)
        if initial.is_empty:
            raise ValueError("Commune associée vide : "+str(props.get("nom_commun")))
        copied = initial if initial.is_valid else make_valid(initial)
        if copied.geom_type not in ("Polygon","MultiPolygon") or not copied.is_valid:
            raise ValueError("Diagnostic non polygonal de : "+str(props.get("nom_commun")))
        transformed = transform(transformer.transform, copied)
        geoms.append(transformed)
        diagnostics.append({
            "nom_associe": str(props.get("nom_commun")),
            "code_associe": str(props.get("code_com_1")),
            "nom_commune": str(props.get("nom")),
            "code_insee_declared_source": str(props.get("code_com_i")),
            "forme_originale_valide": bool(initial.is_valid),
            "reparation_sur_copie": not initial.is_valid,
            "type_original": initial.geom_type,
        })
    composed = unary_union(geoms)
    if not composed.is_valid or composed.is_empty \
       or composed.geom_type not in ("Polygon","MultiPolygon"):
        raise ValueError("Union des huit subdivisions topologiquement invalide")
    return composed, {
        "systeme_source": crs.to_string(),
        "systeme_cible_comparaison": "EPSG:4326",
        "reconstruction_sur_copies": True,
        "nb_subdivisions": len(found),
        "subdivisions": sorted(diagnostics,key=lambda x:x["code_associe"]),
    }


def construire(archive: Path, national: Path, territorial: Path | None = None) -> dict:
    if hashlib.sha256(national.read_bytes()).hexdigest() != NATIONAL_SHA:
        raise ValueError("Empreinte GeoJSON national 2026 inattendue")
    union, info = examiner_source(archive)
    with gzip.open(national, "rt", encoding="utf-8") as stream:
        features = json.load(stream).get("features",[])
    target = [f for f in features if str(f.get("properties",{}).get("code"))=="98745"]
    if len(target)!=1:
        raise ValueError("Polygone national 98745 non unique")
    metrics = stats_comparaison(mapping(union), target[0]["geometry"])
    comparaison_territoriale = None
    if territorial is not None:
        snapshot = json.loads(territorial.read_text(encoding="utf-8"))
        if snapshot.get("schema") != "adlfi.lieux.sources.territoriales.v1":
            raise ValueError("Instantané Te Fenua non conforme")
        source = snapshot.get("sources", {}).get("98745", {})
        props = source.get("proprietes", {})
        if (normaliser(props.get("com_nom", "")) != "tahaa"
            or props.get("com_id") != 45
            or not source.get("geojson", {}).get("geometry")):
            raise ValueError("Référent Tahaa de la source Te Fenua non attesté")
        comparaison_territoriale = {
            "code_cog_presume": "98745",
            "code_source": props["com_id"],
            "empreinte_geojson": source.get("geometrie_sha256", ""),
            "statut": "COMPARAISON_NON_VALIDANTE",
            "mesures": stats_comparaison(
                mapping(union), source["geojson"]["geometry"]
            ),
        }
    return {
        "schema": "adlfi.lieux.tahaa.comparaison_subdivisions2022.v1",
        "statut": "RECETTE_NON_VALIDANTE_NON_PUBLIEE",
        "reconstruction": info,
        "comparaison_national_2026": metrics,
        "comparaison_tefenua": comparaison_territoriale,
        "source_2022_sha256": SOURCE_SHA,
        "national_2026_sha256": NATIONAL_SHA,
        "avertissements": [
            "Union géométrique de huit communes associées, non une frontière officielle certifiée.",
            "Source 2022 et source nationale 2026 de dates distinctes.",
            "Aucune géométrie de reconstruction n'est exportée.",
            "RGPF transformé en WGS84 pour les comparaisons (pas de rétroprojection temporelle).",
        ],
        "alignements_pactols_crees": 0,
        "geometries_publiees": 0,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--national",type=Path,required=True)
    p.add_argument("--sortie",type=Path,required=True)
    p.add_argument("--sources-territoriales",type=Path)
    args=p.parse_args()
    if "docs" in args.sortie.resolve().parts:
        raise ValueError("Dossier docs interdit pour un résultat de recette")
    r=construire(args.archive,args.national,args.sources_territoriales)
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(r,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()
