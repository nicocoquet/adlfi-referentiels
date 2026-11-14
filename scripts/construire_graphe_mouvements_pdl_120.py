#!/usr/bin/env python3
"""Graphe provisoire des mouvements Insee des 120 codes des lieux imbriqués PdL.

Le sommet représente un triplet (TYPECOM, code, libellé) OBSERVÉ et ne peut
pas être interprété comme l'identité durable d'une commune. L'arête représente
UNE ligne du fichier COG mouvements. Le regroupement par date/MOD/composante
connexe produit seulement des groupes candidats, pas des actes juridiques.
"""
import argparse,collections,csv,hashlib,json
from pathlib import Path
M=('MOD','DATE_EFF','TYPECOM_AV','COM_AV','LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP')
H=('COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN')
EXPECTED={'evenements22':188,'evenements98':273,'periodes22':47,'periodes98':120}
SOURCE_SHA={'evenements22':'b8a0f8f089c787bc886786b4cdaafe9bb27d1b79ad9b480d3865895c57db654c',
'evenements98':'502d2c750f5830db8f13e72d4feeccb61f5204dd0b546761b24477b05def5791',
'periodes22':'be931262f1edbef30d723a2413acbdeaa1bb49fe4fba3f1776b2667e62ef86f4',
'periodes98':'2b21df59cb6211ed022efa3da7f38a33c9cc791f87b911d945655f97465592c7'}

def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()
def read(path,required):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f,delimiter=';')
        if not set(required)<=set(r.fieldnames or []):raise ValueError('Colonnes manquantes '+str(path))
        return list(r)
