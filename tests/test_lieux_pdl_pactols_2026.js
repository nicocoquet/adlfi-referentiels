/* L'index public PDL 2026 doit rester strictement distinct des états COG. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.resolve(__dirname,'..');
const loader=require('../docs/assets/lieux-pdl-pactols.js');
const publication=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux-chronologie/pactols-pdl-2026.json'),'utf8'));
const cog=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux-chronologie/cog-pdl.json'),'utf8'));
const result=loader.creer(publication,cog);
assert.equal(result.byCode.size,1140);
assert.equal(result.index.length,1140);
assert.equal(new Set(result.index.map(x=>x.ark)).size,1140);
assert.equal(new Set(result.index.map(x=>x.code)).size,1140);
for(const code of ['44066','85165','85212','85292'])assert.equal(result.byCode.has(code),false,code+' doit rester en instruction');
assert.ok(result.index.every(x=>x.zone==='pdl'&&x.kind==='pactols'));
const sample=result.index[0];
assert.ok(sample.champs.includes(sample.ark.toLocaleLowerCase('fr').replace(/[^a-z0-9]+/g,' ')));
assert.ok(sample.champs.includes(sample.code));
assert.equal(cog.alignements_Pactols_COG_valides_2026.length,0);
assert.equal(cog.geometries_historiques.length,0);
assert.throws(()=>loader.creer({...publication,millesime_cog:'2016-01-01'},cog),/incohérent/);
assert.throws(()=>loader.creer({...publication,source_rdf_sha256:'incorrect'},cog),/incohérent/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 ...publication.alignements_Pactols_COG_valides_2026.slice(0,1139),
 publication.alignements_Pactols_COG_valides_2026[0]
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],code_insee:'44066'},
 ...publication.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],uri_insee:'http://id.insee.fr/geo/commune/44066'},
 ...publication.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],statut:'A_INSTRUIRE'},
 ...publication.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
console.log('PDL_1140_INDEX_OK — 1140 ARK uniques, 88 exceptions et indépendance COG');
