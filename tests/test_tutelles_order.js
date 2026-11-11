'use strict';
// Teste le code réellement exécuté par la page, sans navigateur ni dépendance externe.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../docs/assets/organismes.js'),'utf8');
assert.match(source, /\}\)\(\);\s*$/);
const instrumented = source.replace(/\}\)\(\);\s*$/, `
  globalThis.__test = {
    text: tutelleTextOrder,
    logo: tutelleLogoOrder,
    getTutelles: laboratoryTutelles,
    card: laboratoryCard,
    setData: (relations, authorities) => { relsById = relations; recordById = authorities; }
  };
})();
`);
const context = {
  fetch: () => ({then(){return this;},catch(){return this;}})
};
vm.runInNewContext(instrumented, context, {filename:'organismes.js'});
const api = context.__test;

const authority = (id, label, logo=true) => ({
  id, names:{preferred:label},
  presentation:{media:{logo:logo ? `assets/organismes/${id}-logo.svg` : null}}
});
const ministry = authority('ORG-0023','Ministère de la Culture');
const cnrs = authority('ORG-0004','Centre national de la recherche scientifique');
const university = authority('ORG-0022','Aix Marseille Université');
const blood = authority('ORG-0399','Établissement français du sang',false);
const items=[blood,ministry,university,cnrs];

assert.equal([...items].sort(api.text).map(x=>x.id).join(','),
  'ORG-0022,ORG-0004,ORG-0399,ORG-0023',
  'Texte : ordre alphabétique français, sans priorité institutionnelle');
assert.equal([...items].sort(api.logo).map(x=>x.id).join(','),
  'ORG-0023,ORG-0004,ORG-0022,ORG-0399',
  'Logos : ministère, CNRS, puis les autres par nom');
assert.equal([blood,university,cnrs].sort(api.logo).map(x=>x.id).join(','),
  'ORG-0004,ORG-0022,ORG-0399',
  'Sans ministère, le CNRS est premier');
assert.equal([blood,university].sort(api.logo).map(x=>x.id).join(','),
  'ORG-0022,ORG-0399',
  'Sans organisme prioritaire, classement alphabétique');

const lab = {
  id:'ORG-9999', kind:'ORG', names:{preferred:'Laboratoire de test',acronym:'TEST'},
  classification:{type:'laboratoire'}, identifiers:{lab:'UMR 9999'},
  geography:{cities_label:'Paris',institutional_country_iso2:'FR'},
  website:null, activity:{active:true}, usage:{affiliations_linked:4},
  presentation:{media:{image:null,logo:null}}
};
const authorities = new Map(items.map(x=>[x.id,x]));
const relationships = [
  {source:lab.id,target:blood.id,type:'tutelle',validation:'valide'},
  {source:lab.id,target:ministry.id,type:'tutelle',validation:'validée'},
  {source:lab.id,target:university.id,type:'tutelle',validation:'valide'},
  {source:lab.id,target:cnrs.id,type:'tutelle',validation:'valide'},
  {source:lab.id,target:cnrs.id,type:'tutelle',validation:'a_verifier'},
  {source:lab.id,target:'ORG-0555',type:'tutelle',validation:'valide'},
  {source:lab.id,target:'ORG-0100',type:'autre',validation:'valide'}
];
api.setData(new Map([[lab.id,relationships]]),authorities);
assert.equal(api.getTutelles(lab).map(x=>x.id).join(','),
  'ORG-0022,ORG-0004,ORG-0399,ORG-0023',
  'Les relations validées sont triées et les doublons/relations non établies exclus');
const html=api.card(lab);
const texts=html.match(/<div class="lab-tutelles">([\s\S]*?)<\/div>/)?.[1]||'';
const logos=html.match(/<div class="lab-logo-band"[^>]*>([\s\S]*?)<\/div>/)?.[1]||'';
assert.deepEqual([...texts.matchAll(/<li>([^<]+)<\/li>/g)].map(m=>m[1]).join('|'),
  'Aix Marseille Université|Centre national de la recherche scientifique|Établissement français du sang|Ministère de la Culture');
assert.equal([...logos.matchAll(/title="([^"]+)"/g)].map(m=>m[1]).join('|'),
  'Ministère de la Culture|Centre national de la recherche scientifique|Aix Marseille Université|Établissement français du sang',
  'Le navigateur recherche un JPEG pour chaque tutelle, même sans logo dans le JSON');
assert.match(logos, /assets\/organismes\/ORG-0399\.jpg/,
  'Le logo carré non encore connu du JSON est recherché par son ID');
console.log('OK — classement textuel, logos prioritaires, relations validées et rendu du cartouche');
