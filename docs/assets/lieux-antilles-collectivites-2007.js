/* Antilles 2007 : communes 97123/97127 ≠ collectivités 977/978 ≠ codes 97701/97801.
   COG historique et succession légalement attestée = deux provenances distinctes. */
(function(root,factory){
 'use strict';const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxAntilles2007=factory();
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.antilles2007.etats_cog_juridique_public.v1';
 const ENTITES=[
  {ancien:'97123',nom:'Saint-Barthélemy',collectivite:'977',cinq:'97701',
    article:'18-X',cgct:'LO6211-1',url:'https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006393813'},
  {ancien:'97127',nom:'Saint-Martin',collectivite:'978',cinq:'97801',
    article:'18-XI',cgct:'LO6311-1',url:'https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006394046'}
 ];
 const SHAS={
  'v_commune_depuis_1943.csv':'08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee',
  'v_mvt_commune_2026.csv':'8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1',
  'v_commune_2026.csv':'7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3',
  'v_comer_2026.csv':'d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed',
  'v_tom_depuis_1943.csv':'6814a3ddedfa186557f5f7a10ff0f4c521f72fd388bdd430318d3d0d59b426bd',
  'v_commune_comer_2026.csv':'9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8',
  'v_commune_outremer_depuis_1943.csv':'d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748'
 };
 function rows(raw,n){
  if(typeof raw!=='string')throw Error('Épisodes COG manquants');
  const out=raw.split('\n').map(x=>{
   const p=x.split('|');if(p.length!==n)throw Error('Épisode COG mal formé');
   return p;
  });
  if(out.length!==2)throw Error('Deux transitions insulaires attendues');
  return out;
 }
 function verifier(data){
  if(!data||data.schema!==SCHEMA||
    data.statut!=='ETATS_COG_DOCUMENTAIRES_ET_SUCCESSIONS_JURIDIQUES_SANS_GEOMETRIES'||
    data.date_cog_reforme!=='2007-02-23'||data.date_entree_vigueur_loi_organique!=='2007-02-22'||
    data.start_year!==1943||data.end_year!==2026||
    data.source_codification_977_978!=='https://www.insee.fr/fr/information/7929495'||
    data.source_loi_succession!=='https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006399955'||
    data.correspondances_pactols_guadeloupe_2026_conservees!==32||
    data.nouveaux_alignements_pactols!==0||data.nouveaux_contours_historiques!==0||
    data.retroprojections_anciennes_communes!==0||data.nouvelles_relations_successions_COG_inferrees!==0||
    data.relations_successions_juridiques_documentees!==2||data.codes_communes_actuelles_creees!==0||
    !Array.isArray(data.relations)||data.relations.length!==2||
    JSON.stringify(data.cog_sha256)!==JSON.stringify(SHAS))
   throw Error('Contrat des transitions Antilles 2007 non conforme');
  const anciennes=rows(data.episodes_anciens,4);
  const collectivites=rows(data.episodes_collectivites,4);
  const cinq=rows(data.episodes_codes_cinq_positions,5);
  for(let i=0;i<2;i++){
   const e=ENTITES[i],a=anciennes[i],b=collectivites[i],c=cinq[i],relation=data.relations[i];
   if(JSON.stringify(a)!==JSON.stringify([e.ancien,e.nom,'1946-03-21','2007-02-23'])||
      JSON.stringify(b)!==JSON.stringify([e.collectivite,e.nom,'2007-02-23',''])||
      JSON.stringify(c)!==JSON.stringify([e.cinq,e.nom,'COM','2007-02-23',''])||
      !relation||relation.ancienne_commune?.code!==e.ancien||
      relation.ancienne_commune?.type!=='COMMUNE'||
      relation.collectivite?.code!==e.collectivite||
      relation.collectivite?.type!=='COLLECTIVITE_OUTREMER'||
      relation.code_cinq_positions?.code!==e.cinq||
      relation.code_cinq_positions?.nature_zonage_COG!=='COM'||
      relation.code_cinq_positions?.type!=='CODE_APPLICATION_5_POSITIONS_NON_COMMUNE'||
      relation.mouvement_COG?.modalite!=='30'||
      relation.mouvement_COG?.date_effet!=='2007-02-23'||
      relation.mouvement_COG?.COM_AP!==null||
      relation.succession_juridique?.type!=='SUCCESSION_DROITS_ET_OBLIGATIONS'||
      relation.succession_juridique?.source!=='Loi organique n° 2007-223, article '+e.article||
      relation.succession_juridique?.fondement_CGCT!==e.cgct||
      relation.succession_juridique?.source_CGCT!==e.url||
      relation.succession_juridique?.date_effet_relation_precise_deduite!==null||
      relation.succession_juridique?.identite_pactols_deduite!==false)
     throw Error('Distinction commune–collectivité ou provenance de succession 2007 violée : '+e.ancien);
  }
  return data.relations;
 }
 function creer(data){
  const relations=verifier(data);
  function etat(code,annee){
   if(!Number.isInteger(annee)||annee<1943||annee>2026)return null;
   const rel=relations.find(r=>
    [r.ancienne_commune.code,r.collectivite.code,r.code_cinq_positions.code].includes(code));
   if(!rel)return null;
   const date=annee+'-01-01';
   if(code===rel.ancienne_commune.code)
     return date>='1946-03-21'&&date<'2007-02-23'?
       {code,libelle:rel.ancienne_commune.libelle,type:'ANCIENNE_COMMUNE',debut:'1946-03-21',fin:'2007-02-23'}:null;
   if(date<'2007-02-23')return null;
   return code===rel.collectivite.code?
    {code,libelle:rel.collectivite.libelle,type:'COLLECTIVITE',debut:'2007-02-23',fin:null}:
    {code,libelle:rel.collectivite.libelle,type:'CODE_APPLICATION_NON_COMMUNE',debut:'2007-02-23',fin:null};
  }
  return {
   relations,etat,
   pourCode(code){return relations.find(r=>[
    r.ancienne_commune.code,r.collectivite.code,r.code_cinq_positions.code].includes(code))||null;},
   nombreAnciennes(annee){return ENTITES.filter(e=>etat(e.ancien,annee)).length;},
   nombreCollectivites(annee){return ENTITES.filter(e=>etat(e.collectivite,annee)).length;}
  };
 }
 return {verifier,creer};
}));