/* PDL 2026 : trois UUID Pactols résolus par triplets officiels INSEE, non rétroprojetés. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPDLUUIDResolus=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.pdl.trois_uuid_resolus.2026.public.v1';
 const PACTOLS='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const CODE={
  '44066':{ark:'26678/pcrt99dzcmxdhR',nom:'Grandchamp-des-Fontaines',
    uuid:'493ed29c-e150-4c2e-9880-f94d7002f1f5',date:'2023-01-01',mode:'RENOMMAGE_CODE_CONSERVE',
    sha:'2a74630bb7d7e13460a47e8d8e93cdbb963ced97ddfee9c86a1ab2274648a93f'},
  '85165':{ark:'26678/pcrtsn4IGEserS',nom:"L'Oie",
    uuid:'c518cde7-3eed-4d8a-add5-d603a502dace',date:'2024-01-01',mode:'RETABLISSEMENT_APRES_DEFUSION',
    sha:'82756c6fe552045c995b33d4e565b21dff065ced4d5dc552fb4fcc50a4b531e7'},
  '85212':{ark:'26678/pcrt3AUfSktjqj',nom:'Sainte-Florence',
    uuid:'80c14c7d-5f43-4927-8877-3031578366a5',date:'2024-01-01',mode:'RETABLISSEMENT_APRES_DEFUSION',
    sha:'cfff49e3a18ed56e5ea9aefd5a2265d504f839338dfdfdc4082549c10d73af9e'}
 };
 function normaliser(s){
  return String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function creer(publication,cog,base){
  if(publication?.schema!==SCHEMA||publication.region!=='pdl'||
     publication.millesime_cog!=='2026-01-01'||
     publication.source_audit!=='recette/lieux/PDL-TROIS-UUID-INSEE-RESOLUTIONS-2026.json'||
     publication.alignements_publies_precedemment!==1140||
     publication.alignements_UUID_resolus_ajoutes!==3||
     publication.total_alignements_PDL_2026!==1143||
     publication.communes_PDL_COG_2026!==1228||
     publication.communes_a_instruire!==85||
     publication.cas_Rives_du_Fougerais_exclu!=='85292'||
     publication.geometries_ajoutees!==0||
     publication.identites_historiques_inferees!==0||
     publication.alignements_Pactols_COG_valides_2026?.length!==3||
     cog?.region!=='pdl'||cog.geometries_historiques?.length!==0||
     cog.alignements_Pactols_COG_valides_2026?.length!==0||
     base?.byCode?.size!==1140)
   throw Error('PDL UUID Insee 2026 : registre incomplet');
  const current=new Map();
  for(const p of cog.periodes_com){
   if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&
      (!p.fin_exclue||p.fin_exclue>'2026-01-01')){
    if(current.has(p.code_insee))throw Error('PDL : code communal COG répété');
    current.set(p.code_insee,p.libelle);
   }
  }
  if(current.size!==1228)throw Error('COG PDL hors millésime');
  const used=new Set([...base.byCode.values()].map(x=>x.ark_pactols));
  if(used.size!==1140)throw Error('ARK PDL initialement publiés dupliqués');
  const byCode=new Map();
  for(const a of publication.alignements_Pactols_COG_valides_2026){
   const code=a.code_insee,p=CODE[code];
   if(!p||byCode.has(code)||base.byCode.has(code)||code==='85292'||used.has(a.ark_pactols)||
      a.ark_pactols!==p.ark||a.libelle_COG_2026!==p.nom||
      current.get(code)!==p.nom||
      a.uri_insee_UUID_Pactols_exactMatch!=='http://id.insee.fr/geo/commune/'+p.uuid||
      a.uri_insee_courante_resolue!=='http://id.insee.fr/geo/commune/'+code||
      a.predicat_Pactols!=='skos:exactMatch'||
      a.predicat_resolution_INSEE_code!=='geo:codeINSEE'||
      a.predicat_resolution_INSEE_URI!=='owl:sameAs'||
      a.nature_validation!=='INSEE_RDF_UUID_codeINSEE_owl_sameAs'||
      a.source_RDF_INSEE_sha256!==p.sha||
      a.source_RDF_Pactols_sha256!==PACTOLS||
      a.source_audit!=='recette/lieux/PDL-TROIS-UUID-INSEE-RESOLUTIONS-2026.json'||
      a.date_evenement_COG!==p.date||a.type_evenement_COG!==p.mode||
      a.millesime_validation!==2026||a.date_validation!=='2026-11-18'||
      a.statut!=='correspondance_PDL_UUID_resolue_par_INSEE_validee_2026'||
      a.portee_chronologique!=='2026_SEULEMENT'||
      a.relations_historiques_inferees!==0)
     throw Error('Correspondance UUID Insee PDL insuffisamment prouvée : '+code);
   const movement=cog.lignes_mouvements_cog.filter(x=>
      x.code_apres===code&&x.date_effet===p.date&&
      x.mod===(code==='44066'?'10':'21'));
   if(!movement.length)throw Error('Événement historique PDL non concordant : '+code);
   byCode.set(code,a);
  }
  if(byCode.size!==3||Object.keys(CODE).some(code=>!byCode.has(code))||
     byCode.has('85292'))
   throw Error('Le lot UUID de trois communes PDL est incomplet');
  const index=[...byCode.values()].map(a=>({
    kind:'pactols',id:'pactols:'+a.ark_pactols,
    zone:'pdl',code:a.code_insee,ark:a.ark_pactols,
    label:a.libelle_pactols,noms:[a.libelle_pactols,a.libelle_COG_2026],
    champs:[a.libelle_pactols,a.libelle_COG_2026,a.code_insee,a.ark_pactols].map(normaliser)
  }));
  return {byCode,index};
 }
 return {creer};
}));