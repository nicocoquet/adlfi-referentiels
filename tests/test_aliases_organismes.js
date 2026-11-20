'use strict';
// Contrôle du JS réel : anciens IDs résolus sans inventer une succession.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'docs/assets/organismes.js'),'utf8');
const published=JSON.parse(fs.readFileSync(path.join(root,'docs/data/organismes.json'),'utf8'));
const inject=[
  '  globalThis.__aliasTest={',
  '    setup:d=>{records=d.authorities;recordById=new Map(records.map(x=>[x.id,x]));',
  '      relsById=new Map();(d.relations||[]).forEach(x=>{',
  '        if(!relsById.has(x.source))relsById.set(x.source,[]);relsById.get(x.source).push(x)});',
  '      indexIdentityAliases(d.aliases||[]);',
  '      indexServiceChildren(d.relations||[]);indexEvolutions(d.relations||[]);',
  '      indexFederalAffiliations(d.relations||[]);},',
  '    resolve:resolveIdentityAlias,search:searchText,card:card,',
  '    aliases:()=>canonicalByLegacy,visible:()=>baseRecords().length',
  '  };',
  '})();'
].join('\n');
assert.match(source,/\}\)\(\);\s*$/);
const ctx={fetch:()=>({then(){return this;},catch(){return this;}}),URL};
vm.runInNewContext(source.replace(/\}\)\(\);\s*$/,inject),ctx,{filename:'organismes.js'});
const api=ctx.__aliasTest;
api.setup(published);
assert.equal(published.authorities.length,920);
assert.equal(api.visible(),670);
assert.equal(api.resolve('SER-0063'),'SER-0063',
  'Tant que le JSON publié inclut le SER, ne pas fabriquer un reclassement');
assert.equal(api.aliases().size,0);

const original=published.authorities.find(x=>x.id==='SER-0063');
assert.ok(original);
const migrated={
  ...original,
  id:'ORG-0747',kind:'ORG',
  classification:{...original.classification,type:'association'},
  presentation:{...original.presentation,media:{image:null,logo:null}}
};
const future={
  authorities:[...published.authorities.filter(x=>x.id!=='SER-0063'),migrated],
  aliases:[
    {from:'SER-0063',to:'ORG-0747'},
    {from:'ORG-0395',to:'ORG-0300'},
    {from:'SER-0139',to:'SER-0148'},
    {from:'ORG-0120',to:'ORG-0747'}, // source encore active : exclure
    {from:'SER-4000',to:'ORG-9999'}  // cible inexistante : exclure
  ]
};
api.setup(future);
assert.equal(api.visible(),670,'La migration 1 SER → 1 ORG conserve les cartes');
assert.equal(api.resolve('SER-0063'),'ORG-0747',
  'La reclassification transversale SER/ORG est résolue');
assert.equal(api.resolve('ORG-0395'),'ORG-0300');
assert.equal(api.resolve('SER-0139'),'SER-0148');
assert.equal(api.resolve('ORG-0120'),'ORG-0120',
  'Une autorité actuellement publiée ne peut jamais être détournée par un alias');
assert.equal(api.resolve('SER-4000'),'SER-4000');
assert.match(api.search(migrated),/ser-0063/,
  'Une recherche de l’ancien identifiant retrouve la nouvelle autorité');
assert.match(api.card(migrated),/ORG-0747/);
assert.match(source,/function details\(id,shouldUpdateHash=true\)\{\s*id=resolveIdentityAlias\(id\);/,
  'Les clics vers des identifiants historiques doivent résoudre vers le canonique');
assert.match(source,/if\(recordById.has\(canonical\)\)details\(canonical,canonical!==id\)/,
  'Le fragment URL doit être corrigé au chargement initial');
assert.doesNotMatch(source,/succession.*SER-0063.*ORG-0747/i,
  'La correction de classification ne doit pas créer de succession fictive');
console.log('OK — alias de migration GRASM, deux fusions historiques, URL, recherche, 670 cartes');