def write(path,rows,cols):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols,delimiter=';',extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def construire(e22,e98,p22,p98,sortie,strict=True):
    paths={'evenements22':Path(e22),'evenements98':Path(e98),
           'periodes22':Path(p22),'periodes98':Path(p98)}
    raw={k:read(paths[k],('code_cible',)+(M if 'evenements' in k else H)) for k in paths}
    if strict:
        for k,p in paths.items():
            if sha(p)!=SOURCE_SHA[k]:raise ValueError('Source non conforme à la recette vérifiée : '+k)
            if len(raw[k])!=EXPECTED[k]:raise ValueError('Cardinalité anormale : '+k)
        a={x['code_cible'] for x in raw['evenements22']}
        b={x['code_cible'] for x in raw['evenements98']}
        if len(a)!=22 or len(b)!=98 or a&b:raise ValueError('Périmètre de 120 codes non conforme')
    nodes={}
    def noeud(kind,code,name):
        val={'typecom':kind,'code':code,'libelle':name}
        nid='etat:'+fingerprint(val)
        nodes[nid]={'id':nid,**val,'semantique':'triplet_observe_non_identite_perenne'}
        return nid
    unique={}
    for source in ('evenements22','evenements98'):
        for r in raw[source]:
            vals={k:r[k] for k in M}
            mid='ligne:'+fingerprint(vals)
            if mid not in unique:unique[mid]={'id':mid,**vals,'codes_suivis':set(),'sources':set()}
            elif any(unique[mid][k]!=vals[k] for k in M):raise ValueError('Collision identifiant mouvement')
            unique[mid]['codes_suivis'].add(r['code_cible'])
            unique[mid]['sources'].add(source)
    moves=[]
    for v in unique.values():
        av=noeud(v['TYPECOM_AV'],v['COM_AV'],v['LIBELLE_AV'])
        ap=noeud(v['TYPECOM_AP'],v['COM_AP'],v['LIBELLE_AP'])
        moves.append({**{k:v[k] for k in ('id',)+M},
          'source':av,'cible':ap,'codes_suivis':sorted(v['codes_suivis']),
          'sources_recette':sorted(v['sources']),
          'statut':'ligne_mouvement_officielle_non_validation_Pactols'})
    moves.sort(key=lambda x:(x['DATE_EFF'],x['MOD'],x['id']))
    periods={}
    for source in ('periodes22','periodes98'):
        for r in raw[source]:
            vals={k:r[k] for k in H}
            pid='periode:'+fingerprint(vals)
            if pid not in periods:periods[pid]={**vals,'id':pid,'codes_suivis':set()}
            periods[pid]['codes_suivis'].add(r['code_cible'])
            noeud(r['TYPECOM'],r['COM'],r['LIBELLE'])
    ps=sorted([{**{k:v[k] for k in ('id',)+H},'codes_suivis':sorted(v['codes_suivis'])} for v in periods.values()],
              key=lambda x:(x['COM'],x['DATE_DEBUT'],x['TYPECOM'],x['LIBELLE']))
    # Les connexités sont calculées A DATE/MOD IDENTIQUES, sur codes+TYPECOM
    # (jamais sur les libellés). Regroupements candidats seulement.
    bydate=collections.defaultdict(list)
    for m in moves:bydate[(m['DATE_EFF'],m['MOD'])].append(m)
    bundles=[]
    for (date,mod),rows in sorted(bydate.items()):
        parent={}
        def find(x):
            parent.setdefault(x,x)
            if parent[x]!=x:parent[x]=find(parent[x])
            return parent[x]
        def union(a,b):
            a,b=find(a),find(b)
            if a!=b:parent[max(a,b)]=min(a,b)
        for m in rows:
            union((m['TYPECOM_AV'],m['COM_AV']),(m['TYPECOM_AP'],m['COM_AP']))
        comps=collections.defaultdict(list)
        for m in rows:comps[find((m['TYPECOM_AV'],m['COM_AV']))].append(m)
        for rs in comps.values():
            ids=sorted(m['id'] for m in rs)
            allcodes=sorted({c for m in rs for c in (m['COM_AV'],m['COM_AP']) if c})
            bundles.append({'id':'groupe:'+fingerprint(ids),'date_effet':date,'mod':mod,
               'mouvements_ids':ids,'codes_impliques':allcodes,
               'nombre_lignes':len(ids),'statut':'groupe_connexe_candidat_non_acte_unique'})
    bundles.sort(key=lambda x:(x['date_effet'],x['mod'],x['id']))
    target=Path(sortie)
    names=('graphe-mouvements-pdl-120.json','lignes-mouvements-distinctes.csv','groupes-evenements-candidats.csv','rapport-graphe-120.json')
    if any((target/n).resolve() in {p.resolve() for p in paths.values()} for n in names):raise ValueError('Écrasement interdit')
    target.mkdir(parents=True,exist_ok=True)
    graph={'schema':'adlfi.lieux.mouvements.cog2026.recette.v1',
      'statut_publication':'non_publie','niveau_preuve':'lignes_originales_du_COG_2026',
      'source_insee':'https://www.insee.fr/fr/information/8740222',
      'etats_observes':sorted(nodes.values(),key=lambda x:x['id']),
      'mouvements_lignes':moves,'periodes_libelles':ps,'groupes_candidats':bundles,
      'validations_adlfi':[],'geometries_historiques':[]}
    (target/names[0]).write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    write(target/names[1],[{**{k:m[k] for k in ('id',)+M},
       'codes_suivis':'|'.join(m['codes_suivis'])} for m in moves],['id',*M,'codes_suivis'])
    write(target/names[2],[{'id':b['id'],'date_effet':b['date_effet'],'mod':b['mod'],
       'nombre_lignes':b['nombre_lignes'],'codes_impliques':'|'.join(b['codes_impliques'])} for b in bundles],
       ['id','date_effet','mod','nombre_lignes','codes_impliques'])
    rpt={'etat':'recette_non_validante',
       'lignes_entree':sum(len(raw[k]) for k in ('evenements22','evenements98')),
       'lignes_mouvement_distinctes':len(moves),'lignes_dupliquees_eliminees':sum(len(raw[k]) for k in ('evenements22','evenements98'))-len(moves),
       'periodes_code_libelle':len(ps),'noeuds_triplets_observes':len(nodes),'groupes_connexes_candidats':len(bundles),
       'sha256_sources':{k:sha(v) for k,v in paths.items()},
       'nouveaux_alignements_adlfi':0,'geometries_historiques':0,
       'avertissement':'Les regroupements de mouvements sont des composantes techniques, non des actes officiels ; les noeuds ne sont pas des identités institutionnelles intemporelles.'}
    (target/names[3]).write_text(json.dumps(rpt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if strict and (len(moves)!=396 or len(ps)!=167):raise ValueError('Résultat de dédoublonnage inattendu')
    return rpt

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('evenements22','evenements98','periodes22','periodes98','sortie'):
        p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(construire(a.evenements22,a.evenements98,a.periodes22,a.periodes98,a.sortie),ensure_ascii=False,indent=2))
