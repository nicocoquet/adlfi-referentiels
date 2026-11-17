/* Contrat source du référentiel public Corse 2026. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const loader=require('../docs/assets/lieux-corse-pactols.js');
const publication=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux-chronologie/pactols-corse-2026.json'),'utf8'));
const cog=JSON.parse(fs.readFileSync(path.join(root,'docs/data/lieux-chronologie/cog-corse.json'),'utf8'));
const result=loader.creer(publication,cog);
assert.equal(result.byCode.size,360);
assert.equal(result.index.length,360);
assert.equal(new Set(result.index.map(x=>x.ark)).size,360);
assert.equal(result.byCode.get('2A001').ark_pactols,'26678/pcrtgs2LLPYow2');
assert.equal(result.byCode.get('2B366').ark_pactols,'26678/pcrtfdIIiZUYU6');
assert.ok(result.index.some(x=>x.code==='2A001'&&x.champs.includes('afa')&&
 x.champs.includes('26678 pcrtgs2llpyow2')));
assert.equal(cog.alignements_Pactols_COG_valides_2026.length,0);
assert.equal(cog.geometries_historiques.length,0);
assert.throws(()=>loader.creer({...publication,millesime_cog:'1976-01-01'},cog),/incohérent/);
assert.throws(()=>loader.creer({...publication,source_rdf_sha256:'incorrect'},cog),/incohérent/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 ...publication.alignements_Pactols_COG_valides_2026.slice(0,359),
 publication.alignements_Pactols_COG_valides_2026[0]
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],uri_insee:'http://id.insee.fr/geo/commune/20001'},
 ...publication.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
assert.throws(()=>loader.creer({...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],statut:'candidat'},
 ...publication.alignements_Pactols_COG_valides_2026.slice(1)
]},cog),/non justifié/);
console.log('CORSE_360_PACTOLS_INDEX_OK : codes, ARK, millésime, provenance et non-rétroprojection');
