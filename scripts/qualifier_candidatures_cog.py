#!/usr/bin/env python3
"""Audit géographique des candidatures COG : jamais de validation automatique.

Rejoint les candidats historiques du premier export avec le département
attesté dans une chaîne Pactols et le fichier officiel v_departement_2026.csv.
Les éventuelles discordances historiques ne sont jamais corrigées par inférence.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

from construire_referentiel_lieux_national import normaliser, lire_csv, sha256

PREF_DEPT = re.compile(
    r"^Département\s+(?:de\s+la\s+|de\s+l['’]\s*|des\s+|du\s+|de\s+|d['’]\s*)(.+)$",
    re.IGNORECASE,
)
FIELDS = ['ark_pactols','libelle_documentaire','profil','statut_premier_export',
          'departements_pactols','codes_departement_attendus','codes_cog_lexicaux',
          'codes_cog_departement_concordants','categorie_audit','risque_historique',
          'annees_operation','details_cog_candidats','premiere_attestation','statut_validation']


def code_departement(code: str) -> str:
    """Lecture du préfixe COG, sans présumer sa compatibilité historique."""
    code = str(code)
    if not re.fullmatch(r'[0-9AB]{5}', code):
        return ''
    return code[:3] if code.startswith(('97','98')) else code[:2]


def extraire_departements(chemins):
    labels = set()
    for chemin in chemins:
        for libelle in chemin.get('libelles', []):
            m = PREF_DEPT.match(libelle or '')
            if m:
                labels.add(m.group(1).strip())
    return sorted(labels, key=normaliser)


def lire_departements(path):
    mapped = collections.defaultdict(set)
    for row in lire_csv(path, {'DEP','LIBELLE'}):
        label = row['LIBELLE'].strip()
        code = row['DEP'].strip()
        if label and re.fullmatch(r'[0-9AB]{2,3}', code):
            mapped[normaliser(label)].add(code)
    return mapped


def calculer_risque_historique(candidates, annees):
    """Indicateur éditorial : pas une preuve de contemporanéité du toponyme."""
    if not candidates:
        return 'sans_candidature'
    if not annees:
        return 'annees_operation_absentes'
    try:
        years = [int(x) for x in annees]
    except (ValueError,TypeError):
        return 'annees_operation_non_exploitables'
    if not years:
        return 'annees_operation_absentes'
    finies = [x for x in candidates if x.get('date_fin')]
    if finies and len(finies) == len(candidates):
        if all(min(years) >= int(x['date_fin'][:4]) for x in finies):
            return 'forme_cog_historique_anterieure_aux_operations'
    if any(x.get('date_debut') and max(years) < int(x['date_debut'][:4]) for x in candidates):
        return 'periodes_cog_et_operations_a_expertiser'
    return 'pas_d_anomalie_temporelle_simple'


def determiner_statut(autorite, candidats, deps, codes_deps):
    typ = autorite['profil_geographique_provisoire']
    status = autorite['statut_raccordement']
    code_all = sorted({str(x['code_insee_historique']) for x in candidats})
    candidate_in_dept = sorted(x for x in code_all if code_departement(x) in codes_deps)
    if autorite.get('validation_existante'):
        return 'alignement_editorial_preexistant',candidate_in_dept,code_all
    if typ in ('hydrographie_hors_cog_communal','geographie_physique_hors_cog_communal','autre_hors_champ_cog_communal'):
        return 'hors_perimetre_cog_communal',candidate_in_dept,code_all
    if typ == 'sous_commune_ou_lieu_imbrique_a_qualifier':
        return 'lieu_imbrique_ou_ancienne_commune_a_instruire',candidate_in_dept,code_all
    if not code_all:
        return 'aucune_candidature_lexicale',candidate_in_dept,code_all
    if len(deps) > 1:
        return 'plusieurs_departements_pactols',candidate_in_dept,code_all
    if not deps or not codes_deps:
        return 'departement_non_resolu',candidate_in_dept,code_all
    if len(codes_deps) > 1:
        return 'departement_equivoque_cog',candidate_in_dept,code_all
    if not candidate_in_dept:
        return 'conflit_departement_cog_vs_pactols',candidate_in_dept,code_all
    if len(candidate_in_dept) > 1:
        return 'homonymie_persistante_dans_departement',candidate_in_dept,code_all
    if len(code_all) > 1:
        return 'homonymie_nationale_reduite_a_un_code_par_departement',candidate_in_dept,code_all
    if typ != 'sous_departement_candidat_communal':
        return 'profil_non_communal_a_confirmer',candidate_in_dept,code_all
    return 'un_code_corrobore_par_departement',candidate_in_dept,code_all


def construire(master_path:Path, candidats_path:Path, departements_path:Path, sortie:Path, taille_lot=100):
    paths=[master_path,candidats_path,departements_path]
    for f in paths:
        if not f.is_file():
            raise FileNotFoundError(f)
    expected={sortie/'audit_candidatures_par_ark.csv',sortie/'lot_editorial_prioritaire_001.csv',sortie/'rapport_qualification_cog.json'}
    if {p.resolve() for p in expected} & {p.resolve() for p in paths}:
        raise ValueError('Sortie et source identiques')
    if taille_lot<1 or taille_lot>500:
        raise ValueError('taille_lot doit être comprise entre 1 et 500')
    master=json.loads(master_path.read_text(encoding='utf-8'))
    if not isinstance(master.get('autorites'),list) or master.get('unite')!='concept_pactols_atteste_dans_XML':
        raise ValueError('Schéma du maître national non reconnu')
    idx=collections.defaultdict(list)
    for x in lire_csv(candidats_path, {'ark_pactols','code_insee_historique','libelle_cog','date_debut','date_fin'}):
        idx[x['ark_pactols']].append(x)
    depts=lire_departements(departements_path)
    total_candidatures=sum(len(rows) for rows in idx.values())
    audit=[]
    statuses=collections.Counter()
    for aut in master['autorites']:
        ark=aut['ark_pactols']
        labels=extraire_departements(aut['hierarchies_pactols_attestees'])
        expected_deps=sorted({c for label in labels for c in depts.get(normaliser(label),set())})
        candidate_rows=idx.pop(ark,[])
        cat,confirmed,codes=determiner_statut(aut,candidate_rows,labels,expected_deps)
        statuses[cat]+=1
        risk=calculer_risque_historique([x for x in candidate_rows if x['code_insee_historique'] in confirmed],
                                        aut['annees_operation_attestees'])
        rec={
            'ark_pactols':ark, 'libelle_documentaire':aut['libelle_documentaire'],
            'profil':aut['profil_geographique_provisoire'],
            'statut_premier_export':aut['statut_raccordement'],
            'departements_pactols':json.dumps(labels,ensure_ascii=False),
            'codes_departement_attendus':json.dumps(expected_deps),
            'codes_cog_lexicaux':json.dumps(codes),
            'codes_cog_departement_concordants':json.dumps(confirmed),
            'categorie_audit':cat, 'risque_historique':risk,
            'annees_operation':json.dumps(aut['annees_operation_attestees']),
            'details_cog_candidats':json.dumps([{k:r.get(k,'') for k in ('code_insee_historique','libelle_cog','date_debut','date_fin','typecom')} for r in candidate_rows],ensure_ascii=False),
            'premiere_attestation':aut['attestation_temoin']['notice_id'],
            'statut_validation':'non_valide' if not aut['validation_existante'] else 'valide_pilote_paca_2026',
        }
        audit.append(rec)
    if idx:
        raise ValueError(f'Candidatures pour {len(idx)} ARK absents du maître')
    if len(audit)!=len({x['ark_pactols'] for x in audit}):
        raise ValueError('ARK dupliqués dans le maître')
    # Lot limité et réparti : première passe d'une autorité par département,
    # puis second tour jusqu'à atteindre taille_lot. Les catégories ne valent
    # jamais validation. Les types de lieux imbriqués sont exclus de ce lot.
    eligible=[x for x in audit if x['categorie_audit'] in (
        'un_code_corrobore_par_departement',
        'homonymie_nationale_reduite_a_un_code_par_departement')]
    priority={'homonymie_nationale_reduite_a_un_code_par_departement':0,
              'un_code_corrobore_par_departement':1}
    eligible.sort(key=lambda x:(priority[x['categorie_audit']],
                                x['libelle_documentaire'].casefold(),x['ark_pactols']))
    bydept=collections.defaultdict(list)
    for x in eligible:
        bydept[json.loads(x['codes_departement_attendus'])[0]].append(x)
    lot=[]
    while len(lot)<taille_lot and any(bydept.values()):
        for d in sorted(bydept):
            if bydept[d] and len(lot)<taille_lot:
                lot.append(bydept[d].pop(0))
    sortie.mkdir(parents=True,exist_ok=True)
    for filename, rows in [('audit_candidatures_par_ark.csv',audit),('lot_editorial_prioritaire_001.csv',lot)]:
        with (sortie/filename).open('w',newline='',encoding='utf-8-sig') as fh:
            w=csv.DictWriter(fh,fieldnames=FIELDS,delimiter=';')
            w.writeheader();w.writerows(rows)
    report={
        'schema_version':'0.1.0', 'etat':'audit_non_validant',
        'autorites':len(audit),'candidatures_lignes':total_candidatures,
        'repartition':dict(sorted(statuses.items())),
        'lot_prioritaire_001':len(lot),
        'source_sha256':{p.name:sha256(p) for p in paths},
        'avertissement':'Une concordance départementale ne prouve ni identité historique, ni géométrie, ni équivalence SKOS.',
    }
    # Aucune donnée de publication, aucune géométrie historique inférée.
    (sortie/'rapport_qualification_cog.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--autorites',required=True,type=Path,help='autorites_nationales.json')
    parser.add_argument('--candidatures',required=True,type=Path,help='candidatures_cog_historiques.csv')
    parser.add_argument('--departements',required=True,type=Path,help='v_departement_2026.csv de l’Insee')
    parser.add_argument('--sortie',required=True,type=Path)
    parser.add_argument('--taille-lot',type=int,default=100)
    a=parser.parse_args()
    print(json.dumps(construire(a.autorites,a.candidatures,a.departements,a.sortie,a.taille_lot),
                     ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
