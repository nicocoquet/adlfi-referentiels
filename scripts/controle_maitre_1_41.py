#!/usr/bin/env python3
"""Contrôle non destructif du maître 1.41 (scission Archéologie Alsace).

Usage :
  python3 -m scripts.controle_maitre_1_41 MAITRE.xlsx --report /tmp/controle-1-41.json
  python3 -m scripts.controle_maitre_1_41 MAITRE.xlsx --preview-json /tmp/organismes-1-41.json
L'écriture n'affecte jamais les sources, ni docs/data/organismes.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from .export_organismes import build, parse_workbook


def one(rows, field, ident):
    values = [r for r in rows if r.get(field) == ident]
    if len(values) != 1:
        raise ValueError(f'{field}={ident} : {len(values)} enregistrement(s)')
    return values[0]


def check(sheets: dict, *, check_totals: bool = True) -> dict:
    orgs = sheets['Organismes']
    ser = sheets['Services']
    affs = sheets['Affiliations_sources']
    corrs = sheets['Correspondances_affiliations']
    rels = sheets['Relations']
    history = sheets['Historique']
    statuses = sheets['Statuts_historiques']
    problems = []

    def expect(condition, msg):
        if not condition:
            problems.append(msg)

    if check_totals:
        for name, actual, expected in [
            ('ORG', len(orgs), 654), ('SER', len(ser), 166),
            ('AFF', len(affs), 1580), ('COR', len(corrs), 2140),
            ('REL (ORG)', len(rels), 303),
        ]:
            expect(actual == expected, f'{name} : {actual}, attendu {expected}')

    old = one(orgs, 'organisme_id', 'ORG-0093')
    new = one(orgs, 'organisme_id', 'ORG-0675')
    for org, values in [
        (old, {'nom_normalise':'Archéologie Alsace', 'type_organisme':'etablissement_public',
               'secteur_institutionnel':'public', 'date_debut':'2006-09-01',
               'date_fin':'2020-12-11', 'actif':'non', 'affichage_catalogue':'oui'}),
        (new, {'nom_normalise':'Archéologie Alsace', 'type_organisme':'syndicat_mixte',
               'secteur_institutionnel':'public', 'date_debut':'2020-12-11',
               'actif':'oui', 'affichage_catalogue':'oui',
               'url_site_officiel':'https://www.archeologie.alsace/'})]:
        for key, val in values.items():
            expect(org.get(key) == val, f"{org['organisme_id']}.{key}: {org.get(key)!r}, attendu {val!r}")
        expect(not org.get('echelon_territorial'),
               f"{org['organisme_id']} : échelon institutionnel imputé sans preuve")
    expect(not old.get('url_site_officiel'), 'ORG-0093 : URL actuelle conservée sur l’ancienne autorité')
    expect(not new.get('date_fin'), 'ORG-0675 : date de fin non prévue')

    for ident, field, expected in [
        ('ORG-0249','type_organisme','epci'),
        ('ORG-0249','echelon_territorial','intercommunal'),
        ('ORG-0429','echelon_territorial','communal'),
        ('ORG-0650','type_organisme','collectivite_territoriale'),
        ('ORG-0650','echelon_territorial','metropolitain'),
    ]:
        r = one(orgs,'organisme_id',ident)
        expect(r.get(field)==expected,f'{ident}.{field} : attendu {expected}')

    pair = one(affs,'affiliation_source_id','AFF-0047')
    alsace = one(affs,'affiliation_source_id','AFF-0048')
    for r, label, count in [(pair,'Pair',57),(alsace,'Archéologie Alsace',124)]:
        expect(r.get('organisme_id') == 'ORG-0093', f"{r.get('affiliation_source_id')} : ORG déplacée")
        expect(r.get('libelle_source') == label, f'{label} : libellé source modifié')
        expect(int(r.get('occurrences') or 0) == count, f'{label} : occurrences modifiées')

    for corr_id, aid in [('COR-0054','AFF-0047'),('COR-0055','AFF-0048')]:
        r=one(corrs,'correspondance_id',corr_id)
        expect(r.get('affiliation_source_id') == aid, f'{corr_id} : mauvais AFF')
        expect(r.get('organisme_id') == 'ORG-0093', f'{corr_id} : transfert vers successeur')
        expect(r.get('statut_validation') in ('validee','valide'), f'{corr_id} : validation perdue')
    expect(not any(r.get('organisme_id')=='ORG-0675' for r in corrs),
           'ORG-0675 : des correspondances historiques lui ont été transférées')

    succession=one(rels,'relation_id','REL-0305')
    for key, val in {
        'organisme_source_id':'ORG-0093','organisme_cible_id':'ORG-0675',
        'type_relation':'succession_institutionnelle','date_debut':'2020-12-11',
        'statut_validation':'valide',
    }.items():
        expect(succession.get(key)==val, f'REL-0305.{key} : attendu {val}')
    questionable=one(rels,'relation_id','REL-0054')
    expect(questionable.get('statut_validation')=='a_verifier',
           'REL-0054 : relation historique promue sans vérification')
    expect(questionable.get('organisme_source_id')=='ORG-0093',
           'REL-0054 : transfert silencieux vers le successeur')

    h=one(history,'historique_id','HIS-0003')
    expect(h.get('organisme_id')=='ORG-0093','HIS-0003 : autorité déplacée')
    expect(h.get('date_debut')=='2006-09-01' and h.get('date_fin')=='2016-10-14',
           'HIS-0003 : chronologie de la dénomination inexacte')

    legal={
        'STH-0003':('ORG-0093','institution_interdepartementale'),
        'STH-0004':('ORG-0675','syndicat_mixte_ouvert'),
        'STH-0005':('ORG-0249','communaute_agglomeration'),
        'STH-0006':('ORG-0650','collectivite_statut_particulier'),
    }
    for ident, (org_id, form) in legal.items():
        r=one(statuses,'statut_historique_id',ident)
        expect(r.get('organisme_id')==org_id and r.get('forme_juridique')==form,
               f'{ident} : statut historique ou identité incorrects')
        expect(r.get('statut_validation')=='valide',f'{ident} : statut non validé')
        expect((r.get('source_url') or '').startswith('https://'),f'{ident} : source manquante')

    org_ids=[r['organisme_id'] for r in orgs if r.get('organisme_id')]
    relation_ids=[r['relation_id'] for r in rels if r.get('relation_id')]
    expect(len(set(org_ids))==len(org_ids),'Identifiants ORG dupliqués')
    expect(len(set(relation_ids))==len(relation_ids),'Identifiants de relation dupliqués')
    for r in rels:
        expect(r.get('organisme_source_id') in org_ids and r.get('organisme_cible_id') in org_ids,
               f"{r.get('relation_id')} : référence ORG orpheline")

    if problems:
        raise ValueError('Migration 1.41 invalide :\n- ' + '\n- '.join(problems))
    return {
        'status':'ok',
        'counts':{'organismes':len(orgs),'services':len(ser),
                  'affiliations':len(affs),'correspondances':len(corrs),
                  'relations_organismes':len(rels)},
        'historical':{'org':'ORG-0093','aff_0047':57,'aff_0048':124,
                      'total_occurrences':181,'siren':'200006336'},
        'successor':{'org':'ORG-0675','siren':'200094746','start':'2020-12-11',
                     'affiliations_linked':0},
        'identity_relation':'REL-0305',
        'pending': ['REL-0054 (relation administrative anachronique)',
                    'identification du logo ORG-0093','échelon institutionnel des deux entités'],
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--report',type=Path)
    parser.add_argument('--preview-json',type=Path)
    args=parser.parse_args(argv)
    report=check(parse_workbook(args.source))
    report['source_filename']=args.source.name
    report['source_sha256']=hashlib.sha256(args.source.read_bytes()).hexdigest()
    if args.preview_json:
        exported=build(args.source)
        assert exported['totals']['authorities']==820
        assert exported['totals']['catalog_included']==615
        assert len(exported['relations'])==522
        args.preview_json.parent.mkdir(parents=True,exist_ok=True)
        args.preview_json.write_text(
            json.dumps(exported,ensure_ascii=False,indent=2),encoding='utf-8')
        report['preview_json_sha256']=hashlib.sha256(args.preview_json.read_bytes()).hexdigest()
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
