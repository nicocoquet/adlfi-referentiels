/* PACA : sept communes nouvelles 2026, avec exclusion explicite des sept ARK anciens. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPACANouvelles=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.paca.communes_nouvelles.2026.public.v1';
 const RDF_SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const CASES=new Map([
  ['04033',{name:'Ubaye-Serre-Ponçon',date:'2017-01-01',ark:'26678/pcrtDcVUj2Mdw9',ancien:'26678/pcrtC1Vi7jqzBS'}],
  ['04120',{name:"Val d'Oronaye",date:'2016-01-01',ark:'26678/pcrtjDzQ2Y9N5o',ancien:'26678/pcrtjMIYKdPaHG'}],
  ['05024',{name:'Valdoule',date:'2017-07-01',ark:'26678/pcrtAUevxwngAh',ancien:'26678/pcrteug78RKN9a'}],
  ['05039',{name:'Aubessagne',date:'2018-01-01',ark:'26678/pcrtFGmyycRjcC',ancien:'26678/pcrtp9Ljm1lvVd'}],
  ['05053',{name:'Garde-Colombe',date:'2016-01-01',ark:'26678/pcrtKc33Ttmi9L',ancien:'26678/pcrtYB42tOKsY7'}],
  ['05101',{name:'Vallouise-Pelvoux',date:'2017-01-01',ark:'26678/pcrt2BsRDBxggr',ancien:'26678/pcrt6KSOx6bX7u'}],
  ['05118',{name:'Val Buëch-Méouge',date:'2016-01-01',ark:'26678/pcrtjKbaVOnEjn',ancien:'26678/pcrth0vgSHba4G'}],
 ]);
 function norm(x){
  return String(x??'').replace(/œ/gi,'oe').normalize('NFKD')
    .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
    .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function creer(pub,cog,pilote,complement,renommages){
  if(pub?.schema!==SCHEMA||pub.region!=='paca'||
    pub.millesime_cog!=='2026-01-01'||pub.source_rdf_sha256!==RDF_SHA||
    pub.source_audit!=='recette/lieux/PACA-HUIT-COMMUNES-NOUVELLES-RDF-2026.json'||
    pub.nombre_ajouts!==7||pub.pilote_valide_conserve!==103||
    pub.complements_conserves!==832||pub.renommages_conserves!==3||
    pub.total_alignements_PACA_2026!==945||pub.communes_a_instruire!==1||
    pub.reserve_abries_ristolas!=='05001'||
    pub.candidat_lexical_abries_ristolas!=='26678/pcrtm96gvvfnwmggc9z0wrxn'||
    pub.identites_historiques_inferees!==0||pub.geometries_modifiees!==0||
    pub.anciens_ARK_exclus?.length!==7||
    pub.alignements_Pactols_COG_valides_2026?.length!==7||
    cog?.region!=='paca'||cog.geometries_historiques?.length!==0||
    cog.alignements_Pactols_COG_valides_2026?.length!==103||
    pilote?.autorites?.length!==103||complement?.byCode?.size!==832||
    renommages?.byCode?.size!==3)
    throw Error('Index des sept communes nouvelles PACA non conforme');
  const current=new Map();
  for(const p of cog.periodes_com){
   if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&
      (!p.fin_exclue||p.fin_exclue>'2026-01-01')){
    if(current.has(p.code_insee))throw Error('Doublon COG');
    current.set(p.code_insee,p.libelle);
   }
  }
  if(current.size!==946)throw Error('946 communes PACA COG 2026 attendues');
  const knownCodes=new Set(),knownArks=new Set();
  const add=(code,ark)=>{
   if(knownCodes.has(code)||knownArks.has(ark))throw Error('Doublon de l’index PACA existant');
   knownCodes.add(code);knownArks.add(ark);
  };
  for(const x of pilote.autorites)add(x.correspondances[0].code_insee,x.ark_pactols);
  for(const x of complement.byCode.values())add(x.code_insee,x.ark_pactols);
  for(const x of renommages.byCode.values())add(x.code_insee,x.ark_pactols);
  if(knownCodes.size!==938||knownArks.size!==938||knownCodes.has('05001'))
   throw Error('Les 938 correspondances PACA doivent rester distinctes');
  const oldExcluded=new Map(pub.anciens_ARK_exclus.map(x=>[x.code_insee_reutilise,x]));
  if(oldExcluded.size!==7)throw Error('Exclusions historiques insuffisantes');
  const byCode=new Map();
  for(const x of pub.alignements_Pactols_COG_valides_2026){
   const p=CASES.get(x.code_insee);
   const old=oldExcluded.get(x.code_insee);
   const movements=cog.lignes_mouvements_cog.filter(m=>
     m.mod==='32'&&m.code_apres===x.code_insee&&m.date_effet===p?.date&&
     m.typecom_avant==='COM'&&m.typecom_apres==='COM');
   if(!p||byCode.has(x.code_insee)||knownCodes.has(x.code_insee)||
      knownArks.has(x.ark_pactols)||knownArks.has(p.ancien)||
      x.ark_pactols!==p.ark||x.ark_ancien_exclu!==p.ancien||
      x.libelle_COG_2026!==p.name||x.libelle_pactols!==p.name||
      current.get(x.code_insee)!==p.name||x.date_creation_commune_nouvelle!==p.date||
      x.nature_COG!=='MOD32_FUSION_COMMUNE_NOUVELLE'||
      x.uri_insee!=='http://id.insee.fr/geo/commune/'+x.code_insee||
      x.predicat_source!=='skos:exactMatch'||x.source_rdf_sha256!==RDF_SHA||
      x.millesime_validation!==2026||x.date_validation!=='2026-11-18'||
      x.type_validation!=='exactMatch_2026_plus_prefLabel_commune_nouvelle_plus_historyNote_MOD32'||
      x.statut!=='correspondance_PACA_commune_nouvelle_validee_par_preuves_2026'||
      x.portee_chronologique!=='2026_SEULEMENT'||
      x.communes_sources_COG?.length!==movements.length||movements.length<2||
      !movements.some(m=>m.code_avant===x.code_insee)||
      !old||old.ark_ancienne_commune!==p.ancien||
      old.decision!=='NE_PAS_ALIGNER_ARK_ANCIEN_A_LA_COMMUNE_NOUVELLE')
      throw Error('Commune nouvelle Pactols PACA insuffisamment prouvée : '+x.code_insee);
   const expectedSources=new Set(movements.map(m=>m.code_avant));
   if(new Set(x.communes_sources_COG.map(m=>m.code)).size!==expectedSources.size||
      x.communes_sources_COG.some(m=>!expectedSources.has(m.code)))
      throw Error('Communes anciennes de fusion différentes : '+x.code_insee);
   byCode.set(x.code_insee,x);
  }
  if(byCode.size!==7||[...CASES.keys()].some(c=>!byCode.has(c))||
     byCode.has('05001'))
    throw Error('Liste des sept communes nouvelles non conforme');
  const index=[...byCode.values()].map(x=>({
   kind:'pactols',id:'pactols:'+x.ark_pactols,
   zone:'paca',code:x.code_insee,ark:x.ark_pactols,label:x.libelle_pactols,
   noms:[x.libelle_pactols,x.libelle_COG_2026],
   champs:[x.libelle_pactols,x.libelle_COG_2026,x.code_insee,x.ark_pactols].map(norm)
  }));
  return {byCode,index};
 }
 return {creer};
}));