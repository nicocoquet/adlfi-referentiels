/* PACA 2026 : 103 + 832 + 3 + 7 = 945 identités, Abriès en réserve. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const adapter=require('../docs/assets/lieux-paca-communes-nouvelles.js');
const core=require('../docs/assets/lieux-paca-pactols.js');
const rename=require('../docs/assets/lieux-paca-renommages.js');
const cog=read('docs/data/lieux-chronologie/cog-paca.json');
const pilot=read('docs/data/lieux.json');
const complement=core.creer(read('docs/data/lieux-chronologie/pactols-paca-2026.json'),cog);
const previous=rename.creer(read('docs/data/lieux-chronologie/pactols-paca-renommages-2026.json'),cog,pilot,complement);
const pub=read('docs/data/lieux-chronologie/pactols-paca-communes-nouvelles-2026.json');
const loaded=adapter.creer(pub,cog,pilot,complement,previous);
const oldCodes=new Set(pilot.autorites.map(x=>x.correspondances[0].code_insee));
for(const a of [...complement.byCode.values(),...previous.byCode.values()])oldCodes.add(a.code_insee);
assert.equal(oldCodes.size,938);
assert.equal(previous.byCode.get('04045').ark_pactols,'26678/pcrtHxveTzUMik');
assert.equal(loaded.byCode.size,7);
assert.equal(loaded.index.length,7);
assert.equal(new Set([...oldCodes,...loaded.byCode.keys()]).size,945);
assert.equal(pub.communes_a_instruire,1);
assert.deepEqual(pub.exceptions_restantes,['05001']);
assert.ok(!loaded.byCode.has('05001')&&!loaded.byCode.has('04045'));
assert.ok(loaded.index.every(x=>x.zone==='paca'&&x.kind==='pactols'));
assert.equal(pub.ARK_anciens_concepts_non_promus.length,8);
assert.ok(pub.ARK_anciens_concepts_non_promus.includes('26678/pcrtGQ7nGPZN7K'));
const newARKs=new Set(loaded.index.map(x=>x.ark));
assert.ok(pub.ARK_anciens_concepts_non_promus.every(x=>!newARKs.has(x)));
const wrong={...pub,exceptions_restantes:['04045','05001']};
assert.throws(()=>adapter.creer(wrong,cog,pilot,complement,previous),/non conforme/);
const wrong2={...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],ark_pactols:'26678/pcrtC1Vi7jqzBS'},
 ...pub.alignements_Pactols_COG_valides_2026.slice(1)
]};
assert.throws(()=>adapter.creer(wrong2,cog,pilot,complement,previous),/insuffisante/);
const multi=fs.readFileSync(path.join(ROOT,'docs/assets/lieux-multiechelon.js'),'utf8');
assert.ok(multi.includes('state.pacaNouvelles.index'));
console.log('PACA_945_INDEX_OK — 945 identités, 8 anciens ARK exclus, Abriès seule exception');
