#!/usr/bin/env python3
"""Audit non validant COG 2026 des 736 autorités Pactols de Bourgogne-Franche-Comté.

La source d'identité documentaire est l'ARK, pas le code Insee.
Les mouvements et périodes sont des observations historiques, pas des preuves
d'identité continue ni des contours rétroprojetables.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json
from pathlib import Path

SHAS={'inventaire':'efba75a28e0de837ef8832deff2ce5a5eb20e75132f3406e06cdc7ab6904fcad',
      'communes':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3',
      'historique':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee',
      'mouvements':'8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1'}
DEPS={'21','25','39','58','70','71','89','90'}
PER=('TYPECOM','COM','TNCC','NCC','NCCENR','LIBELLE','DATE_DEBUT','DATE_FIN')
MOV=('MOD','DATE_EFF','TYPECOM_AV','COM_AV','TNCC_AV','NCC_AV','NCCENR_AV','LIBELLE_AV',
     'TYPECOM_AP','COM_AP','TNCC_AP','NCC_AP','NCCENR_AP','LIBELLE_AP')

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def lire(p,required):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:
        first=f.readline();f.seek(0)
        rd=csv.DictReader(f,delimiter=';' if first.count(';')>first.count(',') else ',')
        miss=set(required)-set(rd.fieldnames or [])
        if miss:raise ValueError('Colonnes absentes : '+str(sorted(miss)))
        return list(rd)

def jlist(x):
    a=json.loads(x or '[]')
    if not isinstance(a,list) or not all(isinstance(s,str) for s in a):
        raise ValueError('Chaîne de codes SKOS mal formée')
    return a

def identite(x,prefix):
    raw=json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return prefix+hashlib.sha256(raw.encode()).hexdigest()[:24]

def exporter(p,rows,fields):
    with Path(p).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,delimiter=';',fieldnames=fields,extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def classer(rec,matches):
    codes=jlist(rec['codes_insee_skos'])
    if not codes:return 'hors_code_communal_numerique'
    if not matches:return 'code_historique_absent_cog2026'
    types={m['TYPECOM'] for m in matches}
    if types=={'COM','COMD'}:return 'code_partage_COM_COMD_2026'
    if types=={'COMA'}:return 'commune_associee_2026'
    if types=={'COMD'}:return 'commune_deleguee_2026'
    if types=={'COM'}:
        dep=rec['departement_hierarchie']
        if dep in DEPS and all(m['REG']=='27' and m['DEP']==dep for m in matches):
            return 'commune_COM_2026_code_departement_concordant'
        return 'commune_COM_2026_territoire_a_verifier'
    return 'types_2026_exceptionnels_a_instruire'

def produire(inventaire,communes,historique,mouvements,sortie):
    paths=dict(inventaire=Path(inventaire),communes=Path(communes),
               historique=Path(historique),mouvements=Path(mouvements))
    for k,p in paths.items():
        if sha(p)!=SHAS[k]:raise ValueError('Empreinte source modifiée : '+k)
    inv=lire(inventaire,['region','ark_pactols','codes_insee_skos','libelle_xml',
        'pref_fr_pactols','departement_hierarchie','categorie_geographique','etiquette_instruction'])
    if len(inv)!=736 or len({r['ark_pactols'] for r in inv})!=736 or any(r['region']!='Bourgogne-Franche-Comté' for r in inv):
        raise ValueError('Périmètre régional modifié')
    refs=collections.defaultdict(list);nocommune=[]
    for r in inv:
        code=jlist(r['codes_insee_skos'])
        if len(code)>1:raise ValueError('Plusieurs codes sur ARK : '+r['ark_pactols'])
        if code:refs[code[0]].append(r)
        else:nocommune.append(r)
    if (len(refs),sum(map(len,refs.values())),len(nocommune))!=(725,727,9):
        raise ValueError('Assertions Pactols inattendues')
    current=collections.defaultdict(list)
    for r in lire(communes,['COM','TYPECOM','DEP','REG','LIBELLE','COMPARENT']):
        if r['COM'] in refs:current[r['COM']].append(r)
    per=collections.defaultdict(list);perunique={}
    for r in lire(historique,PER):
        if r['COM'] not in refs:continue
        per[r['COM']].append(r)
        payload={k:r[k] for k in PER}
        perunique[identite(payload,'periode:')]=payload
    mov=collections.defaultdict(list);movunique={};support=collections.defaultdict(set)
    for r in lire(mouvements,MOV):
        codes={r['COM_AV'],r['COM_AP']} & set(refs)
        if not codes:continue
        payload={k:r[k] for k in MOV};key=identite(payload,'mouvement:')
        movunique[key]=payload;support[key].update(codes)
        for code in codes:mov[code].append(r)
    candidates=[];classes=collections.Counter();typestat=collections.Counter();codes_data=[]
    for r in sorted(inv,key=lambda x:x['ark_pactols']):
        vals=jlist(r['codes_insee_skos']);code=vals[0] if vals else ''
        matches=current[code] if code else []
        kind=classer(r,matches);classes[kind]+=1
        candidates.append({'ark_pactols':r['ark_pactols'],'libelle_xml':r['libelle_xml'],
          'pref_fr_pactols':r['pref_fr_pactols'],'departement_pactols':r['departement_hierarchie'],
          'code_skos':code,'categorie_geographique':r['categorie_geographique'],
          'typecom_cog2026':'|'.join(sorted({m['TYPECOM'] for m in matches})),
          'libelles_cog2026':'|'.join(sorted({m['LIBELLE'] for m in matches})),
          'comparent_cog2026':'|'.join(sorted({m['COMPARENT'] for m in matches if m['COMPARENT']})),
          'categorie_audit':kind,'alerte_pactols':r['etiquette_instruction'],
          'nb_periodes':len(per[code]),'nb_lignes_mouvements':len(mov[code]),
          'statut_validation':'non_valide'})
    for code in sorted(refs):
        matches=current[code];types='|'.join(sorted({m['TYPECOM'] for m in matches})) or 'ABSENT'
        typestat[types]+=1
        codes_data.append({'code':code,'arks':json.dumps(sorted(r['ark_pactols'] for r in refs[code]),ensure_ascii=False),
          'typecom_2026':types,'libelles_2026':json.dumps(sorted({m['LIBELLE'] for m in matches}),ensure_ascii=False),
          'parents_2026':json.dumps(sorted({m['COMPARENT'] for m in matches if m['COMPARENT']})),
          'periodes':len(per[code]),'lignes_mouvements':len(mov[code]),'validation':'non_valide'})
    etats={}
    def state(t,c,l):
        payload={'typecom':t,'code':c,'libelle':l};key=identite(payload,'etat:')
        etats[key]={'id':key,**payload};return key
    for p in perunique.values():state(p['TYPECOM'],p['COM'],p['LIBELLE'])
    for rs in current.values():
        for r in rs:state(r['TYPECOM'],r['COM'],r['LIBELLE'])
    mm=[]
    for mid,m in movunique.items():
        codes=sorted(support[mid])
        mm.append({'id':mid,**m,'avant_id':state(m['TYPECOM_AV'],m['COM_AV'],m['LIBELLE_AV']),
          'apres_id':state(m['TYPECOM_AP'],m['COM_AP'],m['LIBELLE_AP']),
          'codes_suivis':codes,'ark_concernes':sorted({r['ark_pactols'] for c in codes for r in refs[c]}),
          'validation':'non_valide'})
    mm.sort(key=lambda x:(x['DATE_EFF'],x['MOD'],x['id']))
    if (len(perunique),len(mm),len(etats))!=(807,393,975):
        raise ValueError('Invariants historiques modifiés')
    missing=sorted(c for c in refs if not current[c])
    report={'etat':'recette_non_validante','region':'Bourgogne-Franche-Comté',
      'ark':736,'ark_avec_code':727,'ark_sans_code':9,'codes_distincts':725,
      'codes_partages_par_ark':sum(len(v)>1 for v in refs.values()),
      'categories_ark':dict(sorted(classes.items())),'categories_codes':dict(sorted(typestat.items())),
      'codes_absents_2026':missing,'periodes_code_libelle_uniques':len(perunique),
      'lignes_mouvements_uniques':len(mm),'etats_observes':len(etats),
      'lignes_mouvements_par_ark':sum(len(m['ark_concernes']) for m in mm),
      'sha256_sources':{k:sha(v) for k,v in paths.items()},
      'validations_nouvelles':0,'geometries_historiques':0,
      'limites':'Couverture XML Bourgogne insuffisante ; le code Insee est une assertion Frantiq, non une validation. États et périodes n attestent pas les contours.'}
    output=Path(sortie)
    names=['candidatures-bfc-736.csv','codes-bfc-725.csv','graphe-cog-bfc-736.json','rapport-cog-bfc-736.json']
    if any((output/n).resolve() in {x.resolve() for x in paths.values()} for n in names):
        raise ValueError('Écrasement des sources interdit')
    output.mkdir(parents=True,exist_ok=True)
    exporter(output/names[0],candidates,list(candidates[0]))
    exporter(output/names[1],codes_data,list(codes_data[0]))
    graph={'schema':'adlfi.lieux.cog2026.bfc736.recette.v1',
      'autorites_pactols':[{'ark':r['ark_pactols'],'libelle':r['libelle_xml'],
         'codes_assertes':jlist(r['codes_insee_skos']),'validation':'non_valide'} for r in inv],
      'etats_observes':sorted(etats.values(),key=lambda x:x['id']),
      'periodes_noms':[{'id':k,**v} for k,v in sorted(perunique.items())],
      'mouvements_lignes':mm,'nouvelles_validations':[],'geometries_historiques':[]}
    (output/names[2]).write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (output/names[3]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('inventaire','communes','historique','mouvements','sortie'):
        p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(produire(a.inventaire,a.communes,a.historique,a.mouvements,a.sortie),ensure_ascii=False,indent=2))
