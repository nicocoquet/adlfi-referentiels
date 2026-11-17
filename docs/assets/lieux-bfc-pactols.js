/* Index documentaire Pactols BFC : 3614 correspondances au COG 2026, sans rétroprojection. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxBFCPactols=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.bfc.2026.public.v1';
 const SOURCE='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const DEPARTEMENTS=/^(?:21|25|39|58|70|71|89|90)[0-9]{3}$/;
 function normaliser(x){
  return String(x??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function creer(publication,cog){
  if(publication?.schema!==SCHEMA||
   publication.region!=='bfc'||publication.millesime_cog!=='2026-01-01'||
   publication.source_rdf_sha256!==SOURCE||
   publication.source_registre!=='recette/lieux/BFC-VALIDATIONS-PACTOLS-COG-2026.csv'||
   publication.nombre_communes!==3614||
   publication.communes_a_instruire!==71||
   publication.nouvelles_geometries!==0||
   publication.liens_historiques_inferes!==0||
   publication.alignements_Pactols_COG_valides_2026?.length!==3614||
   cog?.region!=='bfc'||cog.alignements_Pactols_COG_valides_2026?.length!==0||
   cog.geometries_historiques?.length!==0)
   throw new Error('Publication Pactols BFC 2026 ou COG historique incohérent');
  const current=new Map();
  for(const p of cog.periodes_com){
   if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&
      (!p.fin_exclue||p.fin_exclue>'2026-01-01')){
    if(current.has(p.code_insee))throw new Error('Code communal COG BFC actif plusieurs fois');
    current.set(p.code_insee,p.libelle);
   }
  }
  if(current.size!==3685)throw new Error('Le COG BFC 2026 doit recenser 3685 communes');
  const byCode=new Map(),arks=new Set();
  for(const a of publication.alignements_Pactols_COG_valides_2026){
   const code=a.code_insee,ark=a.ark_pactols;
   if(!DEPARTEMENTS.test(code)||!current.has(code)||byCode.has(code)||
      code==='25060'||typeof ark!=='string'||!/^26678\/[A-Za-z0-9]+$/.test(ark)||
      arks.has(ark)||!a.libelle_COG_2026||!a.libelle_pactols||
      normaliser(a.libelle_COG_2026)!==normaliser(current.get(code))||
      a.uri_insee!=='http://id.insee.fr/geo/commune/'+code||
      a.predicat_source!=='skos:exactMatch'||a.millesime_validation!==2026||
      a.date_validation!=='2026-11-17'||
      a.statut!=='correspondance_BFC_validee_2026')
    throw new Error('Alignement Pactols BFC non justifié : '+code);
   byCode.set(code,a);
   arks.add(ark);
  }
  if(byCode.size!==3614||current.size-byCode.size!==71)
   throw new Error('Publication BFC incomplète : 71 exceptions attendues');
  const index=[...byCode.values()].map(a=>({
   kind:'pactols',id:'pactols:'+a.ark_pactols,
   zone:'bfc',code:a.code_insee,ark:a.ark_pactols,
   label:a.libelle_pactols,noms:[a.libelle_pactols],
   champs:[a.libelle_pactols,a.libelle_COG_2026,a.code_insee,
     a.ark_pactols].map(normaliser)
  }));
  return {byCode,index};
 }
 return {creer};
}));