/* Chronologie COG Guyane : identité par code ET période, sans polygones. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxGuyaneHistorique=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.guyane.etats_cog_public.v1';
 const EXPECTED={'1943':0,'1946':0,'1947':18,'1953':23,'1969':23,'1970':19,
                 '1977':20,'1989':21,'1993':22,'2026':22};
 const OLD_CODES={'97351':'97301','97354':'97352','97355':'97306','97359':'97310'};
 const normalize=s=>String(s??'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'')
   .toLocaleLowerCase('fr').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function verifier(data){
  if(!data||data.schema!==SCHEMA||data.start_year!==1943||data.end_year!==2026||
     data.source_etats_sha256!=='83409c5923f31c80ad265c9b9196646ee5b2afcbcaf82ab0a213c67a3387e2e2'||
     data.date_fusion_cog!=='1969-03-27'||data.fusions_modalite!=='31'||
     data.contours_historiques_publies!==0||data.nouvelles_relations_pactols_validees!==0||
     typeof data.episodes!=='string'||!Array.isArray(data.anciennes))
    throw Error('Chronologie COG Guyane non conforme');
  const episodes=data.episodes.split('\n').map(raw=>{
   const parts=raw.split('|');
   if(parts.length!==4)throw Error('Épisode mal formé');
   const [code,label,start,stop]=parts;
   if(!/^973\d\d$/.test(code)||!label||!date(start)||stop&&(!date(stop)||stop<=start))
    throw Error('Épisode COG invalide : '+raw);
   return {code,label,start,end:stop||null};
  });
  const codes=new Set(episodes.map(x=>x.code));
  if(episodes.length!==41||codes.size!==26)
    throw Error('Cardinalités d’épisodes Guyane incorrectes');
  for(const code of codes){
   const rows=episodes.filter(e=>e.code===code).sort((a,b)=>a.start.localeCompare(b.start));
   for(let i=1;i<rows.length;i++){
    if(!rows[i-1].end||rows[i-1].end>rows[i].start)
      throw Error('Chevauchement des périodes COG : '+code);
   }
  }
  if(data.anciennes.length!==4||
     Object.keys(OLD_CODES).some(code=>!codes.has(code)||
       data.anciennes.filter(x=>x.code===code&&x.code_destination_mouvement_COG_1969===OLD_CODES[code]&&
         /^26678\/[A-Za-z0-9]+$/.test(x.ark_candidat)).length!==1))
    throw Error('Autorités historiques de Guyane incohérentes');
  const allOld=new Set(data.anciennes.map(x=>x.code));
  if(allOld.size!==4||[...allOld].some(c=>!OLD_CODES[c]))
    throw Error('Concept historique inconnu');
  const now=new Set(episodes.filter(x=>x.start<='2026-01-01'&&(!x.end||x.end>'2026-01-01')).map(x=>x.code));
  if(now.size!==22||Object.keys(OLD_CODES).some(c=>now.has(c)))throw Error('COG 2026 modifié');
  for(const [year,count] of Object.entries(EXPECTED))
   if(episodes.filter(x=>x.start<=year+'-01-01'&&(!x.end||x.end>year+'-01-01')).length!==count)
    throw Error('Chronologie INSEE non conforme : '+year);
  return episodes;
 }
 function date(s){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;
  const d=new Date(s+'T00:00:00Z');
  return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===s;
 }
 function creer(data){
  const episodes=verifier(data);
  const byCode=new Map();
  for(const e of episodes){
    if(!byCode.has(e.code))byCode.set(e.code,[]);
    byCode.get(e.code).push(e);
  }
  for(const rows of byCode.values())rows.sort((a,b)=>a.start.localeCompare(b.start));
  const old=new Map(data.anciennes.map(x=>[x.code,x]));
  const historicalIndex=data.anciennes.map(x=>{
    const periods=byCode.get(x.code);
    return {
      kind:'cogHistoriqueGuyane',id:'COG:HIST:'+x.code,
      code:x.code,label:periods[periods.length-1].label,
      parent:'Guyane',arkCandidat:x.ark_candidat,
      champs:[...new Set([x.code,x.ark_candidat,'Guyane',
        ...periods.map(x=>x.label)].map(normalize).filter(Boolean))],
      dernierAnActif:1969
    };
  });
  return {
    episodes,
    old,
    historicalIndex,
    etat(code,annee){
      if(!Number.isInteger(annee)||annee<1943||annee>2026)return null;
      const instant=annee+'-01-01';
      return (byCode.get(code)||[]).find(e=>e.start<=instant&&(!e.end||instant<e.end))||null;
    },
    periodes(code){return [...(byCode.get(code)||[])];},
    count(annee){
      return episodes.filter(e=>e.start<=annee+'-01-01'&&(!e.end||e.end>annee+'-01-01')).length;
    }
  };
 }
 return {verifier,creer,normalize};
}));
