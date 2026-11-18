/* PDL lot 02 : 1149 + 45 = 1194 codes, les anciennes COMD jamais promues. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const read=p=>JSON.parse(fs.readFileSync(path.resolve(__dirname,'..',p),'utf8'));
const cog=read('docs/data/lieux-chronologie/cog-pdl.json');
const base=require('../docs/assets/lieux-pdl-pactols.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-2026.json'),cog);
const uuid=require('../docs/assets/lieux-pdl-uuid-resolus.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json'),cog,base);
const lot01=require('../docs/assets/lieux-pdl-communes-nouvelles-lot01.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot01-2026.json'),cog,base,uuid);
const chemille=require('../docs/assets/lieux-pdl-chemille-2026.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-chemille-2026.json'),cog,base,uuid,lot01);
const pub=read('docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot02-2026.json');
const adapter=require('../docs/assets/lieux-pdl-communes-nouvelles-lot02.js');
const lot02=adapter.creer(pub,cog,base,uuid,lot01,chemille);
assert.equal(lot02.byCode.size,45);
assert.equal(lot02.index.length,45);
assert.equal(pub.total_alignements_PDL_2026,1194);
assert.equal(pub.communes_a_instruire,34);
const all=[...base.byCode.values(),...uuid.byCode.values(),...lot01.byCode.values(),
           ...chemille.byCode.values(),...lot02.byCode.values()];
assert.equal(all.length,1194);
assert.equal(new Set(all.map(x=>x.code_insee)).size,1194);
assert.equal(new Set(all.map(x=>x.ark_pactols)).size,1194);
const historical=pub.alignements_Pactols_COG_valides_2026.map(x=>x.ark_ancienne_commune_distinct);
assert.equal(new Set(historical).size,45);
assert.ok(historical.every(x=>!all.some(a=>a.ark_pactols===x)));
assert.ok(!lot02.byCode.has('85292'));
assert.ok(lot02.index.every(x=>x.kind==='pactols'&&x.zone==='pdl'));
assert.throws(()=>adapter.creer({...pub,communes_a_instruire:33},cog,base,uuid,lot01,chemille),/non conformes/);
assert.throws(()=>adapter.creer({...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],
    ark_pactols:pub.alignements_Pactols_COG_valides_2026[0].ark_ancienne_commune_distinct},
 ...pub.alignements_Pactols_COG_valides_2026.slice(1)
 ]},cog,base,uuid,lot01,chemille),/identité non justifiée/);
const ui=fs.readFileSync(path.resolve(__dirname,'../docs/assets/lieux-multiechelon.js'),'utf8');
assert.ok(ui.includes('state.pdlNouvellesLot02.index'));
assert.ok(ui.includes('state.pdlNouvellesLot02?.byCode.get(x.code)'));
assert.ok(ui.includes('Le concept Pactols de l’ancienne commune'));
const manifest=read('docs/data/manifest.json').modules.lieux.pactols_pdl_2026_lot02_communes_nouvelles;
assert.equal(manifest.liens_PDL_2026_au_total,1194);
assert.equal(manifest.exceptions_2026_restantes,34);
console.log('PDL_LOT02_1194_JS_OK — 45 nouvelles identités, 45 anciennes distinctes');
