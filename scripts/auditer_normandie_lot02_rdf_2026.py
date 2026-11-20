#!/usr/bin/env python3
"""Normandie lot 02 : examiner dix collisions d'ARK sans décider d'alignement.

La preuve du code communal actuel provient du préflight officiel #154 ; le RDF
épinglé est relu, y compris les notes, définitions et liens de remplacement.
L'existence d'un exactMatch commun ne vaut pas assimilation des deux concepts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from auditer_pactols_polynesie_2026 import RDF_SHA, RDF_COMMIT, analyser_rdf, label_compatible
from auditer_normandie_lot01_identites_2026 import rdf_complementaire

SCHEMA="adlfi.lieux.normandie.lot02.candidats.2026.audit.v1"
# Issues du rapport COG/RDF #154. Deux ARK par code, dont un candidat
# contemporain d'après son libellé ; AUCUNE validation automatique.
CASES={
  "27112": {"nom":"Breteuil", "actuel":"26678/pcrtwD0OalOHGK", "ancien":"26678/pcrtKa9QelswXe",
            "label_actuel":"Breteuil (Eure)", "label_ancien":"Breteuil (commune déléguée)"},
  "61341": {"nom":"Écouves", "actuel":"26678/pcrtsZJYVKHuCr", "ancien":"26678/pcrtfjO3sQkDv7",
            "label_actuel":"Écouves", "label_ancien":"Radon"},
  "27471": {"nom":"Porte-de-Seine", "actuel":"26678/pcrtTVZxjfH4A1", "ancien":"26678/pcrtQB6XrQQ9LZ",
            "label_actuel":"Porte-de-Seine", "label_ancien":"Porte-Joie"},
  "50239": {"nom":"Thèreval", "actuel":"26678/pcrtPvLbdZBmws", "ancien":"26678/pcrtkp7pbzeyjj",
            "label_actuel":"Thèreval", "label_ancien":"Hébécrevon"},
  "61211": {"nom":"Juvigny Val d'Andaine", "actuel":"26678/pcrtQPOvb7fsR5", "ancien":"26678/pcrtV19FHEOsRO",
            "label_actuel":"Juvigny Val d'Andaine", "label_ancien":"Juvigny-sous-Andaine"},
  "76258": {"nom":"Terres-de-Caux", "actuel":"26678/pcrt9wS8mfBRqs", "ancien":"26678/pcrtHyxyLS19S7",
            "label_actuel":"Terres-de-Caux", "label_ancien":"Fauville-en-Caux"},
  "50546": {"nom":"Bourgvallées", "actuel":"26678/pcrtgtbpJSZPKx", "ancien":"26678/pcrtiPrPGO44Zc",
            "label_actuel":"Bourgvallées", "label_ancien":"Saint-Samson-de-Bonfossé"},
  "14035": {"nom":"Balleroy-sur-Drôme", "actuel":"26678/crts1h2V4fgZ4", "ancien":"26678/pcrtBZN8Mc6oeC",
            "label_actuel":"Balleroy-sur-Drôme", "label_ancien":"Balleroy"},
  "14342": {"nom":"Isigny-sur-Mer", "actuel":"26678/pcrtJiEVVL4S0d", "ancien":"26678/pcrtOlN1ZN3BqW",
            "label_actuel":"Isigny-sur-Mer", "label_ancien":"Isigny-sur-Mer (commune déléguée)"},
  "14654": {"nom":"Saint-Pierre-en-Auge", "actuel":"26678/pcrtf4lulrxUo6", "ancien":"26678/pcrt5RPJFgGgvO",
            "label_actuel":"Saint-Pierre-en-Auge", "label_ancien":"Saint-Pierre-sur-Dives"},
}


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):
            h.update(block)
    return h.hexdigest()


def produire(rdf:Path)->dict:
    if sha256(rdf)!=RDF_SHA:
        raise ValueError("RDF Pactols différent de la source épinglée")
    all_arks=[a for c in CASES.values() for a in (c['actuel'],c['ancien'])]
    if len(set(all_arks))!=20:
        raise ValueError("Un ARK est réutilisé dans plusieurs dossiers")
    scanned=analyser_rdf(rdf,{code:c['nom'] for code,c in CASES.items()})
    enrichis=rdf_complementaire(rdf,set(all_arks))
    dossiers=[]
    for code,source in sorted(CASES.items()):
        proofs=scanned['explicites'][code]
        hits={x['ark']:x for x in proofs}
        if set(hits)!={source['actuel'],source['ancien']}:
            raise ValueError('Candidatures RDF modifiées pour '+code)
        candidates=[]
        for kind in ('actuel','ancien'):
            ark=source[kind]
            proof=hits[ark]
            rdf_extra=enrichis[ark]
            expected=source['label_'+kind]
            if (proof['prefLabels_fr']!=[expected] or
                    rdf_extra['prefLabels_fr']!=[expected] or
                    rdf_extra['altLabels_fr']!=proof['altLabels_fr'] or
                    rdf_extra['owl_deprecated']!=proof['deprecie']):
                raise ValueError('Libellé ou statut RDF non conforme : '+ark)
            code_uri='http://id.insee.fr/geo/commune/'+code
            if (sum(u['famille']=='commune' and u['code']==code
                    for u in proof['insee_exactMatch'])!=1 or
                    code_uri not in rdf_extra['exactMatch']):
                raise ValueError('Identifiant communal COG absent : '+ark)
            if kind=='actuel' and not label_compatible(source['nom'],expected):
                raise ValueError('Libellé contemporain non compatible : '+ark)
            candidates.append({
                'ark':ark,
                'role_preliminaire': ('CANDIDAT_COMMUNE_ACTUELLE_A_INSTRUIRE'
                                     if kind=='actuel'
                                     else 'IDENTITE_ANTERIEURE_OU_DELEGUEE_A_INSTRUIRE'),
                **rdf_extra,
                'nouvelle_validation':False,
            })
        dossiers.append({
            'code_COG_2026':code,
            'nom_COG_2026':source['nom'],
            'source_COG':'https://www.insee.fr/fr/statistiques/2011101?geo=COM-'+code,
            'candidats_Pactols':candidates,
            'decision_editoriale':'NON_PRISE',
            'nouvelles_geometries':0,
            'liens_historiques_inferes':0,
        })
    summary=Counter(c['role_preliminaire'] for d in dossiers for c in d['candidats_Pactols'])
    return {
        'schema':SCHEMA,
        'statut':'RECETTE_NON_VALIDANTE',
        'source_rdf':{'repo':'frantiq/PACTOLS','commit':RDF_COMMIT,
                      'sha256':RDF_SHA},
        'source_COG':'Préflight Normandie 2026 (PR 154), TYPECOM=COM, REG=28',
        'bilan':{
            'communes_COG_a_instruire':len(dossiers),
            'ARK_candidats':len(all_arks),
            'statuts_candidats':dict(sorted(summary.items())),
            'concepts_RDF_examines':scanned['concepts_RDF_examines'],
            'nouvelles_validations':0,
            'nouvelles_geometries':0,
            'liens_historiques_inferes':0,
        },
        'dossiers':dossiers,
        'limitations':[
            "Un skos:exactMatch commun au même code INSEE peut désigner deux identités administratives datées.",
            "Les rôles provisoires sont fondés sur les libellés : ni décision éditoriale ni preuve de date.",
            "Les notes RDF/INSEE doivent être contrôlées avant toute éventuelle validation 2026.",
            "Aucune année d'opération AdlFI n'est assimilée automatiquement à la date de création d'une commune.",
            "Aucun nouveau contour, ARK ou alignement temporel n'est publié dans ce lot.",
        ],
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rdf',required=True,type=Path)
    parser.add_argument('--sortie',required=True,type=Path)
    args=parser.parse_args()
    target=args.sortie.resolve()
    if target.exists() or 'docs' in target.parts:
        raise ValueError('Sortie neuve hors docs/ uniquement')
    report=produire(args.rdf)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',
                      encoding='utf-8')
    print('NORMANDIE_LOT02',json.dumps(report['bilan'],ensure_ascii=False,sort_keys=True))


if __name__=='__main__':
    main()
