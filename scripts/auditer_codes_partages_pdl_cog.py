#!/usr/bin/env python3
"""Preuves COG des 22 codes partagés entre deux ARK Pays de la Loire.

Audit de recette. Aucun événement n'est assimilé automatiquement à une relation
d'identité Pactols, aucune validation ou géométrie n'est écrite.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,collections
from pathlib import Path
CODES=('44005','44021','44087','44163','49018','49021','49023','49050',
'49069','49092','49125','49167','49244','49248','49301','49323',
'49331','49367','53255','72071','85009','85084')
SHA={'communes':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3',
'historique':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee',
'mouvements':'8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1'}
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def read(p,required):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:
  x=f.readline();f.seek(0)
  reader=csv.DictReader(f,delimiter=';' if x.count(';')>x.count(',') else ',')
  if set(required)-set(reader.fieldnames or []):
   raise ValueError('Colonnes absentes dans '+str(p))
  return list(reader)
def write(path,items):
 if not items:return
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]),delimiter=';');w.writeheader();w.writerows(items)
def audit(communes,historique,mouvements,sortie):
 paths={'communes':communes,'historique':historique,'mouvements':mouvements}
 for k,p in paths.items():
  if digest(p)!=SHA[k]:raise ValueError('SHA-256 Insee non conforme : '+k)
 current=collections.defaultdict(list)
 for x in read(communes,('COM','TYPECOM','LIBELLE','REG','DEP')):
  if x['COM'] in CODES:current[x['COM']].append(x)
 periods=collections.defaultdict(list)
 for x in read(historique,('COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN')):
  if x['COM'] in CODES:periods[x['COM']].append(x)
 moves=collections.defaultdict(list)
 for x in read(mouvements,('MOD','DATE_EFF','TYPECOM_AV','COM_AV','LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP')):
  for c in {x['COM_AV'],x['COM_AP']} & set(CODES):moves[c].append(x)
 summaries=[];history=[];events=[];checks=collections.Counter()
 for code in CODES:
  cur=sorted(current[code],key=lambda x:(x['TYPECOM'],x['LIBELLE']))
  hist=sorted(periods[code],key=lambda x:(x['DATE_DEBUT'],x['TYPECOM'],x['LIBELLE']))
  eve=sorted(moves[code],key=lambda x:(x['DATE_EFF'],x['MOD'],x['COM_AV'],x['COM_AP']))
  for h in hist:
   history.append({'code_cible':code,**{k:h[k] for k in ('COM','TYPECOM','LIBELLE','DATE_DEBUT','DATE_FIN')}})
  for e in eve:
   events.append({'code_cible':code,**{k:e[k] for k in ('MOD','DATE_EFF','TYPECOM_AV','COM_AV','LIBELLE_AV','TYPECOM_AP','COM_AP','LIBELLE_AP')}})
  bymod=collections.Counter(e['MOD'] for e in eve)
  # Distingue le signal d'un événement de sa qualification historique : un
  # code réutilisé n'est pas une identité communale stable.
  categories=[]
  if any(e['MOD'] in ('30','31','32','33','34') for e in eve):categories.append('evenement_regroupement_ou_changement_statut_a_instruire')
  if any(e['MOD']=='10' for e in eve):categories.append('changement_nom_a_instruire')
  if len({(h['TYPECOM'],h['LIBELLE']) for h in hist})>1:categories.append('plusieurs_etats_code_libelle')
  if any(r['TYPECOM'] in ('COMD','COMA') for r in cur):categories.append('statut_delegue_associe_present_2026')
  if not categories:categories=['aucun_evenement_relatif_au_code_a_verifier']
  checks.update(categories)
  summaries.append({'code_insee':code,'communes_cog_2026':json.dumps([{'typecom':x['TYPECOM'],'libelle':x['LIBELLE'],'dep':x['DEP']} for x in cur],ensure_ascii=False),
   'nb_etats_historiques':len(hist),'nb_lignes_mouvement_relatives':len(eve),
   'dates_mouvements':'|'.join(sorted({e['DATE_EFF'] for e in eve})),
   'modalites_mouvements':'|'.join(sorted(bymod)),'signaux_a_instruire':'|'.join(categories),
   'statut_validation':'non_valide'})
 output=Path(sortie)
 sources={p.resolve() for p in paths.values()}
 if any((output/n).resolve() in sources for n in ('codes-partages-22-cog.csv','periodes-codes-partages-22.csv','evenements-codes-partages-22.csv','rapport-codes-partages-22.json')):
  raise ValueError('Écrasement d’une source interdit')
 output.mkdir(parents=True,exist_ok=True)
 write(output/'codes-partages-22-cog.csv',summaries)
 write(output/'periodes-codes-partages-22.csv',history)
 write(output/'evenements-codes-partages-22.csv',events)
 report={'statut':'recette_non_validante','codes':len(summaries),'lignes_periodes':len(history),
 'lignes_evenements_par_code':len(events),'signaux':dict(sorted(checks.items())),
 'sha256_sources':{k:digest(p) for k,p in paths.items()},'nouvelles_validations':0,
 'limites':'Mouvements rattachés par code, pouvant être répétés entre codes. Pas de filiation transitive prouvée ; les dates des couples code–libellé ne datent pas les contours.'}
 (output/'rapport-codes-partages-22.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for arg in ('communes','historique','mouvements','sortie'):p.add_argument('--'+arg,type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(audit(a.communes,a.historique,a.mouvements,a.sortie),ensure_ascii=False,indent=2))
