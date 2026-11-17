/* Saint-Pierre-et-Miquelon : épisodes COG des communes et de la collectivité.
 * La famille du fichier COG COMER ne décrit PAS à elle seule le statut juridique.
 * Aucun Pactols, aucune géométrie, aucune succession rétrospective. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxSaintPierreMiquelonHistorique=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.spm.etats_cog_public.v1';
 const CODES=['97501','97502'];
 const NOMS={'97501':'Miquelon-Langlade','97502':'Saint-Pierre'};
 const SHAS={
  'v_comer_2026.csv':'d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed',
  'v_commune_comer_2026.csv':'9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8',
  'v_tom_depuis_1943.csv':'6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd',
  'v_commune_outremer_depuis_1943.csv':'d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748',
  'v_commune_depuis_1943.csv':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee',
  'v_commune_2026.csv':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3'
 };
 const LOIS=[
  ['1976-07-19','Département d’outre-mer','Loi n° 76-664'],
  ['1985-06-11','Collectivité territoriale','Loi n° 85-595'],
  ['2003-03-28','Collectivité d’outre-mer (article 74)','Loi constitutionnelle n° 2003-276'],
  ['2007-02-21','Actualisation du statut de la COM','Loi organique n° 2007-223']
 ];
 function vraieDate(s){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;
  const d=new Date(s+'T00:00:00Z');
  return !Number.isNaN(d.valueOf())&&d.toISOString().slice(0,10)===s;
 }
 function lignes(raw,taille){
  if(typeof raw!=='string'||(!raw&&taille))throw Error('Épisodes COG Saint-Pierre-et-Miquelon absents');
  const rows=raw?raw.split('\n').map(line=>{
   const p=line.split('|');
   if(p.length!==4||!vraieDate(p[2])||
      (p[3]&&(!vraieDate(p[3])||p[3]<=p[2])))
     throw Error('Épisode COG 975 mal formé : '+line);
   return {code:p[0],label:p[1],start:p[2],end:p[3]||null};
  }):[];
  if(rows.length!==taille)throw Error('Volume COG Saint-Pierre-et-Miquelon inattendu');
  return rows;
 }
 function verifier(data){
  if(!data||data.schema!==SCHEMA||data.statut!=='ETATS_DOCUMENTAIRES_SANS_GEOMETRIES'||
     data.start_year!==1943||data.end_year!==2026||
     data.famille_COG_non_equivalente_au_statut_juridique!==true||
     data.correspondances_Pactols_COG_2026_conservees!==0||
     data.nouveaux_alignements_pactols!==0||
     data.relations_successions_inferrees!==0||
     data.contours_historiques_publies!==0||
     data.identites_historiques_retroprojetees!==0||
     data.code_collectivite_2026!=='975')
    throw Error('Historique COG 975 non conforme');
  if(JSON.stringify(data.cog_sha256)!==JSON.stringify(SHAS))
    throw Error('Provenance COG Saint-Pierre-et-Miquelon différente du snapshot contrôlé');
  const current=data.communes_2026.split('\n').map(x=>x.split('|'));
  if(current.length!==2||!current.every(x=>x.length===2&&
     CODES.includes(x[0])&&NOMS[x[0]]===x[1])||
     new Set(current.map(x=>x[0])).size!==2)
    throw Error('Deux communes COG 2026 attendues');
  const com=lignes(data.episodes_communes_COMER,2);
  const dom=lignes(data.episodes_communes_DROM,0);
  const coll=lignes(data.episodes_collectivite_COG,1);
  if(!com.every(x=>CODES.includes(x.code)&&x.label===NOMS[x.code]&&
      x.start==='1976-07-21'&&x.end===null)||
     new Set(com.map(x=>x.code)).size!==2||dom.length!==0)
    throw Error('Épisodes des communes 975 discordants du COG officiel');
  if(coll[0].code!=='975'||coll[0].label!=='Saint-Pierre-et-Miquelon'||
     coll[0].start!=='1985-06-15'||coll[0].end!==null)
    throw Error('Épisode COG de la collectivité 975 discordant');
  if(!Array.isArray(data.statuts_juridiques_reperes_annuels)||
     data.statuts_juridiques_reperes_annuels.length!==4||
     !data.statuts_juridiques_reperes_annuels.every((x,i)=>
      x.date_loi===LOIS[i][0]&&x.designation===LOIS[i][1]&&
      x.preuve===LOIS[i][2]&&x.date_effet_precise_deduite===false))
    throw Error('Statuts légaux et épisodes COG confondus');
  return {communes:com,collectivite:coll,lois:data.statuts_juridiques_reperes_annuels};
 }
 function creer(data){
  const v=verifier(data);
  const courant=(e,year)=>Number.isInteger(year)&&year>=1943&&year<=2026&&
       e.start<=year+'-01-01'&&(!e.end||year+'-01-01'<e.end);
  return {
   communes:v.communes,collectivite:v.collectivite,
   etatCommune(code,annee){return v.communes.find(x=>x.code===code&&courant(x,annee))||null;},
   etatCollectivite(annee){return v.collectivite.find(x=>courant(x,annee))||null;},
   count(annee){return v.communes.filter(x=>courant(x,annee)).length;},
   statutJuridiqueAnnuel(annee){
    if(!Number.isInteger(annee)||annee<1977||annee>2026)return null;
    if(annee<=1985)return 'Département d’outre-mer (loi du 19 juillet 1976)';
    if(annee<=2003)return 'Collectivité territoriale (loi du 11 juin 1985)';
    return 'Collectivité d’outre-mer (article 74, réforme constitutionnelle de 2003)';
   },
   lois:[...v.lois]
  };
 }
 return {verifier,creer};
}));