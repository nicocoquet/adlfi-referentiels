#!/usr/bin/env python3
"""Audit non validant du corpus Pactols Corse contre le COG Insee 2026.

Les couples code-libellé sont des périodes lexicales, pas des certificats
sur la stabilité des géométries. Les liens SKOS Pactols ne sont jamais
convertis automatiquement en alignements validés AdlFI.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ARK=re.compile(r'^26678/[A-Za-z0-9]+$')
CODE=re.compile(r'^2[AB]\d{3}$')
COLS_REGION={'region','ark_pactols','libelle_xml','pref_fr_pactols',
              'departement_hierarchie','codes_insee_skos','categorie_geographique',
              'etiquette_instruction','nombre_occurrences_region',
              'annees_operation_attestees'}
COLS_COM={'TYPECOM','COM','REG','DEP','LIBELLE'}
COLS_HIST={'TYPECOM','COM','LIBELLE','DATE_DEBUT','DATE_FIN'}
COLS_MVT={'MOD','DATE_EFF','TYPECOM_AV','COM_AV','LIBELLE_AV',
          'TYPECOM_AP','COM_AP','LIBELLE_AP'}
FIELDS=['ark_pactols','libelle_xml','pref_fr_pactols','code_insee_assertion_pactols',
       'departement_pactols','type_lieu','categorie_audit','libelle_cog_2026',
       'statut_cog_2026','concordance_libelle','code_historique_predecessur_mod41',
       'nombre_periodes_historiques_pour_codes','nombre_evenements_cog_relies',
       'codes_mod_evenements','annees_operation_attestees','etiquette_instruction_initiale',
       'statut_alignement_adlfi','commentaire']

def read_csv(path:Path,cols:set)->list[dict]:
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        first=f.readline();f.seek(0)
        sep=';' if first.count(';')>first.count(',') else ','
        reader=csv.DictReader(f,delimiter=sep)
        if not cols<=set(reader.fieldnames or []):
            raise ValueError('Colonnes manquantes dans '+str(path)+': '+repr(cols-set(reader.fieldnames or [])))
        return list(reader)

def sha(path:Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

def norm(s):
    s=(s or '').replace('œ','oe').replace('Œ','Oe')
    s=''.join(x for x in unicodedata.normalize('NFKD',s.casefold()) if unicodedata.category(x)!='Mn')
    return ' '.join(re.sub('[^a-z0-9]+',' ',s).split())

def statut_nom(nom,official):
    if norm(nom)==norm(official):return 'identique_normalise'
    # Strictement une indication de désambiguïsation (aucun renommage tacite).
    for dep in ('Haute-Corse','Corse-du-Sud'):
        if nom.endswith(' ('+dep+')') and norm(nom[:-(len(dep)+3)])==norm(official):
            return 'qualificatif_departement_documentaire'
    return 'divergence_nom_a_instruire'

def iso(s):
    from datetime import date
    if s and date.fromisoformat(s).isoformat()!=s:
        raise ValueError('Date ISO invalide '+s)
    return s

def produire(inventaire:Path,lot:Path,communes:Path,historique:Path,mouvements:Path,sortie:Path):
    paths=[inventaire,lot,communes,historique,mouvements]
    if any(not p.is_file() for p in paths):raise FileNotFoundError('Source manquante')
    inv=read_csv(inventaire,COLS_REGION)
    small=read_csv(lot,COLS_REGION)
    if len(inv)!=200 or len(small)!=25:raise ValueError('Périmètre de recette corse inattendu (200 / 25)')
    byark={r['ark_pactols']:r for r in inv}
    if len(byark)!=len(inv) or any(not ARK.fullmatch(a) for a in byark):raise ValueError('ARK dupliqué ou invalide')
    if any(r['region']!='Corse' for r in inv):raise ValueError('Région inattendue')
    smallarks={r['ark_pactols'] for r in small}
    if len(smallarks)!=25 or not smallarks<=byark.keys():raise ValueError('Lot 25 non distinct / étranger')
    cogs=read_csv(communes,COLS_COM)
    current={}
    for r in cogs:
        if r['COM'] not in current:current[r['COM']]=[]
        current[r['COM']].append(r)
    hist_by_code=collections.defaultdict(list)
    for r in read_csv(historique,COLS_HIST):
        if r['TYPECOM']!='COM':continue
        iso(r['DATE_DEBUT']);iso(r['DATE_FIN'])
        hist_by_code[r['COM']].append(r)
    for v in hist_by_code.values():v.sort(key=lambda r:(r['DATE_DEBUT'],r['DATE_FIN'],r['LIBELLE']))
    moves=read_csv(mouvements,COLS_MVT)
    bycode_moves=collections.defaultdict(list)
    mod41_backward=collections.defaultdict(list)
    for r in moves:
        iso(r['DATE_EFF'])
        for col in ('COM_AV','COM_AP'):
            if r[col]:bycode_moves[r[col]].append(r)
        if (r['MOD']=='41' and r['TYPECOM_AV']=='COM' and r['TYPECOM_AP']=='COM'
            and r['COM_AV']!=r['COM_AP']):
            mod41_backward[r['COM_AP']].append(r)
    output=[];audit_events=[];details=[];counts=collections.Counter()
    for ark,r in sorted(byark.items(),key=lambda pair:(pair[1]['departement_hierarchie'],norm(pair[1]['libelle_xml']),pair[0])):
        codes=json.loads(r['codes_insee_skos'])
        if not isinstance(codes,list) or len(codes)>1:raise ValueError('Codes Pactols multiples: '+ark)
        code=codes[0] if codes else ''
        dept=r['departement_hierarchie']
        official='';statut='';match='sans_code';predecessors=[];local_moves=[];history=[]
        if code:
            if not CODE.fullmatch(code):raise ValueError('Code de commune corse non valide: '+code)
            candidates=[x for x in current.get(code,[]) if x['TYPECOM']=='COM']
            if len(candidates)>1:raise ValueError('Code actuel ambigu '+code)
            cur=candidates[0] if candidates else None
            if cur:
                official=cur['LIBELLE'];match=statut_nom(r['pref_fr_pactols'],official)
                if (cur['REG']!='94' or cur['DEP']!=dept or code[:2]!=dept):
                    statut='conflit_territorial_cog_2026'
                else:
                    statut='commune_presente_cog_2026'
            else:
                statut='code_communal_absent_cog_2026'
            ancestors=set();frontier=[code]
            # L'unique opération de ce parcours concerne le changement de
            # département MOD 41 ; ne jamais le traverser via une fusion.
            while frontier:
                nxt=[]
                for c in frontier:
                    for ev in mod41_backward[c]:
                        prior=ev['COM_AV']
                        if prior!=code and prior not in ancestors:
                            ancestors.add(prior);nxt.append(prior)
                frontier=nxt
            predecessors=sorted(ancestors)
            related={code}|ancestors
            event_uniq={}
            for c in related:
                for ev in bycode_moves.get(c,[]):
                    ident=tuple(ev.get(z,'') for z in sorted(COLS_MVT))
                    event_uniq[ident]=ev
            local_moves=sorted(event_uniq.values(),key=lambda ev:(ev['DATE_EFF'],ev['MOD'],ev['COM_AV'],ev['COM_AP']))
            history=[{k:x[k] for k in ('TYPECOM','COM','LIBELLE','DATE_DEBUT','DATE_FIN')}
                    for c in sorted(related) for x in hist_by_code.get(c,[])]
            for ev in local_moves:
                audit_events.append({'ark_pactols':ark,'code_assertion_skos':code,
                    'date_effet':ev['DATE_EFF'],'mod':ev['MOD'],
                    'typecom_avant':ev['TYPECOM_AV'],'code_avant':ev['COM_AV'],
                    'libelle_avant':ev['LIBELLE_AV'],'typecom_apres':ev['TYPECOM_AP'],
                    'code_apres':ev['COM_AP'],'libelle_apres':ev['LIBELLE_AP'],
                    'qualification':'evenement_cog_rattache_a_un_code_sans_inference_alignement'})
        else:
            if (r['categorie_geographique']=='commune_candidate_directe' and
                not r['etiquette_instruction'].startswith(('T1_','T3_'))):
                statut='concept_sans_code_communal_a_instruire'
            else:statut='hors_champ_communal'
        if statut=='commune_presente_cog_2026' and match=='divergence_nom_a_instruire':
            cat='divergence_libelle_pactols_cog_2026'
        elif statut=='commune_presente_cog_2026' and predecessors:
            cat='commune_avec_predecesseur_code_mod41'
        else:cat=statut
        counts[cat]+=1
        commentary='État non validant ; COG 2026 contemporain. '
        if predecessors:commentary+='Code(s) antérieur(s) liés par MOD=41 ; vérifier les périodes et autres événements. '
        if not code:commentary+='Type d’autorité hors commune ou à instruire ; ne pas attribuer de contour communal. '
        if match=='qualificatif_departement_documentaire':commentary+='Qualificatif départemental documenté, absent du nom officiel. '
        output.append({
            'ark_pactols':ark,'libelle_xml':r['libelle_xml'],'pref_fr_pactols':r['pref_fr_pactols'],
            'code_insee_assertion_pactols':code,'departement_pactols':dept,
            'type_lieu':r['categorie_geographique'],'categorie_audit':cat,
            'libelle_cog_2026':official,'statut_cog_2026':statut,
            'concordance_libelle':match,'code_historique_predecessur_mod41':','.join(predecessors),
            'nombre_periodes_historiques_pour_codes':str(len(history)),
            'nombre_evenements_cog_relies':str(len(local_moves)),
            'codes_mod_evenements':','.join(sorted({x['MOD'] for x in local_moves})),
            'annees_operation_attestees':r['annees_operation_attestees'],
            'etiquette_instruction_initiale':r['etiquette_instruction'],
            'statut_alignement_adlfi':'non_valide','commentaire':commentary})
        details.append({'ark_pactols':ark,'codes_historique_inspectes':sorted({code}|set(predecessors)) if code else [],
                        'couples_code_libelle_historiques':history,'evenements_releves':[
                            {k:ev[k] for k in sorted(COLS_MVT)} for ev in local_moves]})
    if counts.total()!=200 or len([x for x in output if x['code_insee_assertion_pactols']])!=194:
        raise ValueError('Décompte corse incohérent, vérifier les sources')
    selected=[row for row in output if row['ark_pactols'] in smallarks]
    if len(selected)!=25:raise ValueError('Erreur sélection du lot 25')
    required={'Afa':('20001','2A001','1976-01-01'),'Aghione':('20002','2B002','1976-01-01')}
    for name,(old,new,dt) in required.items():
        row=next(x for x in output if x['libelle_xml']==name)
        if row['code_insee_assertion_pactols']!=new or old not in row['code_historique_predecessur_mod41'].split(','):
            raise ValueError('Transition insulaire MOD41 absente: '+name)
        evidence=next(x for x in details if x['ark_pactols']==row['ark_pactols'])['evenements_releves']
        if not any(x['MOD']=='41' and x['DATE_EFF']==dt and x['COM_AV']==old and x['COM_AP']==new for x in evidence):
            raise ValueError('Date de preuve MOD41 incohérente: '+name)
    paths_out=['corse-200-candidatures-cog.csv','corse-25-prioritaires-cog.csv',
               'corse-200-evenements-cog.csv','corse-200-historique-detail.json','rapport-corse-cog-2026.json']
    if any((sortie/f).resolve() in {p.resolve() for p in paths} for f in paths_out):
        raise ValueError('La sortie écraserait une source')
    sortie.mkdir(parents=True,exist_ok=True)
    for filename,rows,fields in [
        (paths_out[0],output,FIELDS),(paths_out[1],selected,FIELDS),
        (paths_out[2],audit_events,['ark_pactols','code_assertion_skos','date_effet','mod',
            'typecom_avant','code_avant','libelle_avant','typecom_apres','code_apres',
            'libelle_apres','qualification'])]:
        with (sortie/filename).open('w',encoding='utf-8-sig',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=fields,delimiter=';');wr.writeheader();wr.writerows(rows)
    (sortie/paths_out[3]).write_text(json.dumps({'statut':'recette_non_validante','autorites':details},
                                            ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'schema_version':'0.1.0','etat':'recette_non_validante','region':'Corse',
            'autorites':len(output),'candidatures_skos_code_commune':194,
            'autres_autorites':6,'premier_lot':25,
            'repartition':dict(sorted(counts.items())),
            'total_lignes_evenements_cog_dans_l_audit':len(audit_events),
            'source_sha256':{p.name:sha(p) for p in paths},
            'note':'Les événements sont répétés par ARK concerné si nécessaire; ne pas sommer les lignes pour compter les opérations uniques. Les périodes datent les noms, non les contours.',
            'nouvelles_validations_pactols_cog':0,'geometries_historiques_validees':0}
    (sortie/paths_out[4]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventaire',type=Path,required=True)
    p.add_argument('--lot',type=Path,required=True)
    p.add_argument('--communes',type=Path,required=True)
    p.add_argument('--historique',type=Path,required=True)
    p.add_argument('--mouvements',type=Path,required=True)
    p.add_argument('--sortie',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(produire(args.inventaire,args.lot,args.communes,args.historique,args.mouvements,args.sortie),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
