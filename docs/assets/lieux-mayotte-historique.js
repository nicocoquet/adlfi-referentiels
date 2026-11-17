/* Mayotte : 17 codes communaux, 34 épisodes COG ; transition COMER / DROM.
   2007 est une borne documentaire, 2011 un changement de statut, pas une création.
   Les 16 alignements 2026 ne sont pas rétroactifs ; Dembeni demeure non validée. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxMayotteHistorique=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.mayotte.etats_cog_public.v1';
 const SHAS={
  comer:'d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748',
  drom:'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee',
  actuel:'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3'
 };
 const CODES=Array.from({length:17},(_,i)=>'976'+String(i+1).padStart(2,'0'));
 const COMPTES={1943:0,2007:0,2008:17,2011:17,2012:17,2025:17,2026:17};
 function date(s){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;
  const d=new Date(s+'T00:00:00Z');
  return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===s;
 }
 function verifier(d){
  if(!d||d.schema!==SCHEMA||d.statut!=='ETATS_DOCUMENTAIRES_SANS_GEOMETRIES'||
     d.start_year!==1943||d.end_year!==2026||
     d.cog_comer_historique_sha256!==SHAS.comer||
     d.cog_drom_historique_sha256!==SHAS.drom||
     d.cog_communes_2026_sha256!==SHAS.actuel||
     d.correspondances_pactols_COG_2026_conservees!==16||
     d.nouveaux_alignements_pactols!==0||
     d.contours_historiques_publies!==0||
     d.nouvelles_relations_successions_inferrees!==0||
     typeof d.episodes!=='string')
   throw Error('Chronologie COG Mayotte non conforme');
  const t=d.transition_famille_cog;
  if(!t||t.date_effet!=='2011-03-31'||t.avant!=='COMER'||t.apres!=='DROM'||
     t.codes_communes_conserves!==17||
     t.nature!=='CHANGEMENT_STATUT_ET_FAMILLE_DE_TABLE_COG'||
     t.date_creation_des_communes!==null||
     t.creation_de_communes_par_cette_transition!==false)
   throw Error('Transition Mayotte 2011 faussement qualifiée');
  if(d.premiere_attestation_de_ce_jeu!=='2007-02-23')
   throw Error('Début documentaire COG Mayotte incohérent');
  const collector=d.collectivite_statut_particulier;
  if(!collector||collector.code_2011_2025!=='976D'||collector.code_2026!=='976R'||
     collector.date_effet_code_2026!=='2026-01-01')
   throw Error('Code de collectivité Mayotte confondu avec les communes');
  if(!d.ark_confirme_sans_alignement_valide||
     d.ark_confirme_sans_alignement_valide.code!=='97607'||
     d.ark_confirme_sans_alignement_valide.ark!=='26678/crtZcuFSJVYZU')
   throw Error('Réserve Pactols Dembeni violée');
  const rows=d.episodes.split('\n').map(line=>{
    const p=line.split('|');
    if(p.length!==5)throw Error('Épisode COG Mayotte mal formé');
    const [code,label,famille,start,stop]=p;
    if(!CODES.includes(code)||!label||!['COMER','DROM'].includes(famille)||
       !date(start)||(stop&&(!date(stop)||stop<=start)))
     throw Error('Épisode COG Mayotte invalide : '+line);
    return {code,label,famille,start,end:stop||null};
  });
  if(rows.length!==34)throw Error('34 épisodes COG Mayotte attendus');
  const byCode=new Map();
  for(const e of rows){
    if(!byCode.has(e.code))byCode.set(e.code,[]);
    byCode.get(e.code).push(e);
  }
  if(byCode.size!==17)throw Error('17 codes COG Mayotte attendus');
  for(const code of CODES){
    const eps=byCode.get(code)||[];
    eps.sort((a,b)=>a.start.localeCompare(b.start));
    if(eps.length!==2||eps[0].famille!=='COMER'||
       eps[0].start!=='2007-02-23'||eps[0].end!=='2011-03-31'||
       eps[1].famille!=='DROM'||eps[1].start!=='2011-03-31'||eps[1].end||
       eps[0].label!==eps[1].label)
      throw Error('Succession de séries COG Mayotte incohérente : '+code);
  }
  const etat=(code,instant)=>(byCode.get(code)||[]).find(e=>
    e.start<=instant&&(!e.end||instant<e.end))||null;
  for(const [y,count]of Object.entries(COMPTES)){
    if(CODES.filter(code=>etat(code,y+'-01-01')).length!==count)
      throw Error('État Mayotte au 1er janvier incohérent : '+y);
  }
  return {rows,byCode};
 }
 function creer(data){
   const {rows,byCode}=verifier(data);
   const etat=(code,annee)=>{
     if(!Number.isInteger(annee)||annee<1943||annee>2026)return null;
     return (byCode.get(code)||[]).find(e=>e.start<=annee+'-01-01'&&
       (!e.end||annee+'-01-01'<e.end))||null;
   };
   return {
      episodes:rows,transition:data.transition_famille_cog,
      collectivite:data.collectivite_statut_particulier,
      arkDembeni:data.ark_confirme_sans_alignement_valide,
      etat,
      periodes(code){return [...(byCode.get(code)||[])];},
      count(annee){
       if(!Number.isInteger(annee)||annee<1943||annee>2026)return 0;
       return CODES.filter(code=>etat(code,annee)).length;
      }
   };
 }
 return {verifier,creer};
}));