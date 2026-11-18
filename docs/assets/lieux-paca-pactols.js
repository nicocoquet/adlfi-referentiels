/* PACA : 832 correspondances Pactols–COG 2026 complémentaires au pilote de 103. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPACAPactols=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.paca.complement.2026.public.v1';
 const RDF_SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const CSV_SHA='647ba3e1fdfd80199b854b512f12269379edaf910f47e34b7f53650ce2844925';
 const REPORT_SHA='a1d032da4c06a69c7d77ec8b6d28977856cc1e22bec1260d5d8e8550303c5a22';
 const DEPARTEMENTS=/^(?:04|05|06|13|83|84)[0-9]{3}$/;
 const EXCEPTIONS=new Set('04033 04045 04120 05001 05024 05039 05053 05101 05118 05127 83052'.split(' '));
 function normaliser(x){
  return String(x??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function creer(publication,cog){
  if(publication?.schema!==SCHEMA || publication.region!=='paca' ||
     publication.millesime_cog!=='2026-01-01'||
     publication.source_rdf_sha256!==RDF_SHA||
     publication.source_registre!=='recette/lieux/PACA-CANDIDATS-EXACTMATCH-2026.csv'||
     publication.sha256_registre!==CSV_SHA||
     publication.source_preflight!=='recette/lieux/PACA-PREFLIGHT-EXACTMATCH-2026.json'||
     publication.sha256_preflight!==REPORT_SHA||
     publication.nombre_ajouts!==832 || publication.pilote_valide_conserve!==103||
     publication.nombre_total_alignements_2026!==935||
     publication.communes_a_instruire!==11 ||
     publication.nouvelles_geometries!==0||publication.liens_historiques_inferes!==0||
     publication.alignements_Pactols_COG_valides_2026?.length!==832 ||
     cog?.region!=='paca'||cog.alignements_Pactols_COG_valides_2026?.length!==103||
     cog.geometries_historiques?.length!==0)
   throw Error('Publication Pactols PACA ou historique COG incohérents');
  const current=new Map();
  for(const period of cog.periodes_com){
   if(period.typecom==='COM'&&period.debut_inclus<='2026-01-01'&&
      (!period.fin_exclue||period.fin_exclue>'2026-01-01')){
     if(current.has(period.code_insee))throw Error('Deux états COG PACA actuels pour le même code');
     current.set(period.code_insee,period.libelle);
   }
  }
  if(current.size!==946)throw Error('946 communes COG PACA attendues');
  const pilot=new Set(),pilotARKs=new Set();
  for(const old of cog.alignements_Pactols_COG_valides_2026){
   if(!current.has(old.code_insee)||pilot.has(old.code_insee)||pilotARKs.has(old.ark_pactols))
    throw Error('Pilote PACA incohérent');
   pilot.add(old.code_insee);
   pilotARKs.add(old.ark_pactols);
  }
  if(pilot.size!==103||!pilot.has('05139')||EXCEPTIONS.has('05139'))
    throw Error('Pilote Dévoluy ou validations historiques manquants');
  const byCode=new Map(),arks=new Set();
  for(const row of publication.alignements_Pactols_COG_valides_2026){
   const code=row.code_insee,ark=row.ark_pactols;
   if(!DEPARTEMENTS.test(code)||!current.has(code)||pilot.has(code)||
      EXCEPTIONS.has(code)||byCode.has(code)||typeof ark!=='string'||
      !/^26678\/[A-Za-z0-9]+$/.test(ark)||arks.has(ark)||pilotARKs.has(ark)||
      !row.libelle_COG_2026||!row.libelle_pactols||
      normaliser(row.libelle_COG_2026)!==normaliser(current.get(code))||
      row.uri_insee!=='http://id.insee.fr/geo/commune/'+code||
      row.predicat_source!=='skos:exactMatch'||
      row.millesime_validation!==2026||row.date_validation!=='2026-11-18'||
      row.statut!=='correspondance_PACA_validee_par_regle_2026'||
      row.type_validation!=='exactMatch_univoque_avec_preflight_URIs_INSEE')
    throw Error('Alignement Pactols PACA non justifié : '+code);
   byCode.set(code,row);
   arks.add(ark);
  }
  if(byCode.size!==832||current.size-byCode.size-pilot.size!==11||
     EXCEPTIONS.size!==11||[...EXCEPTIONS].some(c=>!current.has(c)||pilot.has(c)||byCode.has(c)))
   throw Error('Couverture PACA incomplète ou 11 exceptions modifiées');
  const index=[...byCode.values()].map(a=>({
   kind:'pactols',id:'pactols:'+a.ark_pactols,zone:'paca',
   code:a.code_insee,ark:a.ark_pactols,label:a.libelle_pactols,
   noms:[a.libelle_pactols],
   champs:[a.libelle_pactols,a.libelle_COG_2026,a.code_insee,
     a.ark_pactols].map(normaliser)
  }));
  return {byCode,index};
 }
 return {creer};
}));