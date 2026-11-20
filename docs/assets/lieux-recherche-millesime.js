/* Recherche COG multi-millésimes : donner la priorité aux identités
 * administratives effectivement attestées à l'année de consultation.
 * Ne crée ni relation de succession ni équivalence entre deux ARK Pactols.
 */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxRechercheMillesime=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 function norm(x){
  return String(x??'').replace(/œ/gi,'oe').normalize('NFKD')
   .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
   .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 }
 function preparer(regions,ids){
  const result=new Map();
  if(!Array.isArray(ids)||!regions)throw Error('Corpus COG régional absent');
  for(const zone of ids){
   const cog=regions[zone]?.cog;
   if(!Array.isArray(cog?.periodes_com))throw Error('Chronologie COG absente : '+zone);
   for(const p of cog.periodes_com){
    if(p.typecom!=='COM')continue;
    if(typeof p.code_insee!=='string'||!p.debut_inclus||
       (p.fin_exclue&&p.fin_exclue<=p.debut_inclus))
     throw Error('Intervalle communal mal formé : '+zone+' '+JSON.stringify({code:p.code_insee,debut:p.debut_inclus,fin:p.fin_exclue}));
    const key=zone+':'+p.code_insee;
    if(!result.has(key))result.set(key,[]);
    result.get(key).push({start:p.debut_inclus,end:p.fin_exclue||null});
   }
  }
  return result;
 }
 function etat(h,annee,periodes){
  if(!Number.isInteger(annee)||annee<1943||annee>2026||!(periodes instanceof Map))
   throw Error('Millésime ou index COG incorrect');
  if((h.kind!=='cog'&&h.kind!=='pactols')||!h.zone||!h.code)
   return 'hors_cog_regional';
  const list=periodes.get(h.zone+':'+h.code);
  if(!list)return 'non_documente';
  const date=String(annee)+'-01-01';
  return list.some(p=>p.start<=date&&(!p.end||date<p.end))?'actif':'historique';
 }
 function classe(h,q,annee,periodes){
  const query=norm(q);
  const code=norm(h.code),ark=norm(h.ark||h.arkValide);
  const exactIdentifiant=!!query&&(code===query||ark===query);
  if(exactIdentifiant)return 0; // Saisie explicite d'un code/ARK jamais déclassée.
  const label=norm(h.label);
  const noms=[label,...(h.noms||[]).map(norm)];
  const exact=noms.includes(query);
  const commence=noms.some(n=>n.startsWith(query));
  const current=etat(h,annee,periodes)==='actif';
  const actifEn2026=(h.kind==='pactols'&&annee===2026&&current);
  if(h.kind==='admin'&&h.year===annee&&exact)return 1;
  if(h.kind==='cog'&&current&&exact)return 2;
  if(actifEn2026&&exact)return 3;
  if(h.kind==='cog2026'&&annee===2026&&exact)return 4;
  if(exact)return 5;
  if(h.kind==='cog'&&current&&commence)return 6;
  if(actifEn2026&&commence)return 7;
  if(commence)return 8;
  if(code.startsWith(query))return 9;
  return 10;
 }
 function trier(hits,q,annee,periodes){
  if(!Array.isArray(hits))throw Error('Résultats de recherche invalides');
  return [...hits].sort((a,b)=>classe(a,q,annee,periodes)-
                                   classe(b,q,annee,periodes)||
    String(a.label||'').localeCompare(String(b.label||''),'fr',{sensitivity:'base'})||
    String(a.id||a.code||'').localeCompare(String(b.id||b.code||'')));
 }
 return Object.freeze({preparer,etat,classe,trier});
}));
