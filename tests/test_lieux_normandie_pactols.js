'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=path.join(__dirname,'../docs/data/lieux-chronologie');
const read=name=>JSON.parse(fs.readFileSync(path.join(base,name),'utf8'));
const api=require('../docs/assets/lieux-normandie-pactols.js');

const cog=read('cog-normandie.json'),l1=read('pactols-normandie-lot01-2026.json');
const l2=read('pactols-normandie-lot02-2026.json');
const geo=read('contours-2026-normandie.geojson');
const result=api.creer(l1,l2,cog);
assert.equal(result.byCode.size,16);
assert.equal(result.index.length,16);
assert.equal(geo.type,'FeatureCollection');
assert.equal(geo.features.length,2644);
assert.equal(geo.provenance.millesime,2026);
const codes=new Set();
for(const f of geo.features){
 assert.equal(f.properties.millesime,2026);
 assert.equal(f.properties.ark_pactols_valide_2026,null,
  'Aucune identification Pactols ne doit être inférée des géométries');
 assert(!codes.has(f.properties.code));
 codes.add(f.properties.code);
}
assert.equal(codes.size,2644);
for(const [code,a] of result.byCode){
 assert(codes.has(code),'Contournement du COG géométrique : '+code);
 assert.equal(a.millesime_validation,2026);
 assert.notEqual(a.ark_pactols,a.ancien_ark_non_promu);
 assert(result.index.some(i=>i.kind==='pactols'&&i.zone==='normandie'&&
       i.code===code&&i.ark===a.ark_pactols&&
       i.champs.includes(a.ark_pactols.toLowerCase().replace('/',' '))));
}
for(const code of ['50412','14342','27112','50546']){
 assert(!result.byCode.has(code),'Une exception a été publiée : '+code);
}
assert.equal(result.byCode.get('50129').ark_pactols,'26678/pcrt4Ft3j507NA');
assert.equal(result.byCode.get('14654').ark_pactols,'26678/pcrtf4lulrxUo6');

function rejects(modify,pattern){
 const a=JSON.parse(JSON.stringify(l1)),b=JSON.parse(JSON.stringify(l2));
 modify(a,b);
 assert.throws(()=>api.creer(a,b,cog),pattern);
}
rejects(a=>a.alignements_Pactols_COG_valides_2026[0].ark_pactols=
 a.alignements_Pactols_COG_valides_2026[0].ancien_ark_non_promu,/correspondance/);
rejects((a,b)=>b.exceptions_non_validees[0].alignement_publie=true,/réserves/);
rejects((a,b)=>b.nombre_communes=8,/registres/);
rejects(a=>a.alignements_Pactols_COG_valides_2026[0].millesime_validation=2019,/correspondance/);
rejects(a=>a.alignements_Pactols_COG_valides_2026[0].code_insee='50412',/correspondance/);
const historical=JSON.parse(JSON.stringify(cog));
historical.geometries_historiques=[{inventee:true}];
assert.throws(()=>api.creer(l1,l2,historical),/incohérents/);

console.log('NORMANDIE_2026_INDEX_OK — 2644 communes, 16 ARK vérifiés, 4 réserves, zéro rétroprojection');
