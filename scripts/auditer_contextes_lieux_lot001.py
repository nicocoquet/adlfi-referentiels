#!/usr/bin/env python3
"""Audit reproductible des candidatures du lot Lieux 001 sans validation implicite.

Entrées : revue de lot 001, occurrences et notices issues du même extracteur AdlFI.
Traitement documentaire en lecture seule. Les anomalies éventuelles ne
requalifient jamais automatiquement les autorités Pactols ou les codes COG.
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

FIELDS = [
    'n', 'ark_pactols', 'libelle', 'departement_code', 'code_cog_candidat',
    'profil_revue', 'situation_cog_2026', 'nombre_hierarchies_distinctes',
    'nombre_hierarchies_apres_retrait_racine_facultative',
    'departements_documentaires_distincts', 'nombre_notices_attestant_ark',
    'libelle_present_dans_au_moins_un_titre', 'nb_contextes_transdepartementaux',
    'contexte_a_relire', 'titre_temoin', 'notice_temoin', 'commentaire_contexte',
    'statut_pactols_cog', 'groupe_examen', 'liens_pactols', 'liens_cog'
]


def csv_rows(p):
    with Path(p).open(encoding='utf-8-sig', newline='') as f:
        yield from csv.DictReader(f, delimiter=';')


def hash_file(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def normalize(s):
    s = (s or '').replace('œ', 'oe').replace('Œ', 'Oe')
    s = ''.join(x for x in unicodedata.normalize('NFKD',s).casefold()
                if unicodedata.category(x) != 'Mn')
    return ' '.join(re.sub('[^a-z0-9]+',' ',s).split())


def canon_path(ark_chain, labels):
    # Les imports récents peuvent préfixer un ancêtre global « entités actuelles ».
    # Ce préfixe supplémentaire n'est pas un changement de rattachement territorial.
    ars = list(ark_chain)
    lab = list(labels)
    if lab and lab[0] == 'entités actuelles':
        return (tuple(ars[1:]),tuple(lab[1:]))
    return (tuple(ars),tuple(lab))


def depts_in_chain(labels):
    return tuple(x for x in labels if x.startswith('Département '))


def contextual_flags(ark, occs, all_by_notice, notices, label):
    other_dept = []
    multiple_chain = set()
    normalized = set()
    names = set()
    attested_notices=set()
    titles=set()
    for o in occs:
        paths=json.loads(o['chaine_ark'])
        labels=json.loads(o['chaine_libelles_fr'])
        if len(paths)!=len(labels) or not paths or paths[-1]!=ark:
            raise ValueError('Chaîne Pactols incohérente : '+ark)
        multiple_chain.add((tuple(paths),tuple(labels)))
        normalized.add(canon_path(paths,labels))
        names.add(o.get('libelle_terminal_fr','').strip())
        n=o['notice_id']
        attested_notices.add(n)
        notice=notices.get(n)
        if not notice:
            raise ValueError('Notice manquante : '+n)
        titles.add(notice['titre'])
        dept=set(depts_in_chain(labels))
        other_deps=collections.Counter(
            x for q in all_by_notice[n] if q['ark_terminal']!=ark
            for x in depts_in_chain(json.loads(q['chaine_libelles_fr'])))
        # Indicateur de contexte transdépartemental, non diagnostic d'erreur.
        if sum(other_deps.values()) >= 3 and not dept.intersection(other_deps):
            other_dept.append({
                'notice_id':n, 'titre':notice['titre'],
                'departements_autres':dict(other_deps), 'source_fichier':o['fichier_relatif'],
                'zone_tei':o.get('zone_tei',''),
            })
    has_title=any(normalize(label) in normalize(t) for t in titles)
    return {
        'paths':multiple_chain, 'normalized_paths':normalized, 'names':names,
        'num_notices':len(attested_notices),'has_title':has_title,
        'outliers':other_dept,
    }


def construire(lot, occurrences, notices, out):
    for p in (lot,occurrences,notices):
        if not Path(p).is_file():
            raise FileNotFoundError(p)
    # Ne jamais écraser les sources.
    for dest in (out/'revue_contexte_89.csv',out/'points_a_examiner_001.json',out/'bilan_contextes_lot001.json'):
        if dest.resolve() in {Path(p).resolve() for p in (lot,occurrences,notices)}:
            raise ValueError('Écrasement interdit de fichier source')
    rows=list(csv_rows(lot))
    if len(rows)!=100 or len({r['ark'] for r in rows})!=100:
        raise ValueError('Le lot doit contenir 100 ARK uniques')
    ordinary=[r for r in rows if r['priorite']=='Ordinaire']
    if len(ordinary)!=89:
        raise ValueError('89 autorités ordinaires attendues')
    targets={r['ark'] for r in ordinary}
    source_notices={r['notice_id']:r for r in csv_rows(notices)}
    by_notice=collections.defaultdict(list)
    by_ark=collections.defaultdict(list)
    for r in csv_rows(occurrences):
        by_notice[r['notice_id']].append(r)
        if r['ark_terminal'] in targets:
            by_ark[r['ark_terminal']].append(r)
    if set(by_ark)!=targets:
        raise ValueError('ARK absents des occurrences : '+str(sorted(targets-set(by_ark))))
    observations=[]
    rows_out=[]
    flag_counter=collections.Counter()
    for r in ordinary:
        ark=r['ark']
        info=contextual_flags(ark,by_ark[ark],by_notice,source_notices,r['libelle'])
        nd=sorted({dep for o in by_ark[ark] for dep in depts_in_chain(json.loads(o['chaine_libelles_fr']))})
        if not nd:
            raise ValueError('Département Pactols absent : '+ark)
        # Même si la chaîne contient deux départements, conserver le cas pour revue.
        flags=[]
        if len(nd)!=1:
            flags.append('plusieurs_departements_dans_pactols')
        if len(info['normalized_paths'])>1:
            flags.append('hierarchies_territoriales_divergentes')
        if info['outliers']:
            flags.append('notice_transdepartementale')
        if not info['has_title']:
            flags.append('nom_absent_des_titres')
        # Définir une priorité de lecture, non un score de validité géographique.
        if len(info['normalized_paths'])>1 or len(nd)!=1:
            groupe='A_verifier_hierarchie'
        elif info['outliers'] and not info['has_title']:
            groupe='B_a_relire_contexte'
        elif info['outliers']:
            groupe='C_transversal_mais_atteste'
        else:
            groupe='D_pret_pour_examen_editorial'
        flag_counter.update(flags)
        rows_out.append({
            'n':r['n'], 'ark_pactols':ark, 'libelle':r['libelle'],
            'departement_code':r['departement'], 'code_cog_candidat':r['code'],
            'profil_revue':r['profil_revue'], 'situation_cog_2026':r['date_fin'],
            'nombre_hierarchies_distinctes':len(info['paths']),
            'nombre_hierarchies_apres_retrait_racine_facultative':len(info['normalized_paths']),
            'departements_documentaires_distincts':' | '.join(nd),
            'nombre_notices_attestant_ark':info['num_notices'],
            'libelle_present_dans_au_moins_un_titre':('oui' if info['has_title'] else 'non'),
            'nb_contextes_transdepartementaux':len(info['outliers']),
            'contexte_a_relire':' | '.join(flags),
            'titre_temoin':r['titre_temoin'],'notice_temoin':r['chemin_source'],
            'commentaire_contexte':('Concordance de contexte à instruire ; aucune anomalie démontrée.' if flags else 'Aucune contradiction contextuelle détectée dans les observations extraites.'),
            'statut_pactols_cog':'NON_VALIDE_CANDIDATURE',
            'groupe_examen':groupe,
            'liens_pactols':'https://ark.frantiq.fr/ark:/'+ark,
            'liens_cog':'https://www.insee.fr/fr/metadonnees/geographie/commune/'+r['code'],
        })
        for q in info['outliers']:
            observations.append({'ark':ark,'libelle':r['libelle'],'code_cog_candidat':r['code'],'titre_corps':q['titre'],
                                 'notice_id':q['notice_id'],'autres_departements_index':q['departements_autres'],
                                 'zone_tei':q['zone_tei'],'statut':'controle_contextuel_sans_invalidation'})
    out.mkdir(parents=True,exist_ok=True)
    # Trier par priorité de contrôle, puis ordre déterministe d'origine.
    order={'A_verifier_hierarchie':0,'B_a_relire_contexte':1,'C_transversal_mais_atteste':2,'D_pret_pour_examen_editorial':3}
    rows_out.sort(key=lambda r:(order[r['groupe_examen']],int(r['n'])))
    with (out/'revue_contexte_89.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,delimiter=';',fieldnames=FIELDS)
        w.writeheader();w.writerows(rows_out)
    (out/'points_a_examiner_001.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    categories=collections.Counter(r['groupe_examen'] for r in rows_out)
    report={
        'schema_version':'0.1.0','etat':'audit_documentaire_non_validant',
        'univers':'lot001_89_autorites_ordinaires',
        'autorites':len(rows_out),'alignements_cog_valides_nouveaux':0,
        'toutes_actives_cog_2026':all(r['situation_cog_2026']=='active dans le COG historique 2026' for r in rows_out),
        'plusieurs_departements_dans_pactols':sum('plusieurs_departements_dans_pactols' in r['contexte_a_relire'] for r in rows_out),
        'hierarchies_divergentes_apres_retrait_racine_facultative':sum('hierarchies_territoriales_divergentes' in r['contexte_a_relire'] for r in rows_out),
        'racine_facultative_entites_actuelles_sans_divergence':sum(int(r['nombre_hierarchies_distinctes'])>1 and int(r['nombre_hierarchies_apres_retrait_racine_facultative'])==1 for r in rows_out),
        'absence_nom_dans_tous_les_titres':sum(r['libelle_present_dans_au_moins_un_titre']=='non' for r in rows_out),
        'autorites_avec_notices_transdepartementales':sum(int(r['nb_contextes_transdepartementaux'])>0 for r in rows_out),
        'cas_observations_transdepartementales':len(observations),
        'groupes':dict(sorted(categories.items())),
        'indicateurs':dict(sorted(flag_counter.items())),
        'sources':{Path(p).name:hash_file(p) for p in (lot,occurrences,notices)},
        'limites':['Le nombre de notices atteste la provenance et non la valeur d’une autorité.',
                  'Une absence du libellé dans les titres ne constitue pas une anomalie : l’index peut porter sur le corps.',
                  'Une notice inter-départementale peut être parfaitement correcte, même avec un département Pactols minoritaire.',
                  'Les codes COG et les géométries historiques restent non validés à ce stade.']
    }
    (out/'bilan_contextes_lot001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lot',type=Path,required=True)
    p.add_argument('--occurrences',type=Path,required=True)
    p.add_argument('--notices',type=Path,required=True)
    p.add_argument('--sortie',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(construire(a.lot,a.occurrences,a.notices,a.sortie),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
