#!/usr/bin/env python3
"""Comparer 120 enfants Pactols au COMPARENT COG 2026, sans valider de relation.

Entrées : table des enfants hiérarchiques, contrôle national Pactols (ARK
terminaux), résultats du contrôle COG 2026 des 98 codes non partagés, tables
COG des sept exceptions. Les codes peuvent désigner plusieurs types administratifs.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

PAT = re.compile(r'^https?://id\.insee\.fr/geo/commune/([0-9]{5})$', re.I)
MODALITES = {
    '10': 'changement_de_nom', '20': 'creation', '21': 'retablissement',
    '30': 'suppression', '31': 'fusion_simple', '32': 'creation_commune_nouvelle',
    '33': 'fusion_association', '34': 'transformation_fusion_association_en_fusion_simple',
    '35': 'suppression_commune_deleguee', '41': 'changement_code_departement',
    '50': 'changement_code_transfert_chef_lieu',
    '70': 'commune_associee_vers_deleguee', '71': 'retablissement_commune_deleguee',
}
ATYPIQUES = {'49357','53024','72301','72363','85052','85080','85091'}
EXPECTED = {'accord_code_parent_2026':67,'parent_hors_corpus_terminal':21,
            'ecart_code_parent_historique':3,'sans_compa_2026':7,'code_partage_ark_22':22}

def lire(path, colonnes):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        data=list(csv.DictReader(f,delimiter=';'))
    if not data: raise ValueError('Table vide : '+str(path))
    if set(colonnes)-set(data[0]): raise ValueError('Colonnes manquantes : '+str(path))
    return data

def ecrire(path, data, cols):
    with Path(path).open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=cols,delimiter=';',extrasaction='ignore')
        wr.writeheader(); wr.writerows(data)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def extraire_codes_parent(record):
    if record is None: return []
    uris=json.loads(record['liens_exact_match_pactols'])
    if not isinstance(uris,list):raise ValueError('Liens Pactols corrompus')
    return sorted({m.group(1) for url in uris if (m:=PAT.fullmatch(url))})

def qualifier(enfant, parentcodes, statut_insee, compa):
    """Les 22 codes partagés ne sont pas dans la sous-table COG des 98."""
    if statut_insee is None: return 'code_partage_ark_22'
    if not compa: return 'sans_compa_2026'
    if not parentcodes: return 'parent_hors_corpus_terminal'
    if parentcodes == compa: return 'accord_code_parent_2026'
    return 'ecart_code_parent_historique'

def produire(contextes, skos, synthese98, evenements98, periodes98, sortie,
             controle_120=True):
    inp={'contextes':Path(contextes),'skos':Path(skos),'synthese98':Path(synthese98),
         'evenements98':Path(evenements98),'periodes98':Path(periodes98)}
    ctx=lire(contextes,['ark_pactols','libelle_pactols','code_skos_pactols',
        'parent_ark_hierarchie','parent_libelle_hierarchie'])
    sk={r['ark_pactols']:r for r in lire(skos,['ark_pactols','liens_exact_match_pactols'])}
    idx={r['code']:r for r in lire(synthese98,['code','types_com_2026','parents_2026'])}
    moves=lire(evenements98,['code_cible','MOD','DATE_EFF','TYPECOM_AV','COM_AV',
        'LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP'])
    hist=lire(periodes98,['code_cible','COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN'])
    if controle_120 and (len(ctx)!=120 or len(idx)!=98 or
                        len({r['ark_pactols'] for r in ctx})!=120):
        raise ValueError('Corpus 120/98 ou ARK non unique')
    par=[]; classes=collections.Counter()
    for r in ctx:
        code=r['code_skos_pactols']; candidate=sk.get(r['parent_ark_hierarchie'])
        pc=extraire_codes_parent(candidate)
        stat=idx.get(code)
        cp=[] if stat is None else sorted(set(filter(None,stat['parents_2026'].split('|'))))
        cl=qualifier(r,pc,stat,cp);classes[cl]+=1
        par.append({'ark_enfant':r['ark_pactols'],'libelle_enfant':r['libelle_pactols'],
            'code_skos_enfant':code,'ark_parent_pactols':r['parent_ark_hierarchie'],
            'libelle_parent_pactols':r['parent_libelle_hierarchie'],
            'parent_present_parmi_9928_terminaux':'oui' if candidate else 'non',
            'code_parent_assertion_pactols':'|'.join(pc),
            'typecom_enfant_cog2026':stat['types_com_2026'] if stat else 'COM|COMD (rapport 22)',
            'code_comparent_cog2026':'|'.join(cp),'classe_controle':cl,
            'validation_adlfi':'non_valide'})
    if controle_120 and dict(classes)!=EXPECTED:raise ValueError('Bilan inattendu: '+str(classes))
    bycode=collections.defaultdict(list)
    for m in moves:bycode[m['code_cible']].append(m)
    hp=collections.defaultdict(list)
    for r in hist:hp[r['code_cible']].append(r)
    atyp=[];transitions=[]
    for rec in par:
        code=rec['code_skos_enfant']
        if code not in ATYPIQUES:continue
        states=idx[code]
        evs=sorted(bycode[code],key=lambda v:(v['DATE_EFF'],v['TYPECOM_AV'],v['COM_AV'],v['TYPECOM_AP'],v['COM_AP']))
        old=sorted(hp[code],key=lambda x:x['DATE_DEBUT'])
        detail=[]
        for ev in evs:
            transition={k:ev[k] for k in ('MOD','DATE_EFF','TYPECOM_AV','COM_AV','LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP')}
            transition.update(ark_pactols=rec['ark_enfant'],code_cible=code,
                modalite_officielle=MODALITES.get(ev['MOD'],'modalite_inconnue'))
            transitions.append(transition)
            detail.append({'date':ev['DATE_EFF'],'mod':ev['MOD'],
                'avant':ev['TYPECOM_AV']+':'+ev['COM_AV']+':'+ev['LIBELLE_AV'],
                'apres':ev['TYPECOM_AP']+':'+ev['COM_AP']+':'+ev['LIBELLE_AP']})
        atyp.append({**rec,'code_cog2026':states['code'],
            'libelles_cog2026':states['libelles_2026'],
            'typecom_cog2026':states['types_com_2026'],
            'nb_etats_code_libelle':len(old),'nb_lignes_mouvement':len(evs),
            'etats_historiques':json.dumps(old,ensure_ascii=False),
            'transitions_avant_apres':json.dumps(detail,ensure_ascii=False),
            'etat_validation':'a_instruire_sans_geometrie'})
    if controle_120 and (len(atyp)!=7 or sum(len(bycode[c]) for c in ATYPIQUES)!=25):
        raise ValueError('Lot sept cas incomplet')
    output=Path(sortie)
    names=('parentages-pdl-120.csv','sept-cas-atypiques.csv','transitions-sept-cas.csv','rapport-parentages-120.json')
    if any((output/n).resolve() in {x.resolve() for x in inp.values()} for n in names):
        raise ValueError('Ecrasement interdit')
    output.mkdir(parents=True,exist_ok=True)
    ecrire(output/names[0],par,list(par[0]))
    ecrire(output/names[1],atyp,list(atyp[0]))
    ecrire(output/names[2],transitions,list(transitions[0]))
    report={'etat':'recette_non_validante','children':len(par),
            'classes':dict(sorted(classes.items())),
            'cas_atypiques':len(atyp),'lignes_transitions_sept_cas':len(transitions),
            'source_sha256':{k:sha(v) for k,v in inp.items()},
            'validation_nouvelle':0,'geometrie_historique_attribuee':0,
            'limites':['Le contrôle SKOS ne couvre que les 9928 ARK terminaux, non le thésaurus complet.',
                       'Les 22 codes partagés nécessitent la lecture du COMPARENT COG brut pour vérifier le lien administratif 2026.',
                       'Un COMPARENT concordant ne prouve pas que toutes les relations historiques ont été établies.',
                       'DATE_DEBUT/FIN sont des périodes code–libellé, non des contours historiques.']}
    (output/names[3]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['contextes','skos','synthese98','evenements98','periodes98','sortie']:
        p.add_argument('--'+name.replace('_','-'),type=Path,required=True)
    a=vars(p.parse_args())
    print(json.dumps(produire(**a),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
