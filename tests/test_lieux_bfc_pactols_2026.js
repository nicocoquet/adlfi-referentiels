/* L'index public BFC 2026 doit rester strictement distinct des états COG. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.resolve(__dirname,'..');
const loader=require('../docs/assets/lieux-bfc-pactols.js');
const publication=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux-chronologie/pactols-bfc-2026.json'),'utf8'));
const cog=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux-chronologie/cog-bfc.json'),'utf8'));
const result=loader.creer(publication,cog);
assert.equal(result.byCode.size,3614);
assert.equal(result.index.length,3614);
assert.equal(new Set(result.index.map(x=>x.ark)).size,3614);
assert.equal(new Set(result.index.map(x=>x.code)).size,3614);
assert.equal(result.byCode.has('25060'),false,'Val-d’Usiers reste en instruction');
assert.ok(result.index.every(x=>x.zone==='bfc'&&x.kind==='pactols'));
const sample=result.index[0];
assert.ok(sample.champs.includes(sample.ark.toLocaleLowerCase('fr').replace(/[^a-z0-9]+/g,' ')));
assert.ok(sample.champs.includes(sample.code));
assert.equal(cog.alignements_Pactols_COG_valides_2026.length,0);
assert.equal(cog.geometries_historiques.length,0);
assert.throws(()=>loader.creer({...publication,millesime_cog:'2016-01-01'},cog),/incohérent/);
assert.throws(()=>loader.creer({...publication,source_rdf_sha256:'incorrect'},cog),/incohérent/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 ...publication.alignements_Pactols_COG_valides_2026.slice(0,3613),
 publication.alignements_Pactols_COG_valides_2026[0]
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],code_insee:'25060'},
 ...publication.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],uri_insee:'http://id.insee.fr/geo/commune/25060'},
 ...publication.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],statut:'A_INSTRUIRE'},
 ...publication.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
console.log('BFC_3614_INDEX_OK — 3614 ARK uniques, 71 exceptions et indépendance COG');
