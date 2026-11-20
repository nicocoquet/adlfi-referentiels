'use strict';
// Recette sur jeu synthétique : le lien direct CRP2A -> Archéosciences Bordeaux
// n'est PAS encore inscrit dans le maître XLSX.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../docs/assets/organismes.js'),'utf8');
assert.match(source,/\}\)\(\);\s*$/);
const injection=[
  '  globalThis.__testHistorique={',
  '    setup: d=>{',
  '      records=d.authorities;',
  '      recordById=new Map(records.map(x=>[x.id,x]));',
  '      relsById=new Map();',
  '      for(const rel of d.relations){',
  '        if(!relsById.has(rel.source))relsById.set(rel.source,[]);',
  '        relsById.get(rel.source).push(rel);',
  '      }',
  '      indexEvolutions(d.relations);',
  '    },',
  '    entries:evolutionEntries, block:evolutionBlock,',
  '    tutelles:laboratoryTutelles, parent:parentBlock,',
  '    currentAuthority,currentRelation,currentRattachement',
  '  };',
  '})();'
].join('\n');
const instrumented=source.replace(/\}\)\(\);\s*$/,injection);
const context={fetch:()=>({then(){return this;},catch(){return this;}})};
vm.runInNewContext(instrumented,context,{filename:'organismes.js'});
const api=context.__testHistorique;
function authority(id,name,{kind='ORG',active=true,start=null,end=null}={}){
  return {id,kind,names:{preferred:name,acronym:id},
    presentation:{visible:true,media:{logo:null,image:null}},
    identifiers:{lab:kind==='ORG'?'UMR 9999':null},
    classification:{type:kind==='ORG'?'laboratoire':'service_recherche'},
    activity:{active,start,end}};
}
const utah=authority('ORG-0736','UTAH',{active:false,end:'2006-12-31'});
const crppm=authority('ORG-0737','CRPPM',{active:false,end:'2006-12-31'});
const traces=authority('ORG-0151','TRACES',{start:'2007'});
const crp2a=authority('SER-0196','CRP2A',{kind:'SER',active:false,end:'2021-12-31'});
const bordeaux=authority('ORG-0537','Archéosciences Bordeaux',{start:'2022'});
const chrono=authority('ORG-0746','Chrono-écologie',{active:false,end:'2007-12-31'});
const cnrs=authority('ORG-0004','CNRS',{start:'1939'});
const oldUniv=authority('ORG-0233','Ancienne université',{active:false,end:'2024-12-31'});
const futureUniv=authority('ORG-9998','Université future',{start:'2028-01-01'});
const newLab=authority('ORG-0397','Chrono-environnement',{start:'2008-01-01'});
const relations=[
 {id:'REL-0314',source:utah.id,target:traces.id,type:'fusion_constitutive',start:'2007-01-01',validation:'valide'},
 {id:'REL-0315',source:crppm.id,target:traces.id,type:'fusion_constitutive',start:'2007-01-01',validation:'valide'},
 {id:'RSE-TEST',source:crp2a.id,target:bordeaux.id,type:'filiation_partielle',start:'2022-01-01',validation:'valide'},
 {id:'REL-CHRONO',source:chrono.id,target:cnrs.id,type:'tutelle',validation:'valide'},
 {id:'REL-OLD',source:newLab.id,target:oldUniv.id,type:'tutelle',start:'2008',validation:'valide'},
 {id:'REL-FUTURE',source:newLab.id,target:futureUniv.id,type:'tutelle',start:'2028',validation:'valide'},
 {id:'REL-NEW',source:newLab.id,target:cnrs.id,type:'tutelle',start:'2008',validation:'valide'},
 {id:'REL-HIST-END',source:newLab.id,target:cnrs.id,type:'tutelle',end:'2020',validation:'valide'},
 {id:'REL-UNVALIDATED',source:crp2a.id,target:traces.id,type:'fusion_constitutive',validation:'a_verifier'}
];
api.setup({authorities:[utah,crppm,traces,crp2a,bordeaux,chrono,cnrs,oldUniv,futureUniv,newLab],
  relations});
const origins=api.entries(traces);
assert.equal(origins.length,2,'TRACES a deux unités fondatrices');
assert.ok(origins.every(e=>e.direction==='predecessor'&&e.relation.type==='fusion_constitutive'));
assert.match(api.block(traces,false),/Origines et filiations antérieures/);
assert.match(api.block(traces,false),/Fusion constitutive · 1er janvier 2007/);
assert.match(api.block(traces,false),/data-detail="ORG-0736"/);
assert.match(api.block(traces,false),/data-detail="ORG-0737"/);
assert.match(api.block(utah,false),/Évolutions et filiations ultérieures/);
assert.match(api.block(utah,false),/data-detail="ORG-0151"/);
assert.ok(api.entries(crp2a).some(e=>e.partner.id===bordeaux.id&&e.direction==='successor'));
assert.ok(api.entries(bordeaux).some(e=>e.partner.id===crp2a.id&&e.direction==='predecessor'));
assert.match(api.block(bordeaux,false),/Filiation partielle/);
assert.doesNotMatch(api.block(crp2a,false),/data-detail="ORG-0151"/,
  'Aucune filiation non validée ne doit devenir navigable');
assert.equal(api.tutelles(chrono,'2026-11-20').length,0,
  'Un laboratoire inactif ne présente pas de tutelles actuelles');
assert.match(api.parent(chrono),/Rattachement historique ou non actuel/);
assert.deepEqual([...api.tutelles(newLab,'2026-11-20').map(e=>e.id)],['ORG-0004'],
  'Tutelles anciennes, futures et éteintes exclues du cartouche actuel');
assert.equal(api.currentAuthority(futureUniv,'2026-11-20'),false);
const unknown=authority('ORG-0900','Statut incertain');
unknown.activity.active=null;
assert.equal(api.currentAuthority(unknown,'2026-11-20'),false,
  'Activité inconnue : ne pas présumer une tutelle actuelle');
assert.equal(api.currentRelation({start:'2027'},'2026-11-20'),false);
assert.equal(api.currentRelation({end:'2020'},'2026-11-20'),false);
assert.equal(api.currentRelation({start:'2026-01',end:'2026-12'},'2026-11-20'),true);
console.log('OK — fusions multiples, filiation SER→ORG, réciprocité et tutelles temporelles');
