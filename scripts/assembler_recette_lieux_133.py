#!/usr/bin/env python3
"""Construit une couche de recette homogène (103 validations PACA + 30 candidats).

Ne modifie JAMAIS les fichiers publiés. Reprojette aucun contour.
La géométrie 2026 est un objet cartographique contemporain, non historique.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from auditer_raccordements_geometriques_2026 import lire_geo,sha,ATTRIBUTION,SOURCE_URL,norm

SHA_2026_100M='4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778'


def verifier_entrees(pilote:Path,candidatures:Path):
    base=json.loads(pilote.read_text(encoding='utf-8'))
    aud=json.loads(candidatures.read_text(encoding='utf-8'))
    if base.get('totaux',{}).get('autorites_pactols')!=103 or len(base.get('autorites',[]))!=103:
        raise ValueError('Le pilote d’autorités validées a changé : préflight requis')
    if base.get('provenance',{}).get('millesime_cog')!=2026:
        raise ValueError('Pilote non millésimé 2026')
    results=[];codes=set();arks=set()
    for a in base['autorites']:
        relations=a.get('correspondances',[])
        if len(relations)!=1 or relations[0].get('validation',{}).get('statut')!='VALIDE_EDITEUR_2026_10_18':
            raise ValueError('Validation du pilote non reconnue: '+a.get('ark_pactols',''))
        c=relations[0];x={
            'ark_pactols':a['ark_pactols'],'code_insee':c['code_insee'],
            'libelle_cog':c['libelle_cog'],'statut_relation':'valide_pilote_paca_2026',
            'preuve':'validation_editoriale_2026_10_18',
        }
        results.append(x)
    if aud.get('statut')!='audit_non_validant' or len(aud.get('candidatures',[]))!=30:
        raise ValueError('Il faut exactement 30 candidatures non validées en entrée')
    for a in aud['candidatures']:
        if a.get('statut_validation_lien_pactols_cog')!='non_valide' or a.get('geometrie_historique_validee') is not False:
            raise ValueError('Candidature de recette devenue validée sans arbitrage éditorial')
        if a.get('statut_geometrie_2026')!='code_present_nom_concordant':
            raise ValueError('Candidature sans concordance de nom et code COG : '+a.get('ark_pactols',''))
        results.append({'ark_pactols':a['ark_pactols'],
          'code_insee':a['code_cog_2026_candidat'],
          'libelle_cog':a['nom_geojson_2026'],
          'statut_relation':'candidat_non_valide',
          'preuve':'audit_geo_2026_nominatif_non_validant'})
    for a in results:
        ark,code=a['ark_pactols'],a['code_insee']
        if ark in arks or code in codes:raise ValueError('Collision ARK/code avec le pilote : '+ark+'/'+code)
        arks.add(ark);codes.add(code)
    assert len(results)==133
    return results


def assembler(pilote:Path,candidatures:Path,geo:Path,out:Path,sha_attendu=SHA_2026_100M):
    for p in (pilote,candidatures,geo):
        if not p.is_file():raise FileNotFoundError(p)
    combined=verifier_entrees(pilote,candidatures)
    if sha_attendu and sha(geo)!=sha_attendu:
        raise ValueError('Géométrie 100 m source modifiée : empreinte incorrecte')
    geosource=lire_geo(geo)
    features={};codes={a['code_insee'] for a in combined}
    for f in geosource['features']:
        c=str((f.get('properties') or {}).get('code',''))
        if c in codes:
            if c in features:raise ValueError('Géométrie dupliquée : '+c)
            if not f.get('geometry') or f['geometry'].get('type') not in ('Polygon','MultiPolygon'):
                raise ValueError('Géométrie non polygonale : '+c)
            features[c]=f
    missing=sorted(codes-features.keys())
    if missing:raise ValueError('Codes absents du jeu 2026 100 m : '+','.join(missing))
    output=[];history=[]
    for a in sorted(combined,key=lambda x:(x['code_insee'],x['ark_pactols'])):
        src=features[a['code_insee']]
        official=src.get('properties',{}).get('nom','')
        if norm(official)!=norm(a['libelle_cog']):
            raise ValueError(f'Incohérence code-nom en 2026 : {a["code_insee"]}: {official} / {a["libelle_cog"]}')
        props=dict(src['properties'])
        props.update({'ark_pactols_documentaire':a['ark_pactols'],
          'statut_lien_pactols_cog':a['statut_relation'],
          'validation_geometrie_historique':'non',
          'source_geometrie_millesime':2026,'source_generalisation':'100m'})
        output.append({'type':'Feature','properties':props,'geometry':src['geometry']})
        history.append({**a,'statut_contour_2026':'present',
                        'episode_administratif_historique_valide':False,
                        'source_millesime':2026})
    signature=sha(geo)
    result={'type':'FeatureCollection','metadata':{
      'schema_version':'0.1.0','etat':'recette_non_publiee',
      'perimetre':'103 correspondances PACA validées + 30 candidatures nationales non validées',
      'millesime':2026,'generalisation':'100m','source_url':SOURCE_URL,
      'source_sha256':signature,'licence':'ODbL-1.0',
      'attribution':ATTRIBUTION,
      'regle':'Contours homogènes à 100 m, sans prétention de limites historiques, sans modification du pilote 1000 m.'},
      'features':output}
    rapport={'schema_version':'0.1.0','etat':'recette_non_publiee',
      'validations_preexistantes':103,'candidatures_non_validees':30,
      'communes_distinctes':len(output),
      'codes_absents':missing,'conflits_de_code_ou_ark':0,
      'millesime_geometries':2026,'generalisation':'100m',
      'source_sha256':signature,
      'source_pilote_sha256':sha(pilote),
      'source_rapport_candidats_sha256':sha(candidatures),
      'contraintes':'Ne pas mélanger avec le fond 1000 m du pilote; limites contemporaines non historiques; aucune nouvelle validation.'}
    if out.resolve() in {p.resolve() for p in (pilote,candidatures,geo)}:
        raise ValueError('Répertoire sortie doit être distinct des sources')
    out.mkdir(parents=True,exist_ok=True)
    (out/'carte-lieux-recette-133-communes-2026-100m.geojson').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    (out/'liens-cog-geometries-recette-133.json').write_text(json.dumps({'statut':'recette_non_publiee','liens':history},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'rapport-carte-lieux-recette-133.json').write_text(json.dumps(rapport,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return rapport


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilote',type=Path,required=True)
    p.add_argument('--candidatures',type=Path,required=True)
    p.add_argument('--geometries',type=Path,required=True)
    p.add_argument('--sortie',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(assembler(a.pilote,a.candidatures,a.geometries,a.sortie),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
