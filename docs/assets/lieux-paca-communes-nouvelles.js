/* Sept communes nouvelles PACA 2026 : ARK nouveaux distincts des anciens. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPACANouvelles=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.paca.sept_communes_nouvelles.2026.public.v1';
 const RDF_SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const CODES={
  '04033':'26678/pcrtDcVUj2Mdw9','04120':'26678/pcrtjDzQ2Y9N5o',
  '05024':'26678/pcrtAUevxwngAh','05039':'26678/pcrtFGmyycRjcC',
  '05053':'26678/pcrtKc33Ttmi9L','05101':'26678/pcrt2BsRDBxggr',
  '05118':'26678/pcrtjKbaVOnEjn'
 };
 function normaliser(x){
  return String(x??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function creer(doc,cog,pilote,complement,renommages){
  if(doc?.schema!==SCHEMA||doc.region!=='paca'||doc.millesime_cog!=='2026-01-01'||
     doc.source_rdf_sha256!==RDF_SHA||
     doc.source_audit!=='recette/lieux/PACA-HUIT-COMMUNES-NOUVELLES-RDF-2026.json'||
     doc.liens_communes_nouvelles_ajoutes!==7||doc.pilote_valide_conserve!==103||
     doc.complements_conserves!==832||doc.renommages_conserves!==2||
     doc.alignements_total_PACA_2026!==944||doc.communes_a_instruire!==2||
     JSON.stringify(doc.exceptions_restantes)!=='["04045","05001"]'||
     doc.nouvelles_geometries!==0||doc.identites_historiques_inferees!==0||
     doc.alignements_Pactols_COG_valides_2026?.length!==7||
     doc.ARK_anciens_concepts_non_promus?.length!==8||
     cog?.region!=='paca'||cog.geometries_historiques?.length!==0||
     cog.alignements_Pactols_COG_valides_2026?.length!==103||
     pilote?.autorites?.length!==103||complement?.byCode?.size!==832||
     renommages?.byCode?.size!==2)
    throw Error('Publication des sept communes nouvelles PACA non conforme');
  const current=new Map();
  for(const p of cog.periodes_com){
   if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&(!p.fin_exclue||p.fin_exclue>'2026-01-01')){
    if(current.has(p.code_insee))throw Error('Code COG en doublon');
    current.set(p.code_insee,p.libelle);
   }
  }
  if(current.size!==946)throw Error('COG PACA hors millésime');
  const used=new Set(pilote.autorites.map(x=>x.ark_pactols));
  const coded=new Set(pilote.autorites.map(x=>x.correspondances[0].code_insee));
  for(const o of [...complement.byCode.values(),...renommages.byCode.values()]){
    if(coded.has(o.code_insee)||used.has(o.ark_pactols))
     throw Error('Doublon de correspondance PACA');
    coded.add(o.code_insee);used.add(o.ark_pactols);
  }
  if(coded.size!==937||used.size!==937)throw Error('937 validations précédentes altérées');
  const historic=new Set(doc.ARK_anciens_concepts_non_promus);
  if(historic.size!==8||[...historic].some(ark=>used.has(ark)))
   throw Error('Concepts historiques des communes porteuses modifiés');
  const byCode=new Map();
  for(const a of doc.alignements_Pactols_COG_valides_2026){
   const code=a.code_insee,expected=CODES[code];
   if(!expected||byCode.has(code)||coded.has(code)||used.has(a.ark_pactols)||
      historic.has(a.ark_pactols)||a.ark_pactols!==expected||
      a.libelle_COG_2026!==current.get(code)||a.libelle_pactols!==current.get(code)||
      a.uri_insee!=='http://id.insee.fr/geo/commune/'+code||
      a.predicat_source!=='skos:exactMatch'||a.source_RDF_sha256!==RDF_SHA||
      a.millesime_validation!==2026||a.date_validation!=='2026-11-18'||
      a.statut!=='correspondance_commune_nouvelle_validee_RDF_COG_2026'||
      a.type_validation!=='prefLabel_commune_nouvelle_exactMatch_INSEE_unique_historyNote_COG_MOD32'||
      a.portee_chronologique!=='2026_SEULEMENT'||a.code_ancienne_commune_porteuse!==code||
      !historic.has(a.ark_ancienne_commune_distinct)||
      !Array.isArray(a.preuve_historique_Pactols)||!a.preuve_historique_Pactols.length||
      !a.preuve_historique_Pactols.join(' ').includes(a.date_creation_commune_nouvelle)||
      !a.preuve_historique_Pactols.join(' ').includes(current.get(code)))
    throw Error('Preuve insuffisante pour la commune nouvelle PACA '+code);
   const movements=cog.lignes_mouvements_cog.filter(x=>x.mod==='32'&&x.date_effet===a.date_creation_commune_nouvelle&&
      x.code_apres===code&&x.libelle_apres===current.get(code));
   if(movements.length<2||!movements.some(x=>x.code_avant===code))
    throw Error('Mouvement COG MOD32 absent : '+code);
   byCode.set(code,a);
  }
  if(byCode.size!==7||Object.keys(CODES).some(c=>!byCode.has(c))||
     coded.has('04045')||coded.has('05001')||byCode.has('04045')||byCode.has('05001'))
    throw Error('Lot 7 ou réserves PACA invalides');
  const index=[...byCode.values()].map(x=>({
    kind:'pactols',id:'pactols:'+x.ark_pactols,zone:'paca',
    code:x.code_insee,ark:x.ark_pactols,label:x.libelle_pactols,
    noms:[x.libelle_pactols],champs:[x.libelle_pactols,x.code_insee,x.ark_pactols].map(normaliser)
  }));
  return {byCode,index};
 }
 return {creer};
}));