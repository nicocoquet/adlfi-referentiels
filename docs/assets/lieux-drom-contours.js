/* 129 géométries DROM datées 2026, distinctes des identifiants Pactols. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxDromContours=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const HASH='4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778';
 const REGIONS={'971':32,'972':34,'973':22,'974':24,'976':17};
 const SCHEMA='adlfi.lieux.contours.drom-2026.v1';
 function verifier(fc,entites){
  const p=fc?.provenance;
  if(fc?.type!=='FeatureCollection'||!Array.isArray(fc.features)||
    fc.features.length!==129||p?.schema!==SCHEMA||
    p.millesime!==2026||p.cog_ref!=='2026-01-01'||
    p.edition_geometrie!=='2026-05-04'||p.generalisation_m!==100||
    p.sha256_source_geometrique!==HASH||p.contours_sans_ARK!==true||
    p.restitutions_historiques!==0||p.nombre_contours!==129||
    JSON.stringify(p.effectifs_drom)!==JSON.stringify(REGIONS))
    throw Error('Source géométrique des 129 DROM incompatible');
  const vus=new Set(),compte={};
  for(const f of fc.features){
   const x=f?.properties||{},code=x.code,region=String(code).slice(0,3);
   if(!Object.hasOwn(REGIONS,region)||!entites.has('DROM:COM:'+code)||
      x.ref_cog!=='DROM:COM:'+code||x.ark_pactols!==null||
      x.millesime_cog!=='2026-01-01'||x.edition_geometrie!=='2026-05-04'||
      x.niveau!=='commune'||x.zone!=='drom'||x.annee!==2026||
      x.qualification_geometrie!=='controle_topologique_2026'||
      !['Polygon','MultiPolygon'].includes(f.geometry?.type)||
      !Array.isArray(f.geometry.coordinates)||!f.geometry.coordinates.length||
      x.nom!==entites.get(x.ref_cog)?.label||vus.has(code))
     throw Error('Code ou contour ultramarin invalide : '+code);
   vus.add(code);compte[region]=(compte[region]||0)+1;
  }
  for(const [region,n] of Object.entries(REGIONS)){
   if(compte[region]!==n)throw Error('Effectif DOM incohérent : '+region);
  }
  return fc.features;
 }
 return {verifier};
}));