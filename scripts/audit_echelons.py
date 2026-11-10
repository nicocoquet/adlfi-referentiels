#!/usr/bin/env python3
"""Audit non destructif des échelons ORG du maître AdlFI.

Usage : python3 -m scripts.audit_echelons CHEMIN_MAITRE.xlsx --output-dir /tmp/audit
Les résultats ne sont jamais déposés automatiquement dans docs/ ni dans Git.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from .export_organismes import parse_workbook

LEVELS = frozenset({'communal', 'intercommunal', 'departemental', 'regional',
                    'national', 'cantonal', 'provincial', 'metropole', 'metropolitain'})
FOCUS_LEVELS = frozenset({'intercommunal', 'metropole', 'metropolitain'})
FOCUS_TYPES = frozenset({'epci', 'syndicat_mixte'})
# Dossier historique identifié hors des filtres génériques, à conserver jusqu'à résolution.
FOCUS_IDENTIFIERS = frozenset({'ORG-0093'})


def field(row: dict, key: str) -> str:
    return str(row.get(key) or '').strip()


def audit_org_rows(orgs: list[dict]) -> dict:
    """Signale des incompatibilités potentielles sans corriger les données."""
    issues = []
    focus = []
    levels = Counter()
    types = Counter()
    for row in orgs:
        ident, name = field(row, 'organisme_id'), field(row, 'nom_normalise')
        level, kind = field(row, 'echelon_territorial'), field(row, 'type_organisme')
        if not ident:
            continue
        if level:
            levels[level] += 1
        types[kind] += 1
        if level in FOCUS_LEVELS or kind in FOCUS_TYPES or ident in FOCUS_IDENTIFIERS:
            focus.append(ident)

        def add(code, explanation):
            issues.append({'organisme_id':ident, 'nom_normalise':name,
                           'type_organisme':kind, 'echelon_territorial':level,
                           'code_controle':code, 'motif':explanation,
                           'statut_validation':field(row, 'statut_validation'),
                           'affichage_catalogue':field(row, 'affichage_catalogue')})

        if level and level not in LEVELS:
            add('niveau_hors_vocabulaire', 'Valeur non reconnue du niveau institutionnel')
        if level == 'metropole':
            add('forme_vs_echelon', 'Métropole = forme institutionnelle, pas un niveau administratif distinct')
        if level == 'metropolitain':
            add('exception_metropolitaine', 'Vérifier le statut particulier et le modèle multi-niveaux')
        if kind == 'collectivite_territoriale' and level in ('intercommunal', 'metropole'):
            add('nature_collectivite_a_verifier', 'Possible EPCI ou groupement classé collectivité territoriale')
        if kind == 'epci' and level and level != 'intercommunal':
            add('epci_niveau_a_verifier', 'Un EPCI ordinaire doit relever du niveau intercommunal')
        if kind == 'syndicat_mixte' and level:
            add('syndicat_mixte_niveau_a_verifier', 'Le niveau ne se déduit pas de la seule qualité de syndicat mixte')
        if kind in ('entreprise', 'association') and level == 'national':
            add('portee_vs_niveau', 'Vérifier la confusion avec le territoire d’activité')
        if name.casefold().startswith('commune de ') and level and level != 'communal':
            add('commune_non_communale', 'Commune portée à un autre niveau institutionnel')
    return {
        'summary': {'organismes':len(orgs), 'levels_nonempty':sum(levels.values()),
                    'visible_with_level':sum(bool(field(r, 'echelon_territorial')) and
                        field(r, 'affichage_catalogue') in ('oui', 'inclure') for r in orgs),
                    'focus':len(focus), 'issues':len(issues)},
        'levels':dict(sorted(levels.items())), 'types':dict(sorted(types.items())),
        'focus_ids':sorted(focus), 'issues':issues}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    sheets = parse_workbook(args.source)
    result = audit_org_rows(sheets['Organismes'])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'rapport-echelon.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with (args.output_dir/'points-a-verifier.csv').open('w', newline='', encoding='utf-8-sig') as fh:
        columns = ['organisme_id','nom_normalise','type_organisme','echelon_territorial',
                   'code_controle','motif','statut_validation','affichage_catalogue']
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(result['issues'])
    print(json.dumps(result['summary'], ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
