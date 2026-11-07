'use strict';
// Test du code réel de rendu sans navigateur ni dépendances tierces.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'docs/assets/organismes.js'),'utf8');
const dataset=JSON.parse(fs.readFileSync(path.join(root,'docs/data/organismes.json'),'utf8'));
assert.match(source,/\}\)\(\);\s*$/);
const script=source.replace(/\}\)\(\);\s*$/, `
  globalThis.__test={
    setup: d=>{
      records=d.authorities;
      recordById=new Map(records.map(x=>[x.id,x]));
      indexEvolutions(d.relations);
    },
    entries:evolutionEntries,
    block:evolutionBlock,
    date:evolutionDate
  };
})();
`);
const context={fetch:()=>({then(){return this;},catch(){return this;}})};
vm.runInNewContext(script,context,{filename:'organismes.js'});
const api=context.__test;
api.setup(dataset);
const byId=new Map(dataset.authorities.map(x=>[x.id,x]));
const halma=byId.get('ORG-0079'), hartis=byId.get('ORG-0601');
const oldSra=byId.get('SER-0022'), newSra=byId.get('SER-0009');
assert.ok(halma&&hartis&&oldSra&&newSra);
const halmaEntries=api.entries(halma);
assert.ok(halmaEntries.some(x=>x.partner.id===hartis.id&&x.direction==='successor'));
const hartisEntries=api.entries(hartis);
assert.ok(hartisEntries.some(x=>x.partner.id===halma.id&&x.direction==='predecessor'));
const halmaHtml=api.block(halma,true);
assert.match(halmaHtml,/Structure ayant succédé à ce laboratoire/);
assert.match(halmaHtml,/data-detail="ORG-0601"/);
assert.match(halmaHtml,/Succession institutionnelle · 1er janvier 2026/);
assert.ok(halmaHtml.includes('<strong title="'+hartis.names.preferred+'">'+hartis.names.preferred+'</strong>'),
  'Le nom normalisé de HARTIS est affiché, non son seul acronyme');
assert.ok(halmaHtml.includes('ORG-0601 · HARTIS · UMR 9028'),
  'L’acronyme et le numéro d’unité figurent dans les métadonnées');
const hartisHtml=api.block(hartis,false);
assert.match(hartisHtml,/Structures? antérieures?/);
assert.match(hartisHtml,/data-detail="ORG-0079"/);
assert.match(hartisHtml,/autorités distinctes/);
const oldSraHtml=api.block(oldSra,true);
assert.match(oldSraHtml,/Structure ayant succédé à ce service/);
assert.match(oldSraHtml,/data-detail="SER-0009"/);
const newSraHtml=api.block(newSra,false);
assert.match(newSraHtml,/Structures antérieures/);
assert.match(newSraHtml,/data-detail="SER-0022"/);
assert.match(newSraHtml,/data-detail="SER-0023"/);
assert.equal(api.date('1991'),'1991');
assert.equal(api.date('2016-01-01'),'1er janvier 2016');
// Les relations non validées et les autres types sont exclus du graphe de succession.
const fakeA={id:'ORG-9001',names:{preferred:'A',acronym:'A'},presentation:{visible:true,media:{logo:null,image:null}},identifiers:{},classification:{type:'laboratoire'},kind:'ORG'};
const fakeB={id:'ORG-9002',names:{preferred:'B',acronym:'B'},presentation:{visible:true,media:{logo:null,image:null}},identifiers:{},classification:{type:'laboratoire'},kind:'ORG'};
api.setup({authorities:[fakeA,fakeB],relations:[
  {id:'REL-FAUX',source:fakeA.id,target:fakeB.id,type:'succession_institutionnelle',validation:'a_verifier'},
  {id:'REL-TUTELLE',source:fakeA.id,target:fakeB.id,type:'tutelle',validation:'valide'}
]});
assert.equal(api.entries(fakeA).length,0);
assert.equal(api.entries(fakeB).length,0);
assert.equal(api.block(fakeA,true),'');
console.log('OK — relations réciproques ORG/SER, dates, liens, exclusions et groupes multiples');
