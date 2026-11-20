'use strict';
// Tests sur le JavaScript réellement servi par le module Organismes, sans DOM.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'docs/assets/organismes.js'), 'utf8');
const published = JSON.parse(fs.readFileSync(path.join(root, 'docs/data/organismes.json'), 'utf8'));
assert.match(source, /\}\)\(\);\s*$/);
const instrumented = source.replace(/\}\)\(\);\s*$/, `
  globalThis.__federalTest = {
    setup: d => {
      records=d.authorities;
      recordById=new Map(records.map(x=>[x.id,x]));
      relsById=new Map();
      d.relations.forEach(x=>{
        if(!relsById.has(x.source))relsById.set(x.source,[]);
        relsById.get(x.source).push(x);
      });
      indexServiceChildren(d.relations);
      indexFederalAffiliations(d.relations);
    },
    block:federalAffiliationBlock,
    parent:parentBlock,
    card:card,
    count:()=>baseRecords().length
  };
})();
`);
const ctx = {fetch:()=>({then(){return this;},catch(){return this;}})};
vm.runInNewContext(instrumented,ctx,{filename:'organismes.js'});
const api=ctx.__federalTest;
const byId=new Map(published.authorities.map(x=>[x.id,x]));
assert.equal(published.authorities.length,920);
assert.equal(published.relations.length,586);
api.setup(published);
assert.equal(api.count(),670,'Catalogue limité aux autorités publiquement visibles');
assert.equal(api.block(byId.get('ORG-0120')),'',
  'Ne pas afficher d’affiliations fédérales inventées dans le JSON actuel');
assert.equal(api.block(byId.get('SER-0063')),'',
  'RSE-0083 reste un rattachement de service à corriger dans le maître');
const keys=['ORG-0120','ORG-0069','ORG-0701','ORG-0422','SER-0063'];
const fixture={
  authorities:keys.map(k=>byId.get(k)),
  relations:[
    {id:'REL-F1',source:'ORG-0069',target:'ORG-0120',type:'affiliation_federale',validation:'valide'},
    {id:'REL-F2',source:'ORG-0422',target:'ORG-0701',type:'affiliation_federale',
     validation:'validée',start:'2022',end:'2023'},
    {id:'REL-F3',source:'ORG-0069',target:'ORG-0701',type:'affiliation_federale',
     validation:'a_verifier'},
    {id:'REL-F4',source:'SER-0063',target:'ORG-0120',type:'rattachement_service',
     validation:'valide'},
    {id:'REL-F5',source:'ORG-0069',target:'ORG-0701',type:'tutelle',
     validation:'valide'},
    {id:'REL-F6',source:'ORG-0120',target:'ORG-0120',type:'affiliation_federale',
     validation:'valide'},
    {id:'REL-F7',source:'ORG-0069',target:'ORG-9999',type:'affiliation_federale',
     validation:'valide'},
    {id:'REL-F8',source:'ORG-0069',target:'SER-0063',type:'affiliation_federale',
     validation:'valide'}
  ]
};
api.setup(fixture);
const casavo=api.block(byId.get('ORG-0069'),false);
assert.match(casavo,/Affiliation fédérale/);
assert.match(casavo,/Affilié à/);
assert.match(casavo,/data-detail="ORG-0120"/);
assert.doesNotMatch(casavo,/data-detail="ORG-0701"/,
  'Une relation candidate ou une tutelle ne vaut pas affiliation fédérale');
assert.doesNotMatch(casavo,/data-detail="SER-0063"/,
  'La cible fédérale doit être une ORG');
assert.doesNotMatch(casavo,/actuelle|actuellement/,
  'Sans dates documentées, ne pas affirmer une affiliation actuelle');
assert.match(casavo,/Dates non documentées/);
const ffessm=api.block(byId.get('ORG-0120'),false);
assert.match(ffessm,/Organisations affiliées/);
assert.match(ffessm,/data-detail="ORG-0069"/);
assert.doesNotMatch(ffessm,/data-detail="ORG-0120"/,'Pas de relation réflexive');
assert.doesNotMatch(ffessm,/data-detail="SER-0063"/,
  'Un rattachement_service incorrect ne doit pas être interprété comme fédéral');
const cds=api.block(byId.get('ORG-0422'),false);
assert.match(cds,/Période documentée : 2022 – 2023/);
assert.match(cds,/data-detail="ORG-0701"/);
assert.match(api.block(byId.get('ORG-0701'),false),/data-detail="ORG-0422"/,
  'Navigation réciproque depuis la fédération');
assert.match(api.card(byId.get('ORG-0422')),/data-detail="ORG-0701"/,
  'La carte affiche les affiliations à côté des relations existantes');
assert.equal(api.block(byId.get('SER-0063'),false),'');
assert.match(api.parent(byId.get('SER-0063')), /data-detail="ORG-0120"/,
  'La migration du rattachement SER est réservée au maître : pas de changement opportuniste');
assert.match(source, /indexFederalAffiliations\(d\.relations\)/);
assert.match(source, /<h3>Affiliations fédérales<\/h3>/);
assert.match(source, /x\.type!=='affiliation_federale'/,
  'Les affiliations fédérales sont exclues du bloc générique des rattachements');
console.log('OK — affiliations fédérales réciproques, dates, validation, types distincts, 920/586 conservés');
