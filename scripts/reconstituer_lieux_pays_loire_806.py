#!/usr/bin/env python3
"""Reconstruire et auditer les 806 ARK des Pays de la Loire depuis les sources v2 figées.

Exécution locale en recette ; aucune écriture vers docs/data ni vers les fichiers source.
"""
import argparse,csv,hashlib,json,tempfile
from pathlib import Path
from scripts.preparer_lots_lieux_regions import prepare,COLS
from scripts.auditer_lieux_pays_loire_cog import produire

EXPECTED={
 'autorites':'878aa70f32d43313ea5bd36bbb30bbd6b57b4872ba2f68a5117ac6c35b6380b6',
 'occurrences':'b2e7332515c051e0c63e1fb29c840fa338aa85040fb2358a7df64d735b2942cd',
 'skos_csv':'502db0f84188beca666d521417ad6775fb5f670c5b9a295250a9024fd4ede407',
}
COG_SHA={
 'communes':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3',
 'historique':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee',
 'mouvements':'8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1',
}
# Colonnes d'identité stables du pilote ; les statistiques de contexte sont recalculées.
ID_FIELDS=('ark_pactols','region','departement_hierarchie','libelle_xml',
           'pref_fr_pactols','codes_insee_skos','types_liens_insee_skos',
           'autres_uris_insee','categorie_geographique')

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

def csvrows(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f,delimiter=';'))

def verifier_sources(paths,expected):
    for k,digest in expected.items():
        p=Path(paths[k])
        if not p.is_file():raise FileNotFoundError(str(p))
        if sha(p)!=digest:raise ValueError('Empreinte non conforme pour '+k)

def comparer_pilote(complet,pilote):
    items=csvrows(complet);ref=csvrows(pilote)
    if len(items)!=806 or len(ref)!=25:raise ValueError('Cardinalité 806/25 non conforme')
    byark={x['ark_pactols']:x for x in items}
    if len(byark)!=806:raise ValueError('ARK dupliqués dans inventaire complet')
    for item in ref:
        ark=item['ark_pactols']
        if ark not in byark:raise ValueError('ARK du pilote absent '+ark)
        for c in ID_FIELDS:
            if byark[ark][c]!=item[c]:raise ValueError('Divergence pilote '+ark+' '+c)
    return len(ref)

def executer(autorites,occurrences,skos_csv,pilote,communes,historique,mouvements,sortie):
    paths=dict(autorites=autorites,occurrences=occurrences,skos_csv=skos_csv)
    verifier_sources(paths,EXPECTED)
    if not Path(pilote).is_file():raise FileNotFoundError(str(pilote))
    verifier_sources(dict(communes=communes,historique=historique,mouvements=mouvements),COG_SHA)
    sortie=Path(sortie)
    if any(sortie.resolve()==p.resolve() or sortie.resolve().is_relative_to(p.resolve())
           for p in [*paths.values(),pilote,communes,historique,mouvements]):
        raise ValueError('Sortie située dans une source')
    with tempfile.TemporaryDirectory(prefix='pdl806-') as tmp:
        tmp=Path(tmp)
        rep=prepare(Path(autorites),Path(occurrences),Path(skos_csv),tmp,25)
        inventaire=tmp/'inventaire-pays-de-la-loire.csv'
        if rep['regions']['Pays de la Loire']['ark_distincts']!=806:
            raise ValueError('Le périmètre de 806 ARK a changé')
        comparer_pilote(inventaire,pilote)
        # Ne produire les sorties définitives qu'après tous les contrôles de provenance.
        sortie.mkdir(parents=True,exist_ok=True)
        import shutil
        dest=sortie/'inventaire-pays-de-la-loire.csv'
        if dest.exists():raise FileExistsError(str(dest))
        shutil.copyfile(inventaire,dest)
        try:
            audit=produire(dest,Path(communes),Path(historique),Path(mouvements),sortie/'audit-cog',806)
        except Exception:
            dest.unlink()
            raise
        bilan={'etat':'recette_non_validante','ark':806,'pilote_identique':25,
               'sources_xml_skos_sha256':EXPECTED,'audit':audit,
               'note':'Aucune validation AdlFI ou géométrie historique publiée.'}
        (sortie/'bilan-reconstruction.json').write_text(json.dumps(bilan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        return bilan

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('autorites','occurrences','skos_csv','pilote','communes','historique','mouvements','sortie'):
        p.add_argument('--'+n.replace('_','-'),required=True,type=Path)
    a=vars(p.parse_args())
    print(json.dumps(executer(**a),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
