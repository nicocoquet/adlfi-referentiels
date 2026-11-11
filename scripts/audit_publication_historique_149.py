#!/usr/bin/env python3
"""Audit bloquant du JSON candidat 1.49 avant sa publication.

Usage : python3 scripts/audit_publication_historique_149.py \
        docs/data/organismes.json /chemin/vers/organismes-candidat.json

Le script ne modifie aucun fichier et ne publie jamais le XLSX privé.
"""
from __future__ import annotations
import collections
import copy
import json
import sys
from pathlib import Path

SOURCE_FILE='AdlFI_referentiel_1-49_20261111_Historique_consolide.xlsx'
SOURCE_SHA='41c39072771435c4b5d18eccfee7483aa82af5f3f43c8f06d4d4c8cd13261642'

def audit(baseline:dict,candidate:dict,repo_root:Path)->dict:
    for key in ('schema_version','dataset','totals','locations'):
        assert baseline[key]==candidate[key],f'Changement inattendu : {key}'
    # Les relations ont des identifiants pérennes : leur ordre dans le JSON
    # n'a aucune signification institutionnelle. Le JSON 1.47 place notamment
    # REL-0306 après RSE-0220 ; l'exporteur 1.49 réunit les REL avant les RSE.
    # Vérifier les mêmes identifiants ET les mêmes valeurs, sans doublons.
    def relations_by_id(relations):
        indexed = {rel['id']: rel for rel in relations}
        assert len(indexed) == len(relations), 'Identifiants de relations dupliqués'
        return indexed
    original_relations = relations_by_id(baseline['relations'])
    candidate_relations = relations_by_id(candidate['relations'])
    assert original_relations.keys() == candidate_relations.keys(), 'Relations ajoutées ou supprimées'
    for relation_id, original in original_relations.items():
        assert candidate_relations[relation_id] == original, f'Relation modifiée : {relation_id}'
    assert len(candidate['authorities'])==829
    assert candidate['totals']['organismes']==655
    assert candidate['totals']['services']==174
    assert candidate['totals']['catalog_included']==591
    assert len(candidate['relations'])==531
    assert candidate.get('provenance',{}).get('source_filename')==SOURCE_FILE,'Mauvais XLSX maître source'
    assert candidate['provenance']['source_sha256']==SOURCE_SHA,'Empreinte du maître 1.49 différente'
    old={x['id']:x for x in baseline['authorities']}
    new={x['id']:x for x in candidate['authorities']}
    assert old.keys()==new.keys(),'Liste ORG/SER modifiée'
    additions=[];changed_media=[];updated_old=[]
    for ident in old:
        original=copy.deepcopy(old[ident]);updated=copy.deepcopy(new[ident])
        old_history=original['names'].pop('history')
        new_history=updated['names'].pop('history')
        old_media=original['presentation'].pop('media')
        new_media=updated['presentation'].pop('media')
        assert original==updated,f'Une donnée hors historique/média a changé : {ident}'
        assert len(new_history)>=len(old_history),f'Historique raccourci : {ident}'
        for i,(old_form,new_form) in enumerate(zip(old_history,new_history)):
            comparable={k:v for k,v in new_form.items() if k not in ('id','source')}
            assert comparable==old_form or new_form==old_form,f'Ancien historique modifié : {ident}, index {i}'
            if comparable==old_form and new_form!=old_form:updated_old.append((ident,i))
        additions.extend((ident,x) for x in new_history[len(old_history):])
        if old_media!=new_media:
            expected=f'assets/organismes/{ident}.jpg'
            canonical=repo_root/'docs'/expected
            assert new_media.get('logo')==expected and canonical.is_file(),f'Média perdu ou inattendu : {ident} : {old_media} → {new_media}'
            changed_media.append(ident)
    assert len(additions)==58,f'Nombre d’historiques ajoutés incorrect : {len(additions)}'
    ids=[h['id'] for _,h in additions]
    assert sorted(ids)==[f'HIS-{i:04d}' for i in range(67,125)],'Identifiants HIS incorrects'
    assert len(set(ids))==58
    assert len({ident for ident,_ in additions})==57
    assert collections.Counter(x['type'] for _,x in additions)=={
        'designation_historique_organe':48,'ancienne_denomination':8,'variante_denomination':2}
    assert collections.Counter(x['validation'] for _,x in additions)=={'valide':55,'a_verifier':3}
    assert {i for i,x in additions if x['validation']=='a_verifier'}=={'ORG-0409','ORG-0590','ORG-0670'}
    assert all(x['source'] and x['source'].startswith('https://') for _,x in additions)
    assert all(not x['start'] and x['end']=='2015-03-21'
               for _,x in additions if x['type']=='designation_historique_organe')
    assert sum(len(r['names']['history']) for r in candidate['authorities'] if r['kind']=='ORG')==124
    assert sum(len(r['names']['history']) for r in candidate['authorities'] if r['kind']=='SER')==72
    return {'authorities':len(new),'new_history':len(additions),'orgs_touched':len({i for i,_ in additions}),
            'older_history_enriched_with_source_or_id':len(updated_old),
            'canonical_logo_upgrades':changed_media}

def main():
    if len(sys.argv)!=3:raise SystemExit('Usage : audit_publication_historique_149.py baseline.json candidat.json')
    old=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    new=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
    stats=audit(old,new,Path(__file__).resolve().parents[1])
    print('AUDIT 1.49 OK',json.dumps(stats,ensure_ascii=False))

if __name__=='__main__':main()
