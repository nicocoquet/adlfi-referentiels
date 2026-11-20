'use strict';
// Alias réels du JSON 1.50, URL historiques et cas invalides dans le code publié.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const src=fs.readFileSync(path.join(root,'docs/assets/organismes.js'),'utf8');
const d=JSON.parse(fs.readFileSync(path.join(root,'docs/data/organismes.json'),'utf8'));
const inject=[
 '  globalThis.__aliasTest={',
 '   setup:d=>{records=d.authorities;recordById=new Map(records.map(x=>[x.id,x]));',
 '    relsById=new Map();(d.relations||[]).forEach(x=>{',
 '     if(!relsById.has(x.source))relsById.set(x.source,[]);relsById.get(x.source).push(x)});',
 '    indexIdentityAliases(d.aliases||[]);indexServiceChildren(d.relations||[]);',
 '    indexEvolutions(d.relations||[]);indexFederalAffiliations(d.relations||[]);},',
 '   resolve:resolveIdentityAlias,search:searchText,card:unifiedCard,',
 '   aliases:()=>canonicalByLegacy,visible:()=>baseRecords().length',
 '  };','})();'
].join('\n');
assert.match(src,/\}\)\(\);\s*$/);
const ctx={fetch:()=>({then(){return this;},catch(){return this;}}),URL};
vm.runInNewContext(src.replace(/\}\)\(\);\s*$/,inject),ctx,{filename:'organismes.js'});
const api=ctx.__aliasTest;
api.setup(d);
const by=new Map(d.authorities.map(a=>[a.id,a]));
assert.equal(by.size,934);
assert.equal(api.visible(),682);
assert.equal(api.aliases().size,3);
for(const [old,canonical] of [['SER-0063','ORG-0747'],
 ['ORG-0395','ORG-0300'],['SER-0139','SER-0148']]){
 assert.ok(!by.has(old));
 assert.ok(by.has(canonical));
 assert.equal(api.resolve(old),canonical);
 assert.match(api.search(by.get(canonical)),new RegExp(old.toLowerCase()));
}
assert.match(api.card(by.get('ORG-0747')),/ORG-0747/);
assert.equal(api.resolve('ORG-0120'),'ORG-0120');
assert.equal(api.resolve('ORG-9999'),'ORG-9999');

const invalid={authorities:d.authorities,relations:d.relations,
 aliases:[...d.aliases,
  {from:'ORG-0120',to:'ORG-0747'}, // toujours canonique
  {from:'SER-4000',to:'ORG-9999'}  // cible inconnue
 ]};
api.setup(invalid);
assert.equal(api.resolve('ORG-0120'),'ORG-0120');
assert.equal(api.resolve('SER-4000'),'SER-4000');
assert.match(src,/function details\(id,shouldUpdateHash=true\)\{\s*id=resolveIdentityAlias\(id\);/);
assert.match(src,/if\(recordById.has\(canonical\)\)details\(canonical,canonical!==id\)/);
assert.doesNotMatch(src,/succession.*SER-0063.*ORG-0747/i);
console.log('OK — trois alias réels, recherche, URL, protections et 682 fiches');
