#!/usr/bin/env python3
"""Contrôles bloquants du lot A05b 1.54, sans publication du XLSX privé."""
from __future__ import annotations
import json,sys
from pathlib import Path

SOURCE='AdlFI_referentiel_1-54_A05B_CNRS_INRAP_LABOS_CANDIDAT.xlsx'
SOURCE_SHA='32e69ba481331a0f1470c93ae40827e69dbb58cca20d739921459be30b218f15'
EXPECTED_COUNTS={
    "ORG-0001":  5,
    "ORG-0004":  18,
    "ORG-0008":  14,
    "ORG-0010":  1,
    "ORG-0022":  4,
    "ORG-0076":  2,
    "ORG-0078":  4,
    "ORG-0081":  2,
    "ORG-0147":  3,
    "ORG-0148":  2,
    "ORG-0151":  3,
    "ORG-0152":  3,
    "ORG-0155":  3,
    "ORG-0194":  5,
    "ORG-0218":  2,
    "ORG-0264":  1
}
EXPECTED_LEVELS={'cantonal':2,'communal':56,'departemental':43,
                 'intercommunal':24,'metropolitain':1,'national':24,
                 'not_applicable':8,'provincial':1,'regional':39,'unresolved':2}

def validate(data):
    bad=[]
    def check(ok,msg):
        if not ok:bad.append(msg)
    prov=data.get('provenance',{})
    check(prov.get('source_filename')==SOURCE,'Nom du maître 1.54')
    check(prov.get('source_sha256')==SOURCE_SHA,'SHA-256 du maître 1.54')
    auth=data.get('authorities',[]);rels=data.get('relations',[])
    by={x['id']:x for x in auth}
    check(len(auth)==len(by)==934,'934 autorités uniques')
    check(sum(a.get('kind')=='ORG' for a in auth)==734,'734 ORG')
    check(sum(a.get('kind')=='SER' for a in auth)==200,'200 SER')
    check(sum(a.get('validation',{}).get('established') is True for a in auth)==568,
          '568 autorités documentées')
    check(len(rels)==600,'600 relations inchangées')
    check(sum(x.get('presentation',{}).get('visible') for x in auth)==682,
          '682 autorités visibles')
    for ident,n in EXPECTED_COUNTS.items():
        check(by.get(ident,{}).get('usage',{}).get('affiliations_validated')==n,
              ident+': compteur de correspondances')
    for ident in ('ORG-0004','ORG-0008','ORG-0068'):
        check(by.get(ident,{}).get('validation',{}).get('status')=='valide',
              ident+': qualification globale conservée')
    check(by.get('ORG-0004',{}).get('activity',{}).get('start')=='1939-10-19','Date CNRS')
    check(by.get('ORG-0008',{}).get('activity',{}).get('start')=='2002-02-01','Date Inrap')
    totals=data.get('totals',{})
    check(totals.get('service_level_resolution')==EXPECTED_LEVELS,'Invariants échelon SER')
    check(totals.get('service_sector_resolution')=={'public':197,'prive':3},'Invariants secteur SER')
    check(set(totals.get('service_level_unresolved_ids',[]))=={'SER-0178','SER-0202'},
          'Deux SER non résolus inchangés')
    check(any(r['id']=='REL-0043' and r['source']=='ORG-0068' and r['target']=='ORG-0008'
              and r['type']=='succession_institutionnelle' for r in rels),
          'Succession AFAN vers Inrap conservée')
    return bad

def main():
    target=Path(sys.argv[1]) if len(sys.argv)>1 else Path('docs/data/organismes.json')
    d=json.loads(target.read_text(encoding='utf-8'))
    issues=validate(d)
    for issue in issues:print('ÉCHEC :',issue,file=sys.stderr)
    if issues:return 1
    print('OK — version 1.54 : 15 AFF, 32 COR, 16 compteurs ; 934 autorités et 600 relations.')
    return 0
if __name__=='__main__':sys.exit(main())
