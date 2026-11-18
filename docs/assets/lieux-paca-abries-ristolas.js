/* Abriès-Ristolas : validation éditoriale indirecte Pactols->Wikidata->COG 2026. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPACAAbrièsRistolas=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.paca.abries_ristolas.editorial.2026.public.v1';
 const RDF_SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const WIKIDATA='https://www.wikidata.org/wiki/Q57664391';
 const NEW='26678/pcrtm96gvvfnwmggc9z0wrxn',OLD='26678/pcrtGQ7nGPZN7K';
 const RISTOLAS='26678/pcrt2YWpB2NDPZ';
 const CODE='05001',NAME='Abriès-Ristolas';
 function normalize(s){
  return String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function creer(pub,cog,pilot,complement,renommages,nouvelles){
  if(pub?.schema!==SCHEMA||pub.region!=='paca'||pub.millesime_cog!=='2026-01-01'||
      pub.preuve!=='CONVERGENCE_EDITORIALE_PACTOLS_WIKIDATA_INSEE_COG'||
      pub.predicat_Pactols!=='skos:exactMatch'||pub.cible_Pactols_Wikidata!==WIKIDATA||
      pub.propriete_Wikidata_code_INSEE!=='P374'||pub.valeur_Wikidata_P374!==CODE||
      pub.valeur_Wikidata_P571!=='2019-01-01'||pub.information_Wikidata_non_autorite_INSEE!==true||
      pub.source_RDF_sha256!==RDF_SHA||
      pub.source_audit_RDF!=='recette/lieux/PACA-ABRIES-RISTOLAS-AUDIT-2026.json'||
      pub.alignements_pilote_conserves!==103||pub.alignements_exactMatch_direct_conserves!==832||
      pub.renommages_conserves!==3||pub.communes_nouvelles_explicites_conservees!==7||
      pub.nouvelles_validations_editoriales!==1||pub.total_PACA_alignements_2026!==946||
      pub.communes_PACA_COG_2026!==946||pub.exceptions_restantes?.length!==0||
      pub.geometries_ajoutees!==0||pub.relations_historiques_inferrees!==0||
      pub.alignements_Pactols_COG_valides_2026?.length!==1||
      cog?.region!=='paca'||cog.geometries_historiques?.length!==0||
      cog.alignements_Pactols_COG_valides_2026?.length!==103||
      pilot?.autorites?.length!==103||complement?.byCode?.size!==832||
      renommages?.byCode?.size!==3||nouvelles?.byCode?.size!==7)
     throw Error('Alignement éditorial indirect Abriès-Ristolas incohérent');
  const codes=new Set(),arks=new Set();
  for(const p of pilot.autorites){
    const code=p.correspondances?.[0]?.code_insee;
    if(!code||codes.has(code)||arks.has(p.ark_pactols))throw Error('Pilote PACA incohérent');
    codes.add(code);arks.add(p.ark_pactols);
  }
  for(const data of [complement,renommages,nouvelles]){
    for(const x of data.byCode.values()){
      if(codes.has(x.code_insee)||arks.has(x.ark_pactols))throw Error('Doublon de sources PACA');
      codes.add(x.code_insee);arks.add(x.ark_pactols);
    }
  }
  if(codes.size!==945||arks.size!==945||codes.has(CODE)||arks.has(NEW)||
     arks.has(OLD)||arks.has(RISTOLAS))
    throw Error('945 correspondances précédentes non conservées');
  const periods=cog.periodes_com.filter(x=>x.code_insee===CODE&&x.typecom==='COM')
    .sort((a,b)=>a.debut_inclus.localeCompare(b.debut_inclus));
  if(periods.length!==2||periods[0].libelle!=='Abriès'||
     periods[0].fin_exclue!=='2019-01-01'||periods[1].libelle!==NAME||
     periods[1].debut_inclus!=='2019-01-01'||periods[1].fin_exclue!==null)
     throw Error('Historique COG Abriès-Ristolas altéré');
  const transitions=cog.lignes_mouvements_cog.filter(e=>e.mod==='32'&&
      e.date_effet==='2019-01-01'&&e.code_apres===CODE&&e.libelle_apres===NAME);
  if(!transitions.some(e=>e.code_avant==='05001'&&e.libelle_avant==='Abriès')||
     !transitions.some(e=>e.code_avant==='05120'&&e.libelle_avant==='Ristolas'))
     throw Error('Création COG de 2019 non confirmée');
  const row=pub.alignements_Pactols_COG_valides_2026[0];
  if(row.code_insee!==CODE||row.ark_pactols!==NEW||
     row.libelle_COG_2026!==NAME||row.libelle_pactols!==NAME||
     row.date_creation_commune_nouvelle!=='2019-01-01'||
     row.ancienne_commune_code_conserve!=='Abriès'||
     row.ark_ancienne_commune_distinct!==OLD||
     row.ark_ancienne_Ristolas_distinct!==RISTOLAS||
     row.uri_cog_insee!=='http://id.insee.fr/geo/commune/05001'||
     row.uri_insee_exactMatch_direct_pactols!==null||
     row.uri_exactMatch_pactols_wikidata!==WIKIDATA||
     row.code_insee_wikidata!==CODE||
     row.source_INSEE!==pub.source_INSEE_courante||
     row.source_fusion_COG!==pub.source_arrete_creation||
     row.source_RDF_sha256!==RDF_SHA||
     row.millesime_validation!==2026||row.date_validation!=='2026-11-18'||
     row.statut!=='correspondance_editoriale_indirecte_validee_PACA_2026'||
     row.type_validation!=='Pactols_exactMatch_Wikidata_INSEE_COG_et_fusion_2019'||
     row.portee_chronologique!=='2026_SEULEMENT')
     throw Error('Preuves insuffisantes pour Abriès-Ristolas');
  const byCode=new Map([[CODE,row]]);
  const index=[{
    kind:'pactols',id:'pactols:'+NEW,zone:'paca',code:CODE,ark:NEW,
    label:NAME,noms:[NAME],
    champs:[NAME,CODE,NEW].map(normalize)
  }];
  return {byCode,index};
 }
 return {creer};
}));