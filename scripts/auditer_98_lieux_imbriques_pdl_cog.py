#!/usr/bin/env python3
"""Audit COG 2026 des 98 codes des enfants Pactols sans collision régionale.

Ces codes sont extraits du fichier de recette imbriques-120-contextes.csv
(sha et chaînes Pactols vérifiés lors de l'instruction du lot). Le programme
ne crée aucune relation administrative ni validation Pactols–COG.
"""
import argparse,csv,json,hashlib,collections
from pathlib import Path
CODES=tuple('44004 44040 44059 44180 44181 44213 49001 49004 49006 49016 49019 49031 49034 49037 49040 49047 49049 49051 49071 49077 49081 49086 49088 49094 49095 49103 49104 49119 49136 49137 49145 49149 49153 49156 49157 49158 49163 49179 49181 49184 49185 49186 49189 49190 49191 49194 49199 49206 49207 49208 49212 49225 49226 49229 49233 49242 49245 49258 49268 49276 49277 49280 49281 49287 49290 49292 49295 49300 49304 49309 49313 49317 49345 49346 49349 49354 49357 49363 49366 49372 49373 53004 53017 53024 72025 72108 72301 72308 72363 72384 79224 85043 85044 85052 85063 85069 85080 85091'.split())
SHAS={'communes':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3',
'historique':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee',
'mouvements':'8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1'}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()
def read(p,required):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:
  header=f.readline();f.seek(0)
  reader=csv.DictReader(f,delimiter=';' if header.count(';')>header.count(',') else ',')
  if not set(required)<=set(reader.fieldnames or []):raise ValueError('Colonnes Insee manquantes: '+str(p))
  return list(reader)
def write(p,items,fields):
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter=';');w.writeheader();w.writerows(items)
def audit(communes,historique,mouvements,sortie):
 if len(CODES)!=98 or len(set(CODES))!=98:raise ValueError('Codes 98 non uniques')
 paths=dict(communes=Path(communes),historique=Path(historique),mouvements=Path(mouvements))
 for key,p in paths.items():
  if sha(p)!=SHAS[key]:raise ValueError('SHA Insee incorrect: '+key)
 current=collections.defaultdict(list);periods=collections.defaultdict(list);events=collections.defaultdict(list)
 targets=set(CODES)
 for row in read(communes,('COM','TYPECOM','LIBELLE','REG','DEP','COMPARENT')):
  if row['COM'] in targets:current[row['COM']].append(row)
 for row in read(historique,('COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN')):
  if row['COM'] in targets:periods[row['COM']].append(row)
 for row in read(mouvements,('MOD','DATE_EFF','COM_AV','TYPECOM_AV','LIBELLE_AV','COM_AP','TYPECOM_AP','LIBELLE_AP')):
  for code in {row['COM_AV'],row['COM_AP']} & targets:events[code].append(row)
 summary=[];hist_out=[];events_out=[]
 for code in CODES:
  current_types=sorted({x['TYPECOM'] for x in current[code]})
  mods=sorted({x['MOD'] for x in events[code]})
  label='|'.join(sorted({x['LIBELLE'] for x in current[code]}))
  cats=[]
  if 'COMD' in current_types:cats.append('COMD_2026')
  if 'COMA' in current_types:cats.append('COMA_2026')
  if 'COM' in current_types:cats.append('COM_2026')
  if not current_types:cats.append('code_absent_COG_2026')
  if len({(x['TYPECOM'],x['LIBELLE']) for x in periods[code]})>1:cats.append('etats_historiques_multiples')
  summary.append({'code':code,'types_com_2026':'|'.join(current_types),'libelles_2026':label,
   'parents_2026':'|'.join(sorted({x['COMPARENT'] for x in current[code] if x['COMPARENT']})),
   'nombre_periodes':len(periods[code]),'nombre_lignes_mouvements':len(events[code]),
   'modalites':'|'.join(mods),'dates_mouvements':'|'.join(sorted({x['DATE_EFF'] for x in events[code]})),
   'signaux':'|'.join(cats),'statut_validation_adlfi':'non_valide'})
  hist_out.extend({'code_cible':code,**{k:x[k] for k in ('COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN')}} for x in periods[code])
  events_out.extend({'code_cible':code,**{k:x[k] for k in ('MOD','DATE_EFF','TYPECOM_AV','COM_AV','LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP')}} for x in events[code])
 out=Path(sortie)
 if any((out/f).resolve() in {p.resolve() for p in paths.values()} for f in ('synthese-codes-98.csv','periodes-codes-98.csv','evenements-codes-98.csv','rapport-codes-98.json')):
  raise ValueError('Écrasement de source interdit')
 out.mkdir(parents=True,exist_ok=True)
 write(out/'synthese-codes-98.csv',summary,list(summary[0]))
 write(out/'periodes-codes-98.csv',hist_out,['code_cible','COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN'])
 write(out/'evenements-codes-98.csv',events_out,['code_cible','MOD','DATE_EFF','TYPECOM_AV','COM_AV','LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP'])
 counts=collections.Counter(t for r in summary for t in r['signaux'].split('|') if t)
 report={'etat':'recette_non_validante','codes_audites':len(summary),
  'lignes_periodes':len(hist_out),'lignes_mouvements_par_code':len(events_out),
  'repartition_signaux':dict(sorted(counts.items())),'source_sha256':{k:sha(p) for k,p in paths.items()},
  'validations_nouvelles':0,'geometries_historiques_attribuees':0,
  'limite':'Événements rattachés par code, répétitions possibles. Périodes lexicales non assimilables aux contours ou identités stables.'}
 (out/'rapport-codes-98.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ('communes','historique','mouvements','sortie'):p.add_argument('--'+key,required=True,type=Path)
 a=p.parse_args()
 print(json.dumps(audit(a.communes,a.historique,a.mouvements,a.sortie),ensure_ascii=False,indent=2))
