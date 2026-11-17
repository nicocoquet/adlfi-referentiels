#!/usr/bin/env python3
"""Lire la nomenclature géographique ISPF originale (XLSX) sans l'altérer.

Diagnostic d'un fichier tiers. Toute insertion dans le module Lieux doit
ensuite passer par un contrôle des 98 communes associées, des 18 communes
sans associées, des 30 rattachements et du COG des 48 communes.
"""
from __future__ import annotations
import argparse,collections,json,hashlib,re,sys
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p':'http://schemas.openxmlformats.org/package/2006/relationships'}
M='{'+NS['x']+'}'
def read_xlsx(path:Path):
 if not ZipFile(path).testzip() is None:raise ValueError("XLSX corrompu")
 with ZipFile(path) as z:
  workbook=ET.fromstring(z.read('xl/workbook.xml'))
  rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
  lookup={x.get('Id'):x.get('Target') for x in rels.findall('p:Relationship',NS)}
  strings=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   sr=ET.fromstring(z.read('xl/sharedStrings.xml'))
   strings=[''.join(t.text or '' for t in si.findall('.//x:t',NS))
      for si in sr.findall('x:si',NS)]
  result=[]
  for sh in workbook.findall('x:sheets/x:sheet',NS):
   sheetname=sh.get('name');rid=sh.get('{'+NS['r']+'}id')
   target=lookup.get(rid,'')
   entry=target.lstrip('/') if target.startswith('/') else (
      target if target.startswith('xl/') else 'xl/'+target)
   if entry not in z.namelist():raise ValueError("Fichier de feuille absent : "+entry)
   root=ET.fromstring(z.read(entry))
   rows=[]
   for row in root.findall('x:sheetData/x:row',NS):
    cells={}
    for cell in row.findall('x:c',NS):
     col=re.match(r'^([A-Z]+)',cell.get('r',''))
     if not col:continue
     key=col.group(1)
     typ=cell.get('t')
     if typ=='inlineStr':
      val=''.join(x.text or '' for x in cell.findall('.//x:t',NS))
     else:
      v=cell.find('x:v',NS);val=v.text if v is not None else ''
      if typ=='s' and val:val=strings[int(val)]
     if val:cells[key]=val
    if cells:rows.append({'row':int(row.get('r',0)),'cells':cells})
   result.append({'feuille':sheetname,'lignes':rows})
 return result

def rapport(path:Path)->dict:
 sheets=read_xlsx(path)
 return {'schema':'adlfi.lieux.polynesie.ispf.inspect.v1',
    'source':'https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx',
    'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'taille_octets':path.stat().st_size,
    'feuilles':[{'nom':s['feuille'],'nombre_lignes_non_vides':len(s['lignes']),
        'entetes_et_premieres_lignes':s['lignes'][:12],
        'derniere_ligne':s['lignes'][-1:]} for s in sheets]}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source',type=Path,required=True)
 p.add_argument('--sortie',type=Path)
 a=p.parse_args()
 r=rapport(a.source)
 content=json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
 if a.sortie:
  if 'docs' in a.sortie.resolve().parts:raise ValueError("Données inspectées à garder hors docs/")
  a.sortie.parent.mkdir(parents=True,exist_ok=True)
  a.sortie.write_text(content,encoding='utf-8')
 print(content)
if __name__=='__main__':main()
