#!/usr/bin/env python3
"""Audit topologique des 45 arrondissements et des bordures de leurs communes.

Exige Shapely >= 2 et pyproj. Sans contour communal indépendant, ce programme
ne certifie PAS la conformité à l'enveloppe administrative de la commune.

Exemple, à la racine du dépôt :
    python3 scripts/controler_topologie_arrondissements.py
    python3 scripts/controler_topologie_arrondissements.py \
      --communes-reference /chemin/vers/communes_officielles_2026.geojson

Un jeu de référence indépendant doit comporter les codes communaux 75056,
69123 et 13055 dans les propriétés 'code', 'code_insee' ou 'insee_com'.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / 'docs/data/lieux-arrondissements.geojson'
# Sorties locales par défaut : ne jamais modifier docs/data sans validation explicite.
OUT = Path.cwd() / 'audit-topologie-arrondissements'
DERIVED = OUT / 'lieux-communes-plm-reconstituees.geojson'
AUDIT = OUT / 'lieux-arrondissements-topologie-2026.json'
PARENTS = {'Paris': '75056', 'Lyon': '69123', 'Marseille': '13055'}
MILL = 2026


def _load(filename: Path) -> dict:
    source = json.loads(filename.read_text(encoding='utf-8'))
    if source.get('type') != 'FeatureCollection' or not isinstance(source.get('features'), list):
        raise ValueError(f'FeatureCollection GeoJSON requise : {filename}')
    return source


def _geometry_de_reference(path: Path, project):
    from shapely.geometry import shape

    result = {}
    for feature in _load(path)['features']:
        props = feature.get('properties') or {}
        code = str(next((props[k] for k in ('code', 'code_insee', 'insee_com', 'INSEE_COM',
                                           'code_commune', 'code_insee_commune')
                         if props.get(k) is not None), ''))
        if code in PARENTS.values():
            if code in result:
                raise ValueError(f'Doublon de contour communal de référence : {code}')
            geom = project(shape(feature['geometry']))
            if geom.is_empty or not geom.is_valid:
                raise ValueError(f'Contour communal de référence non valide : {code}')
            result[code] = geom
    missing = set(PARENTS.values()) - result.keys()
    if missing:
        raise ValueError('Le GeoJSON de référence ne contient pas les communes : '
                         + ', '.join(sorted(missing)))
    return result


def analyser(source: Path, reference: Path | None = None):
    """Retourne les deux jeux JSON; aucune écriture sur les sources."""
    from shapely.geometry import shape, mapping
    from shapely.ops import transform, unary_union
    from pyproj import Transformer

    project = Transformer.from_crs('EPSG:4326', 'EPSG:2154', always_xy=True).transform
    unproject = Transformer.from_crs('EPSG:2154', 'EPSG:4326', always_xy=True).transform
    raw = _load(source)
    if raw.get('metadata', {}).get('millesime') != MILL:
        raise ValueError('La source ARM doit être du millésime 2026')

    by_city = defaultdict(list)
    codes = set()
    for feature in raw['features']:
        props = feature.get('properties') or {}
        name = props.get('commune')
        code = props.get('code_insee_arm')
        if name not in PARENTS or props.get('code_commune_parente') != PARENTS[name]:
            raise ValueError('Rattachement communal incorrect : ' + str(code))
        if code in codes:
            raise ValueError('ARK/COG en doublon : ' + str(code))
        codes.add(code)
        geom = transform(project, shape(feature['geometry']))
        if not geom.is_valid or geom.is_empty:
            raise ValueError('Géométrie invalide : ' + str(code))
        by_city[name].append((code, geom))
    if len(codes) != 45 or [len(by_city[c]) for c in ('Paris','Lyon','Marseille')] != [20,9,16]:
        raise ValueError('Le lot doit contenir 20 + 9 + 16 arrondissements, sans doublon')

    refs = _geometry_de_reference(reference, lambda g: transform(project, g)) if reference else None
    foot = []
    synth = {}
    for city in ('Paris', 'Lyon', 'Marseille'):
        entries = by_city[city]
        polygons = [geom for _, geom in entries]
        union = unary_union(polygons)
        overlap = []
        for (a, p), (b, q) in combinations(entries, 2):
            delta = p.intersection(q).area
            if delta > 0.001:
                overlap.append((a, b, round(delta, 6)))
        shared = sum(p.boundary.intersection(q.boundary).length
                     for p, q in combinations(polygons, 2))
        perimeter_sum = sum(g.boundary.length for g in polygons)
        remainder = perimeter_sum - 2 * shared - union.boundary.length
        parts = list(union.geoms) if union.geom_type == 'MultiPolygon' else [union]
        holes = sum(len(p.interiors) for p in parts)
        if not union.is_valid or overlap or holes or abs(remainder) > 0.001:
            raise ValueError(f'Topologie des arrondissements incohérente à {city}')
        stats = {
            'code_commune': PARENTS[city],
            'nombre_arrondissements': len(entries),
            'geometrie_union_valide': union.is_valid,
            'chevauchements_surface_significatifs': len(overlap),
            'trous_internes': holes,
            'composantes_spatiales': len(parts),
            'surface_reconstituee_km2': round(union.area / 1e6, 6),
            'longueur_bordure_exterieure_km': round(union.boundary.length / 1000, 6),
            'frontieres_internes_partagees_km': round(shared / 1000, 6),
            'ecart_additivite_bordures_m': round(remainder, 8),
            'composantes_km2': sorted((round(g.area / 1e6, 6) for g in parts), reverse=True),
            'reference_communale_independante': {'statut': 'non_fournie'},
        }
        if refs is not None:
            ref = refs[PARENTS[city]]
            missing = ref.difference(union).area
            excess = union.difference(ref).area
            stats['reference_communale_independante'] = {
                'statut': 'comparee_non_arbitree',
                'surface_reference_km2': round(ref.area / 1e6, 6),
                'surface_absente_de_l_union_m2': round(missing, 2),
                'surface_union_hors_reference_m2': round(excess, 2),
                'difference_symetrique_m2': round(missing + excess, 2),
                'difference_symetrique_pourcentage_de_reference': round(100 * (missing + excess) / ref.area, 5),
                'distance_hausdorff_des_bordures_m': round(union.boundary.hausdorff_distance(ref.boundary), 2),
                'note': 'Un écart peut provenir de généralisations différentes ; il doit être analysé avant validation.'
            }
        synth[city] = stats
        foot.append({
            'type': 'Feature',
            'properties': {
                'code_commune': PARENTS[city],
                'nom': city,
                'millesime': 2026,
                'statut': 'limite_reconstituee_par_union_des_arrondissements',
                'source': 'docs/data/lieux-arrondissements.geojson',
                'validation_limite_communale_independante': 'non_verifiee' if refs is None else 'a_analyser',
            },
            'geometry': mapping(transform(unproject, union)),
        })
    geo = {
        'type': 'FeatureCollection',
        'metadata': {
            'millesime': 2026,
            'source': 'Union topologique des 45 arrondissements du même jeu data.gouv.fr 2026, 100 m',
            'nature': 'geometrie_derivee',
            'validation_independante': 'non_effectuee' if refs is None else 'comparaison_a_analyser',
            'licence': 'ODbL-1.0',
            'attribution': raw.get('metadata', {}).get('attribution'),
        },
        'features': foot,
    }
    report = {
        'schema_version': '0.1.0',
        'statut': 'audit_topologique_non_validation_de_l_enveloppe_officielle',
        'millesime': MILL,
        'precision': '100m',
        'metrique': 'Lambert-93 (EPSG:2154), longueurs en m, surfaces en m2',
        'source': str(source.name),
        'reference_independante': str(reference) if reference else None,
        'communes': synth,
    }
    return geo, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arm-geojson', type=Path, default=ARM)
    parser.add_argument('--communes-reference', type=Path, default=None,
                        help='Fichier GeoJSON communal INDEPENDANT contenant 75056, 69123 et 13055')
    parser.add_argument('--output-geojson', type=Path, default=DERIVED)
    parser.add_argument('--output-report', type=Path, default=AUDIT)
    args = parser.parse_args()
    if any(p.resolve() == args.arm_geojson.resolve() or
           (args.communes_reference and p.resolve() == args.communes_reference.resolve())
           for p in (args.output_geojson, args.output_report)):
        parser.error('Ne jamais écraser une source avec les résultats')
    geo, report = analyser(args.arm_geojson, args.communes_reference)
    for path, data in ((args.output_geojson, geo), (args.output_report, report)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for city, stat in report['communes'].items():
        print(f"{city} : {stat['nombre_arrondissements']} arr. ; union valide ; "
              f"{stat['composantes_spatiales']} composantes ; "
              f"frontières intérieures {stat['frontieres_internes_partagees_km']} km")
    print('Contrôle externe : ' + ('comparaison à analyser' if args.communes_reference else 'NON EFFECTUÉ'))
    print('Rapport : ' + str(args.output_report))


if __name__ == '__main__':
    main()
