'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const root=require('node:path').resolve(__dirname,'..');
const lib=require('../docs/assets/lieux-drom-contours.js');
const index=require('../docs/assets/lieux-outremer-search.js');
const doc=JSON.parse(fs.readFileSync(root+'/docs/data/lieux-outremer/recherche-2026.json','utf8'));
const entries=new Map(index.creerIndex(doc).map(x=>[x.id,x]));
const fc=JSON.parse(fs.readFileSync(root+'/docs/data/lieux-outremer/contours-communes-drom-2026.geojson','utf8'));
const features=lib.verifier(fc,entries);
assert.equal(features.length,129);
const counts={};for(const f of features){
 const pre=f.properties.code.slice(0,3);
 counts[pre]=(counts[pre]||0)+1;
 assert.equal(f.properties.ark_pactols,null);
 assert.equal(f.properties.ref_cog,'DROM:COM:'+f.properties.code);
}
assert.deepEqual(counts,{'971':32,'972':34,'973':22,'974':24,'976':17});
assert.ok(!features.some(f=>f.properties.code.startsWith('987')||f.properties.code.startsWith('988')));
assert.throws(()=>lib.verifier({...fc,provenance:{...fc.provenance,cog_ref:'2015-01-01'}},entries),/incompatible/);
const bad=JSON.parse(JSON.stringify(fc));
bad.features[0].properties.ark_pactols='26678/pcrtInterdit';
assert.throws(()=>lib.verifier(bad,entries),/invalide/);
const duplicate=JSON.parse(JSON.stringify(fc));
duplicate.features[1]=duplicate.features[0];
assert.throws(()=>lib.verifier(duplicate,entries),/invalide/);
console.log('DROM_129_INDEX_OK — 129 géométries sourcées, 0 ARK inféré, 0 restitution historique');
