#!/usr/bin/env python3
"""Comparer le JSON 1.52 proposé au résultat exact de l'exporteur officiel.

Usage, depuis un clone du dépôt :
  python3 scripts/comparer_export_officiel_organismes_152.py \
      '/chemin/AdlFI_referentiel_1-52_A02_A03_QUALIFIE_CANDIDAT.xlsx'

La comparaison est en lecture seule : le JSON publié et le XLSX privé ne
sont jamais écrits. Les dates du calcul sont fixées au 21 novembre 2026.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

if __package__:
    from .export_organismes import build
else:
    from export_organismes import build

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'docs/data/organismes.json'
SOURCE_NAME = 'AdlFI_referentiel_1-52_A02_A03_QUALIFIE_CANDIDAT.xlsx'
AS_OF_EPOCH = '1795219200'


def differences(expected, actual, path='$', limit=40):
    """Afficher au maximum les premiers chemins divergents, sans commentaires privés."""
    errors = []

    def compare(a, b, position):
        if len(errors) >= limit:
            return
        if type(a) is not type(b):
            errors.append(f'{position}: types différents ({type(a).__name__} / {type(b).__name__})')
        elif isinstance(a, dict):
            aa, bb = set(a), set(b)
            for key in sorted(aa - bb):
                errors.append(f'{position}.{key}: absent du JSON candidat')
            for key in sorted(bb - aa):
                errors.append(f'{position}.{key}: champ supplémentaire dans le JSON candidat')
            for key in sorted(aa & bb):
                compare(a[key], b[key], f'{position}.{key}')
                if len(errors) >= limit:
                    break
        elif isinstance(a, list):
            if len(a) != len(b):
                errors.append(f'{position}: tailles différentes ({len(a)} / {len(b)})')
            for i, (av, bv) in enumerate(zip(a, b)):
                compare(av, bv, f'{position}[{i}]')
                if len(errors) >= limit:
                    break
        elif a != b:
            # Les valeurs ne sont pas imprimées : seule la différence est localisée.
            errors.append(f'{position}: valeurs différentes')
    compare(expected, actual, path)
    return errors[:limit]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('maitre', type=Path, help='Chemin absolu vers le XLSX privé 1.52')
    args = parser.parse_args(argv)
    if args.maitre.name != SOURCE_NAME:
        parser.error(f'Nom de maître inattendu : {args.maitre.name}')
    if not args.maitre.is_file():
        parser.error(f'Classeur absent : {args.maitre}')
    os.environ['SOURCE_DATE_EPOCH'] = AS_OF_EPOCH
    expected = build(args.maitre)
    actual = json.loads(PUBLIC.read_text(encoding='utf-8'))
    errors = differences(expected, actual)
    if errors:
        print('ÉCHEC — le JSON candidat ne correspond pas à la sortie de l’exporteur officiel.')
        print('Premières divergences :')
        for e in errors:
            print(' -', e)
        return 1
    print('OK — sortie officielle et JSON candidat strictement équivalents.')
    print(f"{len(actual['authorities'])} autorités, {len(actual['relations'])} relations, "
          f"maître SHA-256 {actual['provenance']['source_sha256']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
