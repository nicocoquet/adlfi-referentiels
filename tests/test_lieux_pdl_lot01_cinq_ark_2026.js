/* PDL 2026 : cinq communes nouvelles, 1148 identités, 80 exceptions. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const read=p=>JSON.parse(fs.readFileSync(path.join(__dirname,'..',p),'utf8'));
const cog=read('docs/data/lieux-chronologie/cog-pdl.json');
const base=require('../docs/assets/lieux-pdl-pactols.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-2026.json'),cog);
const uuid=require('../docs/assets/lieux-pdl-uuid-resolus.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json'),cog,base);
const pub=read('docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot01-2026.json');
const lot=require('../docs/assets/lieux-pdl-communes-nouvelles-lot01.js');
const item=lot.creer(pub,cog,base,uuid);
const codes=['44005','44021','44029','44087','44163'];
assert.deepEqual([...item.byCode.keys()].sort(),codes);
assert.equal(item.index.length,5);
assert.equal(base.byCode.size,1140);
assert.equal(uuid.byCode.size,3);
const values=[...base.byCode.values(),...uuid.byCode.values(),...item.byCode.values()];
assert.equal(new Set(values.map(x=>x.code_insee)).size,1148);
assert.equal(new Set(values.map(x=>x.ark_pactols)).size,1148);
const past=new Set(pub.alignements_Pactols_COG_valides_2026.map(x=>x.ark_ancienne_commune_distinct));
assert.equal(past.size,5);
assert.ok(values.every(x=>!past.has(x.ark_pactols)));
assert.ok(item.index.every(x=>x.kind==='pactols'&&x.zone==='pdl'));
assert.ok(!item.byCode.has('85292'));
assert.equal(pub.total_alignements_PDL_2026,1148);
assert.equal(pub.communes_a_instruire,80);
const wrong={...pub,communes_a_instruire:79};
assert.throws(()=>lot.creer(wrong,cog,base,uuid),/registre incomplet/);
const wrong2={...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],ark_pactols:pub.alignements_Pactols_COG_valides_2026[0].ark_ancienne_commune_distinct},
 ...pub.alignements_Pactols_COG_valides_2026.slice(1)]};
assert.throws(()=>lot.creer(wrong2,cog,base,uuid),/non prouvée/);
const ui=fs.readFileSync(path.join(__dirname,'../docs/assets/lieux-multiechelon.js'),'utf8');
assert.ok(ui.includes('state.pdlNouvellesLot01.index'));
assert.ok(ui.includes('state.pdlNouvellesLot01?.byCode.get(x.code)'));
assert.ok(ui.includes('L’ancienne commune, devenue commune déléguée'));
const manifest=read('docs/data/manifest.json').modules.lieux.pactols_pdl_2026_lot01_communes_nouvelles;
assert.equal(manifest.liens_PDL_2026_au_total,1148);
assert.equal(manifest.exceptions_2026_restantes,80);
console.log('PDL_LOT01_1148_OK — cinq nouveaux ARK contemporains, aucun ARK ancien promu');