/* PDL 2026 : 1140 + 3 URI INSEE UUID prouvées, sans Rives-du-Fougerais. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const cog=read('docs/data/lieux-chronologie/cog-pdl.json');
const base=require('../docs/assets/lieux-pdl-pactols.js').creer(
  read('docs/data/lieux-chronologie/pactols-pdl-2026.json'),cog);
const pub=read('docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json');
const adapter=require('../docs/assets/lieux-pdl-uuid-resolus.js');
const v=adapter.creer(pub,cog,base);
assert.equal(base.byCode.size,1140);
assert.equal(v.byCode.size,3);
assert.deepEqual([...v.byCode.keys()].sort(),['44066','85165','85212']);
assert.equal(new Set([...base.byCode.keys(),...v.byCode.keys()]).size,1143);
assert.equal(new Set([...base.byCode.values(),...v.byCode.values()].map(x=>x.ark_pactols)).size,1143);
assert.equal(pub.communes_a_instruire,85);
assert.equal(pub.cas_Rives_du_Fougerais_exclu,'85292');
assert.ok(!v.byCode.has('85292')&&!base.byCode.has('85292'));
assert.ok(v.index.every(x=>x.zone==='pdl'&&x.kind==='pactols'));
assert.equal(v.byCode.get('44066').ark_pactols,'26678/pcrt99dzcmxdhR');
assert.equal(v.byCode.get('85165').ark_pactols,'26678/pcrtsn4IGEserS');
assert.equal(v.byCode.get('85212').ark_pactols,'26678/pcrt3AUfSktjqj');
const wrong={...pub,total_alignements_PDL_2026:1144};
assert.throws(()=>adapter.creer(wrong,cog,base),/registre incomplet/);
const wrong2={...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],
    uri_insee_courante_resolue:'http://id.insee.fr/geo/commune/85041'},
 ...pub.alignements_Pactols_COG_valides_2026.slice(1)
]};
assert.throws(()=>adapter.creer(wrong2,cog,base),/insuffisamment prouvée/);
const ui=fs.readFileSync(path.join(ROOT,'docs/assets/lieux-multiechelon.js'),'utf8');
assert.ok(ui.includes('state.pdlUUIDResolus.index'));
assert.ok(ui.includes('geo:codeINSEE et owl:sameAs'));
console.log('PDL_1143_UUID_INDEX_OK — 1143 identités, 85 exceptions, preuve RDF INSEE et 0 rétroprojection');
