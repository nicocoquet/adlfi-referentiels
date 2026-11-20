/* Normandie : 16 alignements Pactols–COG validés uniquement pour 2026.
 * Les deux registres restent indépendants des périodes historiques et des
 * géométries Etalab. Aucun ARK d'ancienne commune n'est assimilé à l'actuel.
 */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxNormandiePactols=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const RDF='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const L1='adlfi.lieux.pactols.normandie.lot01.2026.public.v1';
 const L2='adlfi.lieux.pactols.normandie.lot02.2026.public.v1';
 const EXCLUS=['50412','14342','27112','50546'];
 const RE=/^(?:14|27|50|61|76)[0-9]{3}$/;
 const ARK=/^26678\/[A-Za-z0-9]+$/;
 const norm=s=>String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
  .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
  .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 function creer(lot01,lot02,cog){
  if(lot01?.schema!==L1||lot02?.schema!==L2||
     lot01.region!=='normandie'||lot02.region!=='normandie'||
     lot01.millesime_cog!=='2026-01-01'||lot02.millesime_cog!=='2026-01-01'||
     lot01.source_rdf_sha256!==RDF||lot02.source_rdf_sha256!==RDF||
     lot01.nombre_communes!==9||lot02.nombre_communes!==7||
     lot01.communes_lot01_a_instruire!==1||lot02.communes_lot02_suspendues!==3||
     lot02.cumule_avec_lot01!==16||
     lot01.active_dans_interface!==false||lot02.active_dans_interface!==false||
     lot01.nouvelles_geometries!==0||lot02.nouvelles_geometries!==0||
     lot01.liens_historiques_inferes!==0||lot02.liens_historiques_inferes!==0||
     lot01.couverture_region_entiere!==false||lot02.couverture_region_entiere!==false||
     lot01.alignements_Pactols_COG_valides_2026?.length!==9||
     lot02.alignements_Pactols_COG_valides_2026?.length!==7||
     cog?.region!=='normandie'||cog.millesime_cog!==2026||
     cog.geometries_historiques?.length!==0||
     cog.alignements_Pactols_COG_valides_2026?.length!==0)
   throw Error('Normandie : registres Pactols/COG ou période incohérents');
  const contemporains=new Map();
  for(const p of cog.periodes_com){
   if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&
      (!p.fin_exclue||p.fin_exclue>'2026-01-01')){
    if(contemporains.has(p.code_insee))throw Error('Normandie : état COM actuel dupliqué');
    contemporains.set(p.code_insee,p.libelle);
   }
  }
  if(contemporains.size!==2644)throw Error('Normandie : 2 644 communes attendues en 2026');
  const byCode=new Map(),arks=new Set(),anciens=new Set();
  const exceptions=lot02.exceptions_non_validees;
  if(!Array.isArray(exceptions)||exceptions.length!==3||
     new Set(exceptions.map(e=>e.code_insee)).size!==3||
     !['14342','27112','50546'].every(c=>exceptions.some(e=>e.code_insee===c)&&
       exceptions.find(e=>e.code_insee===c)?.alignement_publie===false))
   throw Error('Normandie : les trois réserves historiques ont changé');
  for(const a of [...lot01.alignements_Pactols_COG_valides_2026,
                    ...lot02.alignements_Pactols_COG_valides_2026]){
   const code=a.code_insee,ark=a.ark_pactols,ancien=a.ancien_ark_non_promu;
   if(!RE.test(code)||!contemporains.has(code)||EXCLUS.includes(code)||
      byCode.has(code)||!ARK.test(ark)||!ARK.test(ancien)||ark===ancien||
      arks.has(ark)||anciens.has(ark)||arks.has(ancien)||anciens.has(ancien)||
      norm(a.libelle_COG_2026)!==norm(contemporains.get(code))||
      !a.libelle_pactols||a.uri_insee!=='http://id.insee.fr/geo/commune/'+code||
      a.predicat_source!=='skos:exactMatch'||a.millesime_validation!==2026||
      a.date_validation!=='2026-11-20'||
      a.statut!=='correspondance_NORMANDIE_validee_pour_2026'||
      !/^20[0-9]{2}-[0-9]{2}-[0-9]{2}$/.test(a.date_creation_commune_nouvelle)||
      a.source_insee!=='https://www.insee.fr/fr/statistiques/2011101?geo=COM-'+code)
     throw Error('Normandie : correspondance non justifiée : '+code);
   if(a.preuve_creation_RDF){
    const p=a.preuve_creation_RDF;
    if(p.ark!==ark||p.code_COG_2026!==code||
       p.date_creation_RDF!==a.date_creation_commune_nouvelle||
       p.source!=='skos:historyNote'||!/^([a-f0-9]{64})$/.test(p.sha256_note_complete))
      throw Error('Normandie : preuve RDF complète incompatible : '+code);
   }
   byCode.set(code,a);arks.add(ark);anciens.add(ancien);
  }
  if(byCode.size!==16)throw Error('Normandie : 16 validations attendues');
  const index=[...byCode.values()].map(a=>({
   kind:'pactols',id:'pactols:'+a.ark_pactols,zone:'normandie',
   code:a.code_insee,ark:a.ark_pactols,label:a.libelle_pactols,
   noms:[a.libelle_pactols],
   champs:[a.libelle_pactols,a.libelle_COG_2026,a.code_insee,
     a.ark_pactols].map(norm)
  }));
  return {byCode,index,exclusions:new Set(EXCLUS)};
 }
 return Object.freeze({creer});
}));
