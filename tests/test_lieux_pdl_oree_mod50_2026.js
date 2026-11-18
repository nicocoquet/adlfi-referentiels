/* Orée d'Anjou 2026 : 1194+1, preuve RDF ancien code et COG MOD50. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
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
const lot02=require('../docs/assets/lieux-pdl-communes-nouvelles-lot02.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot02-2026.json'),
 cog,base,uuid,lot01,chemille);
const p=read('docs/data/lieux-chronologie/pactols-pdl-oree-anjou-mod50-2026.json');
const adapter=require('../docs/assets/lieux-pdl-oree-mod50.js');
const next=adapter.creer(p,cog,base,uuid,lot01,chemille,lot02);
assert.deepEqual([...next.byCode.keys()],['49126']);
assert.equal(next.index.length,1);
assert.equal(next.index[0].ark,'26678/pcrtS50omR9Tb5');
const all=[...base.byCode.values(),...uuid.byCode.values(),...lot01.byCode.values(),
           ...chemille.byCode.values(),...lot02.byCode.values(),...next.byCode.values()];
assert.equal(all.length,1195);
assert.equal(new Set(all.map(x=>x.code_insee)).size,1195);
assert.equal(new Set(all.map(x=>x.ark_pactols)).size,1195);
assert.ok(!all.some(x=>['26678/pcrtlzVsRTHJSP','26678/pcrtJmNskrfHiK'].includes(x.ark_pactols)));
assert.ok(!next.byCode.has('49080'));
assert.throws(()=>adapter.creer({...p,communes_a_instruire:32},cog,base,uuid,lot01,chemille,lot02),/incomplet/);
assert.throws(()=>adapter.creer({...p,alignements_Pactols_COG_valides_2026:[
 {...p.alignements_Pactols_COG_valides_2026[0],code_COG_avant:'49126'}
 ]},cog,base,uuid,lot01,chemille,lot02),/non validées/);
const ui=fs.readFileSync(path.resolve(__dirname,'../docs/assets/lieux-multiechelon.js'),'utf8');
assert.ok(ui.includes('state.pdlOreeMod50.index'));
assert.ok(ui.includes('state.pdlOreeMod50?.byCode.get(x.code)'));
assert.ok(ui.includes('transfert de chef-lieu (MOD50)'));
const manifest=read('docs/data/manifest.json').modules.lieux.pactols_pdl_2026_oree_mod50;
assert.equal(manifest.liens_PDL_2026_au_total,1195);
assert.equal(manifest.exceptions_2026_restantes,33);
console.log('PDL_OREE_MOD50_JS_OK — ancien code 49069, actuel 49126');
