/* Polynésie : 28 contours cartographiques 2026 présélectionnés, sans limite historique. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPFContours=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.contours.polynesie-2026.v1';
 const SOURCE='4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778';
 const AUDIT='49724c979baa2cbedf0612b677b7c273757f8ba58749933e9b1a06a27398f52';
 const CODES=('98714 98715 98718 98722 98723 98724 98725 98729 98731 98733 98734 98735 '+
              '98736 98738 98739 98741 98743 98744 98746 98747 98748 98750 98752 98753 '+
              '98754 98756 98757 98758').split(' ');
 const codes=new Set(CODES);
 function verifier(fc,entites){
  const p=fc?.provenance;
  if(fc?.type!=='FeatureCollection'||fc.features?.length!==28||
     p?.schema!==SCHEMA||p.statut!=='contours_cartographiques_reference_2026'||
     p.cog_ref!=='2026-01-01'||p.edition_geometrie!=='2026-05-04'||
     p.generalisation_m!==100||p.sha256_source_geometrique!==SOURCE||
     p.sha256_audit_comparatif!==AUDIT||p.nombre_contours!==28||
     p.communes_COG_2026!==48||p.tahaa_code!=='98745'||
     p.exclues_a_instruire?.length!==20||p.contours_sans_ARK!==true||
     p.limites_juridiques_homologuees!==false||p.restitutions_historiques!==0||
     p.criteres_recette_iou?.etalab_ISPF!==0.9||
     p.criteres_recette_iou?.etalab_GEO_PF!==0.9||
     p.criteres_recette_iou?.ISPF_GEO_PF!==0.95)
    throw Error('Source cartographique Polynésie non conforme');
  const expected=new Map([...entites.values()].filter(x=>
    x.kind==='cog2026'&&x.code?.startsWith('987')).map(x=>[x.code,x]));
  if(expected.size!==48||!expected.has('98745'))
    throw Error('Index COG Polynésie incomplet');
  const seen=new Set();
  for(const f of fc.features){
   const x=f?.properties||{},c=x.code,ref='COMER:COM:'+c;
   if(!codes.has(c)||seen.has(c)||x.nom!==expected.get(c)?.label||
      x.ref_cog!==ref||!entites.has(ref)||x.zone!=='polynesie'||
      x.niveau!=='commune'||x.annee!==2026||
      x.millesime_cog!=='2026-01-01'||x.edition_geometrie!=='2026-05-04'||
      x.qualification_geometrie!=='audit_comparatif_et_topologique'||
      x.limite_juridique_homologuee!==false||x.ark_pactols!==null||
      !['Polygon','MultiPolygon'].includes(f.geometry?.type)||
      !Array.isArray(f.geometry.coordinates)||!f.geometry.coordinates.length)
     throw Error('Contour polynésien non conforme : '+c);
   seen.add(c);
  }
  if(seen.size!==28||CODES.some(c=>!seen.has(c)))
   throw Error('Lot polynésien incomplet');
  if(p.exclues_a_instruire.some(c=>codes.has(c))||
     !p.exclues_a_instruire.includes('98745')||
     new Set([...CODES,...p.exclues_a_instruire]).size!==48)
   throw Error('Exclusions polynésiennes incohérentes');
  return fc.features;
 }
 return {verifier};
}));