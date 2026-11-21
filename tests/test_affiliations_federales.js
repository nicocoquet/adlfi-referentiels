'use strict';
// Régression des affiliations fédérales : lot 1.51, données et cas négatifs.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const src=fs.readFileSync(path.join(root,'docs/assets/organismes.js'),'utf8');
const published=JSON.parse(fs.readFileSync(path.join(root,'docs/data/organismes.json'),'utf8'));
assert.match(src,/\}\)\(\);\s*$/);
const instrumented=src.replace(/\}\)\(\);\s*$/, `
 globalThis.__federalTest={
  setup:d=>{
   records=d.authorities;recordById=new Map(records.map(a=>[a.id,a]));
   relsById=new Map();d.relations.forEach(x=>{
    if(!relsById.has(x.source))relsById.set(x.source,[]);
    relsById.get(x.source).push(x);
   });
   indexServiceChildren(d.relations);indexEvolutions(d.relations);
   indexFederalAffiliations(d.relations);
  },
  block:federalAffiliationBlock,parent:parentBlock,card:unifiedCard,
  count:()=>baseRecords().length
 };
})();
`);
const ctx={fetch:()=>({then(){return this;},catch(){return this;}})};
vm.runInNewContext(instrumented,ctx,{filename:'organismes.js'});
const api=ctx.__federalTest;
const by=new Map(published.authorities.map(x=>[x.id,x]));
assert.equal(by.size,934);
assert.equal(published.relations.length,600);
assert.ok(!by.has('SER-0063'),'L’ancien SER a été reclassé en ORG');
api.setup(published);
assert.equal(api.count(),682);
assert.match(api.block(by.get('ORG-0747')),/data-detail="ORG-0120"/,
 'GRASM affilié à FFESSM après migration');
assert.match(api.block(by.get('ORG-0120')),/data-detail="ORG-0747"/,
 'Navigation réciproque de FFESSM vers GRASM');
assert.match(api.block(by.get('ORG-0422')),/data-detail="ORG-0701"/);
assert.match(api.block(by.get('ORG-0701')),/data-detail="ORG-0422"/);
assert.match(api.card(by.get('ORG-0747')),/data-detail="ORG-0120"/);
// Quatre nouvelles affiliations documentées ; les deux premières subsistent.
for(const [member,federation,relation] of [
  ['ORG-0069','ORG-0120','REL-0341'],
  ['ORG-0419','ORG-0120','REL-0342'],
  ['ORG-0521','ORG-0120','REL-0343'],
  ['ORG-0355','ORG-0701','REL-0344']
]){
 const r=published.relations.find(x=>x.id===relation);
 assert.ok(r,relation);
 assert.equal(r.source,member);assert.equal(r.target,federation);
 assert.equal(r.type,'affiliation_federale');assert.equal(r.validation,'valide');
 assert.equal(r.start,null,'Date initiale non inférée');
 assert.equal(r.end,null,'Fin non présumée');
 assert.match(api.block(by.get(member)),new RegExp('data-detail="'+federation+'"'));
 assert.match(api.block(by.get(federation)),new RegExp('data-detail="'+member+'"'));
 assert.doesNotMatch(api.parent(by.get(member)),new RegExp('data-detail="'+federation+'"'),
    'Une affiliation n’est pas une tutelle administrative');
}
assert.equal(published.relations.filter(x=>x.type==='affiliation_federale').length,6);
assert.doesNotMatch(api.block(by.get('ORG-0120')),/SER-0063/);
assert.doesNotMatch(api.parent(by.get('ORG-0747')),/data-detail="ORG-0120"/,
 'Une affiliation fédérale n’est pas une tutelle');

const fixture={
 authorities:['ORG-0120','ORG-0069','ORG-0701','ORG-0422','ORG-0747','SER-0197'].map(id=>by.get(id)),
 relations:[
  {id:'F1',source:'ORG-0069',target:'ORG-0120',type:'affiliation_federale',validation:'valide'},
  {id:'F2',source:'ORG-0422',target:'ORG-0701',type:'affiliation_federale',
   validation:'validée',start:'2022',end:'2023'},
  {id:'F3',source:'ORG-0069',target:'ORG-0701',type:'affiliation_federale',validation:'a_verifier'},
  {id:'F4',source:'ORG-0069',target:'ORG-0701',type:'tutelle',validation:'valide'},
  {id:'F5',source:'ORG-0120',target:'ORG-0120',type:'affiliation_federale',validation:'valide'},
  {id:'F6',source:'ORG-0069',target:'ORG-9999',type:'affiliation_federale',validation:'valide'},
  {id:'F7',source:'ORG-0069',target:'SER-0197',type:'affiliation_federale',validation:'valide'}
 ]
};
api.setup(fixture);
const member=api.block(by.get('ORG-0069'));
assert.match(member,/data-detail="ORG-0120"/);
assert.match(member,/Dates non documentées/);
assert.doesNotMatch(member,/data-detail="ORG-0701"/);
assert.doesNotMatch(member,/data-detail="SER-0197"/);
assert.doesNotMatch(member,/actuelle|actuellement/);
assert.match(api.block(by.get('ORG-0422')),/Période documentée : 2022 – 2023/);
assert.match(api.block(by.get('ORG-0701')),/data-detail="ORG-0422"/);
assert.doesNotMatch(api.block(by.get('ORG-0120')),/data-detail="ORG-0120"/);
assert.match(src,/indexFederalAffiliations\(d\.relations\)/);
assert.match(src,/<h3>Affiliations fédérales<\/h3>/);
console.log('OK — six affiliations fédérales FFESSM/FFS du 1.51, navigation et exclusions');
