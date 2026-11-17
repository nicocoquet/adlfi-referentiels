/* La Réunion : 24 épisodes COG documentaires ; Saint-Louis et Cilaos en 1965.
   Ne pas assimiler un même code COG à une même emprise géographique. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxReunionHistorique=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.reunion.etats_cog_public.v1';
 const COG_SHA='08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee';
 const MVT_SHA='8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1';
 const ANNUELS={1943:0,1946:0,1947:23,1965:23,1966:24,2026:24};
 function date(s){
   if(!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;
   const d=new Date(s+'T00:00:00Z');
   return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===s;
 }
 function verifier(data){
   if(!data||data.schema!==SCHEMA||
      data.statut!=='ETATS_DOCUMENTAIRES_SANS_GEOMETRIES'||
      data.start_year!==1943||data.end_year!==2026||
      data.cog_historique_sha256!==COG_SHA||data.cog_mouvements_sha256!==MVT_SHA||
      data.contours_historiques_publies!==0||data.nouveaux_alignements_pactols!==0||
      data.nouvelles_relations_successions_inferrees!==0||
      data.correspondances_pactols_COG_2026_conservees!==24||
      typeof data.episodes!=='string'||!Array.isArray(data.mouvements_decompte)||
      data.mouvements_decompte.length!==2)
     throw Error('Chronologie COG Réunion non conforme');
   const expectedMov=[['1946-03-21','20',23],['1965-02-05','20',2]];
   for(let i=0;i<2;i++){
      const m=data.mouvements_decompte[i],exp=expectedMov[i];
      if(!m||m.date_effet!==exp[0]||m.modalite!==exp[1]||m.lignes!==exp[2])
        throw Error('Mouvements COG Réunion contradictoires');
   }
   const division=data.mouvement_division_1965;
   if(!division||division.date_effet!=='1965-02-05'||division.modalite!=='20'||
      division.code_avant!=='97414'||division.libelle_avant!=='Saint-Louis'||
      JSON.stringify(division.codes_apres)!=='["97414","97424"]'||
      JSON.stringify(division.libelles_apres)!=='["Saint-Louis","Cilaos"]'||
      division.maintient_code_97414!==true||division.change_emprise_97414!==true||
      division.contour_avant_1965!==null||division.contour_apres_1965!==null)
      throw Error('Division Saint-Louis/Cilaos 1965 non conforme');
   const rows=data.episodes.split('\n').map(s=>{
     const parts=s.split('|');
     if(parts.length!==4)throw Error('Épisode COG mal formé');
     const [code,label,start,stop]=parts;
     if(!/^974(?:0[1-9]|1\d|2[0-4])$/.test(code)||!label||!date(start)||
         (stop&&(!date(stop)||stop<=start)))
         throw Error('Période COG Réunion invalide : '+s);
     return {code,label,start,end:stop||null};
   });
   const byCode=new Map();
   for(const e of rows){
     if(byCode.has(e.code))throw Error('Code COG Réunion dupliqué : '+e.code);
     byCode.set(e.code,[e]);
   }
   if(rows.length!==24||byCode.size!==24||
      [...byCode.keys()].sort().join(',')!==Array.from({length:24},(_,i)=>'974'+String(i+1).padStart(2,'0')).join(','))
      throw Error('24 épisodes et codes COG Réunion attendus');
   for(const e of rows){
      if(e.start!==(e.code==='97424'?'1965-02-05':'1946-03-21')||e.end)
         throw Error('Épisodes COG Réunion incohérents : '+e.code);
      if(e.code==='97414'&&e.label!=='Saint-Louis'||e.code==='97424'&&e.label!=='Cilaos')
         throw Error('Libellé Saint-Louis/Cilaos contradictoire');
   }
   const etat=(code,y)=>byCode.get(code)?.find(e=>e.start<=y+'-01-01'&&(!e.end||y+'-01-01'<e.end))||null;
   for(const [y,count] of Object.entries(ANNUELS)){
     if([...byCode.keys()].filter(c=>etat(c,y)).length!==count)
       throw Error('État COG Réunion au 1er janvier incohérent : '+y);
   }
   return {rows,byCode};
 }
 function creer(data){
   const {rows,byCode}=verifier(data);
   const etat=(code,annee)=>{
     if(!Number.isInteger(annee)||annee<1943||annee>2026)return null;
     return byCode.get(code)?.find(e=>e.start<=annee+'-01-01'&&(!e.end||annee+'-01-01'<e.end))||null;
   };
   return {
      episodes:rows,division:data.mouvement_division_1965,
      etat,
      periodes(code){return [...(byCode.get(code)||[])];},
      count(annee){
        if(!Number.isInteger(annee)||annee<1943||annee>2026)return 0;
        return [...byCode.keys()].filter(c=>etat(c,annee)).length;
      },
      // État de périmètre attesté par MOD20 ; aucune géométrie associée.
      perimetreSaintLouis(annee){
        if(!etat('97414',annee))return null;
        return annee<=1965?'AVANT_DIVISION_1965':'APRES_DIVISION_1965';
      }
   };
 }
 return {verifier,creer};
}));