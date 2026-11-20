#!/usr/bin/env python3
"""Préparer un export Organismes depuis le maître privé, sans publication.

Utilisation :
  python3 scripts/preparer_publication_organismes.py \
    /chemin/vers/maitre.xlsx --candidate /tmp/organismes-920.json \
    --report /tmp/organismes-audit.json --authorities 920 --org 725 \
    --ser 195 --relations 586 --require-rse-0252

Le classeur source n'est jamais modifié et le JSON public n'est jamais écrasé.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

if __package__:
    from .export_organismes import build
else:
    from export_organismes import build

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'docs' / 'data' / 'organismes.json'
REQUIRED_RELATION = {
    'id': 'RSE-0252', 'source': 'SER-0196',
    'target': 'ORG-0537', 'type': 'filiation_partielle',
    'start': '2022-01-01', 'end': None, 'validation': 'valide'
}
HISTORIC_TYPES = frozenset({
    'succession_institutionnelle', 'succession_service', 'succession',
    'succession_partielle', 'filiation_partielle',
    'fusion_constitutive', 'scission_constitutive',
})


def _index(records: list[dict], kind: str) -> dict:
    indexed = {}
    for record in records:
        ident = record.get('id')
        if not ident or ident in indexed:
            raise ValueError(f'{kind}: identifiant manquant ou dupliqué : {ident}')
        indexed[ident] = record
    return indexed


def _edges_without_cycle(edges: dict[str, set[str]]) -> None:
    colors = {}
    def visit(node: str) -> None:
        state = colors.get(node, 0)
        if state == 1:
            raise ValueError(f'Cycle historique détecté au niveau de {node}')
        if state == 2:
            return
        colors[node] = 1
        for successor in sorted(edges.get(node, ())):
            visit(successor)
        colors[node] = 2
    for node in sorted(edges):
        visit(node)


def audit(baseline: dict[str, Any], candidate: dict[str, Any],
          *, expected: dict[str, int] | None = None,
          require_rse_0252: bool = False) -> dict[str, Any]:
    if baseline.get('schema_version') != candidate.get('schema_version'):
        raise ValueError('Version de schéma JSON modifiée')
    original = _index(baseline['authorities'], 'autorités publiques')
    new = _index(candidate['authorities'], 'autorités candidates')
    old_rel = _index(baseline['relations'], 'relations publiques')
    new_rel = _index(candidate['relations'], 'relations candidates')

    removed_authorities = sorted(set(original) - set(new))
    removed_relations = sorted(set(old_rel) - set(new_rel))
    if removed_authorities or removed_relations:
        raise ValueError(f'Identifiants supprimés : ORG/SER={removed_authorities[:6]}, REL/RSE={removed_relations[:6]}')
    changed_relations = sorted(x for x in old_rel if old_rel[x] != new_rel[x])
    if changed_relations:
        raise ValueError(f'Relations déjà publiées modifiées sans arbitrage : {changed_relations[:12]}')

    graph = {}
    for rel in new_rel.values():
        source, target, typ = rel.get('source'), rel.get('target'), rel.get('type')
        if source not in new or target not in new:
            raise ValueError(f"{rel['id']} : référence vers une autorité absente")
        if source == target:
            raise ValueError(f"{rel['id']} : relation réflexive")
        source_kind, target_kind = new[source]['kind'], new[target]['kind']
        if rel['id'].startswith('REL-'):
            if source_kind != 'ORG' or target_kind != 'ORG':
                raise ValueError(f"{rel['id']} : schéma REL non ORG→ORG")
        elif rel['id'].startswith('RSE-'):
            if source_kind != 'SER' or target_kind not in ('ORG', 'SER'):
                raise ValueError(f"{rel['id']} : schéma RSE invalide")
        else:
            raise ValueError(f"Identifiant relationnel non reconnu : {rel['id']}")
        if typ in HISTORIC_TYPES and rel.get('validation') in ('valide','validee','validée'):
            graph.setdefault(source, set()).add(target)
    _edges_without_cycle(graph)

    if require_rse_0252:
        got = new_rel.get('RSE-0252')
        if got != REQUIRED_RELATION:
            raise ValueError('RSE-0252 absente ou différente de la filiation CRP2A validée')

    kinds = Counter(a['kind'] for a in new.values())
    counts = {'authorities': len(new), 'org': kinds['ORG'], 'ser': kinds['SER'],
              'relations': len(new_rel)}
    for key, count in (expected or {}).items():
        if counts.get(key) != count:
            raise ValueError(f'Effectif {key}: {counts.get(key)} au lieu de {count}')

    altered_authorities = sorted(x for x in original if original[x] != new[x])
    return {
        'status': 'CANDIDAT_NON_PUBLIE',
        'counts': counts,
        'baseline': {'authorities': len(original), 'relations': len(old_rel)},
        'new_authority_ids': sorted(set(new) - set(original)),
        'new_relation_ids': sorted(set(new_rel) - set(old_rel)),
        'updated_existing_authority_ids': altered_authorities,
        'unchanged_prior_relations': len(old_rel),
        'relation_rse_0252': bool(new_rel.get('RSE-0252') == REQUIRED_RELATION),
        'source': candidate.get('provenance', {}),
    }


def safe_destination(raw: Path, source: Path) -> Path:
    dest = raw.expanduser().resolve()
    if dest.suffix.lower() != '.json':
        raise ValueError('La destination doit être un JSON')
    if dest == source.resolve() or dest == PUBLIC.resolve():
        raise ValueError('Refus d’écraser le maître ou le JSON public')
    if PUBLIC.parent.resolve() in dest.parents:
        raise ValueError('Interdiction de produire le candidat dans docs/data')
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('master', type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--authorities', type=int)
    parser.add_argument('--org', type=int)
    parser.add_argument('--ser', type=int)
    parser.add_argument('--relations', type=int)
    parser.add_argument('--require-rse-0252', action='store_true')
    args = parser.parse_args()

    master = args.master.expanduser().resolve()
    if not master.is_file() or master.suffix.lower() != '.xlsx':
        parser.error('Maître XLSX introuvable')
    candidate_path = safe_destination(args.candidate, master)
    report_path = safe_destination(args.report, master)
    if report_path == candidate_path:
        parser.error('Le candidat et le rapport doivent avoir des chemins distincts')
    baseline = json.loads(PUBLIC.read_text(encoding='utf-8'))
    candidate = build(master)
    expected = {key: getattr(args, key) for key in ('authorities','org','ser','relations')
                if getattr(args, key) is not None}
    result = audit(baseline, candidate, expected=expected,
                   require_rse_0252=args.require_rse_0252)

    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'candidate': str(candidate_path), 'report': str(report_path),
                      'counts': result['counts'],
                      'new_authorities': len(result['new_authority_ids']),
                      'new_relations': len(result['new_relation_ids'])},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
