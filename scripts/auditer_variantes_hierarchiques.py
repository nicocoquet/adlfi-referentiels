#!/usr/bin/env python3
"""Classifier sans altérer les hiérarchies Pactols observées dans les XML AdlFI.

Le concept racine facultatif est identifié par SON ARK, car son libellé a
plusieurs variantes dans les XML (« entités actuelles », « entités
 géopolitiques actuelles »...). Suppression uniquement pour COMPARAISON.
Les chaînes originales sont conservées dans le CSV des exceptions.
"""
from __future__ import annotations
import argparse,csv,collections,hashlib,json
from pathlib import Path

ROOT_CURRENT='26678/pcrtd5d8pstxspv6dbhp7d8g'
HEADERS=['ark_pactols','libelle_terminal_releve','type_variation','nombre_hierarchies_brutes',
         'nombre_hierarchies_sans_racine','nombre_hierarchies_ark_sans_racine',
         'hierarchies_sources','fichiers_temoins','statut_validation']

def lire_csv(p):
    with Path(p).open('r',encoding='utf-8-sig',newline='') as f:
        yield from csv.DictReader(f,delimiter=';')

def sha256(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def normaliser_racine(arks,libelles):
    if len(arks)!=len(libelles):
        raise ValueError('Hiérarchie Pactols de tailles discordantes')
    if arks and arks[0]==ROOT_CURRENT:
        return (tuple(arks[1:]),tuple(libelles[1:]))
    return tuple(arks),tuple(libelles)

def categoriser(paths):
    """paths = ensemble de paires (tuple ARK, tuple libellés), APRÈS racine."""
    if len(paths)<2:return 'aucune_divergence_restante'
    if any(any(label in (None, '') for label in labs) for ark,labs in paths):
        return 'ancetre_sans_libelle_xml_a_reconstituer'
    codes={ark for ark,labs in paths}
    if len(codes)==1:return 'variantes_de_libelles_sans_changement_ark'
    if any(labs and isinstance(labs[0], str) and ('hydro' in labs[0].lower() or 'aquatiques' in labs[0].lower())
           for ark,labs in paths):
        return 'hierarchies_hydrographiques_alternatives'
    return 'branches_hierarchiques_differentes_a_instruire'

def construire(occurrences,sortie):
    source=Path(occurrences)
    if not source.is_file():raise FileNotFoundError(source)
    out=Path(sortie)
    for name in ('rapport_variantes_hierarchiques.json','hierarchies_residuelles_40.csv'):
        if (out/name).resolve()==source.resolve():raise ValueError('La source ne peut être écrasée')
    raw=collections.defaultdict(set)
    norm=collections.defaultdict(set)
    witnesses=collections.defaultdict(set)
    terminal=collections.defaultdict(set)
    for r in lire_csv(source):
        k=r['ark_terminal']; arks=json.loads(r['chaine_ark']); labels=json.loads(r['chaine_libelles_fr'])
        if not isinstance(arks,list) or not isinstance(labels,list) or len(arks)!=len(labels) or not arks or arks[-1]!=k:
            raise ValueError('ARK ou chaînes invalides : '+k)
        orig=(tuple(arks),tuple(labels))
        raw[k].add(orig)
        norm[k].add(normaliser_racine(arks,labels))
        witnesses[k].add(r['fichier_relatif'])
        terminal[k].add(r.get('libelle_terminal_fr',''))
    counts=collections.Counter()
    exceptional=[]
    for k in sorted(raw):
        nraw=len(raw[k]);nnorm=len(norm[k]);ncodes=len({a for a,l in norm[k]})
        if nraw>1:counts['ark_aux_hierarchies_multiples_brutes']+=1
        if len({a for a,l in raw[k]})>1:counts['ark_aux_chemins_ark_multiples_bruts']+=1
        if nraw>1 and nnorm==1:counts['ark_multihierarchies_resolus_par_racine_facultative']+=1
        if nnorm>1:
            cat=categoriser(norm[k]);counts['ark_variations_residuelles']+=1
            counts[cat]+=1
            exceptional.append({
                'ark_pactols':k,
                'libelle_terminal_releve':' | '.join(sorted(terminal[k])),
                'type_variation':cat,
                'nombre_hierarchies_brutes':nraw,
                'nombre_hierarchies_sans_racine':nnorm,
                'nombre_hierarchies_ark_sans_racine':ncodes,
                'hierarchies_sources':json.dumps([{'arks':list(a),'libelles':list(l)} for a,l in sorted(raw[k], key=lambda e: json.dumps(e,ensure_ascii=False))],ensure_ascii=False),
                'fichiers_temoins':json.dumps(sorted(witnesses[k])[:6],ensure_ascii=False),
                'statut_validation':'non_valide_examen_de_referentiel',
            })
    counts['total_ark']=len(raw)
    if (counts['ark_multihierarchies_resolus_par_racine_facultative']+counts['ark_variations_residuelles'] != counts['ark_aux_hierarchies_multiples_brutes']):
        raise AssertionError('Catégories non exhaustives')
    out.mkdir(parents=True,exist_ok=True)
    with (out/'hierarchies_residuelles_40.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=HEADERS,delimiter=';')
        w.writeheader();w.writerows(exceptional)
    report={
        'schema_version':'0.1.0',
        'etat':'audit_des_hierarchies_documentaires_non_validant',
        'racine_optionnelle_pactols':ROOT_CURRENT,
        'normalisation':'La racine supplémentaire est ignorée uniquement dans la comparaison. Aucun ARK ni chemin d’origine n’est effacé.',
        **dict(sorted(counts.items())),
        'source':{'fichier':source.name,'sha256':sha256(source)},
        'prudence':'Les variantes de libellé peuvent refléter des renommages réels ; les chaînes contenant des ancêtres vides ne sont pas des alignements certains.',
    }
    (out/'rapport_variantes_hierarchiques.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--occurrences',type=Path,required=True)
    p.add_argument('--sortie',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(construire(args.occurrences,args.sortie),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
