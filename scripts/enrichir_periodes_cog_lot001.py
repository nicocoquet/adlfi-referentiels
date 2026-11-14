#!/usr/bin/env python3
"""Enrichissement NON VALIDANT des états d'un graphe COG avec des couples code–libellé Insee.

Seules les périodes de couples (TYPECOM, COM, LIBELLE) sont datées par
v_commune_depuis_1943.csv ; ne pas assimiler ces périodes à une stabilité
territoriale ni attribuer de géométrie historique.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import unicodedata

REQUIRED = {'TYPECOM', 'COM', 'LIBELLE', 'DATE_DEBUT', 'DATE_FIN'}
SOURCE_URL = 'https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv'
SOURCE_PAGE = 'https://www.insee.fr/fr/information/8740222'

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def norm(value: str) -> str:
    s = (value or '').replace('œ', 'oe').replace('Œ', 'Oe')
    s = ''.join(c for c in unicodedata.normalize('NFKD', s).casefold() if unicodedata.category(c) != 'Mn')
    return ' '.join(re.sub('[^a-z0-9]+', ' ', s).split())

def date_iso(value: str, nullable: bool=False) -> str:
    if not value and nullable:
        return ''
    if not value or date.fromisoformat(value).isoformat() != value:
        raise ValueError('Date ISO invalide : '+repr(value))
    return value

def lire_historique(path: Path) -> tuple[dict, dict]:
    index = defaultdict(list)
    count = Counter()
    with path.open('r', encoding='utf-8-sig', newline='') as stream:
        first = stream.readline()
        stream.seek(0)
        sep = ';' if first.count(';') > first.count(',') else ','
        reader = csv.DictReader(stream, delimiter=sep)
        if not REQUIRED <= set(reader.fieldnames or []):
            raise ValueError('Colonnes Insee manquantes : '+str(sorted(REQUIRED-set(reader.fieldnames or []))))
        seen = set()
        for number, raw in enumerate(reader, start=2):
            typ = (raw['TYPECOM'] or '').strip()
            code = (raw['COM'] or '').strip()
            label = (raw['LIBELLE'] or '').strip()
            if not re.fullmatch(r'(?:[0-9]{5}|2[AB][0-9]{3})', code) or not typ or not label:
                raise ValueError(f'Entrée Insee invalide ligne {number}: {typ}/{code}/{label}')
            begin = date_iso((raw['DATE_DEBUT'] or '').strip())
            end = date_iso((raw['DATE_FIN'] or '').strip(), nullable=True)
            if end and end < begin:
                raise ValueError(f'Intervalle Insee inversé ligne {number}: {begin}..{end}')
            if end and end == begin:
                # La source Insee 2026 contient des couples à durée nulle.
                # Ils restent traçables, mais ne décrivent aucune journée de validité.
                count['intervalles_de_duree_nulle'] += 1
            fingerprint = (typ, code, label, begin, end)
            if fingerprint in seen:
                count['lignes_identiques_repetées'] += 1
                continue
            seen.add(fingerprint)
            rec = {'typecom': typ, 'code': code, 'libelle': label,
                   'date_debut': begin, 'date_fin_exclusive': end,
                   'source_ligne': number}
            index[(typ, code, norm(label))].append(rec)
            count['lignes_uniques'] += 1
            count['type_'+typ] += 1
    for k in index:
        index[k].sort(key=lambda r: (r['date_debut'],r['date_fin_exclusive'],r['libelle']))
    return index, dict(count)

def couvre(rec:dict, entree:list[str], sortie:list[str]) -> bool:
    debut, fin = rec['date_debut'], rec['date_fin_exclusive']
    if fin and fin == debut:
        return False  # Intervalle [d, d[ vide, conservé en provenance uniquement.
    # Le nouvel état est effectif à la date de l'événement ; la date
    # de sortie marque le début de l'état suivant (borne exclusive).
    for dt in entree:
        if dt < debut or (fin and dt >= fin):
            return False
    for dt in sortie:
        if dt < debut or (fin and dt > fin):
            return False
    return True

def enrichir(graphe: Path, historique: Path, sortie: Path, sha_attendu: str | None=None) -> dict:
    for p in (graphe, historique):
        if not p.is_file():
            raise FileNotFoundError(p)
    dests = [sortie / 'graphe-episodes-cog-lot001-dates.json',
             sortie / 'rapport-periodes-cog-lot001.json',
             sortie / 'revue-periodes-cog-lot001.csv']
    if any(x.resolve() in {graphe.resolve(),historique.resolve()} for x in dests):
        raise ValueError('Une sortie écraserait une source')
    input_sha=sha256(historique)
    if sha_attendu and (not re.fullmatch('[a-f0-9]{64}',sha_attendu) or input_sha != sha_attendu):
        raise ValueError('SHA-256 de la source Insee différent de celui attendu')
    graph = json.loads(graphe.read_text(encoding='utf-8'))
    if graph.get('statut') != 'recette_non_validante' or len(graph.get('etats_administratifs',[])) != 33 or len(graph.get('arcs_evenements',[]))!=23:
        raise ValueError('Graphe du lot 001 attendu : 33 états et 23 arcs, non validant')
    index, stats_source=lire_historique(historique)
    result = dict(graph)
    items = []
    counts = Counter()
    reviews=[]
    for state in graph['etats_administratifs']:
        st = dict(state)
        typ,code,label = st['typecom'],st['code'],st['libelle']
        entrees = [date_iso(x) for x in st['entrees_aux_dates_evenements']]
        sorties = [date_iso(x) for x in st['sorties_aux_dates_evenements']]
        possibles = index.get((typ,code,norm(label)), [])
        compatibles=[rec for rec in possibles if couvre(rec,entrees,sorties)]
        if not possibles:
            statut='aucun_couple_code_libelle_trouve'
        elif len(compatibles)==1:
            statut='couple_code_libelle_unique_compatible'
        elif len(compatibles)>1:
            statut='plusieurs_periodes_compatibles_a_instruire'
        else:
            statut='couples_trouves_mais_dates_incompatibles'
        selected = compatibles[0] if len(compatibles)==1 else None
        st.update({
            'statut_qualification_temporelle':statut,
            'periode_code_libelle_cog': ({'date_debut':selected['date_debut'],
                    'date_fin_exclusive':selected['date_fin_exclusive'] or None,
                    'actif_au_millesime_2026':not bool(selected['date_fin_exclusive']),
                    'date_debut_borne_1943':selected['date_debut']=='1943-01-01',
                    'libelle_exact_insee':selected['libelle'],
                    'source_ligne':selected['source_ligne']}
                 if selected else None),
            'nombre_couples_identite_candidats':len(possibles),
            'nombre_couples_compatibles_dates':len(compatibles),
            'periode_validite_officielle_complete': False,
            'geometrie_historique_validee':False,
            'regle_temporalite':'Le couple code–libellé n’atteste pas la stabilité de l’emprise territoriale ; les périodes des COMD/COMA peuvent être absentes de ce fichier.'
        })
        counts[statut]+=1
        items.append(st)
        reviews.append({'dossier':st['dossier'],'id_etat':st['id'],
            'typecom':typ,'code':code,'libelle_etat':label,
            'entrees_mouvements':json.dumps(entrees,ensure_ascii=False),
            'sorties_mouvements':json.dumps(sorties,ensure_ascii=False),
            'statut':statut,'couples_trouves':len(possibles),
            'couples_compatibles':len(compatibles),
            'date_debut_couple':selected['date_debut'] if selected else '',
            'date_fin_exclusive_couple':selected['date_fin_exclusive'] if selected else '',
            'source_ligne_insee':str(selected['source_ligne']) if selected else '',
            'validation_pactols_cog':'non_valide',
            'validation_geometrie_historique':'non_valide'})
    result['etats_administratifs']=sorted(items,key=lambda x:x['id'])
    result['schema_version']='0.2.0'
    result['statut']='recette_non_validante'
    result['provenance_enrichissement']={
        'source_couples_insee':{'url':SOURCE_URL,'page_documentation':SOURCE_PAGE,
           'sha256':input_sha,'fichier':historique.name,'millesime':2026,
           'semantique_periode':'[DATE_DEBUT, DATE_FIN[ ; DATE_FIN vide = encore actif au 01-01-2026, non une validité future assurée'},
        'graphe_initial':{'nom':graphe.name,'sha256':sha256(graphe)},
        'limite':'Couples COM/ARM et autres TYPECOM effectivement fournis ; pas de preuve automatique des géométries ni des états territoriaux.'}
    if len(items)!=33 or len(result['operations'])!=11 or len(result['arcs_evenements'])!=23:
        raise AssertionError('Cardinalités du graphe historique modifiées')
    if any(x.get('statut_lien_pactols_cog')=='valide' for x in result['operations']):
        raise ValueError('Validation Pactols imprévue')
    report={'schema_version':'0.2.0','etat':'recette_non_validante',
            'nombre_etats_du_graphe':len(items),'operations':len(result['operations']),
            'arcs_evenements':len(result['arcs_evenements']),
            'repartition_statuts':dict(sorted(counts.items())),
            'lignes_historique_insee':stats_source,
            'source_sha256':result['provenance_enrichissement'],
            'nouveaux_alignements_pactols_cog_valides':0,
            'geometries_historiques_validees':0,
            'avertissement':'Les périodes datent les couples code–libellé, pas nécessairement les contours territoriaux ; ne pas déduire une période COMD/COMA par silence de la source.'}
    sortie.mkdir(parents=True,exist_ok=True)
    dests[0].write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    dests[1].write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with dests[2].open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(reviews[0]),delimiter=';')
        writer.writeheader();writer.writerows(reviews)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graphe',type=Path,required=True)
    parser.add_argument('--historique',type=Path,required=True)
    parser.add_argument('--sortie',type=Path,required=True)
    parser.add_argument('--sha256-attendu',default=None)
    args=parser.parse_args()
    print(json.dumps(enrichir(args.graphe,args.historique,args.sortie,args.sha256_attendu),ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
