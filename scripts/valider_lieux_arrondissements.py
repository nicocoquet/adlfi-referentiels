#!/usr/bin/env python3
"""Vérifie le contrat de publication du lot COG 2026 des 45 arrondissements municipaux.

Contrôles sans dépendance externe (pour GitHub Actions). Ne prétend pas remplacer
le contrôle topologique externe effectué en recette avec Shapely/PROJ.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'docs/data/lieux-arrondissements.json'
GEO = BASE / 'docs/data/lieux-arrondissements.geojson'

PARENTS = {
    'Paris': ('75056', '26678/pcrtKWS6It1qMw', '751', 1, 20),
    'Lyon': ('69123', '26678/pcrtykDpsdYKiV', '693', 81, 89),
    'Marseille': ('13055', '26678/pcrtkSBSb8k4Ad', '132', 1, 16),
}
BOITES = {
    'Paris': (2.0, 48.7, 2.6, 49.0),
    'Lyon': (4.5, 45.5, 5.2, 46.0),
    'Marseille': (4.9, 43.1, 5.7, 43.6),
}


def verifier(data, geo):
    if data.get('schema_version') != '0.1.0' or data.get('type_entite') != 'arrondissement_municipal':
        raise ValueError('Schéma d’autorités inconnu')
    if data.get('millesime_cog') != 2026 or data.get('statut_publication') != 'recette_non_publiee':
        raise ValueError('Millésime ou statut incohérent')
    if geo.get('type') != 'FeatureCollection' or geo.get('metadata', {}).get('millesime') != 2026:
        raise ValueError('GeoJSON ou millésime incohérent')
    if geo.get('metadata', {}).get('licence') != 'ODbL-1.0':
        raise ValueError('Licence géographique manquante')
    if geo.get('metadata', {}).get('sha256_source') != data['provenance']['geometries']['sha256_source']:
        raise ValueError('Discordance de provenance des géométries')

    autorites = data.get('autorites', [])
    features = geo.get('features', [])
    if len(autorites) != 45 or len(features) != 45:
        raise ValueError('45 autorités et 45 géométries requises')
    by_code = {}
    for a in autorites:
        code = a['code_insee']
        if code in by_code or a['typecom'] != 'ARM':
            raise ValueError('Code ARM dupliqué ou TYPECOM incorrect')
        parent = a['commune_parente']
        ville = parent['nom']
        if ville not in PARENTS:
            raise ValueError('Commune parente inconnue')
        parent_code, ark, prefix, first, last = PARENTS[ville]
        if parent['code_insee'] != parent_code or parent['ark_pactols'] != ark:
            raise ValueError('Rattachement COG/Pactols incohérent')
        n = a['numero']
        if not isinstance(n, int) or not first <= (n if ville != 'Lyon' else n+80) <= last:
            raise ValueError('Numéro d’arrondissement incorrect')
        wanted_code = prefix + f'{n if ville != "Lyon" else 80+n:02d}'
        if wanted_code != code:
            raise ValueError('Code INSEE non conforme au numéro')
        ordinal = '1er' if n == 1 else f'{n}e'
        if a['libelle'] != f'{ville} ({ordinal})':
            raise ValueError('Libellé de recherche incohérent')
        if a['identification']['millesime'] != 2026 or a['identification']['statut'] != 'verifie_cog_2026':
            raise ValueError('Autorité non vérifiée sur le COG')
        by_code[code] = a
    if len(by_code) != 45:
        raise ValueError('Codes non uniques')
    expected = {f'751{i:02d}' for i in range(1,21)} | {f'693{i:02d}' for i in range(81,90)} | {f'132{i:02d}' for i in range(1,17)}
    if set(by_code) != expected:
        raise ValueError('Liste COG incomplète')
    observed = sum(a['attestation_adlfi']['observe_dans_titre'] is True for a in autorites)
    if observed != 32 or data.get('totaux') != {
        'autorites':45, 'attestees_adlfi':32, 'non_attestees':13, 'geometries':45,
    }:
        raise ValueError('Effectifs d’attestations incohérents')

    seen = set()
    for feature in features:
        if feature.get('type') != 'Feature':
            raise ValueError('Entité géographique invalide')
        props = feature.get('properties', {})
        code = props.get('code_insee_arm')
        if code not in by_code or code in seen:
            raise ValueError('Code géométrique absent ou dupliqué')
        seen.add(code)
        a=by_code[code]
        expected_props={
          'typecom':'ARM','libelle':a['libelle_cog'],
          'commune':a['commune_parente']['nom'],
          'code_commune_parente':a['commune_parente']['code_insee'],
          'ark_pactols_commune':a['commune_parente']['ark_pactols'],
          'numero_arrondissement':a['numero'],
          'millesime_cog':2026,
        }
        if any(props.get(key)!=value for key,value in expected_props.items()):
            raise ValueError('Propriétés GeoJSON discordantes : '+str(code))
        geometry=feature.get('geometry') or {}
        kind=geometry.get('type')
        coords=geometry.get('coordinates')
        if kind not in ('Polygon','MultiPolygon') or not isinstance(coords,list) or not coords:
            raise ValueError('Géométrie Polygon/MultiPolygon absente')
        polygons=[coords] if kind=='Polygon' else coords
        region=BOITES[a['commune_parente']['nom']]
        for polygon in polygons:
            if not isinstance(polygon,list) or not polygon:
                raise ValueError('Polygone vide')
            for ring in polygon:
                if not isinstance(ring,list) or len(ring)<4 or ring[0]!=ring[-1]:
                    raise ValueError('Anneau non fermé ou dégénéré')
                for pt in ring:
                    if (not isinstance(pt,list) or len(pt)!=2 or
                        not all(isinstance(v,(int,float)) and math.isfinite(v) for v in pt) or
                        not (region[0] <= pt[0] <= region[2] and region[1] <= pt[1] <= region[3])):
                        raise ValueError('Coordonnées géographiques hors zone '+str(code))
    return {'autorites':len(by_code),'geometries':len(seen),'attestees_adlfi':observed,'non_attestees':45-observed}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--autorites',type=Path,default=DATA)
    p.add_argument('--geojson',type=Path,default=GEO)
    args=p.parse_args()
    result=verifier(json.loads(args.autorites.read_text(encoding='utf-8')),json.loads(args.geojson.read_text(encoding='utf-8')))
    print('ARRONDISSEMENTS MUNICIPAUX OK : '+json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
