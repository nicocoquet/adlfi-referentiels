/* Index COG 2026 ultramarin : aucune géométrie ni équivalence historique implicite.
   Le format public compact est dérivé de la recette de 233 entités / PR 30.
   Ce module n'interprète PAS les ARK confirmés comme des correspondances validées. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxOutremerSearch=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.recherche.outremer.public.v1';
 const GROUPES={
  '971':['Guadeloupe',32,'DROM'],
  '972':['Martinique',34,'DROM'],
  '973':['Guyane',22,'DROM'],
  '974':['La Réunion',24,'DROM'],
  '975':['Saint-Pierre-et-Miquelon',2,'COMER'],
  '976':['Mayotte',17,'DROM'],
  '987':['Polynésie française',48,'COMER'],
  '988':['Nouvelle-Calédonie',33,'COMER']
 };
 const PARENTS={
  ...Object.fromEntries(Object.entries(GROUPES).map(([k,v])=>[k,v[0]])),
  '977':'Saint-Barthélemy','978':'Saint-Martin',
  '981':'Île des Faisans','984':'Terres australes et antarctiques françaises',
  '986':'Wallis-et-Futuna','989':'La Passion-Clipperton'
 };
 const TYPES={CDM:'Condominium',CIR:'Circonscription',COM:'Zonage particulier',
   CPT:'Territoire',DIS:'District',TERRITOIRE:'Collectivité ou territoire'};
 const normaliser=s=>String(s??'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'')
   .toLocaleLowerCase('fr').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 const CHIFFRES=/^\d{5}$/;
 const ARK=/^26678\/[A-Za-z0-9]+$/;
 function verifierObjet(data){
  if(!data||data.schema!==SCHEMA||data.cog_ref!=='2026-01-01'||
     data.edition_geom!=='2026-05-04'||
     data.source_audit_sha256!=='5aa79d28ab3d7dcf5952937b90e2beb4a558afc1f1b05c9c697b30682ae60b33'||
     !data.communes||!data.autres||!data.pactols_valides||
     !data.ark_confirmes_non_valides||!Array.isArray(data.contours_invalides))
    throw new Error('Export COG ultramarin incompatible');
  if(JSON.stringify(Object.keys(data.communes).sort())!==
      JSON.stringify(Object.keys(GROUPES).sort()))
    throw new Error('Départements/collectivités COG incomplets');
  const valid=Object.keys(data.pactols_valides).sort();
  const confirmed=Object.keys(data.ark_confirmes_non_valides).sort();
  const mayotte=valid.filter(code=>/^976(?:0[1-9]|1[0-7])$/.test(code)&&code!=='97607');
  const guyane=valid.filter(code=>/^973(?:0[1-9]|1[0-4]|5[2-3]|5[6-8]|6[0-2])$/.test(code));
  const martinique=valid.filter(code=>/^972(?:0[1-9]|[12][0-9]|3[0-4])$/.test(code));
  const guadeloupe=valid.filter(code=>/^971(?:0[1-9]|[12][0-9]|3[0-4])$/.test(code)
    &&code!=='97123'&&code!=='97127');
  const reunion=valid.filter(code=>/^974(?:0[1-9]|1[0-9]|2[0-4])$/.test(code));
  const polynesie=valid.filter(code=>/^987(?:[1-5][0-9])$/.test(code));
  if(valid.length!==176||mayotte.length!==16||guyane.length!==22||martinique.length!==34||guadeloupe.length!==32||reunion.length!==24||polynesie.length!==48||
     confirmed.join(',')!=='97607'||
     data.ark_confirmes_non_valides['97607']!=='26678/crtZcuFSJVYZU'||
     data.pactols_valides['97407']!=='26678/pcrtIKvRT9vwUl'||
     data.pactols_valides['98711']!=='26678/pcrtwSlYRcWVFw'||
     data.pactols_valides['98735']!=='26678/pcrtr90gKcAXiG'||
     data.pactols_valides['98745']!=='26678/pcrteZcqWgVUaT'||
     data.pactols_valides['98758']!=='26678/pcrtRw9F7i5M8l'||
     data.contours_invalides.slice().sort().join(',')!=='98745,98805')
    throw new Error('Décisions éditoriales ou diagnostics 2026 modifiés');
  if(new Set(Object.values(data.pactols_valides)).size!==176)
    throw new Error('Plusieurs communes partagent un ARK Pactols');
  for(const [code,ark] of Object.entries({...data.pactols_valides,...data.ark_confirmes_non_valides})){
   if(!CHIFFRES.test(code)||!ARK.test(ark)||valid.includes(code)&&confirmed.includes(code))
    throw new Error('Identifiant Pactols mal attribué : '+code);
  }
 }
 function creerIndex(data){
  verifierObjet(data);
  const ids=new Set(),entries=[];
  for(const [prefix,[parent,count,famille]] of Object.entries(GROUPES)){
   const raw=data.communes[prefix];
   if(typeof raw!=='string')throw new Error('Liste COG absente : '+prefix);
   const records=raw.split('\n');
   if(records.length!==count)throw new Error('Nombre de communes incorrect : '+prefix);
   for(const record of records){
    const at=record.indexOf('|'),code=record.slice(0,at),name=record.slice(at+1);
    if(at!==5||!CHIFFRES.test(code)||!code.startsWith(prefix)||!name.trim())
      throw new Error('Commune 2026 invalide : '+record);
    const id=famille+':COM:'+code;
    if(ids.has(id))throw new Error('Commune dupliquée : '+id);
    ids.add(id);
    const ark=data.pactols_valides[code]??null;
    const arkConfirme=data.ark_confirmes_non_valides[code]??null;
    const champs=[name,code,parent,prefix,ark]
       .map(normaliser).filter(Boolean);
    entries.push({kind:'cog2026',id,code,label:name,parent,parentCode:prefix,
      type:'Commune',famille,arkValide:ark,arkConfirme,
      geomStatut:data.contours_invalides.includes(code)?
       'PRESENTE_INVALIDE':'PRESENTE_VALIDE_A_QUALIFIER',
      dateReference:'2026-01-01',geometriePubliee:false,
      champs:[...new Set(champs)]});
   }
  }
  if(entries.length!==212)throw new Error('212 communes attendues');
  if(!Array.isArray(data.autres)||data.autres.length!==21)
    throw new Error('21 entités particulières attendues');
  let territoire=0;
  for(const pair of data.autres){
   if(!Array.isArray(pair)||pair.length!==2)throw new Error('Zonage invalide');
   const [id,name]=pair;
   const m=/^COMER:(CDM|CIR|COM|CPT|DIS|TERRITOIRE):(\d{3,5})$/.exec(id);
   if(!m||ids.has(id)||!name.trim())throw new Error('Zonage dupliqué/invalide : '+id);
   ids.add(id);
   const type=m[1],code=m[2],parentCode=code.slice(0,3);
   if(!PARENTS[parentCode]||(type==='TERRITOIRE'&&code!==parentCode))
    throw new Error('Rattachement COMER inconnu : '+id);
   if(type==='TERRITOIRE')territoire++;
   entries.push({kind:'autre_cog2026',id,code,label:name,
     parent:type==='TERRITOIRE'?null:PARENTS[parentCode],
     parentCode:type==='TERRITOIRE'?null:parentCode,
     type:TYPES[type],nature:type,dateReference:'2026-01-01',
     geometriePubliee:false,
     champs:[...new Set([name,code,PARENTS[parentCode],parentCode]
       .map(normaliser).filter(Boolean))]});
  }
  if(territoire!==9||entries.length!==233)throw new Error('Collectivités COG incomplètes');
  return entries;
 }
 return {creerIndex,normaliser};
}));
