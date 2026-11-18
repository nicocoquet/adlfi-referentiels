/* PACA : 832 nouveaux ARK uniques, 103 anciennes décisions inchangées, 11 exceptions. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const loader=require('../docs/assets/lieux-paca-pactols.js');
const pub=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux-chronologie/pactols-paca-2026.json'),'utf8'));
const cog=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux-chronologie/cog-paca.json'),'utf8'));
const pilot=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux.json'),'utf8'));
const loaded=loader.creer(pub,cog);
const existing=new Map(pilot.autorites.map(p=>[p.correspondances[0].code_insee,p.ark_pactols]));
const exceptions='04033 04045 04120 05001 05024 05039 05053 05101 05118 05127 83052'.split(' ');
assert.equal(existing.size,103);
assert.equal(existing.get('05139'),'26678/pcrtSeD2WMEIYA');
assert.equal(loaded.byCode.size,832);
assert.equal(loaded.index.length,832);
assert.equal(new Set(loaded.index.map(x=>x.ark)).size,832);
assert.equal(new Set(loaded.index.map(x=>x.code)).size,832);
assert.equal(new Set([...existing.keys(),...loaded.byCode.keys()]).size,935);
assert.ok([...existing.keys()].every(x=>!loaded.byCode.has(x)));
assert.ok(exceptions.every(code=>!loaded.byCode.has(code)&&!existing.has(code)));
assert.ok(loaded.index.every(x=>x.zone==='paca'&&x.kind==='pactols'));
assert.ok(loaded.byCode.has('04001'));
assert.equal(loaded.byCode.get('04001').ark_pactols,'26678/pcrtzU15KxxGTs');
assert.ok(loaded.index.some(x=>x.ark==='26678/pcrtzU15KxxGTs'&&x.champs.includes('04001')));
assert.equal(cog.alignements_Pactols_COG_valides_2026.length,103);
assert.equal(cog.geometries_historiques.length,0);
assert.throws(()=>loader.creer({...pub,source_rdf_sha256:'incorrect'},cog),/incohérent/);
assert.throws(()=>loader.creer({...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],code_insee:'05139'},
 ...pub.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],code_insee:'04033'},
 ...pub.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],millesime_validation:2016},
 ...pub.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
console.log('PACA_935_INDEX_OK — 103 décisions conservées, 832 nouveaux exactMatch, 11 exceptions, 0 historique');
