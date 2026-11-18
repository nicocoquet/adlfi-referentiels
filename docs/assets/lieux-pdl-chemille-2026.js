/* PDL — Chemillé-en-Anjou en 2026, distinct de Chemillé et Chemillé-Melay. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPDLChemille=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.pdl.chemille.2026.public.v1';
 const SOURCE='recette/lieux/PDL-CHEMILLE-49092-2026.md';
 const SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const CODE='49092',ARK='26678/pcrtzDf0WnnRyr';
 const ANCIENS=['26678/pcrtL5GRFXn3Zs','26678/pcrtWU8rdgPSSH'];
 const normalize=s=>String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function creer(pub,cog,base,uuid,lot01){
  if(pub?.schema!==SCHEMA||pub.region!=='pdl'||pub.millesime_cog!=='2026-01-01'||
     pub.source_registre!==SOURCE||pub.source_RDF_Pactols_sha256!==SHA||
     pub.alignements_publies_precedemment!==1148||
     pub.nouveaux_alignements!==1||pub.total_alignements_PDL_2026!==1149||
     pub.communes_PDL_COG_2026!==1228||pub.communes_a_instruire!==79||
     pub.nouvelles_geometries!==0||pub.liens_historiques_inferes!==0||
     pub.alignements_Pactols_COG_valides_2026?.length!==1||
     cog?.region!=='pdl'||cog.geometries_historiques?.length!==0||
     base?.byCode?.size!==1140||uuid?.byCode?.size!==3||lot01?.byCode?.size!==5)
    throw Error('PDL Chemillé 2026 : registre incomplet');
  const existing=[...base.byCode.values(),...uuid.byCode.values(),...lot01.byCode.values()];
  const existingCodes=new Set(existing.map(x=>x.code_insee)),
        existingArks=new Set(existing.map(x=>x.ark_pactols));
  if(existingCodes.size!==1148||existingArks.size!==1148||
     existingCodes.has(CODE)||existingArks.has(ARK)||ANCIENS.some(x=>existingArks.has(x)))
    throw Error('PDL Chemillé : collision avec 1148 correspondances');
  const entry=pub.alignements_Pactols_COG_valides_2026[0];
  if(entry.code_insee!==CODE||entry.libelle_COG_2026!=='Chemillé-en-Anjou'||
     entry.libelle_pactols!=='Chemillé-en-Anjou'||entry.ark_pactols!==ARK||
     entry.ark_ancienne_Chemille!==ANCIENS[0]||
     entry.ark_ancienne_Chemille_Melay!==ANCIENS[1]||
     entry.uri_insee!=='http://id.insee.fr/geo/commune/'+CODE||
     entry.predicat_source!=='skos:exactMatch'||
     entry.source_RDF_Pactols_sha256!==SHA||
     entry.source_registre!==SOURCE||
     entry.date_evenement_COG!=='2015-12-15'||
     JSON.stringify(entry.dates_MOD32)!=='["2013-01-01","2015-12-15"]'||
     entry.nature_evenement_COG!=='MOD32_CREATION_COMMUNE_NOUVELLE'||
     entry.date_validation!=='2026-11-18'||entry.millesime_validation!==2026||
     entry.statut!=='correspondance_PDL_commune_nouvelle_validee_2026'||
     entry.portee_chronologique!=='2026_SEULEMENT'||
     entry.relations_historiques_inferees!==0)
    throw Error('PDL Chemillé : identité 2026 non vérifiée');
  const periods=cog.periodes_com.filter(x=>x.code_insee===CODE&&x.typecom==='COM')
   .sort((a,b)=>a.debut_inclus.localeCompare(b.debut_inclus));
  if(JSON.stringify(periods.map(x=>[x.libelle,x.debut_inclus,x.fin_exclue]))!==
     JSON.stringify([
      ['Chemillé','1943-01-01','2013-01-01'],
      ['Chemillé-Melay','2013-01-01','2015-12-15'],
      ['Chemillé-en-Anjou','2015-12-15',null]]))
    throw Error('PDL Chemillé : succession COG altérée');
  const events=cog.lignes_mouvements_cog.filter(x=>x.mod==='32'&&
                  x.code_apres===CODE&&x.code_avant===CODE);
  if(!events.some(x=>x.date_effet==='2013-01-01'&&
      x.libelle_avant==='Chemillé'&&x.libelle_apres==='Chemillé-Melay'&&x.typecom_apres==='COM')||
     !events.some(x=>x.date_effet==='2015-12-15'&&
      x.libelle_avant==='Chemillé-Melay'&&x.libelle_apres==='Chemillé-en-Anjou'&&x.typecom_apres==='COM'))
    throw Error('PDL Chemillé : créations COG non confirmées');
  const index=[{kind:'pactols',id:'pactols:'+ARK,
    zone:'pdl',code:CODE,ark:ARK,label:'Chemillé-en-Anjou',
    noms:['Chemillé-en-Anjou'],champs:['Chemillé-en-Anjou',CODE,ARK].map(normalize)}];
  return {byCode:new Map([[CODE,entry]]),index};
 }
 return {creer};
}));