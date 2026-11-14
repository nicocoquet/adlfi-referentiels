#!/usr/bin/env python3
"""Contrôle COG 2026 des 22 parentages Pactols à code INSEE partagé.

Un même code peut désigner la commune nouvelle COM et la commune déléguée
COMD. Seul COMPARENT des lignes COMD/COMA détermine le parent courant.
Aucune fusion d'ARK, validation ou géométrie n'est produite.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

SHA_COMMUNES='7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def read(path, fields):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        head=f.readline();f.seek(0)
        reader=csv.DictReader(f,delimiter=';' if head.count(';')>head.count(',') else ',')
        if set(fields)-set(reader.fieldnames or []):
            raise ValueError('Colonnes manquantes dans '+str(path))
        return list(reader)

def analyser(couples, communes):
    mapping=read(couples,['code_insee','ark_enfant','libelle_enfant',
                          'ark_parent_pactols','libelle_parent_pactols'])
    if len(mapping)!=22 or len({r['code_insee'] for r in mapping})!=22:
        raise ValueError('22 codes distincts requis')
    current=collections.defaultdict(list)
    for rec in read(communes,['COM','TYPECOM','LIBELLE','COMPARENT','REG','DEP']):
        current[rec['COM']].append(rec)
    result=[]
    for m in mapping:
        code=m['code_insee']
        rows=current[code]
        sub=[r for r in rows if r['TYPECOM'] in ('COMD','COMA')]
        parents=sorted({r['COMPARENT'] for r in sub if r['COMPARENT']})
        if not sub: status='pas_de_commune_deleguee_associee_2026'
        elif len(parents)>1:status='plusieurs_comparent_a_instruire'
        elif not parents:status='comparent_absent_a_instruire'
        elif parents[0]==code:status='comparent_2026_egal_code_historique'
        else:status='comparent_2026_different_code_historique'
        names={v['LIBELLE'] for p in parents for v in current[p] if v['TYPECOM']=='COM'}
        result.append({**m,
          'types_sur_ce_code_2026':'|'.join(sorted({r['TYPECOM'] for r in rows})),
          'entite_subalterne_2026':'|'.join(sorted({r['LIBELLE'] for r in sub})),
          'comparent_2026':'|'.join(parents),
          'nom_commune_parente_2026':'|'.join(sorted(names)),
          'nombre_lignes_cog_2026':len(rows),
          'type_de_relation':status,
          'validation_adlfi':'non_valide'})
    return result

def produire(couples,communes,sortie):
    paths=[Path(couples),Path(communes)]
    if sha(communes)!=SHA_COMMUNES:
        raise ValueError('Empreinte Insee 2026 non conforme')
    results=analyser(couples,communes)
    output=Path(sortie)
    filenames=['comparent-22-codes-partages.csv','rapport-comparent-22.json']
    if any((output/n).resolve() in {p.resolve() for p in paths} for n in filenames):
        raise ValueError('Écrasement interdit')
    output.mkdir(parents=True,exist_ok=True)
    with (output/filenames[0]).open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(results[0]),delimiter=';')
        wr.writeheader();wr.writerows(results)
    categories=collections.Counter(r['type_de_relation'] for r in results)
    report={'statut':'recette_non_validante','ark_anciens':22,'codes_insee':22,
        'categories':dict(sorted(categories.items())),
        'decales':[{'code':r['code_insee'],'ancien_parent':r['libelle_parent_pactols'],
                    'comparent_2026':r['comparent_2026'],'nom_2026':r['nom_commune_parente_2026']}
                 for r in results if r['type_de_relation']=='comparent_2026_different_code_historique'],
        'sha256_sources':{'couples':sha(couples),'communes':sha(communes)},
        'alignements_valides':0,'geometries_historisees':0,
        'interpretation':'Un même code peut être partagé par COM et COMD ; COMPARENT est millésimé 2026.'}
    (output/filenames[1]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('couples','communes','sortie'):
        p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(produire(a.couples,a.communes,a.sortie),ensure_ascii=False,indent=2))
