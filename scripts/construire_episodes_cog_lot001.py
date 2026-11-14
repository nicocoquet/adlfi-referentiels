#!/usr/bin/env python3
"""Construit des épisodes administratifs COG à partir de preuves de mouvements.

Ce graphe est PARTIEL : il décrit les états avant/après des mouvements archivés,
pas des intervalles exhaustifs ni des identités validées Pactols. Aucun contour.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
from datetime import date
from pathlib import Path

COLUMNS_TRANSITIONS={'ark_pactols','libelle_documentaire','code_avant','code_apres',
                     'date_jointive','nombre_evenements_exacts','codes_MOD','preuve_lignes_cog',
                     'statut_validation_pactols'}
COLUMNS_PARTICULIERS={'dossier','ark_pactols','DATE_EFF','MOD','TYPECOM_AV','COM_AV','LIBELLE_AV',
                      'TYPECOM_AP','COM_AP','LIBELLE_AP','statut_validation_pactols'}


def read_csv(path,expected):
    with path.open('r',encoding='utf-8-sig',newline='') as file:
        rd=csv.DictReader(file,delimiter=';')
        if not expected <= set(rd.fieldnames or []):
            raise ValueError('En-têtes incomplets : '+str(path))
        return list(rd)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def key_str(entry):return f"{entry['typecom']}|{entry['code']}|{entry['libelle']}"

def key_id(prefix,part):
    return prefix+hashlib.sha256(part.encode('utf8')).hexdigest()[:16]


def from_row(row,dossier,ark):
    dt=row['DATE_EFF']
    if date.fromisoformat(dt).isoformat()!=dt:
        raise ValueError('Date mouvement invalide : '+dt)
    mode=row['MOD']
    if mode not in ('32','41'):
        raise ValueError('MOD non pris en charge dans ce lot: '+mode)
    out={'dossier':dossier,'ark_pactols_documentaire':ark,'date_effet':dt,
         'mod':mode,'avant':{'typecom':row['TYPECOM_AV'],'code':row['COM_AV'],'libelle':row['LIBELLE_AV']},
         'apres':{'typecom':row['TYPECOM_AP'],'code':row['COM_AP'],'libelle':row['LIBELLE_AP']},
         'statut_preuve':'mouvement_cog_atteste','statut_alignement_pactols_cog':'non_valide'}
    for v in (out['avant'],out['apres']):
        if v['typecom'] not in ('COM','COMA','COMD','ARM') or not v['code'] or not v['libelle']:
            raise ValueError('Etat COG incomplet : '+str(v))
    return out


def construire(transitions,particuliers,sortie):
    source_rows=read_csv(transitions,COLUMNS_TRANSITIONS)
    special_rows=read_csv(particuliers,COLUMNS_PARTICULIERS)
    if len(source_rows)!=8 or len(special_rows)!=15:
        raise ValueError('Lot attendu : huit transitions et quinze lignes particulières')
    moves=[]
    for r in source_rows:
        if (r['codes_MOD']!='41' or r['nombre_evenements_exacts']!='1' or
            r['statut_validation_pactols']!='non_valide'):
            raise ValueError('La transition 41 ne satisfait pas le contrat de preuve/non-validation')
        evidence=json.loads(r['preuve_lignes_cog'])
        if len(evidence)!=1:raise ValueError('Une preuve directe exacte attendue')
        e=evidence[0]
        if (e['COM_AV']!=r['code_avant'] or e['COM_AP']!=r['code_apres'] or
            e['DATE_EFF']!=r['date_jointive'] or e['MOD']!='41' or
            e['TYPECOM_AV']!='COM' or e['TYPECOM_AP']!='COM'):
            raise ValueError('Preuve directe COG incohérente : '+r['ark_pactols'])
        moves.append(from_row(e,r['libelle_documentaire'],r['ark_pactols']))
    for r in special_rows:
        if r['MOD']!='32' or r['statut_validation_pactols']!='non_valide':
            raise ValueError('Mouvement spécial de statut inattendu')
        moves.append(from_row(r,r['dossier'],r['ark_pactols']))
    # Chaque ligne est un arc d'état administratif, pas une opération distincte.
    groups=collections.defaultdict(list)
    for m in moves:
        groups[(m['dossier'],m['date_effet'],m['mod'])].append(m)
    if len(groups)!=11:
        raise ValueError('Onze opérations attendues (8 MOD41 + 3 MOD32)')
    operations=[]; states={};edges=[]
    for (dossier,dt,mod),members in sorted(groups.items()):
        operation_id=key_id('OP-',f'{dossier}|{dt}|{mod}')
        ark_set={x['ark_pactols_documentaire'] for x in members}
        if len(ark_set)!=1:raise ValueError('ARK différents pour une opération COG')
        operations.append({'id':operation_id,'dossier':dossier,'date_effet':dt,
                'mod':mod,'nombre_lignes_mouvement':len(members),
                'ark_pactols_documentaire':next(iter(ark_set)),
                'statut_lien_pactols_cog':'non_valide',
                'statut_validation_evenement':'confirme_par_preuves_COG'})
        for move in members:
            edge={'operation_id':operation_id,'date_effet':dt,'mod':mod,
                  'dossier':dossier,'statut':'preuve_mouvement_COG'}
            for side in ('avant','apres'):
                record=move[side]
                state_id=key_id('ETAT-',dossier+'|'+key_str(record))
                if state_id not in states:
                    states[state_id]={'id':state_id,'dossier':dossier,
                         **record,'entrees_aux_dates_evenements':[],
                         'sorties_aux_dates_evenements':[],
                         'periode_validite_officielle_complete':False,
                         'geometrie_historique_validee':False}
                state=states[state_id]
                k='sorties_aux_dates_evenements' if side=='avant' else 'entrees_aux_dates_evenements'
                if dt not in state[k]:state[k].append(dt)
                edge['etat_'+side+'_id']=state_id
            edge['id']=key_id('ARC-',operation_id+'|'+edge['etat_avant_id']+'|'+edge['etat_apres_id'])
            edges.append(edge)
    for record in states.values():
        record['entrees_aux_dates_evenements'].sort()
        record['sorties_aux_dates_evenements'].sort()
        # Ces bornes sont partielles, pas des DATE_DEBUT/DATE_FIN COG certifiées.
    if len({x['id'] for x in edges})!=len(edges):
        raise ValueError('Lignes de mouvement COG dupliquées')
    ref={'schema_version':'0.1.0','statut':'recette_non_validante',
         'perimetre':'lot_001_10_dossiers_historiques',
         'sources':[{'fichier':x.name,'sha256':sha(x)} for x in (transitions,particuliers)],
         'identifiants_etats':'identifiants locaux issus du dossier + TYPECOM + COM + libelle ; PAS des identifiants publics COG',
         'note':'Episodes incomplets: uniquement états et transitions présents dans les 23 preuves; pas de datation exhaustive ni de géométrie historique.',
         'operations':operations,'etats_administratifs':sorted(states.values(),key=lambda x:x['id']),
         'arcs_evenements':sorted(edges,key=lambda x:x['id'])}
    counts=collections.Counter(e['mod'] for e in operations)
    result={'schema_version':'0.1.0','statut':'audit_non_validant',
            'nombre_lignes_mouvements':len(moves),
            'operations_distinctes':len(operations),
            'operations_mod':dict(sorted(counts.items())),
            'etats_admin_distincts_dans_le_lot':len(states),
            'liens_pactols_nouveaux_valides':0,
            'geometries_historiques_validees':0,
            'source_sha256':{x.name:sha(x) for x in (transitions,particuliers)},
            'avertissement':'Etat administratif partiel: vérification nécessaire contre la totalité du COG depuis 1943 avant datation complète.'}
    sortie.mkdir(parents=True,exist_ok=True)
    (sortie/'graphe-episodes-cog-lot001.json').write_text(json.dumps(ref,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (sortie/'rapport-episodes-cog-lot001.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--transitions',required=True,type=Path)
    p.add_argument('--particuliers',required=True,type=Path)
    p.add_argument('--sortie',required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(construire(args.transitions,args.particuliers,args.sortie),ensure_ascii=False,indent=2))
if __name__=='__main__':main()

