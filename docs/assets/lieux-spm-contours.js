/* Deux contours cartographiques 2026 de Saint-Pierre-et-Miquelon, sans ARK nouveau. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxSPMContours=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.contours.spm-2026.v1';
 const HASH='4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778';
 const AUDIT='5aa79d28ab3d7dcf5952937b90e2beb4a558afc1f1b05c9c697b30682ae60b33';
 const CODES={'97501':'Miquelon-Langlade','97502':'Saint-Pierre'};
 function verifier(fc,entites){
  const p=fc?.provenance;
  if(fc?.type!=='FeatureCollection'||fc.features?.length!==2||
     p?.schema!==SCHEMA||p.millesime!==2026||p.cog_ref!=='2026-01-01'||
     p.edition_geometrie!=='2026-05-04'||p.generalisation_m!==100||
     p.sha256_source_geometrique!==HASH||p.sha256_audit_COG!==AUDIT||
     p.contours_sans_ARK!==true||p.limites_juridiques_homologuees!==false||
     p.restitutions_historiques!==0||p.nombre_contours!==2||
     p.statut!=='contours_cartographiques_reference_2026')
    throw Error('Source cartographique SPM non conforme');
  const seen=new Set();
  for(const f of fc.features){
   const props=f?.properties||{},c=props.code,ref='COMER:COM:'+c;
   if(!Object.hasOwn(CODES,c)||seen.has(c)||props.nom!==CODES[c]||
      props.ref_cog!==ref||entites.get(ref)?.label!==CODES[c]||
      props.zone!=='spm'||props.niveau!=='commune'||props.annee!==2026||
      props.millesime_cog!=='2026-01-01'||props.edition_geometrie!=='2026-05-04'||
      props.qualification_geometrie!=='controle_topologique_2026'||
      props.limite_juridique_homologuee!==false||
      props.ark_pactols!==null||
      !['Polygon','MultiPolygon'].includes(f.geometry?.type)||
      !Array.isArray(f.geometry.coordinates)||!f.geometry.coordinates.length)
    throw Error('Contour SPM ou code COG non conforme : '+c);
   seen.add(c);
  }
  if(seen.size!==2)throw Error('Deux contours SPM obligatoires');
  return fc.features;
 }
 return {verifier};
}));