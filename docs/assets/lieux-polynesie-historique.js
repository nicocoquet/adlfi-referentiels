/* Polynésie COG 2026 : 48 communes / 48 épisodes depuis 21 mai 1972.
 * Première attestation COG ≠ date de création juridique des 4 anciennes
 * communes. Les 98 communes associées sont à documenter avec ISPF, pas ici.
 */
(function(root,factory){
 'use strict';const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPolynesieHistorique=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.polynesie.etats_cog_public.v1';
 const SHAS={
  'v_comer_2026.csv':'d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed',
  'v_commune_comer_2026.csv':'9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8',
  'v_tom_depuis_1943.csv':'6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd',
  'v_commune_outremer_depuis_1943.csv':'d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748',
  'v_commune_2026.csv':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3',
  'v_commune_depuis_1943.csv':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee'
 };
 const first='1972-05-21';
 function lines(raw,size){
  if(typeof raw!=='string'||!raw)throw Error('Épisodes de Polynésie manquants');
  return raw.split('\n').map(s=>{
   const t=s.split('|');if(t.length!==size||!t[0]||!t[1])
    throw Error('Ligne COG polynésienne non conforme');
   return t;
  });
 }
 function verifier(d){
  if(!d||d.schema!==SCHEMA||
    d.statut!=='ETATS_COG_DOCUMENTAIRES_SANS_GEOMETRIES_NI_RELATIONS_ASSOCIEES'||
    d.start_year!==1943||d.end_year!==2026||
    d.source_cog!=='https://www.insee.fr/fr/information/8740222'||
    JSON.stringify(d.cog_sha256)!==JSON.stringify(SHAS)||
    d.alignements_pactols_2026_valides!==0||
    d.nouveaux_alignements_pactols!==0||d.contours_historiques_publies!==0||
    d.communes_associees_creees!==0||d.subdivisions_mises_dans_communes!==0||
    d.relations_historiques_inferrees!==0)
   throw Error('Contrat COG Polynésie : sous-unités ou alignements usurpés');
  const assoc=d.decoupage_ISPF;
  if(!assoc||assoc.nombre_communes_associees!==98||
    assoc.nombre_communes_avec_associees!==30||
    assoc.nombre_communes_sans_associees!==18||
    assoc.nombre_unites_de_nomenclature_fine!==116||
    assoc.nombre_subdivisions_administratives!==5||
    assoc.liste_codes_associes_incluse!==false||
    assoc.correspondance_automatique_commune_ile!==false)
   throw Error('ISPF : communes associées et subdivisions mélangées');
  const law=d.historique_juridique;
  if(!law||law.communes_preexistantes_avant_1971!==4||
    law.communes_ajoutees_reforme!==44||
    law.creation_juridique_toutes_communes_deduite_1972!==false)
   throw Error('Date d’existence juridique des communes inférée abusivement');
  const rep=d.recette_COG;
  if(!rep||rep.nombre_communes!==48||rep.nombre_episodes!==48||
    rep.nombre_changements_code_libelle_ulterieurs!==0||
    rep.premiere_attestation_COG!==first||
    rep.nombre_episodes_territoire!==1||rep.anciens_codes_autres_a_qualifier!==1)
   throw Error('Épisodes COG 987 non certifiés');
  const current=lines(d.communes_actuelles_2026,2);
  const history=lines(d.episodes_communes_COG,4);
  const bycode=new Map();
  for(let i=0;i<48;i++){
    const code='987'+String(i+11).padStart(2,'0');
    const p=current[i],q=history[i];
    if(!p||!q||p[0]!==code||q[0]!==code||p[1]!==q[1]||
       q[2]!==first||q[3]!==''||bycode.has(code))
      throw Error('Épisode communal historique incompatible : '+code);
    bycode.set(code,{code,label:p[1],start:q[2],end:null,nature:'COM'});
  }
  if(current.length!==48||history.length!==48)throw Error('48 communes et épisodes attendus');
  const terr=lines(d.episode_territoire_COG,4);
  if(terr.length!==1||JSON.stringify(terr[0])!==
     JSON.stringify(['987','Polynésie française',first,'']))
    throw Error('Territoire COG 987 altéré');
  const clip=d.ancien_code_Clipperton_COG;
  if(!clip||clip.code!=='98799'||clip.libelle!=='Clipperton'||
    clip.debut_inclus!==first||clip.fin_exclue!=='2007-02-23'||
    clip.code_actuel!==false)
   throw Error('Code historique Clipperton improprement conservé');
  return {bycode,territoire:{code:'987',label:'Polynésie française',
       start:first,end:null},clipperton:clip};
 }
 function creer(d){
  const x=verifier(d);
  const actif=(start,end,year)=>Number.isInteger(year)&&year>=1943&&year<=2026&&
     year+'-01-01'>=start&&(!end||year+'-01-01'<end);
  return {
   etat(code,year){
    const p=x.bycode.get(code);
    return p&&actif(p.start,p.end,year)?p:null;
   },
   etatTerritoire(year){
    const p=x.territoire;
    return actif(p.start,p.end,year)?p:null;
   },
   ancienClipperton(year){
    const p=x.clipperton;
    return actif(p.debut_inclus,p.fin_exclue,year)?p:null;
   },
   nombreCommunes(year){
    return [...x.bycode.values()].filter(p=>actif(p.start,p.end,year)).length;
   },
   premiereAttestationCOG:first,
   referenceISPF:d.decoupage_ISPF
  };
 }
 return {verifier,creer};
}));