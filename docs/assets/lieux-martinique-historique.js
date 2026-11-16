/* Martinique : 34 états communaux COG datés, sans rétroprojection d'ARK. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxMartiniqueHistorique=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.martinique.etats_cog_public.v1';
 const DATES={1943:0,1946:0,1947:32,1949:32,1950:33,1951:34,2026:34};
 const COG_SHA='08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee';
 function date(s){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;
  const d=new Date(s+'T00:00:00Z');
  return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===s;
 }
 function verifier(data){
  if(!data||data.schema!==SCHEMA||data.start_year!==1943||data.end_year!==2026||
     data.cog_source_sha256!==COG_SHA||data.contours_historiques_publies!==0||
     data.nouveaux_alignements_pactols!==0||data.nouvelles_succession_inferrees!==0||
     data.correspondances_pactols_validees_pour_2026!==34||
     !Array.isArray(data.codes_historiques_non_courants)||
     data.codes_historiques_non_courants.length!==0||
     !Array.isArray(data.mouvements_par_date)||
     data.mouvements_par_date.length!==3||typeof data.episodes!=='string')
    throw Error('Chronologie COG Martinique non conforme');
  const expect=[
   ['1946-03-21','20',32],['1949-03-25','20',2],['1950-08-26','20',2]
  ];
  for(let i=0;i<expect.length;i++){
   const x=data.mouvements_par_date[i],e=expect[i];
   if(x.date_effet!==e[0]||x.modalite!==e[1]||x.lignes!==e[2])
    throw Error('Mouvement COG inattendu');
  }
  const rows=data.episodes.split('\n').map(raw=>{
   const parts=raw.split('|');
   if(parts.length!==4)throw Error('Épisode COG mal formé');
   const [code,label,start,stop]=parts;
   if(!/^972(?:0[1-9]|[12]\d|3[0-4])$/.test(code)||!label||!date(start)||
      stop&&(!date(stop)||stop<=start))
    throw Error('Période communale non valide : '+raw);
   return {code,label,start,end:stop||null};
  });
  if(rows.length!==34||new Set(rows.map(x=>x.code)).size!==34)
    throw Error('34 autorités communales Martinique attendues');
  const bycode=Object.fromEntries(rows.map(r=>[r.code,r]));
  for(let i=1;i<=34;i++){
   const code='972'+String(i).padStart(2,'0');
   const expected=code==='97233'?'1949-03-25':code==='97234'?'1950-08-26':'1946-03-21';
   if(!bycode[code]||bycode[code].start!==expected||bycode[code].end)
    throw Error('Épisode COG contredit : '+code);
  }
  for(const [year,count] of Object.entries(DATES)){
   if(rows.filter(e=>e.start<=year+'-01-01'&&(!e.end||e.end>year+'-01-01')).length!==count)
    throw Error('Etat COG au 1er janvier incorrect : '+year);
  }
  return rows;
 }
 function creer(data){
  const rows=verifier(data),bycode=new Map(rows.map(r=>[r.code,r]));
  return {
   episodes:rows,
   etat(code,annee){
     if(!Number.isInteger(annee)||annee<1943||annee>2026)return null;
     const r=bycode.get(code),instant=annee+'-01-01';
     return r&&r.start<=instant&&(!r.end||instant<r.end)?r:null;
   },
   periodes(code){return bycode.has(code)?[bycode.get(code)]:[]},
   count(annee){
     if(!Number.isInteger(annee)||annee<1943||annee>2026)return 0;
     return rows.filter(r=>r.start<=annee+'-01-01'&&(!r.end||r.end>annee+'-01-01')).length;
   }
  };
 }
 return {verifier,creer};
}));
