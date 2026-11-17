/* Guadeloupe : 35 épisodes communaux COG, 34 codes, 2 anciens non alignés. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxGuadeloupeHistorique=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.guadeloupe.etats_cog_public.v1';
 const COG_SHA='08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee';
 const OLD=['97123','97127'];
 const ANNUELS={1943:0,1946:0,1947:34,1976:34,1977:34,2007:34,2008:32,2026:32};
 const normaliser=s=>String(s??'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'')
   .toLocaleLowerCase('fr').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function date(s){
   if(!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;
   const d=new Date(s+'T00:00:00Z');
   return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===s;
 }
 function verifier(data){
   if(!data||data.schema!==SCHEMA||data.start_year!==1943||data.end_year!==2026||
      data.cog_historique_sha256!==COG_SHA||data.contours_historiques_publies!==0||
      data.nouveaux_alignements_pactols!==0||data.nouvelles_relations_successions_inferrees!==0||
      data.correspondances_pactols_COG_2026_conservees!==32||
      typeof data.episodes!=='string'||!Array.isArray(data.anciens_codes)||
      data.anciens_codes.length!==2||!Array.isArray(data.mouvements_decompte)||
      data.mouvements_decompte.length!==3)
     throw Error('Chronologie COG Guadeloupe non conforme');
   const expectedMov=[['1946-03-21','20',34],['1976-06-04','10',1],['2007-02-23','30',2]];
   for(let i=0;i<expectedMov.length;i++){
      const row=data.mouvements_decompte[i],exp=expectedMov[i];
      if(row.date_effet!==exp[0]||row.modalite!==exp[1]||row.lignes!==exp[2])
         throw Error('Mouvements de Guadeloupe contradictoires');
   }
   const rows=data.episodes.split('\n').map(s=>{
      const parts=s.split('|');
      if(parts.length!==4)throw Error('Épisode COG mal formé');
      const [code,label,start,stop]=parts;
      if(!/^971(?:0[1-9]|[12]\d|3[0-4])$/.test(code)||!label||!date(start)||
         stop&&(!date(stop)||stop<=start))
         throw Error('Période COG invalide : '+s);
      return {code,label,start,end:stop||null};
   });
   const codes=[...new Set(rows.map(x=>x.code))];
   if(rows.length!==35||codes.length!==34)
      throw Error('Cardinalités historiques COG contradictoires');
   const byCode=new Map();
   for(const e of rows){
     if(!byCode.has(e.code))byCode.set(e.code,[]);
     byCode.get(e.code).push(e);
   }
   for(const [code,eps]of byCode){
      eps.sort((a,b)=>a.start.localeCompare(b.start));
      if(eps[0].start!=='1946-03-21')throw Error('Première date COG inattendue : '+code);
      for(let i=1;i<eps.length;i++){
        if(!eps[i-1].end||eps[i-1].end!==eps[i].start)
           throw Error('Épisodes COG discontinus ou en conflit : '+code);
      }
      if(code==='97107'){
        if(eps.length!==2||eps[0].label!=='Capesterre-de-Guadeloupe'||
           eps[0].end!=='1976-06-04'||eps[1].label!=='Capesterre-Belle-Eau'||
           eps[1].start!=='1976-06-04'||eps[1].end)
           throw Error('Renommage Capesterre 1976 contradictoire');
      }else if(eps.length!==1)throw Error('Épisode multiple inattendu : '+code);
      if(OLD.includes(code)){
        if(eps[0].end!=='2007-02-23')throw Error('Date de fin code historique 971 incorrecte');
      }else if(eps[eps.length-1].end){
        throw Error('Code actuel terminé dans le fichier COG');
      }
   }
   for(const code of OLD){
      const x=data.anciens_codes.find(e=>e.code===code);
      const label=code==='97123'?'Saint-Barthélemy':'Saint-Martin';
      if(!x||x.libelle!==label||x.date_fin_exclue!=='2007-02-23'||
         x.modalite_mouvement!=='30'||x.destination_com_ap!==null||
         x.ark_pactols_uri_insee_atteste!==null)
         throw Error('Ancien code 971 mal documenté : '+code);
   }
   if(data.anciens_codes.some(x=>!OLD.includes(x.code))||
      new Set(data.anciens_codes.map(x=>x.code)).size!==2)throw Error('Autorités anciennes inconnues');
   const rename=data.mouvement_renommage;
   if(!rename||rename.code!=='97107'||rename.date_effet!=='1976-06-04'||
      rename.modalite!=='10'||rename.libelle_avant!=='Capesterre-de-Guadeloupe'||
      rename.libelle_apres!=='Capesterre-Belle-Eau')throw Error('Mouvement 1976 contradictoire');
   const etat=(c,year)=>{
       const instant=year+'-01-01';
       return (byCode.get(c)||[]).find(e=>e.start<=instant&&(!e.end||instant<e.end))||null;
   };
   for(const [yr,count] of Object.entries(ANNUELS)){
     if(codes.filter(c=>etat(c,yr)).length!==count)
       throw Error('État COG 971 au 1er janvier incohérent : '+yr);
   }
   return {rows,byCode};
 }
 function creer(data){
   const {rows,byCode}=verifier(data);
   const old=new Map(data.anciens_codes.map(x=>[x.code,x]));
   return {
     episodes:rows,old,
     historicalIndex:data.anciens_codes.map(x=>({
       kind:'cogHistoriqueGuadeloupe',id:'COG:HIST:'+x.code,code:x.code,
       label:x.libelle,parent:'Guadeloupe',dernierAnActif:2007,
       champs:[...new Set([x.code,x.libelle,'Guadeloupe','COG historique'].map(normaliser))]
     })),
     etat(code,annee){
       if(!Number.isInteger(annee)||annee<1943||annee>2026)return null;
       return (byCode.get(code)||[]).find(e=>e.start<=annee+'-01-01'&&
           (!e.end||annee+'-01-01'<e.end))||null;
     },
     periodes(code){return [...(byCode.get(code)||[])];},
     count(annee){
       if(!Number.isInteger(annee)||annee<1943||annee>2026)return 0;
       return [...byCode].filter(([code,rows])=>rows.some(e=>e.start<=annee+'-01-01'&&
           (!e.end||annee+'-01-01'<e.end))).length;
     }
   };
 }
 return {verifier,creer,normaliser};
}));
