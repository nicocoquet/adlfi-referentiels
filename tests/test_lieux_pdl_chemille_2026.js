/* Chemillé 2026 : 1149/1228 et trois ARK temporellement distincts. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const read=p=>JSON.parse(fs.readFileSync(path.resolve(__dirname,'..',p),'utf8'));
const cog=read('docs/data/lieux-chronologie/cog-pdl.json');
const base=require('../docs/assets/lieux-pdl-pactols.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-2026.json'),cog);
const uuid=require('../docs/assets/lieux-pdl-uuid-resolus.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-uuid-resolus-2026.json'),cog,base);
const lot01=require('../docs/assets/lieux-pdl-communes-nouvelles-lot01.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot01-2026.json'),cog,base,uuid);
const pub=read('docs/data/lieux-chronologie/pactols-pdl-chemille-2026.json');
const adapter=require('../docs/assets/lieux-pdl-chemille-2026.js');
const next=adapter.creer(pub,cog,base,uuid,lot01);
assert.deepEqual([...next.byCode.keys()],['49092']);
assert.equal(next.index.length,1);
assert.equal(next.index[0].ark,'26678/pcrtzDf0WnnRyr');
const all=[...base.byCode.values(),...uuid.byCode.values(),...lot01.byCode.values(),...next.byCode.values()];
assert.equal(all.length,1149);
assert.equal(new Set(all.map(x=>x.code_insee)).size,1149);
assert.equal(new Set(all.map(x=>x.ark_pactols)).size,1149);
assert.ok(!all.some(x=>['26678/pcrtL5GRFXn3Zs','26678/pcrtWU8rdgPSSH'].includes(x.ark_pactols)));
assert.ok(!next.byCode.has('85292'));
assert.throws(()=>adapter.creer({...pub,communes_a_instruire:80},cog,base,uuid,lot01),/registre incomplet/);
assert.throws(()=>adapter.creer({...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],ark_pactols:'26678/pcrtWU8rdgPSSH'}]},cog,base,uuid,lot01),/non vérifiée/);
const main=fs.readFileSync(path.resolve(__dirname,'../docs/assets/lieux-multiechelon.js'),'utf8');
assert.ok(main.includes('state.pdlChemille.index'));
assert.ok(main.includes('state.pdlChemille?.byCode.get(x.code)'));
assert.ok(main.includes('Chemillé-en-Anjou est créée le 15 décembre 2015'));
const manifest=read('docs/data/manifest.json').modules.lieux.pactols_pdl_2026_chemille;
assert.equal(manifest.liens_PDL_2026_au_total,1149);
assert.equal(manifest.exceptions_2026_restantes,79);
console.log('PDL_CHEMILLE_1149_JS_OK — ancien Chemillé et Chemillé-Melay distincts');
