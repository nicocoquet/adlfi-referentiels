#!/usr/bin/env python3
"""Recette bloquante du JSON 1.51, sur le socle de validation historique 1.50.

Usage : python3 scripts/recette_publication_organismes_151.py docs/data/organismes.json
Aucune modification du XLSX privé ou du JSON n'est effectuée par ce contrôle.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

if __package__:
    from .recette_publication_organismes_150 import validate_candidate
else:
    from recette_publication_organismes_150 import validate_candidate

NEW = {
    'REL-0341': ('ORG-0069', 'ORG-0120'),
    'REL-0342': ('ORG-0419', 'ORG-0120'),
    'REL-0343': ('ORG-0521', 'ORG-0120'),
    'REL-0344': ('ORG-0355', 'ORG-0701'),
}
MASTER='AdlFI_referentiel_1-51_affiliations_federales_20261120_RECETTE.xlsx'
SHA256='af3ee809099a28373a5b183afe70af27066aeb3d23e1776fd501a192be91e1d4'


def validate_151(data: dict) -> list[str]:
    errors = []
    def check(ok, label):
        if not ok:
            errors.append(label)

    relations=data.get('relations', [])
    authorities=data.get('authorities', [])
    rels={r.get('id'):r for r in relations}
    records={a.get('id'):a for a in authorities}
    check(len(relations)==598, '598 relations attendues (342 REL et 256 RSE)')
    check(sum(r.get('id','').startswith('REL-') for r in relations)==342,
          '342 relations ORG↔ORG attendues')
    check(sum(r.get('id','').startswith('RSE-') for r in relations)==256,
          '256 relations concernant les SER attendues')
    check(len([r for r in relations if r.get('type')=='affiliation_federale'])==6,
          'six affiliations fédérales dont les deux du maître 1.50')
    for ident, (src, dest) in NEW.items():
        relation=rels.get(ident, {})
        check((relation.get('source'),relation.get('target'),
               relation.get('type'),relation.get('validation'),
               relation.get('start'),relation.get('end')) ==
              (src,dest,'affiliation_federale','valide',None,None),
              f'{ident} : affiliation validée mais sans dates extrapolées')
    check(len(set(rels))==len(relations),'IDs de relations sans doublons')
    check(data.get('provenance',{}).get('source_filename')==MASTER,
          'Nom exact du maître 1.51')
    check(data.get('provenance',{}).get('source_sha256')==SHA256,
          'Empreinte SHA-256 du maître 1.51')
    check(records.get('ORG-0069',{}).get('website')=='https://casavo.fr/',
          'Site CASAVO officiellement identifié')
    check(records.get('ORG-0419',{}).get('geography',{}).get('cities_label')=='Hyères',
          'Ville du club IERO qualifiée')
    for ident in ('ORG-0355','ORG-0419','ORG-0521'):
        check(records.get(ident,{}).get('validation',{}).get('status')=='a_verifier',
              f'{ident} : qualification globale à vérifier préservée')
    # Conservation intégrale du contrat 1.50 sur les enregistrements historiques.
    historical=copy.deepcopy(data)
    historical['relations']=[r for r in relations if r.get('id') not in NEW]
    errors += ['1.50 : '+e for e in validate_candidate(historical)]
    return errors


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('json_file', type=Path)
    args=parser.parse_args(argv)
    data=json.loads(args.json_file.read_text(encoding='utf-8'))
    errors=validate_151(data)
    for error in errors:
        print('ÉCHEC : '+error, file=sys.stderr)
    if errors:
        return 2
    print('OK — maître 1.51 : 934 autorités, 598 relations, six affiliations fédérales et contrat 1.50 préservé')
    return 0


if __name__=='__main__':
    sys.exit(main())
