#!/usr/bin/env python3
"""Recette des états COMD/COMA, confrontés aux événements 1943–2026 et au COG courant.

Décrit les dates d'événements et les statuts actifs au millésime 2026,
mais ne prétend pas restituer la durée complète d'un territoire historique.
Aucun lien Pactols–COG ou contour n'est créé.
"""
from __future__ import annotations
import argparse
from collections import defaultdict, Counter
import csv
import json
from pathlib import Path
from enrichir_periodes_cog_lot001 import norm, sha256, date_iso

FIELDS_ACTIVE={'TYPECOM','COM','LIBELLE','COMPARENT'}
FIELDS_EVENTS={'DATE_EFF','MOD','TYPECOM_AV','COM_AV','LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP'}

def read_csv(path:Path,required:set[str]):
    with path.open(encoding='utf-8-sig',newline='') as stream:
        first=stream.readline();stream.seek(0)
        sep=';' if first.count(';')>first.count(',') else ','
        reader=csv.DictReader(stream,delimiter=sep)
        if not required<=set(reader.fieldnames or []):
            raise ValueError('Colonnes manquantes '+str(path)+' '+str(sorted(required-set(reader.fieldnames or []))))
        return list(reader)

def k(typ,code,lib):return typ,code,norm(lib)

def analyser(graphe:Path,communes:Path,mouvements:Path,sortie:Path,sha_mouvements_attendu:str|None=None):
    for p in (graphe,communes,mouvements):
        if not p.is_file():raise FileNotFoundError(p)
    if sha_mouvements_attendu and sha256(mouvements)!=sha_mouvements_attendu:
        raise ValueError('SHA-256 des mouvements COG différent de l’empreinte attendue')
    graph=json.loads(graphe.read_text(encoding='utf-8'))
    states=[s for s in graph.get('etats_administratifs',[]) if s['typecom'] in ('COMD','COMA')]
    if len(states)!=7 or len({s['id'] for s in states})!=7:
        raise ValueError('Sept états de type COMD/COMA attendus')
    active=read_csv(communes,FIELDS_ACTIVE)
    mvt=read_csv(mouvements,FIELDS_EVENTS)
    active_map=defaultdict(list)
    for a in active:active_map[k(a['TYPECOM'],a['COM'],a['LIBELLE'])].append(a)
    idx=defaultdict(list)
    wanted={k(s['typecom'],s['code'],s['libelle']) for s in states}
    for n,ev in enumerate(mvt,start=2):
        date_iso(ev['DATE_EFF'])
        side_before=k(ev['TYPECOM_AV'],ev['COM_AV'],ev['LIBELLE_AV'])
        side_after=k(ev['TYPECOM_AP'],ev['COM_AP'],ev['LIBELLE_AP'])
        for side,ident in (('avant',side_before),('apres',side_after)):
            if ident in wanted:
                idx[ident].append({'ligne_source':n,'date_effet':ev['DATE_EFF'],
                    'mod':ev['MOD'],'sens':side,
                    'avant':{'typecom':ev['TYPECOM_AV'],'code':ev['COM_AV'],'libelle':ev['LIBELLE_AV']},
                    'apres':{'typecom':ev['TYPECOM_AP'],'code':ev['COM_AP'],'libelle':ev['LIBELLE_AP']}})
    report=[];counts=Counter()
    for st in sorted(states,key=lambda x:(x['dossier'],x['typecom'],x['code'])):
        ident=k(st['typecom'],st['code'],st['libelle'])
        exact=active_map[ident]
        if len(exact)>1:raise ValueError('Doublon de commune active : '+str(ident))
        period=defaultdict(lambda:{'avant':0,'apres':0,'mod':set()})
        for e in idx[ident]:
            dt=e['date_effet'];period[dt][e['sens']]+=1;period[dt]['mod'].add(e['mod'])
        first_entry=sorted(dt for dt,p in period.items() if p['apres']>0 and p['avant']==0)
        last_exit=sorted(dt for dt,p in period.items() if p['avant']>0 and p['apres']==0)
        crossings=sorted(dt for dt,p in period.items() if p['avant']>0 and p['apres']>0)
        if exact:
            state='present_au_cog_2026'
            parent=exact[0]['COMPARENT']
        elif last_exit:
            state='absent_2026_sortie_attestee'
            parent=None
        else:
            state='absent_2026_sans_sortie_identifiee'
            parent=None
        counts[state]+=1
        report.append({'id_etat':st['id'],'dossier':st['dossier'],
            'typecom':st['typecom'],'code':st['code'],'libelle':st['libelle'],
            'statut_au_millesime_2026':state,'comparent_2026':parent,
            'date_premiere_entree_attestee':first_entry[0] if first_entry else None,
            'date_derniere_sortie_attestee':last_exit[-1] if last_exit else None,
            'dates_mouvements_internes':crossings,
            'nombre_lignes_evenements':len(idx[ident]),
            'evenements_traces':idx[ident],
            'date_debut_complete_certifiee':False,
            'date_fin_complete_certifiee':False,
            'geometrie_historique_validee':False,
            'statut_lien_pactols_cog':'non_valide',
            'limite':'La présence au COG 2026 ne prouve pas la stabilité de l’emprise passée ; dates déduites uniquement des événements directement attestés.'})
    dests=[sortie/'audit-statut-delegue-associe-lot001.json',sortie/'rapport-statut-delegue-associe-lot001.json',sortie/'revue-statut-delegue-associe-lot001.csv']
    if any(p.resolve() in {graphe.resolve(),communes.resolve(),mouvements.resolve()} for p in dests):
        raise ValueError('Une sortie écraserait une entrée')
    statut={'schema_version':'0.1.0','etat':'recette_non_validante',
        'nombre_etats':len(report),'repartition':dict(sorted(counts.items())),
        'source':{'graphe':{'nom':graphe.name,'sha256':sha256(graphe)},
            'communes_2026':{'nom':communes.name,'sha256':sha256(communes)},
            'evenements_2026':{'nom':mouvements.name,'sha256':sha256(mouvements)}},
        'nombre_lignes_fichier_mouvements':len(mvt),
        'nombre_lignes_communes_2026':len(active),
        'liens_pactols_cog_nouveaux_valides':0,
        'geometries_historiques_validees':0,
        'note':'Sept états COMD/COMA ; recherche des mouvements directs et présence au millésime 2026, sans certification de toute la période historique.'}
    sortie.mkdir(parents=True,exist_ok=True)
    dests[0].write_text(json.dumps({'schema_version':'0.1.0','etat':'recette_non_validante','observations':report},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    dests[1].write_text(json.dumps(statut,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    fields=['dossier','typecom','code','libelle','statut_au_millesime_2026','comparent_2026',
            'date_premiere_entree_attestee','date_derniere_sortie_attestee','nombre_lignes_evenements',
            'geometrie_historique_validee','statut_lien_pactols_cog']
    with dests[2].open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter=';');w.writeheader()
        for r in report:w.writerow({x:r[x] for x in fields})
    return statut

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--graphe',required=True,type=Path)
    p.add_argument('--communes-2026',required=True,type=Path)
    p.add_argument('--evenements-2026',required=True,type=Path)
    p.add_argument('--sortie',required=True,type=Path)
    p.add_argument('--sha256-evenements-attendu')
    args=p.parse_args()
    print(json.dumps(analyser(args.graphe,args.communes_2026,args.evenements_2026,
                              args.sortie,args.sha256_evenements_attendu),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
