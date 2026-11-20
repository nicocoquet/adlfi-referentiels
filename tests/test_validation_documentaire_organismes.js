'use strict';
// Contrôle de la présence explicite du statut sans modifier l'index existant.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const src=fs.readFileSync(path.join(root,'docs/assets/organismes.js'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(root,'docs/data/organismes.json'),'utf8'));
const inject=[
  '  globalThis.__validationTest={',
  '    setup:d=>{records=d.authorities;recordById=new Map(records.map(x=>[x.id,x]));',
  '      relsById=new Map();d.relations.forEach(x=>{',
  '      if(!relsById.has(x.source))relsById.set(x.source,[]);relsById.get(x.source).push(x)});',
  '      indexIdentityAliases(d.aliases||[]);indexServiceChildren(d.relations);',
  '      indexFederalAffiliations(d.relations);indexEvolutions(d.relations);},',
  '    card:unifiedCard,count:()=>baseRecords().length',
  '  };',
  '})();'
].join('\n');
assert.match(src,/\}\)\(\);\s*$/);
const ctx={fetch:()=>({then(){return this;},catch(){return this;}}),URL};
vm.runInNewContext(src.replace(/\}\)\(\);\s*$/,inject),ctx,{filename:'organismes.js'});
const api=ctx.__validationTest;
api.setup(data);
assert.equal(api.count(),682,'Catalogue 1.50 avec qualification documentaire explicite');
const prototype=data.authorities.find(x=>x.id==='ORG-0747');
assert.ok(prototype);
const draft={...prototype,validation:{status:'a_verifier',established:false}};
const established={...prototype,validation:{status:'valide',established:true}};
assert.match(api.card(draft),/class="editorial-state">À vérifier<\/span>/);
assert.doesNotMatch(api.card(established),/class="editorial-state">À vérifier<\/span>/);
const older={...prototype};delete older.validation;
assert.doesNotMatch(api.card(older),/class="editorial-state">À vérifier<\/span>/,
  'Rétrocompatibilité : ancien JSON sans validation explicite');
assert.match(src,/Qualification documentaire à vérifier : certains attributs/);
assert.match(src,/Validation documentaire/);
assert.match(src,/Sa présence au catalogue ne signifie pas/);
console.log('OK — statut documentaire explicite, visibilité inchangée, rétrocompatibilité');
