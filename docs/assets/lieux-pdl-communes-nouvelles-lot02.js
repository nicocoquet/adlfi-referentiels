/* PDL 2026 — 45 communes nouvelles : ARK courants, anciennes COMD distinctes. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPDLNouvellesLot02=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.pdl.lot02.2026.public.v1';
 const SOURCE='recette/lieux/PDL-LOT02-45-COMMUNES-NOUVELLES-2026.md';
 const SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const clean=s=>String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
  .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
  .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function creer(pub,cog,base,uuid,lot01,chemille){
  if(pub?.schema!==SCHEMA||pub.region!=='pdl'||pub.millesime_cog!=='2026-01-01'||
     pub.source_registre!==SOURCE||pub.source_RDF_Pactols_sha256!==SHA||
     pub.source_qualification!=='recette/lieux/PDL-LOT02-PREQUALIFICATION-2026.md'||
     pub.alignements_publies_precedemment!==1149||pub.nouveaux_alignements!==45||
     pub.total_alignements_PDL_2026!==1194||
     pub.communes_PDL_COG_2026!==1228||pub.communes_a_instruire!==34||
     pub.codes_multiples_restant_a_instruire!==9||pub.divergences_restantes!==24||
     pub.cas_Rives_du_Fougerais_exclu!=='85292'||
     pub.nouvelles_geometries!==0||pub.liens_historiques_inferes!==0||
     pub.alignements_Pactols_COG_valides_2026?.length!==45||
     cog?.region!=='pdl'||cog.geometries_historiques?.length!==0||
     base?.byCode?.size!==1140||uuid?.byCode?.size!==3||
     lot01?.byCode?.size!==5||chemille?.byCode?.size!==1)
   throw Error('PDL lot02 : registre ou sources non conformes');
  const previous=[...base.byCode.values(),...uuid.byCode.values(),
                  ...lot01.byCode.values(),...chemille.byCode.values()];
  const usedCodes=new Set(previous.map(x=>x.code_insee));
  const usedArks=new Set(previous.map(x=>x.ark_pactols));
  if(previous.length!==1149||usedCodes.size!==1149||usedArks.size!==1149)
    throw Error('PDL lot02 : publications précédentes non uniques');
  const current=new Map();
  for(const p of cog.periodes_com){
   if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&
      (!p.fin_exclue||p.fin_exclue>'2026-01-01')){
     if(current.has(p.code_insee))throw Error('PDL lot02 : code COM en doublon');
     current.set(p.code_insee,p);
   }
  }
  if(current.size!==1228)throw Error('PDL lot02 : nombre de communes COG incorrect');
  const codes=new Set(),arks=new Set(),anciens=new Set(),byCode=new Map();
  for(const a of pub.alignements_Pactols_COG_valides_2026){
   const code=a.code_insee,ark=a.ark_pactols,ancien=a.ark_ancienne_commune_distinct;
   const c=current.get(code);
   if(!c||codes.has(code)||arks.has(ark)||anciens.has(ancien)||
      usedCodes.has(code)||usedArks.has(ark)||usedArks.has(ancien)||
      code==='85292'||!ark?.startsWith('26678/')||!ancien?.startsWith('26678/')||
      ark===ancien||a.libelle_COG_2026!==c.libelle||
      a.libelle_pactols!==c.libelle||!a.libelle_ancienne_commune||
      a.date_evenement_COG!==c.debut_inclus||
      a.uri_insee!=='http://id.insee.fr/geo/commune/'+code||
      a.predicat_source!=='skos:exactMatch'||
      a.source_RDF_Pactols_sha256!==SHA||a.source_registre!==SOURCE||
      a.nature_evenement_COG!=='MOD32_CREATION_COMMUNE_NOUVELLE'||
      a.type_ancienne_commune_apres!=='COMD'||a.millesime_validation!==2026||
      a.date_validation!=='2026-11-18'||
      a.statut!=='correspondance_PDL_commune_nouvelle_validee_2026'||
      a.portee_chronologique!=='2026_SEULEMENT'||
      a.relations_historiques_inferees!==0)
    throw Error('PDL lot02 : identité non justifiée '+code);
   const moves=cog.lignes_mouvements_cog.filter(m=>m.code_apres===code&&
      m.mod==='32'&&m.date_effet===a.date_evenement_COG);
   if(!moves.some(m=>m.typecom_apres==='COM'&&m.libelle_apres===c.libelle)||
      !moves.some(m=>m.code_avant===code&&m.typecom_avant==='COM'&&
        m.typecom_apres==='COMD'&&m.libelle_apres===a.libelle_ancienne_commune))
     throw Error('PDL lot02 : sources MOD32 non concordantes '+code);
   codes.add(code);arks.add(ark);anciens.add(ancien);byCode.set(code,a);
  }
  if(codes.size!==45||arks.size!==45||anciens.size!==45||
     [...arks].some(x=>anciens.has(x)))
   throw Error('PDL lot02 : collisions internes entre ARK');
  const index=[...byCode.values()].map(a=>({
    kind:'pactols',id:'pactols:'+a.ark_pactols,
    zone:'pdl',code:a.code_insee,ark:a.ark_pactols,
    label:a.libelle_pactols,noms:[a.libelle_pactols],
    champs:[a.libelle_pactols,a.libelle_COG_2026,
            a.code_insee,a.ark_pactols].map(clean)
  }));
  return {byCode,index};
 }
 return {creer};
}));