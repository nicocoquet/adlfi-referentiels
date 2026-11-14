#!/usr/bin/env python3
"""Audit non validant Pays de la Loire, COG 2026. Entrée : lot 25 ou inventaire 806."""
import argparse,csv,json,hashlib,collections
from pathlib import Path

COLS=['ark_pactols','libelle_pactols','departement_pactols','code_skos','types_uri_skos','uri_non_numeriques','candidats_cog_2026','categorie_instruction','periodes_liees','mouvements_lies','validation_adlfi']
DEPS={'44','49','53','72','85'}

def lire(path,champs):
    with open(path,encoding='utf-8-sig',newline='') as f:
        line=f.readline();f.seek(0)
        rd=csv.DictReader(f,delimiter=';' if line.count(';')>line.count(',') else ',')
        if set(champs)-set(rd.fieldnames or []):raise ValueError('Champs manquants : '+str(path))
        return list(rd)

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def liens(x):
    y=json.loads(x or '[]')
    if not isinstance(y,list) or not all(isinstance(a,str) for a in y):raise ValueError('Liens SKOS invalides')
    return y

def produire(inventaire,communes,historique,mouvements,sortie,attendu):
    sources=[Path(x) for x in (inventaire,communes,historique,mouvements)]
    inv=lire(inventaire,['region','ark_pactols','pref_fr_pactols','departement_hierarchie','codes_insee_skos','types_liens_insee_skos','autres_uris_insee'])
    if attendu and len(inv)!=attendu:raise ValueError('Cardinalite inattendue : '+str(len(inv)))
    if len(set(r['ark_pactols'] for r in inv))!=len(inv):raise ValueError('ARK dupliques')
    if any(x['region']!='Pays de la Loire' or x['departement_hierarchie'] not in DEPS|{''} for x in inv):raise ValueError('Region ou departement inattendu')
    curr=collections.defaultdict(list)
    for x in lire(communes,['COM','TYPECOM','REG','DEP','LIBELLE']):
        curr[x['COM']].append(x)
    hist=collections.defaultdict(list)
    for x in lire(historique,['COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN']):hist[x['COM']].append(x)
    evts=collections.defaultdict(list)
    for x in lire(mouvements,['MOD','DATE_EFF','COM_AV','TYPECOM_AV','COM_AP','TYPECOM_AP']):
        for code in {x['COM_AV'],x['COM_AP']}-{''}:evts[code].append(x)
    sorties=[];periodes=[];events=[];counts=collections.Counter()
    for r in sorted(inv,key=lambda x:x['ark_pactols']):
        cs=liens(r['codes_insee_skos'])
        if len(cs)>1:raise ValueError('Codes multiples: '+r['ark_pactols'])
        code=cs[0] if cs else ''
        matches=curr[code] if code else []
        if not code:statut='sans_code_skos_a_instruire'
        elif not matches:statut='code_absent_cog_2026'
        elif len(matches)>1:statut='code_partage_types_a_instruire'
        elif matches[0]['TYPECOM'] in ('COMA','COMD'):statut='commune_associee_deleguee_a_instruire'
        elif matches[0]['TYPECOM']=='COM' and matches[0]['REG']=='52' and matches[0]['DEP']==r['departement_hierarchie']:statut='commune_presente_cog_2026'
        else:statut='discordance_territoriale_ou_type_a_instruire'
        ps=hist[code] if code else [];es=evts[code] if code else []
        for p in ps:periodes.append(dict(ark_pactols=r['ark_pactols'],code_skos=code,**{k:p[k] for k in ('COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN')}))
        for e in es:events.append(dict(ark_pactols=r['ark_pactols'],code_skos=code,**{k:e[k] for k in ('MOD','DATE_EFF','COM_AV','TYPECOM_AV','COM_AP','TYPECOM_AP')}))
        counts[statut]+=1
        sorties.append({'ark_pactols':r['ark_pactols'],'libelle_pactols':r['pref_fr_pactols'],'departement_pactols':r['departement_hierarchie'],
            'code_skos':code,'types_uri_skos':'|'.join(liens(r['types_liens_insee_skos'])),'uri_non_numeriques':'|'.join(liens(r['autres_uris_insee'])),
            'candidats_cog_2026':json.dumps([{k:m.get(k,'') for k in ('COM','TYPECOM','LIBELLE','DEP','COMPARENT')} for m in matches],ensure_ascii=False),
            'categorie_instruction':statut,'periodes_liees':len(ps),'mouvements_lies':len(es),'validation_adlfi':'non_valide'})
    sortie=Path(sortie)
    targets={'candidatures.csv':(sorties,COLS),'periodes.csv':(periodes,['ark_pactols','code_skos','COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN']),
        'evenements.csv':(events,['ark_pactols','code_skos','MOD','DATE_EFF','COM_AV','TYPECOM_AV','COM_AP','TYPECOM_AP'])}
    if any((sortie/name).resolve() in {p.resolve() for p in sources} for name in (*targets,'rapport.json')):raise ValueError('Sortie ecraserait une source')
    sortie.mkdir(parents=True,exist_ok=True)
    for name,(data,fields) in targets.items():
        with (sortie/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,delimiter=';');w.writeheader();w.writerows(data)
    report={'etat':'recette_non_validante','ark':len(inv),'assertions_code_skos':sum(bool(liens(r['codes_insee_skos'])) for r in inv),
        'repartition':dict(sorted(counts.items())),'lignes_periodes':len(periodes),'lignes_mouvements_par_ark':len(events),
        'source_sha256':{p.name:sha(p) for p in sources},'validations_nouvelles':0,'geometries_attribuees':0,
        'limite':'Les mouvements et periodes sont lies au code declare et peuvent se repeter par ARK ; aucune continuite territoriale inferee.'}
    (sortie/'rapport.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('inventaire','communes','historique','mouvements','sortie'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--attendu',type=int,default=0)
    a=p.parse_args()
    print(json.dumps(produire(a.inventaire,a.communes,a.historique,a.mouvements,a.sortie,a.attendu),ensure_ascii=False,indent=2))
