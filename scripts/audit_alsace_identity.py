#!/usr/bin/env python3
"""Audit documentaire non destructif de la rupture de personne morale d'Archéologie Alsace.

Usage : python3 -m scripts.audit_alsace_identity MAITRE.xlsx --xml-corpus *.xml --output-dir /tmp/audit-alsace
Ne modifie jamais le classeur et ne crée aucune autorité ni correspondance validée.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from .export_organismes import parse_workbook
from .audit_alsace_xml import audit_xml_documents

OLD = 'ORG-0093'
SOURCE_PAIR = 'AFF-0047'
SOURCE_ALSACE = 'AFF-0048'
DATE_RENAME = '2016-10-15'
DATE_SUCCESSION = '2020-12-11'
DOCUMENTATION = {
    'rename': 'https://www.archeologie.alsace/fr/actualites-archivees',
    'current_entity': 'https://www.banatic.interieur.gouv.fr/intercommunalite/200094746-smo-archeologie-alsace-aa',
    'historic_entity': 'https://www.pappers.fr/entreprise/pair-archeologie-alsace-200006336',
}


def _one(rows: list[dict], column: str, value: str) -> dict:
    matches = [r for r in rows if str(r.get(column, '')).strip() == value]
    if len(matches) != 1:
        raise ValueError(f'{column}={value} : {len(matches)} lignes au lieu d’une')
    return matches[0]


def _next_id(rows: list[dict], field: str, prefix: str) -> str:
    ids = [int(r[field].split('-')[1]) for r in rows
           if isinstance(r.get(field), str) and re.fullmatch(rf'{prefix}-[0-9]{{4}}', r[field])]
    if not ids or max(ids) >= 9999:
        raise ValueError(f'Impossible de proposer un ID après {prefix}')
    return f'{prefix}-{max(ids)+1:04d}'


def build_dossier(sheets: dict, source_sha256: str | None = None, corpus_report: dict | None = None) -> dict:
    corpus_verified = False
    if corpus_report is not None:
        if corpus_report.get('status') != 'reconciliation_complete' or corpus_report.get('total') != 181 or corpus_report.get('actual') != {'Pair': 57, 'Archéologie Alsace': 124}:
            raise ValueError('Corpus XML non réconcilié avec les 181 occurrences du maître')
        corpus_verified = True
    orgs = sheets['Organismes']
    sources = sheets['Affiliations_sources']
    corrs = sheets['Correspondances_affiliations']
    histories = sheets['Historique']
    relations = sheets['Relations']

    old = _one(orgs, 'organisme_id', OLD)
    if old.get('nom_normalise') != 'Archéologie Alsace':
        raise ValueError('ORG-0093 : nom inattendu, migration à réexaminer')
    if old.get('date_debut') not in ('2006', '2006-09-01'):
        raise ValueError('ORG-0093 : date de création inattendue')
    if old.get('type_organisme') != 'collectivite_territoriale':
        raise ValueError('ORG-0093 : type déjà modifié ; réévaluer l’audit')
    oldhistory = _one(histories, 'historique_id', 'HIS-0003')
    if oldhistory.get('organisme_id') != OLD:
        raise ValueError('HIS-0003 ne concerne plus ORG-0093')
    current_relation = _one(relations, 'relation_id', 'REL-0054')
    if current_relation.get('organisme_source_id') != OLD:
        raise ValueError('REL-0054 ne concerne plus ORG-0093')

    rows = []
    for sid, expected_label, expected_count, expected_corr in [
        (SOURCE_PAIR, 'Pair', 57, 'COR-0054'),
        (SOURCE_ALSACE, 'Archéologie Alsace', 124, 'COR-0055'),
    ]:
        src = _one(sources, 'affiliation_source_id', sid)
        corr = _one(corrs, 'correspondance_id', expected_corr)
        if src.get('libelle_source') != expected_label:
            raise ValueError(f'{sid} : libellé XML inattendu')
        if int(src.get('occurrences', '0')) != expected_count:
            raise ValueError(f'{sid} : décompte inattendu')
        if src.get('organisme_id') != OLD or corr.get('organisme_id') != OLD:
            raise ValueError(f'{sid} : correspondance source modifiée')
        if corr.get('affiliation_source_id') != sid:
            raise ValueError(f'{expected_corr} : mauvais identifiant AFF')
        rows.append({
            'affiliation_source_id': sid,
            'correspondance_id': expected_corr,
            'source_label': expected_label,
            'occurrences': expected_count,
            'current_authority': OLD,
            'proposed_handling': (
                ('conserver sur ORG-0093 : opérations 2014–2015 vérifiées dans les XML'
                 if corpus_verified else
                 'conserver sur l’autorité historique (libellé ancien ; contrôler les emplois tardifs)')
                if sid == SOURCE_PAIR else
                ('conserver sur ORG-0093 : 48 opérations 2016 et 76 opérations 2017 documentées'
                 if corpus_verified else
                 'ne pas répartir sans examen des notices XML, de leurs dates et du contexte')
            ),
            'validation': 'documente_par_xml' if corpus_verified else 'a_revoir_pour_identite',
            'context_required': sid == SOURCE_ALSACE and not corpus_verified,
        })

    if sum(x['occurrences'] for x in rows) != 181:
        raise ValueError('Total des occurrences non cohérent')
    candidate = _next_id(orgs, 'organisme_id', 'ORG')
    relation_candidate = _next_id(relations, 'relation_id', 'REL')
    return {
        'status': 'proposition_non_appliquee',
        'source_sha256': source_sha256,
        'existing_authority': OLD,
        'proposed_new_authority': candidate,
        'proposed_succession_relation': relation_candidate,
        'identity': {
            'historical': {
                'id': OLD,
                'preferred_name': 'Archéologie Alsace',
                'historical_name': 'Pôle d’archéologie interdépartemental rhénan (Pair)',
                'siren': '200006336',
                'start': '2006-09-01', 'end_exclusive': DATE_SUCCESSION,
                'type_organisme': 'etablissement_public', 'sector': 'public',
                'level': None, 'activity': 'non',
                'comment': 'Institution interdépartementale distincte d’une collectivité territoriale. '
                           'L’échelon reste à normaliser.',
            },
            'successor': {
                'id': candidate, 'preferred_name': 'Archéologie Alsace',
                'siren': '200094746', 'start': DATE_SUCCESSION,
                'type_organisme': 'syndicat_mixte', 'sector': 'public',
                'level': None, 'activity': 'oui',
                'comment': 'Syndicat mixte ouvert (SMO), ne pas assimiler son activité '
                           'en Alsace à l’échelon régional ni à un EPCI.',
            },
        },
        'history_correction': {
            'id': 'HIS-0003', 'organisme': OLD, 'start': '2006-09-01',
            'end_inclusive': '2016-10-14', 'rename_effective': DATE_RENAME,
        },
        'succession': {
            'id': relation_candidate, 'source': OLD, 'target': candidate,
            'type': 'succession_institutionnelle', 'effective': DATE_SUCCESSION,
            'validation': 'a_confirmer_apres_creation_des_autorites',
        },
        'existing_relation_to_review': {
            'id': 'REL-0054',
            'current_source': OLD, 'current_target': 'ORG-0092',
            'status': current_relation.get('statut_validation'),
            'warning': 'Adhésion/membre du syndicat mixte et rattachement administratif ne sont pas synonymes ; '
                       'ne pas transférer automatiquement la relation à la nouvelle autorité.',
        },
        'affiliations': rows,
        'total_source_occurrences': 181,
        'xml_corpus_reconciled': corpus_verified,
        'xml_corpus_sha256': [item['sha256'] for item in corpus_report['sources']] if corpus_verified else [],
        'blocked': ([] if corpus_verified else ['Répartition des 124 occurrences AFF-0048 sans corpus XML'])
                   + ['Transfert automatique de REL-0054',
                      'Attribution automatique d’un échelon régional',
                      'Modification non contrôlée des identifiants et relations du maître'],
        'documentation': DOCUMENTATION,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--xml-corpus', type=Path, nargs='+', default=None)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    corpus_report = audit_xml_documents(args.xml_corpus) if args.xml_corpus else None
    dossier = build_dossier(parse_workbook(args.source),
                            hashlib.sha256(args.source.read_bytes()).hexdigest(),
                            corpus_report=corpus_report)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    target = args.output_dir / 'dossier-identites-alsace.json'
    target.write_text(json.dumps(dossier, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'candidat_org': dossier['proposed_new_authority'],
        'occurrences': dossier['total_source_occurrences'],
        'a_contextualiser': sum(a['occurrences'] for a in dossier['affiliations']
                               if a['context_required']),
        'rapport': str(target),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
