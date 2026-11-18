/* PACA : 946 identités, alignement Abriès-Ristolas indirect, anciennes communes exclues. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const pilote=read('docs/data/lieux.json');
const cog=read('docs/data/lieux-chronologie/cog-paca.json');
const complet=require('../docs/assets/lieux-paca-pactols.js').creer(
  read('docs/data/lieux-chronologie/pactols-paca-2026.json'),cog);
const renommages=require('../docs/assets/lieux-paca-renommages.js').creer(
  read('docs/data/lieux-chronologie/pactols-paca-renommages-2026.json'),
  cog,pilote,complet);
const nouvelles=require('../docs/assets/lieux-paca-communes-nouvelles.js').creer(
  read('docs/data/lieux-chronologie/pactols-paca-communes-nouvelles-2026.json'),
  cog,pilote,complet,renommages);
const pub=read('docs/data/lieux-chronologie/pactols-paca-abries-ristolas-2026.json');
const adapter=require('../docs/assets/lieux-paca-abries-ristolas.js');
const result=adapter.creer(pub,cog,pilote,complet,renommages,nouvelles);
assert.equal(result.byCode.size,1);
assert.equal(result.index.length,1);
assert.equal(result.byCode.get('05001').ark_pactols,'26678/pcrtm96gvvfnwmggc9z0wrxn');
assert.equal(result.byCode.get('05001').uri_insee_exactMatch_direct_pactols,null);
assert.equal(result.byCode.get('05001').uri_exactMatch_pactols_wikidata,
  'https://www.wikidata.org/wiki/Q57664391');
assert.equal(result.index[0].kind,'pactols');
assert.ok(result.index[0].champs.includes('05001'));
const keys=new Set(pilote.autorites.map(x=>x.correspondances[0].code_insee));
const arks=new Set(pilote.autorites.map(x=>x.ark_pactols));
for(const source of [complet,renommages,nouvelles]){
 for(const x of source.byCode.values()){keys.add(x.code_insee);arks.add(x.ark_pactols);}
}
assert.equal(keys.size,945);
assert.equal(arks.size,945);
keys.add('05001');arks.add('26678/pcrtm96gvvfnwmggc9z0wrxn');
assert.equal(keys.size,946);assert.equal(arks.size,946);
assert.ok(!arks.has('26678/pcrtGQ7nGPZN7K'));
assert.ok(!arks.has('26678/pcrt2YWpB2NDPZ'));
const historicalProof={...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],
    ark_pactols:'26678/pcrtGQ7nGPZN7K'}
]};
assert.throws(()=>adapter.creer(historicalProof,cog,pilote,complet,renommages,nouvelles),
  /Preuves insuffisantes/);
assert.throws(()=>adapter.creer({...pub,valeur_Wikidata_P374:'05120'},
 cog,pilote,complet,renommages,nouvelles),/incohérent/);
assert.throws(()=>adapter.creer({...pub,alignements_Pactols_COG_valides_2026:[
 {...pub.alignements_Pactols_COG_valides_2026[0],
    uri_insee_exactMatch_direct_pactols:'http://id.insee.fr/geo/commune/05001'}
]},cog,pilote,complet,renommages,nouvelles),/Preuves insuffisantes/);
const page=fs.readFileSync(path.join(ROOT,'docs/assets/lieux-multiechelon.js'),'utf8');
assert.ok(page.includes('state.pacaAbriesRistolas.index'));
assert.ok(page.includes('Pactols ne fournit pas d’exactMatch INSEE direct'));
console.log('PACA_946_EDITORIAL_OK — 946/946, une preuve indirecte documentée, anciens ARK exclus');
