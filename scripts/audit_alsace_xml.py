#!/usr/bin/env python3
"""Rapproche les affiliations Pair / Archéologie Alsace de leurs notices TEI.

Lecture seule : accepte des .xml et .zip ; aucun corpus source n'est publié.
Usage : python3 -m scripts.audit_alsace_xml fichiers.xml fichier.zip --output-dir /tmp/audit-alsace
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
LABELS = {'Pair': ('AFF-0047', 57), 'Archéologie Alsace': ('AFF-0048', 124)}
SUCCESSION_YEAR = 2020


def _documents(paths):
    """Yield (nom source, contenu) ; ignorer les copies binaires identiques."""
    seen = set()
    for path in map(Path, paths):
        if path.suffix.casefold() == '.zip':
            with zipfile.ZipFile(path) as archive:
                inputs = [(f'{path.name}!{name}', archive.read(name)) for name in archive.namelist()
                          if name.lower().endswith('.xml') and not name.startswith('__MACOSX/')]
        else:
            inputs = [(path.name, path.read_bytes())]
        for name, data in inputs:
            sha = hashlib.sha256(data).hexdigest()
            if sha not in seen:
                seen.add(sha)
                yield name, data, sha


def _date_years(notice):
    return [s.strip() for date in notice.findall(f'.//{TEI}ab[@type="meta-archeo"]/{TEI}date')
            if (s := ''.join(date.itertext()).strip())]


def audit_xml_documents(paths, expected=None):
    expected = expected or {name: count for name, (_, count) in LABELS.items()}
    records, sources = [], []
    for name, data, sha in _documents(paths):
        root = ET.parse(io.BytesIO(data)).getroot()
        notices = root.findall(f'.//{TEI}div[@subtype="notice"]')
        before = len(records)
        for notice_number, notice in enumerate(notices, 1):
            for aff in notice.findall(f'.//{TEI}affiliation'):
                label = ' '.join(''.join(aff.itertext()).split())
                if label not in LABELS:
                    continue
                years = _date_years(notice)
                if not years or any(not year.isdigit() or int(year) >= SUCCESSION_YEAR for year in years):
                    raise ValueError(f'{name} : notice {notice_number}, année incompatible : {years}')
                head = notice.find(f'./{TEI}head[@style="T_2"]')
                place = []
                title = ''
                if head is not None:
                    place = [' '.join(''.join(t.itertext()).split()) for t in
                             head.findall(f'./{TEI}index/{TEI}term[@type="orig"]')]
                    title = ((head.text or '') + ''.join(c.tail or '' for c in head)).strip()
                records.append({
                    'fichier_xml': name,
                    'sha256': sha,
                    'notice_numero': notice_number,
                    'localites': '; '.join(place),
                    'titre_notice': title,
                    'annees_operation': '; '.join(years),
                    'affiliation_xml_id': aff.get(XMLID) or '',
                    'libelle_affiliation': label,
                    'affiliation_source': LABELS[label][0],
                    'org_historique': 'ORG-0093',
                })
        found = records[before:]
        sources.append({
            'fichier_xml': name, 'sha256': sha, 'notices': len(notices),
            'pair': sum(r['libelle_affiliation'] == 'Pair' for r in found),
            'archeologie_alsace': sum(r['libelle_affiliation'] == 'Archéologie Alsace' for r in found),
        })
    actual = Counter(r['libelle_affiliation'] for r in records)
    if dict(actual) != expected:
        raise ValueError(f'Écart au maître : effectifs XML {dict(actual)}, attendus {expected}')
    if len({(r['fichier_xml'], r['affiliation_xml_id']) for r in records}) != len(records):
        raise ValueError('Identifiants XML d’affiliation dupliqués dans un fichier')
    return {
        'status': 'reconciliation_complete',
        'expected': expected,
        'actual': dict(actual),
        'total': len(records),
        'historic_authority': 'ORG-0093',
        'chronological_basis': 'annees_operation_anterieures_au_11_decembre_2020',
        'caveat': 'Les dates de publication et de révision des XML peuvent être postérieures à 2020 ; les années d’opération attestent le contexte historique des notices, pas les dates des affiliations administratives actuelles.',
        'sources': sources,
        'occurrences': records,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path, nargs='+')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    result = audit_xml_documents(args.sources)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'audit-alsace-xml.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (args.output_dir / 'affiliations-alsace-xml.csv').open('w', encoding='utf-8-sig', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(result['occurrences'][0]), delimiter=';')
        writer.writeheader()
        writer.writerows(result['occurrences'])
    print(json.dumps({'statut': result['status'], 'total': result['total'],
                      'counts': result['actual']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
