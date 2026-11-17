/* Nomenclature ISPF des 98 communes associées de Polynésie (source non millésimée).
 * 98 véritables communes associées ; les 18 codes xx0 ne créent AUCUNE
 * autorité supplémentaire. Aucun ARK, aucun COG à 5 chiffres inventé,
 * aucune géométrie et aucune validité juridique historique déduite.
 */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPolynesieAssociees=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.polynesie.associees_ispf_nomenclature.v1';
 const SHA='d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6';
 const normaliser=s=>String(s??'').normalize('NFKD')
    .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
    .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function creer(data,publicCOG){
  if(!data||data.schema!==SCHEMA||
     data.statut!=='NOMENCLATURE_ISPF_CONSULTEE_2026-11-17_SANS_VALIDITE_HISTORIQUE_RETROPROJETEE'||
     data.source_ispf?.sha256!==SHA||
     data.source_ispf?.consultee_le!=='2026-11-17'||
     data.referentiel_parent_COG!=='2026-01-01')
   throw Error('Source ISPF des communes associées non conforme');
  const st=data.statistiques;
  if(!st||st.communes_COG_parentes!==48||st.communes_associees!==98||
     st.communes_avec_associees!==30||st.communes_non_subdivisees!==18||
     st.unites_nomenclature_fine!==116||st.subdivisions_ISPF!==5||
     st.iles_rattachees_lignes_Geo!==64||
     st.nombre_iles_rattachees_notice_ISPF!==63||
     st.codes_geo_sans_ligne_de_base?.join(',')!=='190'||
     st.lignes_geo_Gambier_190_toutes_IR!==16||
     st.lignes_geo_source!==179||
     st.nouveaux_ARK_Pactols_crees!==0||
     st.geometries_nouvelles_publiees!==0||
     st.validite_historique_inferree!==0||
     st.alignements_Pactols_communes_conserves!==176||
     st.alignements_Pactols_collectivites_conserves!==4)
   throw Error('Comptes administratifs ISPF incohérents');
  const inter=data.interdits;
  if(!inter||Object.values(inter).some(x=>x!==false)||
     data.ecarts_libelles_48_parents_ISPF_COG?.length!==0||
     data.anomalie_geo_ispf?.code_unite_non_subdivisee!=='190'||
     data.anomalie_geo_ispf?.ligne_base_19000_absente!==true||
     data.anomalie_geo_ispf?.lignes_iles_rattachees_19001_19016!==16)
   throw Error('Confusion de nomenclature ou écart Geo ISPF non documenté');
  if(!publicCOG||publicCOG.schema!=='adlfi.lieux.recherche.outremer.public.v1'||
     Object.keys(publicCOG.pactols_valides||{}).length!==176||
     Object.keys(publicCOG.pactols_collectivites_valides||{}).length!==4)
   throw Error('Index COG/Pactols 2026 parent absent');
  const parents=new Map(publicCOG.communes['987'].split('\n').map(s=>s.split('|')));
  const sub=new Map(data.subdivisions.map(r=>[r.code_ispf,r.libelle]));
  if(parents.size!==48||sub.size!==5||
     !Array.isArray(data.communes_associees)||data.communes_associees.length!==98||
     !Array.isArray(data.unites_communes_non_subdivisees)||
     data.unites_communes_non_subdivisees.length!==18)
   throw Error('Rattachements du référentiel ISPF incomplets');
  const ids=new Set(),parParent=new Map(),nonSub=new Map(),entries=[];
  const valider=(r,associee)=>{
   if(!r||!/^[1-5][0-9][0-9]$/.test(r.code_ispf||'')||
      r.code_ispf.endsWith('0')===associee||
      ids.has(r.code_ispf)||
      r.commune_parent_cog!=='987'+r.code_ispf.slice(0,2)||
      !parents.has(r.commune_parent_cog)||
      parents.get(r.commune_parent_cog)!==r.commune_parent_libelle_cog||
      !sub.has(r.subdivision_ispf)||
      sub.get(r.subdivision_ispf)!==r.subdivision_libelle||
      !r.libelle.trim())
    throw Error('Autorité ISPF sans parent COG ou code valide : '+r?.code_ispf);
   ids.add(r.code_ispf);
  };
  for(const r of data.communes_associees){
   valider(r,true);
   const e={kind:'associee_ispf',id:'ISPF:COMAS:'+r.code_ispf,
     code:r.code_ispf,label:r.libelle,parentCode:r.commune_parent_cog,
     parent:r.commune_parent_libelle_cog,
     subdivision:r.subdivision_libelle,subdivisionCode:r.subdivision_ispf,
     type:'Commune associée (ISPF)',arkValide:null,geometriePubliee:false,
     codeInseePropre:null,dateSource:'2026-11-17',
     validiteHistoriqueEtablie:false,
     champs:[...new Set([r.libelle,r.code_ispf,r.commune_parent_cog,
       r.commune_parent_libelle_cog,r.subdivision_libelle,'commune associée ispf']
       .map(normaliser).filter(Boolean))]};
   entries.push(e);
   if(!parParent.has(e.parentCode))parParent.set(e.parentCode,[]);
   parParent.get(e.parentCode).push(e);
  }
  for(const r of data.unites_communes_non_subdivisees){
   valider(r,false);
   if(normaliser(r.libelle)!==normaliser(r.commune_parent_libelle_cog))
    throw Error('Code xx0 d’une commune entière non compatible : '+r.code_ispf);
   nonSub.set(r.commune_parent_cog,{code_ispf:r.code_ispf,label:r.libelle});
  }
  if(parParent.size!==30||nonSub.size!==18||ids.size!==116||
     [...parParent.keys()].some(x=>nonSub.has(x))||
     parParent.size+nonSub.size!==48)
   throw Error('Partition ISPF 30/18 des 48 communes non établie');
  const avera=entries.filter(e=>normaliser(e.label).startsWith('avera'));
  if(avera.length!==2||avera.find(e=>e.code==='441')?.parentCode!=='98744'||
     avera.find(e=>e.code==='501')?.parentCode!=='98750')
   throw Error('Homonymes Avera mal différenciés');
  return {entries,parParent,nonSub,
    byId:new Map(entries.map(e=>[e.id,e])),
    source:data.source_ispf,
    anomalieGeo:data.anomalie_geo_ispf,
    statistiques:st};
 }
 return {creer,normaliser};
}));