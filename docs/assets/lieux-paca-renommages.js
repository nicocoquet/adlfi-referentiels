/* PACA : trois renommages 2026, dont Céreste (UUID Insee officiellement résolu). */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPACARenommages=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.paca.renommages.2026.public.v2';
 const UUID_URI='http://id.insee.fr/geo/commune/3cb419d3-63ba-4e7c-be42-2640cf521de8';
 const UUID_PROOF='recette/lieux/PACA-CERESTE-UUID-INSEE-AUDIT-2026.json';
 const CODE_PRED='http://rdf.insee.fr/def/geo#codeINSEE';
 const SOURCE='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const CASES=new Map([
  ['04045',{ark:'26678/pcrtHxveTzUMik',old:'Céreste',name:'Céreste-en-Luberon',date:'2024-01-01',decret:'2023-959',pref:'Céreste-en-Luberon'}],
  ['05127',{ark:'26678/pcrtla4EHGDgDd',old:'Rousset',name:'Rousset-Serre-Ponçon',date:'2025-01-01',decret:'2024-863',pref:'Rousset (Hautes-Alpes)'}],
  ['83052',{ark:'26678/pcrt7B7bs9P5g2',old:'Esparron',name:'Esparron-de-Pallières',date:'2026-01-01',decret:'2025-815',pref:'Esparron (Var)'}],
 ]);
 function normalize(x){
  return String(x??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function creer(data,cog,pilote,complement){
  if(data?.schema!==SCHEMA||data.region!=='paca'||data.millesime_cog!=='2026-01-01'||
     data.source_rdf_sha256!==SOURCE||
     data.source_audit!=='recette/lieux/PACA-TROIS-RENOMMAGES-RDF-2026.json'||
     data.liens_renommages_ajoutes!==3||data.pilotage_valide_conserve!==103||
     data.complements_existants_conserves!==832||
     data.total_alignements_PACA_2026!==938||data.communes_a_instruire!==8||
     data.Cereste_UUID_resolu_code_COG!=='04045'||data.preuve_Cereste_UUID!==UUID_PROOF||
     data.autres_renommages_historiques_inferes!==0||data.geometries_modifiees!==0||
     data.alignements_Pactols_COG_valides_2026?.length!==3||
     cog?.region!=='paca'||cog.geometries_historiques?.length!==0||
     cog.alignements_Pactols_COG_valides_2026?.length!==103||
     pilote?.autorites?.length!==103||complement?.byCode?.size!==832)
   throw Error('Index PACA des trois renommages non conforme');
  const current=new Map();
  for(const p of cog.periodes_com){
   if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&
      (!p.fin_exclue||p.fin_exclue>'2026-01-01')){
     if(current.has(p.code_insee))throw Error('Doublon COG PACA');
     current.set(p.code_insee,p.libelle);
   }
  }
  if(current.size!==946)throw Error('Couverture communale PACA incorrecte');
  const oldCodes=new Set(pilote.autorites.map(x=>x.correspondances[0].code_insee));
  const oldArks=new Set(pilote.autorites.map(x=>x.ark_pactols));
  if(oldCodes.size!==103||oldArks.size!==103||complement.byCode.has('04045')||
     oldCodes.has('04045'))
   throw Error('Pilote PACA ou réserve Céreste incohérents');
  for(const a of complement.byCode.values()){ oldCodes.add(a.code_insee);oldArks.add(a.ark_pactols); }
  if(oldCodes.size!==935||oldArks.size!==935)throw Error('Anciennes validations PACA non uniques');
  const byCode=new Map();
  for(const x of data.alignements_Pactols_COG_valides_2026){
   const spec=CASES.get(x.code_insee);
   if(!spec||byCode.has(x.code_insee)||oldCodes.has(x.code_insee)||
      oldArks.has(x.ark_pactols)||x.ark_pactols!==spec.ark||
      x.libelle_COG_2026!==spec.name||x.libelle_ancien_COG!==spec.old||
      x.libelle_pactols!==spec.pref||x.decret!==spec.decret||
      x.date_effet_renommage!==spec.date||
      x.uri_insee!==(x.code_insee==='04045'?UUID_URI:'http://id.insee.fr/geo/commune/'+x.code_insee)||
      x.predicat_source!=='skos:exactMatch'||x.source_rdf_sha256!==SOURCE||
      x.millesime_validation!==2026||x.date_validation!=='2026-11-18'||
      x.statut!=='correspondance_PACA_renommage_validee_par_preuves_2026'||
      x.type_validation!==(x.code_insee==='04045'?'exactMatch_UUID_resolu_INSEE_plus_MOD10_plus_decret':'exactMatch_code_2026_plus_MOD10_plus_decret')||
      (x.code_insee==='04045'&&(x.code_insee_resolu!=='04045'||
        x.predicat_resolution!==CODE_PRED||x.source_preuve_uuid!==UUID_PROOF))||
      x.portee_chronologique!=='2026_SEULEMENT'||
      current.get(x.code_insee)!==x.libelle_COG_2026)
    throw Error('Renommage PACA insuffisamment prouvé : '+x.code_insee);
   const event=cog.lignes_mouvements_cog.filter(m=>
    m.mod==='10'&&m.code_avant===x.code_insee&&m.code_apres===x.code_insee&&
    m.date_effet===spec.date&&m.libelle_avant===spec.old&&m.libelle_apres===spec.name);
   if(event.length!==1)throw Error('Historique MOD10 non conforme : '+x.code_insee);
   byCode.set(x.code_insee,x);
  }
  if(byCode.size!==3||[...CASES.keys()].some(c=>!byCode.has(c)))
   throw Error('Lot de trois renommages PACA incomplet');
  const index=[...byCode.values()].map(x=>({
   kind:'pactols',id:'pactols:'+x.ark_pactols,
   zone:'paca',code:x.code_insee,ark:x.ark_pactols,
   label:x.libelle_pactols,noms:[x.libelle_pactols,x.libelle_COG_2026],
   champs:[x.libelle_pactols,x.libelle_COG_2026,x.libelle_ancien_COG,
           x.code_insee,x.ark_pactols].map(normalize)
  }));
  return {byCode,index};
 }
 return {creer};
}));