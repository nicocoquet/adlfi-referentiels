#!/usr/bin/env python3
"""Qualifie les 42 exceptions lexicales du contrôle national Pactols Lieux.

Entrée = CSV de l'audit de l'export RDF de Frantiq (22/07/2026).
Aucune relation Pactols–COG n'est validée ni publiée. Python standard.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import re
from pathlib import Path

HIST = {
    '26678/pcrtBXhVhHIr4F': 'identite_historique_ou_commune_deleguee',
    '26678/pcrtRNBicOhFjL': 'identite_historique_ou_commune_deleguee',
    '26678/pcrtV597Kj16Ap': 'renommage_administratif',
    '26678/pcrtYQmFfwxLq8': 'ile_non_assimilable_a_une_commune',
    '26678/pcrtlhwJPMkYwg': 'identite_historique_ou_commune_deleguee',
    '26678/pcrtzYbHiu1Bx5': 'identite_historique_ou_commune_deleguee',
}
COLUMNS = ('ark_pactols','libelle_xml','pref_fr_pactols','alt_fr_pactols',
           'categorie_revue','sous_type','alerte_altlabel_numerique',
           'statut_comparaison_skos','controle_a_realiser',
           'alignement_pactols_cog','geometrie_historique_validee')
SOURCE_RDF_SHA = '3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7'


def charger_csv(path: Path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        data=list(csv.DictReader(f,delimiter=';'))
    if not data or not {'ark_pactols','libelle_xml','pref_fr_pactols','alt_fr_pactols',
                        'statut_comparaison','concept_deprecie_export'} <= set(data[0]):
        raise ValueError('Export de contrôle Pactols invalide')
    if len({r['ark_pactols'] for r in data})!=len(data):
        raise ValueError('ARK dupliqués dans l’audit Pactols')
    return data


def traiter(rows):
    exceptions=[]
    for r in rows:
        st=r['statut_comparaison']
        if st=='libelle_pref_fr_concordant':
            continue
        ark=r['ark_pactols']; alt=json.loads(r['alt_fr_pactols']); pref=json.loads(r['pref_fr_pactols'])
        if st=='libelle_alt_fr_concordant':
            categorie='variante_skos_attestee'; subtype='altLabel_fr'
            action='Conserver l’ARK et le libellé XML ; afficher le prefLabel daté ; dater séparément un éventuel nom administratif.'
        elif st=='concept_deprecie_a_instruire':
            categorie='concept_skos_deprecie'; subtype='aucun_successeur_deduit'
            action='Conserver l’attestation historique ; vérifier le concept vivant et son éventuel remplacement auprès de Frantiq.'
        elif st=='libelle_xml_non_retrouve' and ark in HIST:
            categorie='distinction_historique_ou_typologique'; subtype=HIST[ark]
            action='Instruire le type de lieu et les épisodes COG ; ne pas utiliser le seul code INSEE comme identité historique.'
        elif st=='libelle_xml_non_retrouve' and re.search(r'(?:\bR|\bL|\bMer|\bCausse)$',r['libelle_xml'],re.I):
            categorie='abreviation_documentaire_physique'; subtype='toponyme_hydrographique_ou_physique'
            action='Conserver la forme XML ; proposer le prefLabel français pour affichage ; aucun raccordement communal automatique.'
        else:
            categorie='exception_non_classee';subtype='a_instruire'
            action='Contrôler le concept Pactols et le contexte XML avant toute qualification.'
        numeric=[a for a in alt if re.fullmatch(r'[0-9A-Z]{5}',a)]
        exceptions.append(dict(
            ark_pactols=ark,libelle_xml=r['libelle_xml'],
            pref_fr_pactols=' | '.join(pref),alt_fr_pactols=' | '.join(alt),
            categorie_revue=categorie,sous_type=subtype,
            alerte_altlabel_numerique=' | '.join(numeric),
            statut_comparaison_skos=st,controle_a_realiser=action,
            alignement_pactols_cog='non_valide',geometrie_historique_validee='non',
        ))
    return sorted(exceptions,key=lambda x:x['ark_pactols'])


def construire(source:Path,sortie:Path,attendu:int|None=42):
    if not source.is_file():raise FileNotFoundError(source)
    if (sortie/'qualifications-skos-exceptions-42.csv').resolve()==source.resolve():
        raise ValueError('Source et destination identiques')
    items=traiter(charger_csv(source))
    if attendu is not None and len(items)!=attendu:
        raise ValueError(f'Attendu {attendu} exceptions, obtenu {len(items)}')
    categories=collections.Counter(x['categorie_revue'] for x in items)
    if attendu==42 and (categories != {'abreviation_documentaire_physique':26,'variante_skos_attestee':9,
        'distinction_historique_ou_typologique':6,'concept_skos_deprecie':1}):
        raise ValueError(f'Répartition inattendue des 42 cas: {dict(categories)}')
    sortie.mkdir(parents=True,exist_ok=True)
    destination=sortie/'qualifications-skos-exceptions-42.csv'
    with destination.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS,delimiter=';');writer.writeheader();writer.writerows(items)
    report={'schema_version':'0.1.0','statut':'recette_non_validante',
       'nombre_exceptions':len(items),'repartition':dict(sorted(categories.items())),
       'alertes_altlabel_numerique':[
           {'ark':i['ark_pactols'],'libelle':i['libelle_xml'],'valeur':i['alerte_altlabel_numerique']}
           for i in items if i['alerte_altlabel_numerique']],
       'source_audit_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
       'source_pactols_rdf_sha256':SOURCE_RDF_SHA,
       'limites': 'Comparaison lexicale SKOS, sans validation d’identité administrative ni géométrie historique.'}
    (sortie/'rapport-qualifications-skos-42.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--controle-skos',type=Path,required=True)
    p.add_argument('--sortie',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(construire(a.controle_skos,a.sortie),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
