/* Contours communaux néo-calédoniens Etalab 2026 : Dumbéa exclue. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxNCContours=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.contours.nouvelle-caledonie-2026.v1';
 const SOURCE='4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778';
 function verifier(fc,entites){
  const p=fc?.provenance;
  if(fc?.type!=='FeatureCollection'||fc.features?.length!==32||
    p?.schema!==SCHEMA||p?.statut!=='contours_cartographiques_reference_2026'||
    p.cog_ref!=='2026-01-01'||p.edition_geometrie!=='2026-05-04'||
    p.generalisation_m!==100||p.sha256_source_geometrique!==SOURCE||
    p.nombre_contours!==32||p.exclusion?.code!=='98805'||
    p.contours_sans_ARK!==true||p.limites_juridiques_homologuees!==false||
    p.restitutions_historiques!==0)
   throw Error('Source cartographique Nouvelle-Calédonie non conforme');
  const expected=new Map([...entites.values()].filter(e=>
    e.kind==='cog2026'&&e.code?.startsWith('988')&&e.code!=='98805')
    .map(e=>[e.code,e]));
  if(expected.size!==32||!entites.has('COMER:COM:98805'))
   throw Error('Index COG Nouvelle-Calédonie incomplet');
  const seen=new Set();
  for(const f of fc.features){
   const x=f?.properties||{},c=x.code,entry=expected.get(c);
   if(!entry||seen.has(c)||x.nom!==entry.label||
      x.ref_cog!=='COMER:COM:'+c||x.zone!=='nouvelle-caledonie'||
      x.niveau!=='commune'||x.annee!==2026||
      x.millesime_cog!=='2026-01-01'||x.edition_geometrie!=='2026-05-04'||
      x.qualification_geometrie!=='controle_topologique_2026'||
      x.limite_juridique_homologuee!==false||x.ark_pactols!==null||
      !['Polygon','MultiPolygon'].includes(f.geometry?.type)||
      !Array.isArray(f.geometry.coordinates)||!f.geometry.coordinates.length)
    throw Error('Contour NC ou correspondance COG non conforme : '+c);
   seen.add(c);
  }
  if(seen.size!==32)throw Error('Couverture NC incomplète');
  return fc.features;
 }
 return {verifier};
}));