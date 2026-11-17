/* Index indépendant des états historiques COG — 360 correspondances Pactols Corse 2026. */
(function(root,factory){
  'use strict';
  const api=factory();
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  if(root)root.AdlfiLieuxCorsePactols=api;
}(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const SCHEMA='adlfi.lieux.pactols.corse.2026.public.v1';
  const SOURCE='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
  const RE=/^2[AB][0-9]{3}$/;
  function normaliser(x){
    return String(x??'').replace(/œ/gi,'oe').normalize('NFKD')
      .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
      .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
  }
  function creer(publication,cog){
    if(publication?.schema!==SCHEMA||publication.region!=='corse'||
       publication.millesime_cog!=='2026-01-01'||
       publication.source_rdf_sha256!==SOURCE||
       publication.nombre_communes!==360||
       publication.nouvelles_geometries!==0||
       publication.liens_historiques_inferes!==0||
       publication.alignements_Pactols_COG_valides_2026?.length!==360||
       cog?.region!=='corse'||
       cog.alignements_Pactols_COG_valides_2026?.length!==0||
       cog.geometries_historiques?.length!==0)
      throw new Error('Publication Pactols Corse 2026 ou état COG source incohérent');
    const reference=new Map();
    for(const period of cog.periodes_com){
      if(period.typecom==='COM'&&period.debut_inclus<='2026-01-01'&&
         (!period.fin_exclue||period.fin_exclue>'2026-01-01')){
        if(reference.has(period.code_insee))throw new Error('Deux communes corses simultanées');
        reference.set(period.code_insee,period.libelle);
      }
    }
    if(reference.size!==360)throw new Error('Le COG corse 2026 doit contenir 360 communes');
    const byCode=new Map(),used=new Set();
    for(const row of publication.alignements_Pactols_COG_valides_2026){
      const c=row.code_insee,ark=row.ark_pactols;
      if(!RE.test(c)||!reference.has(c)||byCode.has(c)||
         typeof ark!=='string'||!/^26678\/[A-Za-z0-9]+$/.test(ark)||
         used.has(ark)||
         !row.libelle_pactols||!row.libelle_COG_2026||
         normaliser(row.libelle_COG_2026)!==normaliser(reference.get(c))||
         row.uri_insee!=='http://id.insee.fr/geo/commune/'+c||
         row.predicat_source!=='skos:exactMatch'||
         row.millesime_validation!==2026||
         row.statut!=='correspondance_CORSE_validee_2026')
        throw new Error('Alignement Pactols corse non justifié : '+c);
      byCode.set(c,row);used.add(ark);
    }
    if(byCode.size!==360||[...reference.keys()].some(c=>!byCode.has(c)))
      throw new Error('Publication Corse incomplète');
    const index=[...byCode.values()].map(a=>({
      kind:'pactols',id:'pactols:'+a.ark_pactols,
      zone:'corse',code:a.code_insee,ark:a.ark_pactols,
      label:a.libelle_pactols,noms:[a.libelle_pactols],
      champs:[a.libelle_pactols,a.libelle_COG_2026,a.code_insee,
              a.ark_pactols].map(normaliser)
    }));
    return {byCode,index};
  }
  return {creer};
}));