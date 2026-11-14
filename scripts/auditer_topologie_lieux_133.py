#!/usr/bin/env python3
"""Audit non destructif de 133 communes COG 2026 à 100m contre leur source nationale.

Le contrôle ne déduit pas des limites historiques de contours actuels.
Les écarts avec le fond publié PACA 1000m sont des écarts de représentation.
Dépendances explicites: shapely>=2, pyproj>=3.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform
from shapely.strtree import STRtree
from shapely.validation import explain_validity
from pyproj import Transformer

SHA_2026 = '4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778'
TRANSFORM = Transformer.from_crs('EPSG:4326', 'EPSG:2154', always_xy=True).transform

def fichier_sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as file:
        for part in iter(lambda: file.read(1 << 20), b''):
            h.update(part)
    return h.hexdigest()

def geojson(path):
    with (gzip.open(path,'rt',encoding='utf-8') if str(path).endswith('.gz') else
          path.open(encoding='utf-8')) as f:
        obj = json.load(f)
    if obj.get('type') != 'FeatureCollection' or not isinstance(obj.get('features'),list):
        raise ValueError('FeatureCollection attendue: '+str(path))
    return obj

def geometries(doc, code_field='code'):
    lookup = {}
    for feature in doc['features']:
        if feature.get('type') != 'Feature':
            raise ValueError('Feature attendu')
        code = str(feature.get('properties',{}).get(code_field,''))
        if not code or code in lookup:
            raise ValueError('Code absent ou dupliqué : '+code)
        g = feature.get('geometry')
        if not g or g.get('type') not in ('Polygon','MultiPolygon'):
            raise ValueError('Polygone attendu pour '+code)
        geom = transform(TRANSFORM,shape(g))
        if geom.is_empty:
            raise ValueError('Polygone vide '+code)
        lookup[code] = (geom, feature.get('properties',{}))
    return lookup

def mesurer(carte_133, source, ancien, sortie, sha_attendu=SHA_2026):
    for p in (carte_133,source,ancien):
        if not p.is_file():
            raise FileNotFoundError(p)
    source_sha = fichier_sha256(source)
    if sha_attendu and source_sha.lower() != sha_attendu.lower():
        raise ValueError('SHA source 2026 inattendu : '+source_sha)
    doc = geojson(carte_133)
    meta = doc.get('metadata',{})
    if meta.get('etat') != 'recette_non_publiee' or meta.get('millesime') != 2026 or meta.get('generalisation') != '100m':
        raise ValueError('Contrat de recette 2026 / 100m non respecté')
    if meta.get('source_sha256') != source_sha:
        raise ValueError('La carte 133 ne dérive pas de la même source que le témoin national')
    selected = geometries(doc)
    if len(selected) != 133:
        raise ValueError('Il faut exactement 133 géométries sélectionnées')
    full = geometries(geojson(source))
    old = geometries(geojson(ancien))
    if len(old)!=103:
        raise ValueError('103 géométries attendues dans le pilote actuel')
    if not set(selected) <= set(full):
        raise ValueError('Codes sélectionnés absents de la source 2026 : '+str(sorted(set(selected)-set(full))))
    if not set(old) <= set(selected):
        raise ValueError('Codes 103 PACA manquants : '+str(sorted(set(old)-set(selected))))
    source_codes=list(full)
    source_shapes=[full[c][0] for c in source_codes]
    tree=STRtree(source_shapes)
    rows=[]
    invalid=[]; source_mismatch=[]; overlaps=[]; adjacencies=[]; shifts=[]
    for code in sorted(selected):
        geom,props=selected[code]
        org,orgprops=full[code]
        # Géométrie issue directement du même GeoJSON, sans traitement géométrique : égalité exacte attendue.
        if not geom.equals_exact(org, tolerance=1e-8):
            source_mismatch.append(code)
        if not geom.is_valid:
            invalid.append({'code':code,'raison':explain_validity(geom)})
        # Sur chaque géométrie sélectionnée, comparer aux objets limitrophes du fichier source entier.
        neighbors=[]; shared=0.0; overlap=0.0
        for idx in tree.query(geom):
            ncode=source_codes[int(idx)]
            if ncode == code:continue
            ng=source_shapes[int(idx)]
            if not geom.intersects(ng):continue
            try:
                intersect = geom.intersection(ng)
                a = intersect.area
                b = geom.boundary.intersection(ng.boundary).length
            except Exception as ex:
                invalid.append({'code':code,'avec':ncode,'raison':type(ex).__name__+': '+str(ex)[:160]})
                continue
            if a>1:
                overlaps.append({'code':code,'voisin':ncode,'surface_m2':round(a,2), 'dans_selection':ncode in selected})
                overlap+=a
            if b>0.1:
                neighbors.append(ncode)
                shared+=b
                if ncode in selected and code < ncode:
                    adjacencies.append({'code':code,'code_voisin':ncode,'frontiere_commune_m':round(b,2)})
        record={'code':code,'nom':props.get('nom',''),
                'statut_lien':props.get('statut_lien_pactols_cog'),
                'valide':geom.is_valid,'raison_invalide':explain_validity(geom) if not geom.is_valid else None,
                'surface_km2':round(geom.area/1e6,5),
                'nombre_composantes':len(geom.geoms) if geom.geom_type=='MultiPolygon' else 1,
                'voisins_dans_source_nationale':len(set(neighbors)),
                'longueur_frontieres_communes_m':round(shared,2),
                'surface_chevauchements_voisins_m2':round(overlap,2)}
        if code in old:
            prev=old[code][0]
            if prev.is_valid and geom.is_valid:
                delta=geom.symmetric_difference(prev).area
                r=delta/geom.area if geom.area else None
                record['ecart_1000m_100m_km2']=round(delta/1e6,5)
                record['ecart_relatif_surface_geometrie_100m_pct']=round(r*100,3)
                shifts.append({'code':code,'nom':props.get('nom',''),'difference_symetrique_km2':round(delta/1e6,5),'pct_surface_100m':round(r*100,3)})
            else:
                record['comparaison_1000m_non_mesurable']='geometrie_invalide'
        rows.append(record)
    repartition=Counter(r['statut_lien'] for r in rows)
    significant=[x for x in overlaps if x['surface_m2']>100]
    report={'schema_version':'0.1.0','statut':'audit_topologique_non_validant',
            'nombre_contours_2026':len(selected),'nombre_contours_pilote_1000m':len(old),
            'repartition_statuts_lien':dict(sorted(repartition.items())),
            'origine':{'source_2026':'communes-100m.geojson.gz','sha256_source_2026':source_sha,
                       'source_pilote_geojson':str(ancien.name),'sha256_pilote_geojson':fichier_sha256(ancien),
                       'carte_133':str(carte_133.name),'sha256_carte_133':fichier_sha256(carte_133)},
            'nombre_geometries_invalides':len([x for x in invalid if 'avec' not in x]),
            'nombre_erreurs_intersection':len([x for x in invalid if 'avec' in x]),
            'nombre_contours_non_identiques_source':len(source_mismatch),
            'nombre_chevauchements_voisins_superieurs_1m2':len(overlaps),
            'nombre_chevauchements_voisins_superieurs_100m2':len(significant),
            'nombre_paires_contigues_dans_133':len(adjacencies),
            'nombre_contours_pilote_comparables':len(shifts),
            'ecarts_1000m_100m_plus_importants':sorted(shifts,key=lambda x:-x['difference_symetrique_km2'])[:15],
            'reserves':['Les voisins sont recherchés dans la source 2026 entière, non seulement dans les 133 contours.',
                        'Les chevauchements de simplification doivent être qualifiés ; pas de correction automatique.',
                        'Un test de non-chevauchement ne démontre pas l’absence de lacunes sans enveloppe indépendante.',
                        'La différence symétrique avec le pilote 1000m mesure une généralisation, non une évolution historique.',
                        'Pas de validation Pactols–COG ni de géométrie historique.']}
    sortie.mkdir(parents=True,exist_ok=True)
    (sortie/'rapport-topologie-133.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (sortie/'details-topologie-133.json').write_text(json.dumps({'contours':rows,'anomalies':invalid,'differences_source':source_mismatch,'chevauchements':overlaps,'adjacences_133':adjacencies},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--carte',type=Path,required=True)
    a.add_argument('--source-communes',type=Path,required=True)
    a.add_argument('--pilote-1000m',type=Path,required=True)
    a.add_argument('--sortie',type=Path,required=True)
    a.add_argument('--sha256-source',default=SHA_2026)
    args=a.parse_args()
    print(json.dumps(mesurer(args.carte,args.source_communes,args.pilote_1000m,args.sortie,args.sha256_source),ensure_ascii=False,indent=2))
if __name__=='__main__':main()

