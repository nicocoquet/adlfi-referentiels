/* PDL : cinq communes nouvelles 2026 distinctes de leurs anciennes communes. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPDLNouvellesLot01=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.pdl.lot01-communes-nouvelles.2026.public.v1';
 const SOURCE='recette/lieux/PDL-LOT01-CINQ-ARK-2026.csv';
 const RDF='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const CODES={
  '44005':{nom:'Chaumes-en-Retz',ark:'26678/pcrtN3127ZAunw',ancien:'26678/pcrtju3LL59HiZ',ancienNom:'Arthon-en-Retz'},
  '44021':{nom:'Villeneuve-en-Retz',ark:'26678/pcrt5umeCC5nWQ',ancien:'26678/pcrt7IaoJP82qR',ancienNom:'Bourgneuf-en-Retz'},
  '44029':{nom:'Divatte-sur-Loire',ark:'26678/pcrtir0x0oi7Z7',ancien:'26678/pcrt5I1iVlmViA',ancienNom:'La Chapelle-Basse-Mer'},
  '44087':{nom:'Machecoul-Saint-Même',ark:'26678/pcrt9dHhZhLkZ1',ancien:'26678/pcrtRIS4y4XXSl',ancienNom:'Machecoul'},
  '44163':{nom:'Vair-sur-Loire',ark:'26678/pcrthouCaXtWcI',ancien:'26678/pcrtl9Hc5lXKyi',ancienNom:'Saint-Herblon'}
 };
 const normaliser=s=>String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
  .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
  .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function creer(pub,cog,base,uuid){
  if(pub?.schema!==SCHEMA||pub.region!=='pdl'||pub.millesime_cog!=='2026-01-01'||
     pub.source_registre!==SOURCE||pub.source_RDF_Pactols_sha256!==RDF||
     pub.alignements_publies_precedemment!==1143||pub.nouveaux_alignements!==5||
     pub.total_alignements_PDL_2026!==1148||pub.communes_PDL_COG_2026!==1228||
     pub.communes_a_instruire!==80||pub.nouvelles_geometries!==0||
     pub.liens_historiques_inferes!==0||
     pub.alignements_Pactols_COG_valides_2026?.length!==5||
     cog?.region!=='pdl'||cog.geometries_historiques?.length!==0||
     base?.byCode?.size!==1140||uuid?.byCode?.size!==3)
    throw Error('PDL communes nouvelles : registre incomplet');
  const usedCodes=new Set([...base.byCode.keys(),...uuid.byCode.keys()]);
  const usedArks=new Set([...base.byCode.values(),...uuid.byCode.values()]
                         .map(x=>x.ark_pactols));
  if(usedCodes.size!==1143||usedArks.size!==1143)
   throw Error('PDL communes nouvelles : codes déjà publiés dupliqués');
  const current=new Map();
  for(const p of cog.periodes_com){
   if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&
      (!p.fin_exclue||p.fin_exclue>'2026-01-01')){
     if(current.has(p.code_insee))throw Error('PDL : COM actuelle en double');
     current.set(p.code_insee,p.libelle);
   }
  }
  if(current.size!==1228)throw Error('COG PDL : effectif actuel incorrect');
  const byCode=new Map(),historical=new Set();
  for(const a of pub.alignements_Pactols_COG_valides_2026){
   const c=CODES[a.code_insee],code=a.code_insee;
   if(!c||byCode.has(code)||usedCodes.has(code)||usedArks.has(a.ark_pactols)||
      usedArks.has(a.ark_ancienne_commune_distinct)||code==='85292'||
      a.ark_pactols!==c.ark||a.ark_ancienne_commune_distinct!==c.ancien||
      a.libelle_COG_2026!==c.nom||a.libelle_pactols!==c.nom||
      current.get(code)!==c.nom||a.libelle_ancienne_commune!==c.ancienNom||
      a.uri_insee!=='http://id.insee.fr/geo/commune/'+code||
      a.predicat_source!=='skos:exactMatch'||a.source_RDF_Pactols_sha256!==RDF||
      a.source_registre!==SOURCE||a.date_evenement_COG!=='2016-01-01'||
      a.nature_evenement_COG!=='MOD32_CREATION_COMMUNE_NOUVELLE'||
      a.type_ancienne_commune_apres!=='COMD'||a.millesime_validation!==2026||
      a.date_validation!=='2026-11-18'||
      a.statut!=='correspondance_PDL_commune_nouvelle_validee_2026'||
      a.portee_chronologique!=='2026_SEULEMENT'||a.relations_historiques_inferees!==0||
      historical.has(c.ancien))
    throw Error('PDL : correspondance commune nouvelle non prouvée '+code);
   const events=cog.lignes_mouvements_cog.filter(x=>x.date_effet==='2016-01-01'&&
      x.mod==='32'&&x.code_apres===code);
   if(!events.some(x=>x.libelle_apres===c.nom&&x.typecom_apres==='COM')||
      !events.some(x=>x.code_avant===code&&x.libelle_apres===c.ancienNom&&
         x.typecom_apres==='COMD'))
    throw Error('PDL : mouvement COG ne distingue pas ancienne commune '+code);
   historical.add(c.ancien);
   byCode.set(code,a);
  }
  if(byCode.size!==5||Object.keys(CODES).some(c=>!byCode.has(c)))
   throw Error('PDL : cinq identités 2026 requises');
  const index=[...byCode.values()].map(a=>({
   kind:'pactols',id:'pactols:'+a.ark_pactols,
   zone:'pdl',code:a.code_insee,ark:a.ark_pactols,
   label:a.libelle_pactols,noms:[a.libelle_pactols],
   champs:[a.libelle_pactols,a.libelle_COG_2026,a.code_insee,a.ark_pactols].map(normaliser)
  }));
  return {byCode,index};
 }
 return {creer};
}));