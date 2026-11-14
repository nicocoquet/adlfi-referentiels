#!/usr/bin/env python3
"""Graphe non validant du COG 2026 pour 806 ARK Pactols des Pays de la Loire.

Une assertion SKOS est une source, pas une validation éditoriale.
Un triplet TYPECOM/code/libellé est un état observé, pas une identité
administrative intemporelle ; les périodes de libellé ne sont pas des contours.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json
from pathlib import Path
from auditer_lieux_pays_loire_cog import lire,liens,sha

INVENTAIRE_SHA='ea06d1bddbf53ec49410aa122b9f3e80842f0f770b9f364c3677a0a7c35e91db'
COG_SHA={
 'communes':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3',
 'historique':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee',
 'mouvements':'8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1'}
MOV=('MOD','DATE_EFF','TYPECOM_AV','COM_AV','TNCC_AV','NCC_AV','NCCENR_AV','LIBELLE_AV',
     'TYPECOM_AP','COM_AP','TNCC_AP','NCC_AP','NCCENR_AP','LIBELLE_AP')
PER=('TYPECOM','COM','TNCC','NCC','NCCENR','LIBELLE','DATE_DEBUT','DATE_FIN')

def uid(data,prefix):
    packed=json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return prefix+hashlib.sha256(packed.encode()).hexdigest()[:24]

def csv_export(path,rows,columns):
    with Path(path).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,delimiter=';',extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def construire(inventaire,communes,historique,mouvements,sortie):
    sources={'inventaire':Path(inventaire),'communes':Path(communes),
             'historique':Path(historique),'mouvements':Path(mouvements)}
    for role,path in sources.items():
        expected=INVENTAIRE_SHA if role=='inventaire' else COG_SHA[role]
        if sha(path)!=expected:raise ValueError('SHA256 source inattendu : '+role)
    rows=lire(inventaire,['ark_pactols','region','codes_insee_skos','libelle_xml',
                         'pref_fr_pactols','autres_uris_insee'])
    if len(rows)!=806 or len({r['ark_pactols'] for r in rows})!=806 or any(r['region']!='Pays de la Loire' for r in rows):
        raise ValueError('Inventaire régional de 806 ARK invalide')
    refs=collections.defaultdict(list);no_code=[]
    for r in rows:
        cc=liens(r['codes_insee_skos'])
        if len(cc)>1:raise ValueError('Plusieurs codes sur un seul ARK')
        if cc:refs[cc[0]].append(r['ark_pactols'])
        else:no_code.append(r)
    if (len(refs),sum(map(len,refs.values())),len(no_code),sum(len(x)>1 for x in refs.values()))!=(775,797,9,22):
        raise ValueError('Population 797/775/9/22 inattendue')
    current=collections.defaultdict(list)
    for r in lire(communes,['COM','TYPECOM','REG','DEP','LIBELLE','COMPARENT']):
        if r['COM'] in refs:current[r['COM']].append(r)
    typestat=collections.Counter()
    tablecodes=[]
    for code in sorted(refs):
        recs=current[code]
        typ='|'.join(sorted({r['TYPECOM'] for r in recs})) or 'ABSENT'
        typestat[typ]+=1
        tablecodes.append({'code_insee_assertion':code,
            'ark_pactols':json.dumps(sorted(refs[code]),ensure_ascii=False),
            'typecom_2026':typ,
            'noms_cog_2026':json.dumps(sorted({r['LIBELLE'] for r in recs}),ensure_ascii=False),
            'comparent_2026':json.dumps(sorted({r['COMPARENT'] for r in recs if r['COMPARENT']})),
            'validation_adlfi':'non_valide'})
    histories={}
    for rec in lire(historique,PER):
        code=rec['COM']
        if code not in refs:continue
        vals={f:rec[f] for f in PER}
        key=uid(vals,'periode:')
        histories[key]={'id':key,**vals}
    movements_unique=collections.defaultdict(set)
    movements_by_key={}
    for rec in lire(mouvements,MOV):
        relevant={rec['COM_AV'],rec['COM_AP']} & set(refs)
        if not relevant:continue
        vals={f:rec[f] for f in MOV}
        key=uid(vals,'mouvement:')
        movements_by_key[key]={'id':key,**vals}
        movements_unique[key].update(relevant)
    states={}
    def state(t,c,label):
        val={'typecom':t,'code':c,'libelle':label}
        key=uid(val,'etat:')
        states[key]={'id':key,**val}
        return key
    for r in histories.values():state(r['TYPECOM'],r['COM'],r['LIBELLE'])
    for recs in current.values():
        for r in recs:state(r['TYPECOM'],r['COM'],r['LIBELLE'])
    moves=[]
    for k,r in movements_by_key.items():
        seen=sorted(movements_unique[k])
        moves.append({**r,
            'avant_id':state(r['TYPECOM_AV'],r['COM_AV'],r['LIBELLE_AV']),
            'apres_id':state(r['TYPECOM_AP'],r['COM_AP'],r['LIBELLE_AP']),
            'codes_suivis':seen,
            'ark_pactols_concernes':sorted({ark for c in seen for ark in refs[c]}),
            'statut_relation':'observation_COG_non_validation_AdlFI'})
    periods=sorted(histories.values(),key=lambda p:(p['COM'],p['TYPECOM'],p['DATE_DEBUT'],p['LIBELLE']))
    moves.sort(key=lambda r:(r['DATE_EFF'],r['MOD'],r['id']))
    if (len(periods),len(moves),len(states))!=(898,709,1295):
        raise ValueError('Résultat historique inattendu : '+str((len(periods),len(moves),len(states))))
    absent=[code for code in sorted(refs) if not current[code]]
    report={'schema_version':'1.0.0','etat':'recette_non_validante','ark':806,
        'assertions_ark_code':797,'ark_hors_code_numerique':9,'codes_insee_distincts':775,
        'codes_partages_entre_ark':22,
        'repartition_codes_par_typecom':dict(sorted(typestat.items())),
        'codes_absents_cog2026':absent,
        'periodes_code_libelle_uniques':len(periods),
        'lignes_mouvements_distinctes':len(moves),
        'etats_observes_distincts':len(states),
        'lignes_mouvements_rattachees_aux_ark':sum(len(m['ark_pactols_concernes']) for m in moves),
        'sha256_sources':{role:sha(path) for role,path in sources.items()},
        'nouvelles_validations':0,'geometries_historiques_attribuees':0,
        'limite':'Pas de fermeture transitive ni de géométrie historique ; code, type et libellé ne sont pas une identité intemporelle.'}
    out=Path(sortie)
    files=('graphe-cog-806.json','rapport-graphe-806.json','codes-cog-775.csv','mouvements-distincts-709.csv')
    if any((out/name).resolve() in {p.resolve() for p in sources.values()} for name in files):
        raise ValueError('Sortie écraserait une source')
    out.mkdir(parents=True,exist_ok=True)
    graph={'schema':'adlfi.lieux.cog2026.graphe_pdl806.recette.v1',
         'provenance':report['sha256_sources'],
         'autorites_pactols':[{'ark':r['ark_pactols'],'libelle_xml':r['libelle_xml'],
              'pref_fr_pactols':r['pref_fr_pactols'],'codes_skos':liens(r['codes_insee_skos']),
              'autres_uris_insee':liens(r['autres_uris_insee']),'validation':'non_valide'} for r in rows],
         'etats_observes':sorted(states.values(),key=lambda r:r['id']),
         'periodes_noms':periods,'mouvements_lignes':moves,
         'alignements_valides_nouveaux':[],'geometries_historiques':[]}
    (out/files[0]).write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (out/files[1]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    csv_export(out/files[2],tablecodes,list(tablecodes[0]))
    csv_export(out/files[3],[{**m,'codes_suivis':'|'.join(m['codes_suivis']),
       'ark_pactols_concernes':'|'.join(m['ark_pactols_concernes'])} for m in moves],
       ['id',*MOV,'avant_id','apres_id','codes_suivis','ark_pactols_concernes','statut_relation'])
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('inventaire','communes','historique','mouvements','sortie'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(construire(args.inventaire,args.communes,args.historique,args.mouvements,args.sortie),ensure_ascii=False,indent=2))
