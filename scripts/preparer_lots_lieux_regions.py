#!/usr/bin/env python3
"""Préparer, sans les valider, les lots Pactols–COG de trois régions prioritaires.

Sources réelles : tables CSV extraites des XML AdlFI et audit SKOS de Pactols
Lieux th17 (2026-07-22). Aucune concordance lexicale ou URI ne crée de
relation éditorialement validée. Ne modifie aucune donnée GitHub Pages.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

REGIONS = {
    'Corse': {
        'code': '94', 'slug': 'corse', 'labels': {'Corse'},
        'source_prefix': 'AdlFI_Corse/',
        'departements': {'Département de la Corse-du-Sud': '2A',
                         'Département de la Haute-Corse': '2B'}},
    'Pays de la Loire': {
        'code': '52', 'slug': 'pays-de-la-loire',
        'labels': {'Pays de la Loire'}, 'source_prefix': 'AdlFI_Pays-de-la-Loire/',
        'departements': {'Département de la Loire-Atlantique': '44',
                         'Département de Maine-et-Loire': '49',
                         'Département de la Mayenne': '53',
                         'Département de la Sarthe': '72',
                         'Département de la Vendée': '85'}},
    'Bourgogne-Franche-Comté': {
        'code': '27', 'slug': 'bourgogne-franche-comte',
        'labels': {'Bourgogne-Franche-Comté', 'Bourgogne', 'Franche-Comté'},
        'source_prefix': 'AdlFI_Bourgogne_Franche-Comte/',
        'departements': {"Département de la Côte-d'Or": '21',
                         'Département du Doubs': '25',
                         'Département du Jura': '39',
                         'Département de la Nièvre': '58',
                         'Département de la Haute-Saône': '70',
                         'Département de Saône-et-Loire': '71',
                         "Département de l'Yonne": '89',
                         'Territoire de Belfort': '90',
                         'Département du Territoire de Belfort': '90'}}
}

# Alertes documentaires instruites précédemment (pas des validations d'ARK–COG).
ALERTES_DOCUMENTAIRES = {
    '26678/pcrtXSoREPOwqU': 'X1_Brain_21_suspect_dans_notice_A28_Pays_de_Retz',
    '26678/pcrtGHlbdiOta1': 'X2_Bethon_Sarthe_ark_distinct_a_confronter_notice_A28',
    '26678/pcrtgs2LLPYow2': 'H5_Afa_changement_code_1976_confirme_MOD41',
    '26678/pcrtGx0ke7aJM6': 'H5_Aghione_changement_code_1976_confirme_MOD41',
}
# Objets indexés sous un département sans pour autant être des communes.
OBJETS_NON_COMMUNAUX_VERIFIES = {
    '26678/pcrtqaxEBKYzD3': 'T3_region_naturelle_Cap_Corse',
    '26678/pcrtw6p8JfvWX7': 'T3_region_naturelle_Balagne',
    '26678/pcrt2jEAL85n1L': 'T3_site_archeologique_Filitosa',
}
# Les dossiers documentaires/historiques doivent être visibles dans les 25
# premières lignes de chaque région ; l'échantillonnage complémentaire tourne
# ensuite entre les départements pour ne pas surpondérer une zone.
PRESELECTION_ARK = {
    'Corse': ('26678/pcrtgs2LLPYow2','26678/pcrtGx0ke7aJM6',
              '26678/pcrtqaxEBKYzD3','26678/pcrtw6p8JfvWX7','26678/pcrt2jEAL85n1L'),
    'Pays de la Loire': ('26678/pcrtGHlbdiOta1','26678/pcrtthzSDyCh4Z',
                       '26678/pcrt99dzcmxdhR','26678/pcrtk5xjv8vgwk9w8fmrz9z3',
                       '26678/pcrtRm3hz8YCOM'),
    'Bourgogne-Franche-Comté': ('26678/pcrtXSoREPOwqU',
                               '26678/pcrtdIcMrh2mh8','26678/pcrtANt29rHaDo'),
}

INSEE_URL = re.compile(r'^https?://id\.insee\.fr/geo/([^/?#]+)/([^?#/]+)', re.I)
CODE_INSEE = re.compile(r'^(?:[0-9]{5}|2[AB][0-9]{3})$')
COLS = ['region','code_region_2026','departement_hierarchie','ark_pactols',
        'libelle_xml','pref_fr_pactols','statut_pactols_20260722',
        'categorie_geographique','codes_insee_skos','types_liens_insee_skos',
        'autres_uris_insee','concordance_code_departement',
        'nombre_occurrences_region','nombre_notices_region',
        'nombre_fichiers_region','annees_operation_attestees',
        'fichier_temoin','notice_temoin','etiquette_instruction',
        'statut_validation_pactols_cog','source_pactols_ark']


def lire_csv(path: Path, required: set[str]):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        if not required <= set(reader.fieldnames or []):
            raise ValueError(f'Colonnes absentes dans {path}: {sorted(required-set(reader.fieldnames or []))}')
        yield from reader


def sha(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def skos_insee(links):
    codes=set();types=set();others=set()
    for uri in json.loads(links or '[]'):
        m=INSEE_URL.search(uri)
        if not m:continue
        kind,ident=m.group(1),m.group(2)
        types.add(kind)
        if kind.lower() == 'commune' and CODE_INSEE.fullmatch(ident.upper()):
            codes.add(ident.upper())
        else:
            others.add(uri)
    return sorted(codes),sorted(types),sorted(others)


def classe_geo(labels,info):
    dep_labels=set(info['departements'])
    if labels[-1] in info['labels']:
        return 'region_administrative_ou_historique'
    if labels[-1] in dep_labels:
        return 'departement'
    if len(labels)>1 and labels[-2] in dep_labels:
        return 'commune_candidate_directe'
    if any(x in dep_labels for x in labels):
        return 'lieu_imbrique_sous_departement'
    return 'sans_departement_dans_hierarchie'


def classe_risque(row):
    ark=row['ark_pactols']
    if ark in OBJETS_NON_COMMUNAUX_VERIFIES:
        return OBJETS_NON_COMMUNAUX_VERIFIES[ark]
    if ark in ALERTES_DOCUMENTAIRES:
        return ALERTES_DOCUMENTAIRES[ark]
    genre=row['categorie_geographique']; dept=row['departement_hierarchie']
    codes=json.loads(row['codes_insee_skos']);others=json.loads(row['autres_uris_insee']);
    if row['concordance_code_departement']=='code_hors_departement_de_hierarchie':
        return 'H1_episode_historique_interdepartemental'
    if genre in ('region_administrative_ou_historique','departement'):
        return 'T1_entite_supracommunale'
    if len(codes)>1:return 'H2_plusieurs_codes_INSEE'
    if others and not codes:return 'H3_insee_uri_non_numerique_ou_autre_type'
    if not codes:return 'H4_absence_lien_commune_INSEE'
    if genre=='lieu_imbrique_sous_departement':return 'T2_lieu_imbrique_ou_ancien'
    return 'C0_code_INSEE_deja_asserté_a_controler'


def prepare(autorites:Path, occurrences:Path, skos_csv:Path, sortie:Path, lot_taille:int=25):
    if not 1<=lot_taille<=250:raise ValueError('lot_taille doit être dans 1..250')
    inputs={'autorites_xml':autorites,'occurrences_xml':occurrences,'audit_skos_20260722':skos_csv}
    for p in inputs.values():
        if not p.is_file():raise FileNotFoundError(p)
    if any(sortie.resolve()==p.resolve() or sortie.resolve().is_relative_to(p.resolve()) for p in inputs.values()):
        raise ValueError('Dossier de sortie doit être séparé des sources')
    auth={r['ark_pactols']:r for r in lire_csv(autorites,{'ark_pactols','libelle_fr_xml','annees_operation_relevees'})}
    skos={r['ark_pactols']:r for r in lire_csv(skos_csv,{'ark_pactols','pref_fr_pactols','liens_exact_match_pactols','statut_comparaison'})}
    if len(auth)!=9928 or len(skos)!=9928:
        raise ValueError('Attente 9 928 ARK distincts (sources nationales v2).')
    if set(auth)!=set(skos):raise ValueError('Index des ARK non identiques entre extraction et SKOS')
    collected={reg:{} for reg in REGIONS}
    outside=collections.defaultdict(lambda:collections.defaultdict(lambda:{'occurrences':0,'notices':set(),'fichiers':set(),'chaines':set(),'libelle':''}))
    regional_occ=collections.Counter()
    editorial_occ=collections.Counter()
    editorial_notices=collections.defaultdict(set)
    for r in lire_csv(occurrences,{'ark_terminal','chaine_libelles_fr','chaine_ark','notice_id','fichier_relatif'}):
        ark=r['ark_terminal']
        if ark not in auth:raise ValueError(f'ARK de l’occurrence absent des autorités : {ark}')
        labels=json.loads(r['chaine_libelles_fr']); ids=json.loads(r['chaine_ark'])
        if not labels or len(labels)!=len(ids) or ids[-1]!=ark:
            raise ValueError('Chaîne de lieu invalide : '+ark)
        source_reg=[k for k,v in REGIONS.items() if r['fichier_relatif'].startswith(v['source_prefix'])]
        target_reg=[k for k,v in REGIONS.items() if set(labels)&v['labels']]
        for reg in target_reg:
            regional_occ[reg]+=1
            record=collected[reg].setdefault(ark,{'occurrences':0,'notices':set(),'fichiers':set(),'deps':set(),
                                                   'types':set(),'temoins':[],'chaines':set()})
            record['occurrences']+=1;record['notices'].add(r['notice_id']);
            record['fichiers'].add(r['fichier_relatif']);record['chaines'].add(tuple(ids))
            record['deps'].update(REGIONS[reg]['departements'][label] for label in labels if label in REGIONS[reg]['departements'])
            record['types'].add(classe_geo(labels,REGIONS[reg]))
            if len(record['temoins'])<3:
                record['temoins'].append((r['fichier_relatif'],r['notice_id']))
        for reg in source_reg:
            editorial_occ[reg]+=1;editorial_notices[reg].add(r['notice_id'])
            if reg not in target_reg:
                ref=outside[reg][ark];ref['occurrences']+=1;ref['notices'].add(r['notice_id']);ref['fichiers'].add(r['fichier_relatif'])
                ref['chaines'].add(' > '.join(labels));ref['libelle']=auth[ark]['libelle_fr_xml']
    if sum(regional_occ.values()) != 5898:raise ValueError('Sources XML différentes de l’audit national 2026-11-14')
    if [len(collected[r]) for r in REGIONS] != [200,806,736]:
        raise ValueError('Périmètre régional différent de l’audit national 2026-11-14')
    if any(len({r for r in REGIONS if ark in collected[r]})>1 for ark in auth):
        raise ValueError('ARK affecté à plusieurs régions prioritaires')
    result=[]; report={'schema_version':'0.1.0','etat':'recette_non_validante',
      'source_sha256':{k:sha(v) for k,v in inputs.items()},'regions':{},
      'regle':'Sélection par hiérarchie Pactols, pas par région du fichier XML ; exactMatch = assertion Frantiq, pas validation AdlFI.'}
    sortie.mkdir(parents=True,exist_ok=True)
    for reg,info in REGIONS.items():
        entries=[]
        for ark,record in collected[reg].items():
            sk=skos[ark]; a=auth[ark]
            codes,types,other=skos_insee(sk['liens_exact_match_pactols'])
            deps=sorted(record['deps']);types_geo=sorted(record['types'])
            if len(deps)>1:
                coherence='plusieurs_departements_a_expertiser'
            elif len(deps)==1 and codes and any(x[:2]!=deps[0] for x in codes):
                coherence='code_hors_departement_de_hierarchie'
            elif len(deps)==1 and codes:
                coherence='code_dans_departement'
            else:coherence='non_comparable_ou_hors_commune'
            genre=types_geo[0] if len(types_geo)==1 else 'plusieurs_profils_a_instruire'
            row={'region':reg,'code_region_2026':info['code'],
                'departement_hierarchie':','.join(deps), 'ark_pactols':ark,
                'libelle_xml':a['libelle_fr_xml'],
                'pref_fr_pactols':' | '.join(json.loads(sk['pref_fr_pactols'])),
                'statut_pactols_20260722':sk['statut_comparaison'],
                'categorie_geographique':genre,
                'codes_insee_skos':json.dumps(codes,ensure_ascii=False),
                'types_liens_insee_skos':json.dumps(types,ensure_ascii=False),
                'autres_uris_insee':json.dumps(other,ensure_ascii=False),
                'concordance_code_departement':coherence,
                'nombre_occurrences_region':record['occurrences'],
                'nombre_notices_region':len(record['notices']),
                'nombre_fichiers_region':len(record['fichiers']),
                'annees_operation_attestees':a['annees_operation_relevees'],
                'fichier_temoin':record['temoins'][0][0],
                'notice_temoin':record['temoins'][0][1],
                'etiquette_instruction':'',
                'statut_validation_pactols_cog':'non_nouvellement_valide',
                'source_pactols_ark':'https://ark.frantiq.fr/ark:/'+ark}
            row['etiquette_instruction']=classe_risque(row)
            entries.append(row)
        entries.sort(key=lambda x:(x['departement_hierarchie'],x['libelle_xml'].casefold(),x['ark_pactols']))
        make_csv(sortie/f'inventaire-{info["slug"]}.csv',entries,COLS)
        counted=collections.Counter(r['etiquette_instruction'] for r in entries)
        dept_counts=collections.Counter(r['departement_hierarchie'] or 'non_departemental' for r in entries)
        no_code=[r for r in entries if not json.loads(r['codes_insee_skos'])]
        report['regions'][reg]={
          'code_region_2026':info['code'],'ark_distincts':len(entries),
          'occurrences_xml':regional_occ[reg],
          'notices_xml_distinctes':len(set(n for item in collected[reg].values() for n in item['notices'])),
          'fichiers_xml_distincts':len(set(n for item in collected[reg].values() for n in item['fichiers'])),
          'avec_lien_commune_insee_code_lisible':len(entries)-len(no_code),
          'sans_lien_commune_insee_code_lisible':len(no_code),
          'departs_par_hierarchie':dict(sorted(dept_counts.items())),
          'statuts_instruction':dict(sorted(counted.items())),
          'occurrences_dans_fichiers_editoriaux_region':editorial_occ[reg],
          'autorites_hors_hierarchie_region_mais_dans_source_editoriale':len(outside[reg]),
          'occurrences_hors_hierarchie_region_mais_dans_source_editoriale':sum(y['occurrences'] for y in outside[reg].values())}
        # Lot équilibré par département, les exceptions avant les cas ordinaires.
        buckets=collections.defaultdict(list)
        for row in entries:
            bucket=row['departement_hierarchie'] or 'region_ou_hors_departement'
            buckets[bucket].append(row)
        for b in buckets.values():
            b.sort(key=lambda x:(0 if x['etiquette_instruction'].startswith('H1') else 1,
                                0 if x['etiquette_instruction'].startswith('H3') else 1,
                                0 if x['etiquette_instruction'].startswith('H4') else 1,
                                0 if x['categorie_geographique']=='commune_candidate_directe' else 1,
                                -x['nombre_notices_region'], x['libelle_xml'].casefold()))
        priority=[]
        by_ark={row['ark_pactols']:row for row in entries}
        for ark in PRESELECTION_ARK[reg]:
            if ark not in by_ark:raise ValueError('ARK prioritaire absent du corpus régional : '+ark)
            row=by_ark[ark];priority.append(row)
            buckets[row['departement_hierarchie'] or 'region_ou_hors_departement'].remove(row)
        dept_order=sorted(k for k in buckets if k!='region_ou_hors_departement')
        while len(priority)<lot_taille and any(buckets[d] for d in dept_order):
            for dep in dept_order:
                if buckets[dep] and len(priority)<lot_taille:
                    priority.append(buckets[dep].pop(0))
        if len(priority)<lot_taille:
            priority.extend(buckets['region_ou_hors_departement'][:lot_taille-len(priority)])
        make_csv(sortie/f'lot-01-{info["slug"]}.csv',priority,COLS)
        report['regions'][reg]['lot_01_ark']=len(priority)
        result.extend(entries)
    flags=[r for r in result if r['etiquette_instruction'].startswith(('H','T','X'))]
    make_csv(sortie/'points_instruction_prioritaires.csv',flags,COLS)
    missing=[]
    for reg, entries in outside.items():
        for ark,o in entries.items():
            missing.append({'region_source':reg,'ark_pactols':ark,'libelle_xml':o['libelle'],
             'nombre_occurrences':o['occurrences'],'nombre_notices':len(o['notices']),
             'hierarchies_observees':' | '.join(sorted(o['chaines'])),
             'fichier_temoin':sorted(o['fichiers'])[0],
             'statut':'contexte_editorial_hors_region_sans_inference_spatiale'})
    make_csv(sortie/'contextes-editoriaux-hors-region.csv',missing,
       ['region_source','ark_pactols','libelle_xml','nombre_occurrences','nombre_notices','hierarchies_observees','fichier_temoin','statut'])
    report['synthese']={'ark_regionaux_distincts':len(result),
       'occurrences_region_hierarchie':sum(regional_occ.values()),
       'ark_avec_lien_commune_insee_code_lisible':sum(bool(json.loads(r['codes_insee_skos'])) for r in result),
       'ark_code_hors_departement':sum(r['concordance_code_departement']=='code_hors_departement_de_hierarchie' for r in result),
       'points_instruction_prioritaires':len(flags),
       'contextes_ark_edition_region_hors_hierarchie':sum(len(x) for x in outside.values())}
    (sortie/'rapport-priorites-regionales.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report


def make_csv(path,rows,cols):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols,delimiter=';',extrasaction='ignore')
        w.writeheader();w.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--autorites',type=Path,required=True)
    p.add_argument('--occurrences',type=Path,required=True)
    p.add_argument('--skos-csv',type=Path,required=True)
    p.add_argument('--sortie',type=Path,required=True)
    p.add_argument('--taille-lot',type=int,default=25)
    x=p.parse_args()
    print(json.dumps(prepare(x.autorites,x.occurrences,x.skos_csv,x.sortie,x.taille_lot)['synthese'],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
