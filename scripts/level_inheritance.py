"""Résolution de l'échelon institutionnel effectif des SER (sans géocodage).

N'utilise que les relations de rattachement validées, non terminées et
applicables à la date d'export. Les valeurs non résolues restent explicites.
"""
from collections import Counter, defaultdict
from datetime import date

LEVELS = frozenset({'national', 'regional', 'departemental', 'intercommunal',
                    'communal', 'metropolitain', 'cantonal', 'provincial'})


def _current(rel, as_of):
    if rel.get('end'):
        return False
    start = rel.get('start')
    if not start:
        return True
    try:
        return date.fromisoformat(start) <= as_of
    except (ValueError, TypeError):
        try:
            return int(str(start)[:4]) <= as_of.year
        except (ValueError, TypeError):
            return False


def apply_level_inheritance(authorities, relations, *, as_of=None):
    """Résout classification.level, level_origin et quality.level_unresolved."""
    as_of = as_of or date.today()
    by_id = {a['id']: a for a in authorities}
    if len(by_id) != len(authorities):
        raise ValueError("Identifiants d'autorités dupliqués")
    edges = defaultdict(list)
    for rel in relations:
        if (rel.get('type') != 'rattachement_service' or
                rel.get('validation') not in ('valide', 'validee', 'validée') or
                not _current(rel, as_of)):
            continue
        src, dst = rel['source'], rel['target']
        if src not in by_id or dst not in by_id:
            raise ValueError(f"Rattachement {rel['id']} vers autorité inconnue")
        if by_id[src]['kind'] != 'SER':
            raise ValueError(f"Rattachement {rel['id']} : source non SER")
        edges[src].append((dst, rel['id']))

    def origins(ser_id, ancestors=()):
        if ser_id in ancestors:
            raise ValueError('Cycle de rattachements SER : ' + ' → '.join((*ancestors, ser_id)))
        paths = []
        for parent, rid in edges[ser_id]:
            if by_id[parent]['kind'] == 'ORG':
                paths.append((parent, (rid,)))
            elif by_id[parent]['kind'] == 'SER':
                paths.extend((org, (rid, *route))
                             for org, route in origins(parent, (*ancestors, ser_id)))
        return paths

    counts, unresolved = Counter(), []
    for authority in authorities:
        if authority['kind'] != 'SER':
            continue
        ident = authority['id']
        classification = authority['classification']
        explicit = classification.get('level')
        if explicit is not None and explicit not in LEVELS:
            raise ValueError(f'Échelon explicite inconnu pour {ident}: {explicit}')
        paths = origins(ident)
        if explicit:
            classification['level_origin'] = {
                'method': 'explicit', 'field': 'Services.echelon_institutionnel'}
            authority['quality']['level_unresolved'] = False
            counts[explicit] += 1
            continue
        values = {org: by_id[org]['classification'].get('level') for org, _ in paths}
        distinct = set(values.values())
        if paths and len(distinct) == 1 and next(iter(distinct)) in LEVELS:
            level = distinct.pop()
            classification['level'] = level
            classification['level_origin'] = {
                'method': 'inherited',
                'org_ids': sorted(values),
                'relation_ids': sorted({rid for _, route in paths for rid in route})}
            authority['quality']['level_unresolved'] = False
            counts[level] += 1
        else:
            reason = ('no_validated_current_attachment' if not paths else
                      'missing_parent_level' if None in distinct else
                      'conflicting_parent_levels')
            classification['level'] = None
            classification['level_origin'] = {
                'method': 'unresolved', 'reason': reason, 'org_ids': sorted(values)}
            authority['quality']['level_unresolved'] = True
            counts['unresolved'] += 1
            unresolved.append(ident)
    return {'counts': dict(sorted(counts.items())),
            'unresolved_service_ids': sorted(unresolved)}
