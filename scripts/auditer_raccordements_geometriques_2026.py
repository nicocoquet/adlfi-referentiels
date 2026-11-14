#!/usr/bin/env python3
"""Prépare une recette de contours COG 2026 pour les couples Pactols–COG proposés.

Source : contours-administratifs data.gouv.fr, communes-100m.geojson.gz
(ou GeoJSON non compressé). Réutilisation ODbL avec attribution.

Un contour trouvé en 2026 n'est PAS une géométrie historique, et une
correspondance Pactols–COG reste NON VALIDÉE même si le code est présent.
"""
from __future__ import annotations
import argparse
import collections
import csv
import gzip
import hashlib
import json
import re
import unicodedata
from pathlib import Path

SOURCE_URL='https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-100m.geojson.gz'
ATTRIBUTION='Contours administratifs — data.gouv.fr / IGN et contributeurs OpenStreetMap'
COLS={'n','libelle_pactols','ark_pactols','departement_pactols',
      'code_cog_2026_candidat','statut_alignement_pactols_cog'}
CODE=re.compile(r'(?:\d{5}|2[AB]\d{3})$')
ARK=re.compile(r'26678/[A-Za-z0-9]+$')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def norm(t):
    s=unicodedata.normalize('NFKD',(t or '').replace('œ','oe').replace('Œ','Oe'))
    s=''.join(x for x in s.casefold() if unicodedata.category(x)!='Mn')
    return re.sub(r'[^a-z0-9]+',' ',s).strip()


def lire_lots(paths):
    rows=[]; seen=set();codes=set()
    if not paths:raise ValueError('Aucun sous-lot fourni')
    for path in paths:
        with path.open(encoding='utf-8-sig',newline='') as f:
            rdr=csv.DictReader(f,delimiter=';')
            if not COLS<=set(rdr.fieldnames or []):raise ValueError(f'En-têtes manquants : {path}')
            for x in rdr:
                ark=x['ark_pactols'];code=x['code_cog_2026_candidat']
                if not ARK.fullmatch(ark) or not CODE.fullmatch(code):
                    raise ValueError(f'ARK ou code invalide: {ark} / {code}')
                if x['statut_alignement_pactols_cog'] != 'non_valide':
                    raise ValueError('Ne pas ingérer un lot dont le statut de validation est différent de non_valide')
                if ark in seen:raise ValueError('ARK dupliqué entre sous-lots: '+ark)
                seen.add(ark);codes.add(code)
                rows.append({k:x.get(k,'') for k in x})
    return sorted(rows,key=lambda r:(int(r['n']),r['ark_pactols']))


def lire_geo(path):
    with (gzip.open(path,'rt',encoding='utf-8') if path.name.endswith('.gz') else path.open(encoding='utf-8')) as f:
        data=json.load(f)
    if data.get('type')!='FeatureCollection' or not isinstance(data.get('features'),list):
        raise ValueError('GeoJSON attendu : FeatureCollection')
    return data


def construire(lots,geosource,sortie,millesime=2026,generalisation='100m'):
    if millesime!=2026 or generalisation!='100m':
        raise ValueError('Contrat de recette verrouillé sur 2026 / 100m')
    paths=list(lots)
    for p in paths+[geosource]:
        if not p.is_file():raise FileNotFoundError(p)
    dest_geo=sortie/'contours-candidats-cog2026.geojson'
    dest_json=sortie/'raccordements-candidats-cog2026.json'
    dest_report=sortie/'rapport-raccordement-geometries-2026.json'
    if {x.resolve() for x in [dest_geo,dest_json,dest_report]} & {p.resolve() for p in paths+[geosource]}:
        raise ValueError('Une cible écraserait une source')
    rows=lire_lots(paths); codes={r['code_cog_2026_candidat'] for r in rows}
    source=lire_geo(geosource)
    features={}; duplicates=set()
    for feature in source['features']:
        code=str((feature.get('properties') or {}).get('code',''))
        if code not in codes:continue
        if code in features:duplicates.add(code)
        if feature.get('type')!='Feature' or (feature.get('geometry') or {}).get('type') not in ('Polygon','MultiPolygon'):
            raise ValueError('Géométrie communale non polygonale '+code)
        features[code]=feature
    if duplicates:raise ValueError('Codes dupliqués dans le GeoJSON: '+','.join(sorted(duplicates)))
    sha_src=sha(geosource)
    provenance={'producteur':'data.gouv.fr','source_url':SOURCE_URL,
                'fichier_geometrique_source':geosource.name,'sha256_fichier_source':sha_src,
                'millesime':millesime,'generalisation':generalisation,'licence':'ODbL-1.0',
                'attribution':ATTRIBUTION,
                'note':'Contours administratifs contemporains, sans prétention de délimitation historique.'}
    items=[]; exported=[]; statuses=collections.Counter();unique=set()
    for row in rows:
        code=row['code_cog_2026_candidat'];feat=features.get(code)
        if feat:
            official=(feat['properties'] or {}).get('nom','')
            status='code_present_nom_concordant' if norm(row['libelle_pactols'])==norm(official) else 'code_present_nom_a_verifier'
            if code not in unique:
                # Conserver le Feature original seulement en recette, par identifiant COG.
                exported.append(feat);unique.add(code)
        else:
            official='';status='code_sans_contour_dans_source'
        statuses[status]+=1
        items.append({
          'ark_pactols':row['ark_pactols'],'libelle_documentaire':row['libelle_pactols'],
          'code_cog_2026_candidat':code,'nom_geojson_2026':official,
          'statut_geometrie_2026':status,
          'millesime_geometrie':2026 if feat else None,
          'source_geometrie':geosource.name if feat else None,
          'identite_administrative_historique':'non_resolue_dans_cette_etape',
          'statut_validation_lien_pactols_cog':'non_valide',
          'geometrie_historique_validee':False,
        })
    sortie.mkdir(parents=True,exist_ok=True)
    gj={'type':'FeatureCollection','metadata':{
        **provenance,'statut_publication':'recette_non_publiee',
        'note_raccordement':'Attribution par CODE COG actuel uniquement, jamais par concordance du libellé'},
        'features':exported}
    dest_geo.write_text(json.dumps(gj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    payload={'schema_version':'0.1.0','statut':'audit_non_validant',
        'provenance_geometries':provenance,
        'sources_candidatures':[{'fichier':x.name,'sha256':sha(x)} for x in paths],
        'candidatures':items}
    dest_json.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'schema_version':'0.1.0','statut':'audit_non_validant','millesime':2026,'generalisation':'100m',
        'candidatures':len(rows),'codes_distincts':len(codes),
        'contours_extraits':len(exported),
        'repartition':dict(sorted(statuses.items())),
        'sources_sha256':{'geojson':sha_src,**{p.name:sha(p) for p in paths}},
        'avertissement':'Aucune correspondance Pactols–COG ni géométrie historique validée.'}
    dest_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sous-lot',action='append',required=True,type=Path)
    p.add_argument('--geometries',required=True,type=Path)
    p.add_argument('--sortie',required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(construire(a.sous_lot,a.geometries,a.sortie),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
