/* Wallis-et-Futuna : 986 territoire, 98611/12/13 circonscriptions, 0 commune.
 * L'article 17 de la loi de 1961 ne donne pas aux codes COG une validité
 * rétroactive : premiers épisodes 98611–13 en 1985 seulement.
 */
(function(root,factory){
 'use strict';const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxWallisFutunaHistorique=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.wallis-futuna.etats_cog_public.v1';
 const NOMS={'98611':'Alo','98612':'Sigave','98613':'Uvea'};
 const SHAS={
  'v_comer_2026.csv':'d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed',
  'v_commune_comer_2026.csv':'9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8',
  'v_tom_depuis_1943.csv':'6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd',
  'v_commune_outremer_depuis_1943.csv':'d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748',
  'v_commune_2026.csv':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3',
  'v_commune_depuis_1943.csv':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee'
 };
 const LEGAL='https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000684031';
 function lines(raw,n){
   if(typeof raw!=='string'||!raw)throw Error('Chronologie Wallis-et-Futuna absente');
   return raw.split('\n').map(line=>{
    const p=line.split('|');
    if(p.length!==n||!p[0]||!p[1]||!p[n-2])throw Error('Épisode COG 986 mal formé');
    const date=x=>/^\d{4}-\d{2}-\d{2}$/.test(x)&&
      new Date(x+'T00:00:00Z').toISOString().slice(0,10)===x;
    if(!date(p[n-2])||(p[n-1]&&(!date(p[n-1])||p[n-1]<=p[n-2])))
     throw Error('Période COG 986 invalide');
    return p;
   });
 }
 function verifier(data){
  if(!data||data.schema!==SCHEMA||
    data.statut!=='ETATS_COG_DOCUMENTAIRES_CIRCONSCRIPTIONS_NON_COMMUNALES_SANS_GEOMETRIES'||
    data.start_year!==1943||data.end_year!==2026||
    JSON.stringify(data.cog_sha256)!==JSON.stringify(SHAS)||
    data.territoire_courant?.code!=='986'||data.territoire_courant?.libelle!=='Wallis-et-Futuna'||
    data.territoire_courant?.type!=='TERRITOIRE_COMER_NON_COMMUNAL'||
    data.territoire_courant?.communes!==0||data.territoire_courant?.circonscriptions!==3||
    data.creation_circonscriptions_inferree_de_1985!==false||
    data.succession_juridique_98609_986_inferree!==false||
    data.lien_de_identite_98607_986_inferre!==false||
    data.trois_circonscriptions_sont_les_3_royaumes_coutumiers!==false||
    data.nouveaux_alignements_pactols!==0||
    data.contours_historiques_publies!==0||
    data.codes_communes_creees!==0||
    data.correspondances_pactols_2026_validees_pour_les_3_circonscriptions!==0||
    data.publication_autorites_pactols!==false||
    data.famille_COG_distincte_statut_juridique!==true)
   throw Error('Contrat COG 986 : CIR et communes confondues');
  if(data.ancien_code_contextuel_non_adopte?.code!=='98607'||
    data.ancien_code_contextuel_non_adopte?.libelle!=='Nouvelle-Calédonie'||
    data.ancien_code_contextuel_non_adopte?.debut_cog!=='1943-01-01'||
    data.ancien_code_contextuel_non_adopte?.fin_exclue_cog!=='1969-03-30')
   throw Error('Code 98607 de Nouvelle-Calédonie attribué abusivement à Wallis');
  const legal=data.loi_circonscriptions;
  if(!legal||legal.lien!==LEGAL||legal.entree_en_vigueur!=='1961-07-30'||
    legal.personnalite_morale!==true||
    JSON.stringify(legal.articles)!==JSON.stringify(['17','18'])||
    JSON.stringify(legal.circonscriptions)!==JSON.stringify(['Uvea','Alo','Sigave'])||
    legal.debut_institutionnel_différent_date_premiere_attestation_COG!==true)
   throw Error('Fondement légal des circonscriptions incomplet');
  const current=lines(data.circonscriptions_2026.replaceAll('|CIR','|CIR|1985-01-01|'),5);
  const dates=lines(data.episodes_circonscriptions,5);
  if(current.length!==3||dates.length!==3)throw Error('Trois CIR COG 2026 attendues');
  const seen=new Set();
  for(let i=0;i<3;i++){
    const p=dates[i],code=p[0];
    if(!Object.hasOwn(NOMS,code)||NOMS[code]!==p[1]||p[2]!=='CIR'||
       p[3]!=='1985-01-01'||p[4]!==''||seen.has(code))
      throw Error('Épisode circonscription COG 986 incohérent');
    seen.add(code);
    if(current[i][0]!==code||current[i][1]!==p[1]||current[i][2]!=='CIR')
      throw Error('Circonscription courante et épisode COG incohérents');
  }
  const territory=lines(data.episodes_territoire,4);
  const old=lines(data.code_territorial_ancien_documente,4);
  if(territory.length!==1||JSON.stringify(territory[0])!==JSON.stringify([
      '986','Wallis-et-Futuna','1985-01-01',''])||
     old.length!==1||JSON.stringify(old[0])!==JSON.stringify([
      '98609','Wallis-et-Futuna','1961-07-31','1985-01-01']))
     throw Error('Code territorial 986/98609 non conforme au COG');
  return {circonscriptions:dates.map(([code,label,nature,start,end])=>({
     code,label,nature,start,end:end||null})),
    territoire:{code:'986',label:'Wallis-et-Futuna',start:'1985-01-01',end:null},
    ancien:{code:'98609',label:'Wallis-et-Futuna',start:'1961-07-31',end:'1985-01-01'},
    loi:legal};
 }
 function creer(data){
   const d=verifier(data);
   const active=(e,y)=>Number.isInteger(y)&&y>=1943&&y<=2026&&
     e.start<=y+'-01-01'&&(!e.end||y+'-01-01'<e.end);
   return {
     etatCirconscription(code,year){
       const p=d.circonscriptions.find(x=>x.code===code);
       return p&&active(p,year)?p:null;
     },
     etatTerritoire(year){return active(d.territoire,year)?d.territoire:null;},
     codeTerritoireHistorique(year){return active(d.ancien,year)?d.ancien:null;},
     nombreCirconscriptions(year){
       return d.circonscriptions.filter(x=>active(x,year)).length;
     },
     statutCirconscriptionsLegal(year){
       return Number.isInteger(year)&&year>=1962&&year<=2026?
         'Trois circonscriptions territoriales prévues par la loi n° 61-814 du 29 juillet 1961 (articles 17 et 18)':
         null;
     },
     loi:d.loi
   };
 }
 return {verifier,creer};
}));