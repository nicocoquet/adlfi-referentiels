"""Resolve the sector of AdlFI services from documented institutional attachments.

The resulting sector is *not* a status at a given date: the full set of validated
'rattachement_service' relations is examined without projecting it retrospectively.
Only the XLSX source records institutional attachments; this module derives values
for the publication JSON without changing the editorial master.
"""
from __future__ import annotations

from collections import Counter, defaultdict


SECTORS = frozenset({'public', 'prive', 'mixte'})


def apply_sector_inheritance(authorities: list[dict], relations: list[dict]) -> dict:
    """Enrich SER classifications and return a summary of resolutions.

    Each derived value has an auditable set of originating ORGs and relation IDs.
    A graph cycle, inconsistent source, or competing sectors blocks publication.
    SERs without a valid attachment remain unresolved, rather than being assigned
    the sector of a successor or any unverified institution.
    """
    by_id = {authority['id']: authority for authority in authorities}
    if len(by_id) != len(authorities):
        raise ValueError('Identifiants d’autorités dupliqués')

    attached = defaultdict(list)
    for rel in relations:
        if rel.get('type') != 'rattachement_service' or rel.get('validation') != 'valide':
            continue
        source, target, relation_id = rel['source'], rel['target'], rel['id']
        if source not in by_id or target not in by_id:
            raise ValueError(f'Rattachement {relation_id} avec autorité inconnue')
        if by_id[source]['kind'] != 'SER':
            raise ValueError(f'Rattachement {relation_id} dont la source n’est pas un SER')
        attached[source].append((target, relation_id))

    def paths_to_org(service_id: str, ancestors: tuple[str, ...] = ()) -> list[tuple[str, tuple[str, ...]]]:
        if service_id in ancestors:
            raise ValueError('Cycle de rattachements SER : ' + ' → '.join((*ancestors, service_id)))
        paths = []
        for target, relation_id in attached[service_id]:
            if by_id[target]['kind'] == 'ORG':
                paths.append((target, (relation_id,)))
            elif by_id[target]['kind'] == 'SER':
                for org_id, nested in paths_to_org(target, (*ancestors, service_id)):
                    paths.append((org_id, (relation_id, *nested)))
            else:
                raise ValueError(f'Type d’autorité invalide : {target}')
        return paths

    counts = Counter()
    unresolved = []
    for authority in authorities:
        if authority['kind'] != 'SER':
            continue
        service_id = authority['id']
        paths = paths_to_org(service_id)
        if not paths:
            authority['classification']['sector'] = None
            authority['classification']['sector_origin'] = {
                'method': 'unresolved', 'reason': 'no_validated_attachment'}
            authority['quality']['sector_unresolved'] = True
            unresolved.append(service_id)
            counts['unresolved'] += 1
            continue

        sectors = {}
        for org_id, _ in paths:
            sector = by_id[org_id]['classification'].get('sector')
            if sector not in SECTORS:
                raise ValueError(f'Secteur inconnu pour {org_id} (rattachement de {service_id}) : {sector!r}')
            sectors[org_id] = sector
        distinct = set(sectors.values())
        if len(distinct) != 1:
            detail = ', '.join(f'{org_id}={sector}' for org_id, sector in sorted(sectors.items()))
            raise ValueError(f'Secteurs contradictoires pour {service_id} : {detail}')

        authority['classification']['sector'] = distinct.pop()
        authority['classification']['sector_origin'] = {
            'method': 'inherited',
            'scope': 'all_validated_attachments',
            'org_ids': sorted(sectors),
            'relation_ids': sorted({rid for _, route in paths for rid in route}),
        }
        authority['quality']['sector_unresolved'] = False
        counts[authority['classification']['sector']] += 1

    return {'counts': dict(sorted(counts.items())), 'unresolved_service_ids': sorted(unresolved)}
