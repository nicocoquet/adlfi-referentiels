#!/usr/bin/env python3
"""Audit en lecture seule d'ARK AdlFI contre l'export RDF/XML SKOS Pactols Lieux.

Ne produit ni équivalences SKOS ni correspondances COG validées. Pour les gros
exports (LFS), analyse XML en flux. La version de juillet 2026 est figée par
son empreinte SHA-256, sauf choix explicite d'une autre empreinte.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

SHA_RDF_20260722 = '3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7'
SKOS = '{http://www.w3.org/2004/02/skos/core#}'
RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
XML = '{http://www.w3.org/XML/1998/namespace}'
OWL = '{http://www.w3.org/2002/07/owl#}'
ARK_RE = re.compile(r'/ark:/26678/([A-Za-z0-9]+)(?:$|[?#])')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1 << 20), b''):
            h.update(data)
    return h.hexdigest()


def norm(value: str) -> str:
    value = (value or '').replace('œ', 'oe').replace('Œ', 'Oe')
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ',
        ''.join(x for x in unicodedata.normalize('NFKD', value).casefold()
                if unicodedata.category(x) != 'Mn')).split())


def charger_autorites(path: Path) -> list[dict]:
    doc = json.loads(path.read_text(encoding='utf-8'))
    items = doc.get('autorites', [])
    if doc.get('unite') != 'concept_pactols_atteste_dans_XML' or not isinstance(items, list):
        raise ValueError('Source non conforme à autorites_nationales.json')
    ids = [x.get('ark_pactols') for x in items]
    if len(set(ids)) != len(ids) or any(not re.fullmatch(r'26678/[A-Za-z0-9]+', k or '') for k in ids):
        raise ValueError('ARK mal formé ou dupliqué')
    return items


def lire_skos(path: Path, wanted: set[str]) -> dict:
    found = {}
    # RDF/XML réel : skos:Concept, et éventuelle représentation rdf:Description.
    for event, elem in ET.iterparse(path, events=('end',)):
        if elem.tag not in (SKOS+'Concept', RDF+'Description'):
            continue
        about = elem.attrib.get(RDF+'about', '')
        m = ARK_RE.search(about)
        if m and ('26678/'+m.group(1)) in wanted:
            ark = '26678/'+m.group(1)
            prefs, alts, hidden, matches = [], [], [], []
            for child in elem:
                lang = (child.attrib.get(XML+'lang') or '').lower()
                value = ''.join(child.itertext()).strip()
                if child.tag == SKOS+'prefLabel' and (lang == 'fr' or lang.startswith('fr-')) and value:
                    prefs.append(value)
                if child.tag == SKOS+'altLabel' and (lang == 'fr' or lang.startswith('fr-')) and value:
                    alts.append(value)
                if child.tag == SKOS+'hiddenLabel' and (lang == 'fr' or lang.startswith('fr-')) and value:
                    hidden.append(value)
                if child.tag == SKOS+'exactMatch':
                    url = child.attrib.get(RDF+'resource', '')
                    if url:
                        matches.append(url)
            dep = any(child.tag == OWL+'deprecated' and ''.join(child.itertext()).strip().lower() in ('true','1') for child in elem)
            if prefs or alts or hidden or matches or dep:
                if ark in found:
                    raise ValueError('Concept Pactols présent plusieurs fois : '+ark)
                found[ark] = dict(pref=sorted(set(prefs)),alt=sorted(set(alts)),hidden=sorted(set(hidden)),exact=sorted(set(matches)),deprecated=dep)
        elem.clear()
    return found


def audit(autorites: Path, rdf: Path, sortie: Path, sha_attendu: str) -> dict:
    if not autorites.is_file() or not rdf.is_file():
        raise FileNotFoundError('Autorités nationales ou export RDF introuvable')
    items = charger_autorites(autorites)
    target = sortie/'controle_concepts_pactols.csv'
    report_path = sortie/'rapport_concepts_pactols.json'
    if target.resolve() in (autorites.resolve(),rdf.resolve()) or report_path.resolve() in (autorites.resolve(),rdf.resolve()):
        raise ValueError('Ne pas écraser une source')
    if not re.fullmatch(r'[0-9a-fA-F]{64}',sha_attendu):
        raise ValueError('Empreinte SHA-256 attendue invalide')
    sh = sha256(rdf)
    if sh.lower() != sha_attendu.lower():
        raise ValueError(f'Empreinte inattendue de Pactols : {sh} != {sha_attendu}; vérifier que ce n\'est pas un pointeur Git LFS')
    found = lire_skos(rdf, {i['ark_pactols'] for i in items})
    result=[]
    count=collections.Counter()
    for item in sorted(items,key=lambda x:x['ark_pactols']):
        ark,label=item['ark_pactols'],item.get('libelle_documentaire','')
        rec=found.get(ark)
        if rec is None:
            status='absent_export_date'
            rec=dict(pref=[],alt=[],hidden=[],exact=[],deprecated=False)
        elif rec['deprecated']:
            status='concept_deprecie_a_instruire'
        elif norm(label) in {norm(x) for x in rec['pref']}:
            status='libelle_pref_fr_concordant'
        elif norm(label) in {norm(x) for x in rec['alt']}:
            status='libelle_alt_fr_concordant'
        elif norm(label) in {norm(x) for x in rec['hidden']}:
            status='libelle_cache_fr_a_instruire'
        elif not rec['pref']:
            status='pref_label_fr_absent'
        else:
            status='libelle_xml_non_retrouve'
        count[status]+=1
        result.append({'ark_pactols':ark,'libelle_xml':label,
            'pref_fr_pactols':json.dumps(rec['pref'],ensure_ascii=False),
            'alt_fr_pactols':json.dumps(rec['alt'],ensure_ascii=False),
            'hidden_fr_pactols':json.dumps(rec['hidden'],ensure_ascii=False),
            'liens_exact_match_pactols':json.dumps(rec['exact'],ensure_ascii=False),
            'concept_deprecie_export':'oui' if rec['deprecated'] else 'non',
            'statut_comparaison':status,
            'statut_alignement_pactols_cog': 'non_nouvellement_valide'})
    sortie.mkdir(parents=True, exist_ok=True)
    fields=list(result[0]) if result else ['ark_pactols','libelle_xml','statut_comparaison']
    with target.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,delimiter=';',fieldnames=fields)
        w.writeheader();w.writerows(result)
    rapport={'schema_version':'0.1.0','etat':'recette_non_validante',
             'ark_analyses':len(items),'ark_trouves_dans_export':len(found),
             'repartition':dict(sorted(count.items())),
             'source_pactols':{'institution':'CNRS-Frantiq','thesaurus':'th17',
              'fichier':rdf.name,'sha256':sh,'licence':'ODbL-1.0',
              'depot':'https://github.com/frantiq/PACTOLS'},
             'source_autorites':{'fichier':autorites.name,'sha256':sha256(autorites)},
             'avertissement':'L’absence dans un export daté ne prouve pas l’absence dans Pactols vivant. Aucun lien COG ni géométrie n’est validé.'}
    report_path.write_text(json.dumps(rapport,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return rapport


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--autorites',type=Path,required=True)
    p.add_argument('--pactols-rdf',type=Path,required=True)
    p.add_argument('--sortie',type=Path,required=True)
    p.add_argument('--sha256-attendu',default=SHA_RDF_20260722)
    a=p.parse_args()
    print(json.dumps(audit(a.autorites,a.pactols_rdf,a.sortie,a.sha256_attendu),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
