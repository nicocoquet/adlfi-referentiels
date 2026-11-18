/* PDL 2026 : commune nouvelle Ingrandes 2024 et rétablissements Essarts 2024. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPDLDeux2024=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.pdl.2024-ingrandes-essarts.2026.public.v1';
 const SOURCE='recette/lieux/PDL-INGRANDES-ESSARTS-PUBLICATION-2026.md';
 const SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const QUALIF='recette/lieux/PDL-INGRANDES-ESSARTS-2024.md';
 const WIKI='recette/lieux/PDL-INGRANDES-WIKIDATA-2024.json';
 const COG='docs/data/lieux-chronologie/cog-pdl.json';
 const CASES={
  '49160':{name:'Ingrandes-le-Fresne-sur-Loire',ark:'26678/pcrtj64zr6gnns4mnfd2828b',
   old:'26678/pcrtQBSwT6fBDW',mod:'MOD32_CREATION_COMMUNE_NOUVELLE',
   status:'correspondance_PDL_2024_via_Wikidata_validee_2026',
   oldName:'Ingrandes-Le Fresne sur Loire'},
  '85084':{name:'Essarts-en-Bocage',ark:'26678/pcrt0PrU3oVWxo',
   old:'26678/pcrtFmygG5m3QZ',mod:'MOD21_RETABLISSEMENT_COMMUNES',
   status:'correspondance_PDL_2024_MOD21_validee_2026',
   oldName:'Essarts en Bocage'}
 };
 const normalize=s=>String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
  .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
  .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function creer(pub,cog,...previous){
  if(pub?.schema!==SCHEMA||pub.region!=='pdl'||pub.millesime_cog!=='2026-01-01'||
    pub.source_registre!==SOURCE||pub.source_qualification!==QUALIF||
    pub.source_COG!==COG||pub.source_Wikidata_2024!==WIKI||
    pub.source_RDF_Pactols_sha256!==SHA||
    pub.alignements_publies_precedemment!==1215||pub.nouveaux_alignements!==2||
    pub.total_alignements_PDL_2026!==1217||pub.communes_PDL_COG_2026!==1228||
    pub.communes_a_instruire!==11||pub.geometries_nouvelles!==0||
    pub.liens_historiques_inferes!==0||
    pub.alignements_Pactols_COG_valides_2026?.length!==2||
    cog?.region!=='pdl'||cog.geometries_historiques?.length!==0||
    previous.length!==8)
   throw Error('PDL mouvements 2024 : registre incomplet');
  const prior=previous.flatMap(p=>[...p?.byCode?.values()||[]]);
  const usedCodes=new Set(prior.map(x=>x.code_insee));
  const usedArks=new Set(prior.map(x=>x.ark_pactols));
  if(prior.length!==1215||usedCodes.size!==1215||usedArks.size!==1215)
   throw Error('PDL mouvements 2024 : correspondances antérieures en collision');
  const byCode=new Map(),index=[];
  for(const a of pub.alignements_Pactols_COG_valides_2026){
   const c=CASES[a.code_insee],code=a.code_insee;
   if(!c||byCode.has(code)||usedCodes.has(code)||usedArks.has(a.ark_pactols)||
     usedArks.has(c.old)||a.libelle_COG_2026!==c.name||
     a.libelle_pactols!==c.name||a.ark_pactols!==c.ark||
     a.nature_evenement_COG!==c.mod||a.statut!==c.status||
     a.date_evenement_COG!=='2024-01-01'||
     a.source_registre!==SOURCE||a.source_qualification!==QUALIF||
     a.source_RDF_Pactols_sha256!==SHA||
     a.portee_chronologique!=='2026_SEULEMENT'||
     a.relations_historiques_inferees!==0||
     a.millesime_validation!==2026||a.date_validation!=='2026-11-18')
    throw Error('PDL mouvements 2024 : identité contemporaine invalide '+code);
   if(code==='49160'){
    if(a.ark_concept_2016_non_promu!==c.old||a.uri_insee_uuid_resolue!==false||
       a.uri_insee_uuid_RDF_Pactols!=='http://id.insee.fr/geo/commune/2cdbc96f-9287-4279-80c9-b3c169bb1fed'||
       a.uri_insee_courante_COG!=='http://id.insee.fr/geo/commune/49160'||
       a.qid_Wikidata!=='Q123475717'||a.revision_Wikidata!==2309862185||
       a.revision_Wikidata_url!=='https://www.wikidata.org/w/index.php?title=Q123475717&oldid=2309862185'||
       a.URI_Wikidata_exactMatch!=='https://www.wikidata.org/wiki/Q123475717'||
       a.code_INSEE_Wikidata_P374!=='49160'||
       a.predicat_Pactols_Wikidata!=='skos:exactMatch'||
       a.predicat_Wikidata_INSEE!=='P374')
      throw Error('PDL mouvements 2024 : preuve indirecte Ingrandes déformée');
   }else if(a.ark_ancienne_commune_distinct!==c.old||
       a.uri_insee_RDF_Pactols!=='http://id.insee.fr/geo/commune/85084'||
       a.predicat_Pactols_INSEE!=='skos:exactMatch'||
       JSON.stringify(a.codes_communes_retablies)!=='["85165","85212"]')
      throw Error('PDL mouvements 2024 : preuve MOD21 Essarts déformée');
   const episodes=cog.periodes_com.filter(p=>p.typecom==='COM'&&p.code_insee===code)
    .sort((p,q)=>p.debut_inclus.localeCompare(q.debut_inclus));
   if(episodes.length!==3||episodes[1].libelle!==c.oldName||
      episodes[1].fin_exclue!=='2024-01-01'||episodes[2].libelle!==c.name||
      episodes[2].debut_inclus!=='2024-01-01'||episodes[2].fin_exclue!==null)
    throw Error('PDL mouvements 2024 : périodes COG incohérentes '+code);
   const mod=code==='49160'?'32':'21';
   if(!cog.lignes_mouvements_cog.some(m=>m.date_effet==='2024-01-01'&&
       m.mod===mod&&m.code_avant===code&&m.code_apres===code&&
       m.libelle_apres===c.name&&m.typecom_apres==='COM'))
    throw Error('PDL mouvements 2024 : modalité COG manquante '+code);
   byCode.set(code,a);
   index.push({kind:'pactols',id:'pactols:'+a.ark_pactols,
      zone:'pdl',code,ark:a.ark_pactols,label:c.name,noms:[c.name],
      champs:[c.name,code,a.ark_pactols].map(normalize)});
  }
  if(byCode.size!==2||index.length!==2||
     [...byCode.values()].some(x=>usedArks.has(x.ark_pactols)))
   throw Error('PDL mouvements 2024 : doublons');
  return {byCode,index};
 }
 return {creer};
}));