#!/usr/bin/env python3
"""Recette de l'export JSON Organismes 1.52 A02-A03, sans lecture du maître privé.

Usage : python3 scripts/recette_publication_organismes_152.py docs/data/organismes.json
À exécuter après l'export du XLSX privé dans une copie de travail locale.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import sys

SOURCE = 'AdlFI_referentiel_1-52_A02_A03_QUALIFIE_CANDIDAT.xlsx'
SHA256 = '373091d86be0378313068e64db842be45a99a3a71bdf21f57b0915c77a7772d5'
EXPECTED_LEVELS = {
    'cantonal': 2, 'communal': 56, 'departemental': 43,
    'intercommunal': 24, 'metropolitain': 1, 'national': 24,
    'not_applicable': 8, 'provincial': 1, 'regional': 39, 'unresolved': 2
}
EXPECTED_NON_APPLICABLE = {
    'SER-0107', 'SER-0150', 'SER-0187', 'SER-0195',
    'SER-0196', 'SER-0197', 'SER-0198', 'SER-0199'
}
EXPECTED_UNRESOLVED = {'SER-0178', 'SER-0202'}
EXPECTED_HISTORICAL = 33


def verify(data):
    errors = []
    def expect(condition, message):
        if not condition: errors.append(message)

    provenance = data.get('provenance', {})
    expect(provenance.get('source_filename') == SOURCE, 'Nom de maître source différent')
    expect(provenance.get('source_sha256') == SHA256, 'Empreinte SHA-256 du maître source différente')
    a = data.get('authorities', [])
    rels = data.get('relations', [])
    totals = data.get('totals', {})
    by_id = {x['id']: x for x in a}
    expect(len(by_id) == len(a), 'Identifiants d’autorité dupliqués')
    for k,v in {'authorities':934,'organismes':734,'services':200,
                'catalog_included':682,'catalog_excluded':252}.items():
        expect(totals.get(k) == v, f'{k} : {totals.get(k)} au lieu de {v}')
    expect(len(rels) == 600, f'{len(rels)} relations au lieu de 600')
    expect(not any(r.get('source') not in by_id or r.get('target') not in by_id for r in rels),
           'Relation vers une autorité absente')
    services = [x for x in a if x['kind'] == 'SER']
    methods = Counter(x['classification'].get('level_origin',{}).get('method') for x in services)
    actual_levels = Counter(
        'not_applicable' if x['classification'].get('level_origin',{}).get('method') == 'not_applicable'
        else x['classification'].get('level') or 'unresolved' for x in services)
    expect(dict(actual_levels) == EXPECTED_LEVELS,
           f'Échelons inattendus : {dict(actual_levels)}')
    expect(totals.get('service_level_resolution') == EXPECTED_LEVELS,
           'Décompte de résolution des SER du JSON incompatible avec la recette')
    expect(methods.get('inherited_historical') == EXPECTED_HISTORICAL,
           f'Héritages historiques : {methods.get("inherited_historical")} au lieu de {EXPECTED_HISTORICAL}')
    non_app = {x['id'] for x in services if x['classification'].get('level_origin',{}).get('method') == 'not_applicable'}
    expect(non_app == EXPECTED_NON_APPLICABLE, f'Non-applicables inattendus : {sorted(non_app)}')
    for ident in non_app:
        x=by_id[ident]
        expect(x['classification'].get('level') is None, f'{ident} : échelon non vide')
        expect(x['quality'].get('level_unresolved') is False, f'{ident} : lacune signalée à tort')
    unresolved = {x['id'] for x in services if x['quality'].get('level_unresolved')}
    expect(unresolved == EXPECTED_UNRESOLVED,
           f'Services non résolus inattendus : {sorted(unresolved)}')
    expect(set(totals.get('service_level_unresolved_ids',[])) == EXPECTED_UNRESOLVED,
           'Liste des services non résolus incohérente')
    for rid, sid in [('RSE-0259','SER-0151'),('RSE-0260','SER-0152')]:
        matching=[r for r in rels if r['id']==rid]
        expect(len(matching)==1 and matching[0].get('source')==sid and
               matching[0].get('target')=='ORG-0023' and
               matching[0].get('type')=='rattachement_service' and
               matching[0].get('validation') in ('valide','validee','validée'),
               f'Rattachement historique manquant ou non validé : {rid}')
    expect(any(r['id']=='RSE-0229' and r.get('validation') in ('valide','validee','validée')
               for r in rels),'RSE-0229 non validée')
    for rid in ('RSE-0231','RSE-0258'):
        expect(any(r['id']==rid and r.get('validation')=='a_verifier' for r in rels),
               f'{rid} ne conserve pas son statut provisoire')
    return errors, actual_levels, methods


def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path('docs/data/organismes.json')
    data=json.loads(path.read_text(encoding='utf-8'))
    errors,levels,methods=verify(data)
    print('Échelons :',dict(sorted(levels.items())))
    print('Provenances :',dict(sorted(methods.items())))
    if errors:
        print('ECHEC —',len(errors),'anomalie(s)',file=sys.stderr)
        for e in errors:print(' -',e,file=sys.stderr)
        raise SystemExit(1)
    print('OK — 934 autorités, 600 relations, 190 échelons, 8 non applicables, 2 non résolus.')


if __name__=='__main__': main()
