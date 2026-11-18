/* PDL Wikidata P374 : 1195+17=1212, sans ARK historique promu. */
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
const oree=require('../docs/assets/lieux-pdl-oree-mod50.js').creer(
 read('docs/data/lieux-chronologie/pactols-pdl-oree-anjou-mod50-2026.json'),
 cog,base,uuid,lot01,chemille,lot02);
const pub=read('docs/data/lieux-chronologie/pactols-pdl-wikidata-p374-2026.json');
const adapter=require('../docs/assets/lieux-pdl-wikidata-p374.js');
const next=adapter.creer(pub,cog,base,uuid,lot01,chemille,lot02,oree);
assert.equal(next.byCode.size,17);
assert.equal(next.index.length,17);
const all=[...base.byCode.values(),...uuid.byCode.values(),...lot01.byCode.values(),
           ...chemille.byCode.values(),...lot02.byCode.values(),...oree.byCode.values(),
           ...next.byCode.values()];
assert.equal(all.length,1212);
assert.equal(new Set(all.map(x=>x.code_insee)).size,1212);
assert.equal(new Set(all.map(x=>x.ark_pactols)).size,1212);
const historical=pub.alignements_Pactols_COG_valides_2026.map(x=>x.ark_ancienne_commune_distinct);
assert.equal(new Set(historical).size,17);
assert.ok(historical.every(x=>!all.some(a=>a.ark_pactols===x)));
assert.ok(!next.byCode.has('49080'));
assert.ok(!next.byCode.has('85292'));
const codes=['44003','49060','53062','72080','85001'];
for(const code of codes){
 const item=next.byCode.get(code);
 assert.ok(item,'Missing representative '+code);
 assert.equal(item.code_INSEE_Wikidata_P374,code);
 assert.ok(next.index.some(i=>i.code===code&&i.ark===item.ark_pactols));
}
assert.throws(()=>adapter.creer({...pub,communes_a_instruire:15},cog,base,uuid,lot01,chemille,lot02,oree),/non conformes/);
const tainted={...pub,alignements_Pactols_COG_valides_2026:[
  {...pub.alignements_Pactols_COG_valides_2026[0],code_INSEE_Wikidata_P374:'00000'},
  ...pub.alignements_Pactols_COG_valides_2026.slice(1)
]};
assert.throws(()=>adapter.creer(tainted,cog,base,uuid,lot01,chemille,lot02,oree),/non vérifiées/);
const ui=fs.readFileSync(path.resolve(__dirname,'../docs/assets/lieux-multiechelon.js'),'utf8');
assert.ok(ui.includes('state.pdlWikidataP374.index'));
assert.ok(ui.includes('state.pdlWikidataP374?.byCode.get(x.code)'));
assert.ok(ui.includes('Pactols ne fournit pas directement d’exactMatch INSEE'));
const manifest=read('docs/data/manifest.json').modules.lieux.pactols_pdl_2026_wikidata_p374;
assert.equal(manifest.liens_PDL_2026_au_total,1212);
assert.equal(manifest.exceptions_2026_restantes,16);
console.log('PDL_WIKIDATA_1212_JS_OK — 17 indirects, zéro ARK ancien promu');
