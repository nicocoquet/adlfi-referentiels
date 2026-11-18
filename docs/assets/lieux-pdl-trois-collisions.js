/* PDL 2026 — trois nouvelles communes avec ARK historiques non promus. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPDLTroisCollisions=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SOURCE='recette/lieux/PDL-TROIS-COLLISIONS-2026.md';
 const SCHEMA='adlfi.lieux.pactols.pdl.trois-collisions.2026.public.v1';
 const SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const CASES={
 '49244':['Mauges-sur-Loire','La Pommeraye','2015-12-15','26678/pcrtVBIl6UNl1S','26678/pcrtE0bVL7JsdM'],
 '53255':['Sainte-Suzanne-et-Chammes','Sainte-Suzanne','2016-01-01','26678/pcrtwUykeFf31u','26678/pcrts0lDLWcVyJ'],
 '72137':['Villeneuve-en-Perseigne','La Fresnaye-sur-Chédouet','2015-01-01','26678/pcrtoVf9Ovfyy7','26678/pcrtg6rwdnGM9r']
 };
 const clean=s=>String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function creer(pub,cog,...previous){
  if(pub?.schema!==SCHEMA||pub.region!=='pdl'||pub.millesime_cog!=='2026-01-01'||
     pub.source_registre!==SOURCE||pub.source_RDF_Pactols_sha256!==SHA||
     pub.source_qualification!=='recette/lieux/PDL-NEUF-COLLISIONS-HISTORIQUES-2026.md'||
     pub.alignements_publies_precedemment!==1212||pub.nouveaux_alignements!==3||
     pub.total_alignements_PDL_2026!==1215||pub.communes_PDL_COG_2026!==1228||
     pub.communes_a_instruire!==13||pub.nouvelles_geometries!==0||
     pub.liens_historiques_inferes!==0||
     pub.alignements_Pactols_COG_valides_2026?.length!==3||
     cog?.region!=='pdl'||previous.length!==7)
    throw Error('PDL trois collisions : registre incomplet');
  const prev=previous.flatMap(p=>[...p?.byCode?.values()||[]]);
  const codes=new Set(prev.map(x=>x.code_insee)),arks=new Set(prev.map(x=>x.ark_pactols));
  if(prev.length!==1212||codes.size!==1212||arks.size!==1212)
    throw Error('PDL trois collisions : 1212 liens antérieurs non uniques');
  const byCode=new Map(),index=[],ancients=new Set();
  for(const a of pub.alignements_Pactols_COG_valides_2026){
    const c=CASES[a.code_insee];
    if(!c||byCode.has(a.code_insee)||codes.has(a.code_insee)||
       arks.has(a.ark_pactols)||arks.has(a.ark_ancienne_commune_distinct)||
       ancients.has(a.ark_ancienne_commune_distinct)||
       a.libelle_COG_2026!==c[0]||a.libelle_pactols!==c[0]||
       a.libelle_ancienne_commune!==c[1]||
       a.date_evenement_COG!==c[2]||a.ark_pactols!==c[3]||
       a.ark_ancienne_commune_distinct!==c[4]||
       a.uri_insee!=='http://id.insee.fr/geo/commune/'+a.code_insee||
       a.predicat_source!=='skos:exactMatch'||a.source_RDF_Pactols_sha256!==SHA||
       a.source_registre!==SOURCE||
       a.nature_evenement_COG!=='MOD32_CREATION_COMMUNE_NOUVELLE'||
       a.type_ancienne_commune_apres!=='COMD'||a.millesime_validation!==2026||
       a.date_validation!=='2026-11-18'||
       a.statut!=='correspondance_PDL_commune_nouvelle_validee_2026'||
       a.portee_chronologique!=='2026_SEULEMENT'||
       a.relations_historiques_inferees!==0)
       throw Error('PDL trois collisions : identités non établies '+a.code_insee);
    const episodes=cog.periodes_com.filter(p=>p.typecom==='COM'&&p.code_insee===a.code_insee)
      .sort((p,q)=>p.debut_inclus.localeCompare(q.debut_inclus));
    if(episodes.length!==2||episodes[0].libelle!==c[1]||
       episodes[0].fin_exclue!==c[2]||episodes[1].libelle!==c[0]||
       episodes[1].debut_inclus!==c[2]||episodes[1].fin_exclue!==null)
      throw Error('PDL trois collisions : épisodes COG incompatibles');
    const moves=cog.lignes_mouvements_cog.filter(m=>m.mod==='32'&&
        m.date_effet===c[2]&&m.code_apres===a.code_insee);
    if(!moves.some(m=>m.code_avant===a.code_insee&&m.typecom_avant==='COM'&&
        m.typecom_apres==='COM'&&m.libelle_avant===c[1]&&m.libelle_apres===c[0])||
       !moves.some(m=>m.code_avant===a.code_insee&&m.typecom_avant==='COM'&&
        m.typecom_apres==='COMD'&&m.libelle_apres===c[1]))
      throw Error('PDL trois collisions : création et COMD non attestées');
    byCode.set(a.code_insee,a);
    ancients.add(a.ark_ancienne_commune_distinct);
    index.push({kind:'pactols',id:'pactols:'+a.ark_pactols,zone:'pdl',
                code:a.code_insee,ark:a.ark_pactols,label:a.libelle_pactols,
                noms:[a.libelle_pactols],
                champs:[a.libelle_pactols,a.code_insee,a.ark_pactols].map(clean)});
  }
  if(byCode.size!==3||index.length!==3||
     [...byCode.values()].some(x=>ancients.has(x.ark_pactols)))
     throw Error('PDL trois collisions : collision entre ARK récents et anciens');
  return {byCode,index};
 }
 return {creer};
}));