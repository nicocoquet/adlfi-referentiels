#!/usr/bin/env python3
"""Génère un JSON de publication (aucun commentaire éditorial interne).

Python standard library uniquement. Lit les tables OOXML du maître AdlFI sans le modifier.
Usage : python3 scripts/export_organismes.py CHEMIN_VERS_MAITRE.xlsx
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS = {'x': MAIN}
CORE = ('Organismes','Services','Historique','Historique_services','Statuts_historiques','Relations','Relations_services','Localisations','Affiliations_sources','Correspondances_affiliations')


def column_number(cell: str) -> int:
    letters = re.match(r'[A-Z]+',cell).group(0)
    index = 0
    for char in letters: index = index * 26 + ord(char) - 64
    return index - 1


def parse_workbook(path: Path) -> dict[str,list[dict]]:
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        paths = {e.attrib['Id']:e.attrib['Target'] for e in rels}
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            for item in ET.fromstring(z.read('xl/sharedStrings.xml')).findall(f'{{{MAIN}}}si'):
                shared.append(''.join(t.text or '' for t in item.findall(f'.//{{{MAIN}}}t')))
        sheets = {}
        for s in wb.findall('x:sheets/x:sheet',NS):
            name = s.get('name')
            if name not in CORE: continue
            target = paths[s.attrib[f'{{{REL}}}id']]
            realpath = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            root = ET.fromstring(z.read(realpath))
            values = []
            for row in root.findall('x:sheetData/x:row',NS):
                record = {}
                for cell in row.findall('x:c',NS):
                    ref = cell.get('r'); idx = column_number(ref)
                    vv = cell.find('x:v',NS)
                    v = vv.text if vv is not None and vv.text is not None else None
                    if cell.get('t') == 's' and v is not None: v = shared[int(v)]
                    if cell.get('t') == 'inlineStr':
                        it = cell.find('x:is',NS)
                        v = ''.join(n.text or '' for n in it.findall('.//x:t',NS)) if it is not None else None
                    if cell.get('t') == 'b': v = v == '1'
                    if cell.get('t') == 'e': v = None  # no spreadsheet errors in published JSON
                    if v is not None: record[idx] = v
                if record: values.append(record)
            if not values: sheets[name] = []; continue
            header = values[0]
            if len(set(header.values())) != len(header):
                raise ValueError('En-têtes dupliqués dans ' + name)
            sheets[name] = [{str(header[c]):v for c,v in row.items() if c in header and v not in ('',None)} for row in values[1:]]
        for required in CORE:
            if required not in sheets: raise ValueError(f'Feuille indispensable absente : {required}')
    return sheets


def value(obj,key):
    v = obj.get(key)
    if v is None: return None
    t = str(v).strip()
    return t if t and t != 'None' else None


def flag(raw):
    return {'oui':True,'non':False}.get(str(raw or '').strip().lower(),None)


def normdate(raw):
    if raw is None:return None
    if isinstance(raw,(int,float)): return str(raw)
    s=str(raw).strip()
    if not s:return None
    if re.fullmatch(r'\d{4}(?:-\d{2}(?:-\d{2})?)?',s):return s
    # Numeric Excel date when sourced from OOXML numeric <v> ; avoids treating 2020 as a serial date
    try:
        n=float(s)
        if 22000<n<90000:
            return (dt.date(1899,12,30)+dt.timedelta(days=int(n))).isoformat()
    except ValueError:pass
    return s


def clean_url(v):
    if not v:return None
    s=v.strip()
    return s if s.startswith(('https://','http://')) else None


def split_sigles(raw):
    if not raw:return []
    return [v.strip() for v in re.split(r'\s*[;|]\s*',raw) if v.strip()]


# Images déposées manuellement, sans inférence ni téléchargement de logos.
MEDIA_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.svg')
SITE_ROOT = Path(__file__).resolve().parents[1]

def media_for(ident: str):
    if not re.fullmatch(r'(?:ORG|SER)-[0-9]{4}', ident):
        return {'image': None, 'logo': None}
    def find(folder):
        candidates = [SITE_ROOT / 'assets' / folder / (ident + suffix) for suffix in MEDIA_EXTENSIONS]
        matches = [p for p in candidates if p.is_file()]
        if len(matches) > 1:
            raise ValueError(f'Plusieurs fichiers image pour {ident} dans {folder}: {matches}')
        return 'assets/' + folder + '/' + matches[0].name if matches else None
    return {'image': find('organismes'), 'logo': find('logos')}

def build(source: Path):
    sh=parse_workbook(source)
    names={}
    for sheet,kind in [('Organismes','ORG'),('Services','SER')]:
        for row in sh[sheet]:
            ident = value(row,'organisme_id' if kind=='ORG' else 'service_id')
            if ident: names[ident] = value(row,'nom_normalise') or ident
    history=defaultdict(list)
    for sheet,ident in [('Historique','organisme_id'),('Historique_services','service_id')]:
        for r in sh[sheet]:
            k=value(r,ident)
            if k not in names:continue
            history[k].append({'label':value(r,'denomination'),
                'type':value(r,'type_denomination') or value(r,'type_forme'),
                'start':normdate(value(r,'date_debut')),'end':normdate(value(r,'date_fin')),
                'validation':value(r,'statut_validation'),
                'acronym':value(r,'acronyme_historique')})
    legal_history=defaultdict(list)
    for r in sh['Statuts_historiques']:
        ident=value(r,'organisme_id')
        if ident not in names: continue
        legal_history[ident].append({
            'id':value(r,'statut_historique_id'),
            'type':value(r,'type_organisme'),
            'sector':value(r,'secteur_institutionnel'),
            'bsr':value(r,'categorie_bsr'),
            'legal_form':value(r,'forme_juridique'),
            'start':normdate(value(r,'date_debut')),
            'end':normdate(value(r,'date_fin')),
            'date_precision':value(r,'precision_dates'),
            'validation':value(r,'statut_validation'),
            'source':clean_url(value(r,'source_url'))
        })
    relations=[]
    for r in sh['Relations']:
        src=value(r,'organisme_source_id'); dst=value(r,'organisme_cible_id')
        if src not in names or dst not in names:continue
        relations.append({'id':value(r,'relation_id'),'source':src,'target':dst,'type':value(r,'type_relation'),
              'start':normdate(value(r,'date_debut')),'end':normdate(value(r,'date_fin')),
              'validation':value(r,'statut_validation')})
    for r in sh['Relations_services']:
        src=value(r,'service_source_id')
        dst=value(r,'service_cible_id') or value(r,'organisme_cible_id')
        if src not in names or dst not in names:continue
        relations.append({'id':value(r,'relation_service_id'),'source':src,'target':dst,'type':value(r,'type_relation'),
              'start':normdate(value(r,'date_debut')),'end':normdate(value(r,'date_fin')),
              'validation':value(r,'statut_validation')})
    # Preserved separately: a city name is not a geocoded/verified place.
    locations=[]
    for r in sh['Localisations']:
        k=value(r,'autorite_id')
        if k not in names:continue
        def number(k):
            v=value(r,k)
            try:return float(v) if v is not None else None
            except ValueError:return None
        locations.append({'id':value(r,'localisation_id'), 'authority':k,'kind':value(r,'type_localisation'),
            'city':value(r,'ville'),'country':value(r,'pays_iso2'),'geonames_id':value(r,'geonames_id'),
            'latitude':number('latitude'),'longitude':number('longitude'),
            'validation':value(r,'statut_validation'),
            'start':normdate(value(r,'date_debut')),'end':normdate(value(r,'date_fin'))})
    aff={value(r,'affiliation_source_id'):r for r in sh['Affiliations_sources'] if value(r,'affiliation_source_id')}
    per_authority=defaultdict(dict)
    for corr in sh['Correspondances_affiliations']:
        aid=value(corr,'affiliation_source_id')
        if aid not in aff:continue
        for key in ('organisme_id','service_id'):
            ident=value(corr,key)
            if ident not in names:continue
            old=per_authority[ident].get(aid)
            status=value(corr,'statut_validation')
            valid=status in ('valide','validee','validée')
            per_authority[ident][aid] = valid or old or False
    entities=[]
    for shname,kind in [('Organismes','ORG'),('Services','SER')]:
        for r in sh[shname]:
            ident=value(r,'organisme_id' if kind=='ORG' else 'service_id')
            if not ident:continue
            label=value(r,'nom_normalise') or ident
            acronym=value(r,'acronyme')
            if acronym and acronym.casefold()==label.casefold(): acronym=None
            country=value(r,'pays_iso2')
            city=value(r,'ville_reference')
            a=per_authority.get(ident,{})
            # Source AFF occurrences are editorial counts; do not present them as document counts.
            occurrences=sum(int(float(value(aff[x],'occurrences') or 0)) for x in a)
            active=flag(value(r,'actif'))
            site=clean_url(value(r,'url_site_officiel'))
            catalog_raw = value(r, 'affichage_catalogue')
            catalog = {'oui':'inclure','non':'exclure',
                       'inclure':'inclure','exclure':'exclure'}.get(
                           (catalog_raw or '').lower())
            if catalog is None:
                raise ValueError(f'Affichage catalogue invalide pour {ident}: {catalog_raw!r}')
            rec={'id':ident,'kind':kind,
                'presentation':{'catalog':catalog,'visible':catalog=='inclure','media':media_for(ident)},
                'names':{'preferred':label,'acronym':acronym,'other_acronyms':split_sigles(value(r,'autres_acronymes')),
                         'historical_free_text':value(r,'anciennes_denominations') if kind=='ORG' else None,
                         'history':history.get(ident,[]), 'legal_status_history':legal_history.get(ident,[])},
                'classification':{'type':value(r,'type_organisme' if kind=='ORG' else 'type_service'),
                                  'bsr':value(r,'categorie_bsr'),
                                  'sector':value(r,'secteur_institutionnel') if kind=='ORG' else None,
                                  'level':value(r,'echelon_territorial') if kind=='ORG' else None},
                'activity':{'active':active,'start':normdate(value(r,'date_debut')),'end':normdate(value(r,'date_fin')),
                            'catalog':catalog},
                'identifiers':{'ror':clean_url(value(r,'identifiant_ror')) if kind=='ORG' else None,
                    'rnsr':value(r,'identifiant_rnsr') if kind=='ORG' else None,
                    'idref':value(r,'identifiant_idref') if kind=='ORG' else None,
                    'wikidata':value(r,'identifiant_wikidata') if kind=='ORG' else None,
                    'lab':value(r,'numero_lab') if kind=='ORG' else None},
                'geography':{'institutional_country_iso2':country,'cities_label':city,
                             'locations': [loc['id'] for loc in locations if loc['authority']==ident]},
                'website':site,
                'usage':{'affiliations_linked':len(a),'affiliations_validated':sum(a.values()),
                         'source_occurrences_linked':occurrences},
                'quality':{'activity_unknown':active is None,'end_missing':active is False and not normdate(value(r,'date_fin')),
                           'city_unrecorded':not bool(city),'country_unrecorded':not bool(country),
                           'no_website':not bool(site)}}
            entities.append(rec)
    if len({x['id'] for x in entities})!=len(entities):raise ValueError('IDs ORG/SER dupliqués')
    # No unverified relation automatically converted into an established institutional fact.
    by_kind=Counter(x['kind'] for x in entities)
    public={'schema_version':'0.3.0','dataset':'adlfi-referentiels/organismes',
        'provenance':{'source_filename':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                      'exported_at_utc':dt.datetime.fromtimestamp(int(os.environ['SOURCE_DATE_EPOCH']),dt.timezone.utc).isoformat(timespec='seconds') if os.environ.get('SOURCE_DATE_EPOCH') else None,
                      'caution':'Villes déclarées non géocodées ; seules les relations validées sont présentées comme établies. Les statuts historiques non validés sont signalés comme provisoires.'},
        'totals':{'authorities':len(entities),'organismes':by_kind['ORG'],'services':by_kind['SER'],
                  'catalog_included':sum(x['presentation']['visible'] for x in entities),
                  'catalog_excluded':sum(not x['presentation']['visible'] for x in entities)},
        'authorities':entities, 'relations':relations,'locations':locations}
    return public


def main():
    if len(sys.argv)<2: raise SystemExit('Usage: python3 scripts/export_organismes.py classeur.xlsx')
    source=Path(sys.argv[1]); dst=Path(__file__).resolve().parents[1]/'docs/data/organismes.json'
    d=build(source);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"{dst} : {d['totals']}, relations={len(d['relations'])}, localisations={len(d['locations'])}")

if __name__=='__main__': main()
