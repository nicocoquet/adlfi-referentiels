#!/usr/bin/env python3
"""Construire une carte SVG autonome de recette : régions/départements métropolitains 2015/2016.

Les limites GEOFLA sont simplifiées en EPSG:2154 à 100 m pour affichage uniquement ;
les sources géographiques originales restent disponibles séparément dans la CI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from auditer_cog_regions_millesimes import HASHES, csv_lire, sha256
from construire_regions_metropole_geofla_2015_2016 import (
    IGN_EDITION, charger_departements
)

LIMITES = {2015: (22, 96), 2016: (13, 96)}
SIMPLIFICATION_METRES = 100
MARQUEUR = '__LIEUX_MULTIECHELON_INLINE_DATA__'


def verifier_regions(geo: dict, year: int, source: dict) -> list[dict]:
    from shapely.geometry import shape, mapping
    from shapely.ops import transform
    from pyproj import Transformer

    if geo.get('type') != 'FeatureCollection' or len(geo.get('features', [])) != LIMITES[year][0]:
        raise ValueError('Couche régionale manquante ou incomplète : ' + str(year))
    provenance = geo.get('provenance', {})
    if not (str(year) in provenance.get('edition', '') and
            provenance.get('producteur') == 'IGN' and
            provenance.get('geometries_2026_utilisees') is False):
        raise ValueError('Provenance régionale incohérente')
    vers_l93 = Transformer.from_crs(4326, 2154, always_xy=True).transform
    vers_wgs = Transformer.from_crs(2154, 4326, always_xy=True).transform
    result = []
    codes = set()
    for feature in geo['features']:
        props = feature['properties']
        code = str(props['code_region'])
        if code in codes or code not in source or props['nom_COG'] != source[code]:
            raise ValueError('Code ou nom régional incompatible : ' + code)
        if (props.get('millesime_COG') != year or
            props.get('date_edition_IGN') != IGN_EDITION[year] or
            props.get('contour_regional_natif') is not False or
            props.get('alignement_Pactols_valide') is not False):
            raise ValueError('Qualification du contour régional incohérente : ' + code)
        codes.add(code)
        geom = transform(vers_l93, shape(feature['geometry']))
        simplifie = geom.simplify(SIMPLIFICATION_METRES, preserve_topology=True)
        if simplifie.is_empty or not simplifie.is_valid:
            raise ValueError('Simplification régionale invalide : ' + code)
        result.append({'type': 'Feature', 'geometry': mapping(transform(vers_wgs, simplifie)),
                       'properties': {
                           'code': code, 'nom': source[code], 'niveau': 'region', 'annee': year,
                           'departements': sorted(props['code_departement_sources']),
                           'code_region_parent': None, 'nom_region_parent': None,
                           'source_geometrie': 'union des départements IGN GEOFLA',
                           'contour_regional_natif': False, 'pactols_valide': False,
                       }})
    return sorted(result, key=lambda f: f['properties']['code'])


def preparer(shp2015: Path, shp2016: Path, regions2015: Path, regions2016: Path,
             dep2015: Path, dep2016: Path, reg2015: Path, reg2016: Path) -> dict:
    from shapely.geometry import mapping
    from shapely.ops import transform
    from pyproj import Transformer

    source_cog = {}
    for year, dep_path, reg_path in ((2015, dep2015, reg2015), (2016, dep2016, reg2016)):
        for kind, path in (('dep', dep_path), ('reg', reg_path)):
            if sha256(path) != HASHES[f'{kind}{year}']:
                raise ValueError(f'Empreinte COG invalide : {kind}{year}')
        dep_rows = csv_lire(dep_path, 'dep', year)
        reg_rows = csv_lire(reg_path, 'reg', year)
        if len(dep_rows) != 101 or len(reg_rows) != (27 if year == 2015 else 18):
            raise ValueError('Nombre de lignes COG erroné')
        source_cog[year] = (
            {r['DEP']: r for r in dep_rows},
            {r['REGION']: r['NCCENR'] for r in reg_rows},
        )

    layers = {}
    vers_wgs = Transformer.from_crs(2154, 4326, always_xy=True).transform
    for year, shp, regions_path in ((2015, shp2015, regions2015), (2016, shp2016, regions2016)):
        dep_idx, reg_idx = source_cog[year]
        originaux = charger_departements(shp, year)
        if len(originaux) != 96:
            raise ValueError('96 départements requis')
        geo = json.loads(Path(regions_path).read_text(encoding='utf8'))
        regions = verifier_regions(geo, year, reg_idx)
        departments = []
        for code, (region, geom) in sorted(originaux.items()):
            if code not in dep_idx or dep_idx[code]['REGION'] != region or region not in reg_idx:
                raise ValueError(f'Rattachement IGN/COG erroné pour {year}/{code}')
            simplifie = geom.simplify(SIMPLIFICATION_METRES, preserve_topology=True)
            if simplifie.is_empty or not simplifie.is_valid:
                raise ValueError(f'Simplification départementale invalide {year}/{code}')
            departments.append({
                'type': 'Feature', 'geometry': mapping(transform(vers_wgs, simplifie)),
                'properties': {
                    'code': code, 'nom': dep_idx[code]['NCCENR'],
                    'niveau': 'departement', 'annee': year,
                    'departements': [], 'code_region_parent': region,
                    'nom_region_parent': reg_idx[region],
                    'source_geometrie': 'contour départemental IGN GEOFLA',
                    'contour_regional_natif': False, 'pactols_valide': False,
                },
            })
        layers[str(year)] = {'region': regions, 'departement': departments}
    if (len(layers['2015']['region']),len(layers['2016']['region']),
        len(layers['2015']['departement']),len(layers['2016']['departement'])) != (22,13,96,96):
        raise ValueError('Cardinalités historiques erronées')
    return {
        'schema': 'adlfi.lieux.interface_multiechelon_recette.v1',
        'statut': 'RECETTE_HORS_PAGES_NON_VALIDANTE',
        'simplification_affichage_metres': SIMPLIFICATION_METRES,
        'source_COG': {str(y): f'https://www.insee.fr/fr/information/{"2560698" if y==2015 else "2114819"}' for y in (2015,2016)},
        'edition_IGN': {str(y): IGN_EDITION[y] for y in (2015,2016)},
        'sources_COG_SHA256': {f'{kind}{year}': HASHES[f'{kind}{year}'] for kind in ('dep','reg') for year in (2015,2016)},
        'layers': layers,
        'alignements_Pactols_generes': 0,
        'aucune_geometrie_2026_retroprojetee': True,
    }


def construire(modele: Path, sortie: Path, donnees: dict) -> dict:
    dest = Path(sortie)
    if 'docs' in dest.resolve().parts:
        raise ValueError('Recette interdite sous docs/')
    template = Path(modele).read_text(encoding='utf8')
    if template.count(MARQUEUR) != 1:
        raise ValueError('Modèle HTML incomplet')
    if donnees.get('alignements_Pactols_generes') != 0:
        raise ValueError('Ne pas publier des alignements Pactols inférés')
    if donnees.get('aucune_geometrie_2026_retroprojetee') is not True:
        raise ValueError('La rétroprojection est interdite')
    for year, counts in ((2015,(22,96)),(2016,(13,96))):
        couche=donnees.get('layers',{}).get(str(year),{})
        if (len(couche.get('region',[])),len(couche.get('departement',[]))) != counts:
            raise ValueError('Nombre de contours inattendu')
    payload = json.dumps(donnees, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':')).replace('<', '\\u003c')
    html = template.replace(MARQUEUR, payload)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding='utf8')
    resume={
        'schema': 'adlfi.lieux.interface_multiechelon_recette.rapport.v1',
        'fichier': dest.name,
        'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
        'taille_octets': dest.stat().st_size,
        'regions_2015':22,'regions_2016':13,
        'departements_2015':96,'departements_2016':96,
        'simplification_affichage_metres':SIMPLIFICATION_METRES,
        'publication_docs':False, 'alignements_Pactols_generes':0,
        'couverture': 'France métropolitaine seulement, COG 2015 et 2016',
    }
    (dest.parent / 'rapport-interface-multiechelon-2015-2016.json').write_text(
        json.dumps(resume,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return resume


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for param in ('modele', 'shp2015','shp2016','regions2015','regions2016',
                  'dep2015','dep2016','reg2015','reg2016','sortie'):
        parser.add_argument('--'+param, type=Path, required=True)
    args = vars(parser.parse_args())
    modele,sortie = args.pop('modele'),args.pop('sortie')
    report=construire(modele,sortie,preparer(**args))
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))