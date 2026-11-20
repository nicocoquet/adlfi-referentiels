#!/usr/bin/env python3
"""Contrôle bloquant du JSON candidat 1.50 (lecture seule).

Usage : python3 scripts/recette_publication_organismes_150.py chemin/organismes.json

Le script n'altère ni le maître XLSX privé, ni le JSON publié. Il sert à contrôler
un export candidat produit depuis le XLSX 1.50 qualifié.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def validate_candidate(data: dict) -> list[str]:
    failures = []
    def check(condition: bool, text: str):
        if not condition:
            failures.append(text)

    authorities=data.get('authorities',[])
    relations=data.get('relations',[])
    aliases=data.get('aliases',[])
    ids=[x.get('id') for x in authorities]
    index={x.get('id'):x for x in authorities}
    kinds=Counter(x.get('kind') for x in authorities)

    check(len(authorities)==934,'934 autorités attendues')
    check(kinds['ORG']==734 and kinds['SER']==200,'734 ORG et 200 SER attendus')
    check(len(relations)==594,'594 relations attendues')
    check(len(ids)==len(set(ids)),'identifiants d’autorité uniques')
    check(all(r.get('source') in index and r.get('target') in index for r in relations),
          'aucune relation orpheline')
    check(len(aliases)==3,'trois alias historiques attendus')
    alias_by_from={a.get('from'):a.get('to') for a in aliases}
    for old,new in [('SER-0063','ORG-0747'),('ORG-0395','ORG-0300'),('SER-0139','SER-0148')]:
        check(alias_by_from.get(old)==new,f'alias {old} → {new}')
        check(old not in index,f'identifiant retiré {old} absent des autorités')
        check(new in index,f'identifiant canonique {new} présent')

    grasm=index.get('ORG-0747',{})
    check(grasm.get('kind')=='ORG','GRASM classé ORG')
    check(grasm.get('usage',{}).get('affiliations_linked')==3,
          'trois correspondances éditoriales liées au GRASM')
    check(grasm.get('classification',{}).get('bsr')=='ASS','catégorie BSR ASS du GRASM')
    check(any(r.get('id')=='REL-0338' and r.get('source')=='ORG-0747'
                  and r.get('target')=='ORG-0120' and r.get('type')=='affiliation_federale'
                  and r.get('validation') in ('valide','validée','validee') for r in relations),
          'affiliation fédérale GRASM → FFESSM validée')

    sfecag=index.get('ORG-0751',{})
    check(sfecag.get('validation',{}).get('established') is True,'SFECAG validée')
    check(sfecag.get('activity',{}).get('start')=='1962','SFECAG fondée en 1962')
    check(any(x.get('label')=='Groupe d’étude de la céramique antique en Gaule'
                  and x.get('start')=='1962' and x.get('end')=='1973'
                  and x.get('validation')=='valide'
                  for x in sfecag.get('names',{}).get('history',[])),
          'historique GECAG 1962–1973 conservé')

    riez=index.get('SER-0202',{})
    check(riez.get('validation',{}).get('status')=='a_verifier','Riez reste à vérifier')
    check(riez.get('activity',{}).get('active') is None,
          'activité actuelle du musée de Riez indéterminée')
    check(any(r.get('id')=='RSE-0258' and r.get('source')=='SER-0202'
              and r.get('target')=='ORG-0755'
              and r.get('validation')=='a_verifier' for r in relations),
          'rattachement municipal RSE-0258 non validé')

    check(all('validation' in a and a['validation'].get('status') in
              ('valide','validee','validée','a_verifier','non_renseigne')
              for a in authorities),
          'statut documentaire explicitement exporté sur toutes les autorités')
    check(all(a.get('validation',{}).get('established') is not True
              for a in authorities if a.get('validation',{}).get('status')=='a_verifier'),
          'aucune autorité a_verifier n’est indiquée comme validée')
    check(sum(a.get('presentation',{}).get('visible',False) for a in authorities)>670,
          'les nouvelles autorités sont visibles sans cacher la majorité du catalogue')
    return failures


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('json_file',type=Path)
    a=p.parse_args(argv)
    d=json.loads(a.json_file.read_text(encoding='utf8'))
    failures=validate_candidate(d)
    if failures:
        for item in failures:
            print('ÉCHEC :',item,file=sys.stderr)
        return 2
    print('OK — recette métier du JSON 1.50 : autorités, relations, alias, GRASM, SFECAG, Riez')
    return 0


if __name__=='__main__':
    sys.exit(main())
