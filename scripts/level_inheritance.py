"""Résolution documentée de l'échelon institutionnel des SER (actuel ou historique).

Une date partielle représente un intervalle possible, jamais un jour précis.
L'héritage historique n'établit pas la stabilité de l'échelon sur toute la vie du SER.
"""
from collections import Counter, defaultdict
from datetime import date
from calendar import monthrange
import re

LEVELS = frozenset({'national', 'regional', 'departemental', 'intercommunal',
                    'communal', 'metropolitain', 'cantonal', 'provincial'})
VALID = {'valide', 'validee', 'validée'}
# Uniquement pour les SER explicitement qualifies dans le maitre prive.
NOT_APPLICABLE_TYPES = frozenset({
    'cellule_transfert_technologique',
    'service_archeologie_preventive_universitaire',
    'departement_entreprise_archeologie',
    'service_recherche',
    'composante_laboratoire',
    'centre_universitaire',
})


def _bound(raw, upper):
    if not raw:
        return date.max if upper else date.min
    if not re.fullmatch(r'\d{4}(?:-\d{2}(?:-\d{2})?)?', str(raw)):
        raise ValueError(f'Date non interprétable : {raw!r}')
    parts = [int(v) for v in str(raw).split('-')]
    y = parts[0]
    m = parts[1] if len(parts) > 1 else (12 if upper else 1)
    d = parts[2] if len(parts) > 2 else (monthrange(y, m)[1] if upper else 1)
    return date(y, m, d)


def _interval(obj):
    return _bound(obj.get('start'), False), _bound(obj.get('end'), True)


def _intersect(*periods):
    lo = max(x[0] for x in periods)
    hi = min(x[1] for x in periods)
    return (lo, hi) if lo <= hi else None


def _current(rel, as_of):
    # Le mode actuel exige une relation non terminee.
    try:
        return not rel.get('end') and _bound(rel.get('start'), False) <= as_of
    except ValueError:
        return False


def apply_level_inheritance(authorities, relations, *, as_of=None):
    """Résout classification.level, level_origin et quality.level_unresolved."""
    as_of = as_of or date.today()
    by_id = {a['id']: a for a in authorities}
    if len(by_id) != len(authorities):
        raise ValueError('Identifiants d’autorités dupliqués')
    edges = defaultdict(list)
    for rel in relations:
        if rel.get('type') != 'rattachement_service' or rel.get('validation') not in VALID:
            continue
        src, dst = rel['source'], rel['target']
        if src not in by_id or dst not in by_id:
            raise ValueError(f"Rattachement {rel['id']} vers autorité inconnue")
        if by_id[src]['kind'] != 'SER':
            raise ValueError(f"Rattachement {rel['id']} : source non SER")
        edges[src].append(rel)

    def origins(ident, historical, period=None, ancestors=()):
        if ident in ancestors:
            raise ValueError('Cycle de rattachements SER : '+' → '.join((*ancestors, ident)))
        paths, issues = [], []
        for r in edges[ident]:
            parent = by_id[r['target']]
            rid = r['id']
            if historical:
                try:
                    overlap = _intersect(period, _interval(r), _interval(parent.get('activity', {})))
                except ValueError:
                    issues.append(rid)
                    continue
                if overlap is None:
                    issues.append(rid)
                    continue
            else:
                if not _current(r, as_of):
                    continue
                overlap = None
            if parent['kind'] == 'ORG':
                paths.append((parent['id'], (rid,)))
            else:
                sub, err = origins(parent['id'], historical, overlap, (*ancestors, ident))
                paths.extend((org, (rid, *route)) for org, route in sub)
                issues.extend(err)
                if historical and not sub:
                    issues.append(rid)
        return paths, issues

    counts, unresolved = Counter(), []
    for authority in authorities:
        if authority['kind'] != 'SER':
            continue
        ident = authority['id']
        classification = authority['classification']
        explicit = classification.get('level')
        activity = authority.get('activity', {})
        historical = activity.get('active') is False
        applicability = classification.get('level_applicability')
        if applicability not in (None, 'not_applicable'):
            raise ValueError(f'Applicabilite echelon inconnue pour {ident}: {applicability!r}')
        if applicability == 'not_applicable' and classification.get('type') not in NOT_APPLICABLE_TYPES:
            raise ValueError(f'Type de service incompatible avec non applicable: {ident}')
        if applicability == 'not_applicable' and explicit:
            raise ValueError(f'Echelon explicite contradictoire avec non applicable: {ident}')
        if explicit is not None and explicit not in LEVELS:
            raise ValueError(f'Échelon explicite inconnu pour {ident}: {explicit}')
        if historical:
            try:
                period = _intersect(_interval(activity), (date.min, as_of))
            except ValueError:
                period = None
            paths, issues = origins(ident, True, period) if period else ([], [ident])
        else:
            paths, issues = origins(ident, False)
        values = {org: by_id[org]['classification'].get('level') for org, _ in paths}
        distinct = set(values.values())
        if explicit:
            level = explicit
            origin = {'method': 'explicit', 'field': 'Services.echelon_institutionnel'}
        elif applicability == 'not_applicable':
            level = None
            origin = {'method': 'not_applicable',
                      'reason': 'explicit_service_applicability_qualification',
                      'service_type': classification['type'],
                      'field': 'Qualification_echelons.applicabilite_echelon'}
        elif not issues and paths and len(distinct) == 1 and next(iter(distinct)) in LEVELS:
            level = next(iter(distinct))
            origin = {'method': 'inherited_historical' if historical else 'inherited',
                      'org_ids': sorted(values),
                      'relation_ids': sorted({rid for _, route in paths for rid in route})}
        else:
            level = None
            reason = ('historical_temporal_uncertainty' if issues else
                      ('no_validated_historical_attachment' if historical else
                       'no_validated_current_attachment') if not paths else
                      'missing_parent_level' if None in distinct else
                      'conflicting_parent_levels')
            origin = {'method': 'unresolved', 'reason': reason,
                      'org_ids': sorted(values)}
            if issues:
                origin['relation_ids_to_review'] = sorted(set(issues))
        classification['level'] = level
        classification['level_origin'] = origin
        applicable = origin['method'] != 'not_applicable'
        authority['quality']['level_unresolved'] = level is None and applicable
        counts['not_applicable' if not applicable else level or 'unresolved'] += 1
        if level is None and applicable:
            unresolved.append(ident)
    return {'counts': dict(sorted(counts.items())),
            'unresolved_service_ids': sorted(unresolved)}
