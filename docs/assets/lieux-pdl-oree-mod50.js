/* PDL 2026 — Orée d'Anjou : code 49069→49126 par transfert de chef-lieu MOD50. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPDLOreeMod50=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.pdl.oree-anjou.mod50.2026.public.v1';
 const SOURCE='recette/lieux/PDL-OREE-ANJOU-MOD50-2026.md';
 const SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const NOM="Orée d'Anjou",CODE='49126',OLD='49069';
 const ARK='26678/pcrtS50omR9Tb5',DRAIN='26678/pcrtlzVsRTHJSP';
 const normalize=s=>String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function creer(pub,cog,base,uuid,lot01,chemille,lot02){
  if(pub?.schema!==SCHEMA||pub.region!=='pdl'||pub.millesime_cog!=='2026-01-01'||
    pub.source_registre!==SOURCE||pub.source_RDF_Pactols_sha256!==SHA||
    pub.source_COG!=='docs/data/lieux-chronologie/cog-pdl.json'||
    pub.source_insee_modalites!=='https://www.insee.fr/fr/information/8377252'||
    pub.alignements_publies_precedemment!==1194||pub.nouveaux_alignements!==1||
    pub.total_alignements_PDL_2026!==1195||pub.communes_PDL_COG_2026!==1228||
    pub.communes_a_instruire!==33||pub.nouvelles_geometries!==0||
    pub.liens_historiques_inferes!==0||
    pub.alignements_Pactols_COG_valides_2026?.length!==1||
    cog?.region!=='pdl'||cog.geometries_historiques?.length!==0||
    base?.byCode?.size!==1140||uuid?.byCode?.size!==3||
    lot01?.byCode?.size!==5||chemille?.byCode?.size!==1||lot02?.byCode?.size!==45)
   throw Error('PDL Orée MOD50 : registre incomplet');
  const previous=[...base.byCode.values(),...uuid.byCode.values(),...lot01.byCode.values(),
                  ...chemille.byCode.values(),...lot02.byCode.values()];
  const usedCodes=new Set(previous.map(x=>x.code_insee));
  const usedArks=new Set(previous.map(x=>x.ark_pactols));
  if(previous.length!==1194||usedCodes.size!==1194||usedArks.size!==1194||
     usedCodes.has(CODE)||usedArks.has(ARK)||usedArks.has(DRAIN)||
     usedArks.has('26678/pcrtJmNskrfHiK'))
   throw Error('PDL Orée MOD50 : collision avec l’existant');
  const a=pub.alignements_Pactols_COG_valides_2026[0];
  if(a.code_insee!==CODE||a.libelle_COG_2026!==NOM||a.libelle_pactols!==NOM||
     a.ark_pactols!==ARK||a.ark_ancienne_commune_distinct!==DRAIN||
     a.uri_insee_RDF_Pactols!=='http://id.insee.fr/geo/commune/'+OLD||
     a.uri_insee_courante!=='http://id.insee.fr/geo/commune/'+CODE||
     a.predicat_RDF_Pactols!=='skos:exactMatch'||
     a.source_RDF_Pactols_sha256!==SHA||a.source_registre!==SOURCE||
     a.date_evenement_COG!=='2025-01-01'||
     a.nature_evenement_COG!=='MOD50_TRANSFERT_CHEF_LIEU'||
     a.code_COG_avant!==OLD||a.code_COG_apres!==CODE||
     a.millesime_validation!==2026||a.date_validation!=='2026-11-18'||
     a.statut!=='correspondance_PDL_validee_COG_MOD50_2026'||
     a.portee_chronologique!=='2026_SEULEMENT'||a.relations_historiques_inferees!==0)
   throw Error('PDL Orée MOD50 : identité et transition non validées');
  const current=cog.periodes_com.filter(p=>p.typecom==='COM'&&
                       p.code_insee===CODE&&p.debut_inclus<='2026-01-01'&&
                       (!p.fin_exclue||p.fin_exclue>'2026-01-01'));
  if(current.length!==1||current[0].libelle!==NOM||current[0].debut_inclus!=='2025-01-01')
   throw Error('PDL Orée MOD50 : commune actuelle COG non prouvée');
  const former=cog.periodes_com.filter(p=>p.typecom==='COM'&&
                       p.code_insee===OLD&&p.libelle===NOM);
  if(former.length!==1||former[0].debut_inclus!=='2015-12-15'||
     former[0].fin_exclue!=='2025-01-01')
   throw Error('PDL Orée MOD50 : code antérieur COG non prouvé');
  const transitions=cog.lignes_mouvements_cog.filter(m=>
       m.date_effet==='2025-01-01'&&m.code_avant===OLD&&m.code_apres===CODE);
  if(transitions.length!==1||transitions[0].mod!=='50'||
     transitions[0].libelle_avant!==NOM||transitions[0].libelle_apres!==NOM||
     transitions[0].typecom_avant!=='COM'||transitions[0].typecom_apres!=='COM')
   throw Error('PDL Orée MOD50 : transfert de chef-lieu non attesté');
  const index=[{kind:'pactols',id:'pactols:'+ARK,zone:'pdl',code:CODE,ark:ARK,
                label:NOM,noms:[NOM],champs:[NOM,CODE,ARK].map(normalize)}];
  return {byCode:new Map([[CODE,a]]),index};
 }
 return {creer};
}));