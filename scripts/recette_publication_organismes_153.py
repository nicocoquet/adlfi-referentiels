#!/usr/bin/env python3
"""Recette bloquante du lot A05, fondée sur les différences du maître 1.53."""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import Counter

SOURCE='AdlFI_referentiel_1-53_A05_AFAN_CNRS_INRAP_CANDIDAT.xlsx'
SHA256='fbea8c20b5867e742fa6bf82e058409c249c1017e0d0ec61e9612f926b878415'
DIFF_VALIDATED={
    'ORG-0001':4,'ORG-0004':10,'ORG-0008':7,'ORG-0022':3,
    'ORG-0068':5,'ORG-0137':3,'ORG-0194':3,'ORG-0335':1
}
MAJOR={'ORG-0004','ORG-0008','ORG-0068'}
PRESERVED_UNRESOLVED={'SER-0178','SER-0202'}


def validate_153(data):
    errors=[]
    def check(condition,message):
        if not condition: errors.append(message)
    p=data.get('provenance',{})
    check(p.get('source_filename')==SOURCE,'Nom du maître 1.53 incorrect')
    check(p.get('source_sha256')==SHA256,'Empreinte SHA-256 du maître 1.53 incorrecte')
    a=data.get('authorities',[]);links=data.get('relations',[])
    by={v['id']:v for v in a}
    check(len(by)==934 and len(a)==934,'934 autorités uniques attendues')
    check(len(links)==600,'600 relations attendues')
    check(sum(x['kind']=='ORG' for x in a)==734,'734 ORG attendues')
    check(sum(x['kind']=='SER' for x in a)==200,'200 SER attendus')
    check(sum(x['presentation']['visible'] for x in a)==682,'682 autorités visibles')
    check(sum(x['validation']['established'] for x in a)==568,'568 autorités validées')
    for id,n in DIFF_VALIDATED.items():
        record=by.get(id,{})
        check(record.get('usage',{}).get('affiliations_validated')==n,
              f'{id} : correspondances validées attendues = {n}')
    for id in MAJOR:
        record=by.get(id,{})
        check(record.get('validation',{}).get('status')=='valide' and
              record.get('validation',{}).get('established') is True,
              f'{id} : validation institutionnelle attendue')
    for id,start in {'ORG-0004':'1939-10-19','ORG-0008':'2002-02-01',
                     'ORG-0068':'1973-12-26'}.items():
        check(by.get(id,{}).get('activity',{}).get('start')==start,
              f'{id} : chronologie non conforme')
    check(by.get('ORG-0004',{}).get('classification',{}).get('level')=='national',
          'ORG-0004 : niveau national absent')
    check(by.get('ORG-0068',{}).get('classification',{}).get('sector')=='prive',
          'AFAN doit conserver son secteur privé')
    check(by.get('ORG-0068',{}).get('activity',{}).get('end')=='2002-01-31',
          'AFAN : fin au 31 janvier 2002')
    check(by.get('ORG-0008',{}).get('classification',{}).get('sector')=='public',
          'Inrap : secteur public')
    rel={r['id']:r for r in links}
    r=rel.get('REL-0043',{})
    check((r.get('source'),r.get('target'),r.get('type'),r.get('start'),r.get('validation'))==
          ('ORG-0068','ORG-0008','succession_institutionnelle','2002-02-01','valide'),
          'REL-0043 : succession AFAN-Inrap conservée')
    check(set(data.get('totals',{}).get('service_level_unresolved_ids',[]))==PRESERVED_UNRESOLVED,
          'Deux SER indéterminés inchangés')
    levels=data.get('totals',{}).get('service_level_resolution',{})
    check(levels.get('not_applicable')==8 and levels.get('unresolved')==2,
          'Applicabilité des échelons SER inchangée')
    sectors=data.get('totals',{}).get('service_sector_resolution',{})
    check(sectors=={'public':197,'prive':3},'200 secteurs SER inchangés')
    return errors


def main(argv=None):
    target=Path((argv or sys.argv[1:])[0]) if (argv or sys.argv[1:]) else Path('docs/data/organismes.json')
    data=json.loads(target.read_text(encoding='utf-8'))
    errors=validate_153(data)
    for e in errors:print('ÉCHEC :',e,file=sys.stderr)
    if errors:return 1
    print('OK — 1.53 : 934 autorités, 568 validées, 600 relations ; AFAN, CNRS, Inrap qualifiés.')
    return 0


if __name__=='__main__':sys.exit(main())
