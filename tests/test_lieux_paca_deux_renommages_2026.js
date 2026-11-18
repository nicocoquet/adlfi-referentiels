/* PACA 937/946 : Rousset 05127, Esparron 83052 et Céreste retenue en réserve. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const core=require('../docs/assets/lieux-paca-pactols.js');
const loader=require('../docs/assets/lieux-paca-renommages.js');
const cog=read('docs/data/lieux-chronologie/cog-paca.json');
const pilote=read('docs/data/lieux.json');
const complet=core.creer(read('docs/data/lieux-chronologie/pactols-paca-2026.json'),cog);
const publication=read('docs/data/lieux-chronologie/pactols-paca-renommages-2026.json');
const loaded=loader.creer(publication,cog,pilote,complet);
const pilotCodes=new Set(pilote.autorites.map(x=>x.correspondances[0].code_insee));
assert.equal(pilotCodes.size,103);
assert.equal(complet.byCode.size,832);
assert.equal(loaded.byCode.size,2);
assert.deepEqual([...loaded.byCode.keys()].sort(),['05127','83052']);
assert.equal(loaded.byCode.get('05127').ark_pactols,'26678/pcrtla4EHGDgDd');
assert.equal(loaded.byCode.get('83052').ark_pactols,'26678/pcrt7B7bs9P5g2');
assert.equal(new Set([...pilotCodes,...complet.byCode.keys(),...loaded.byCode.keys()]).size,937);
assert.equal(946-937,9);
assert.ok(!loaded.byCode.has('04045')&&!complet.byCode.has('04045')&&!pilotCodes.has('04045'));
assert.ok(loaded.index.every(x=>x.zone==='paca'&&x.kind==='pactols'));
assert.ok(loaded.index.every(x=>x.champs.includes(x.code)));
assert.equal(cog.geometries_historiques.length,0);
const wrong={...publication,total_alignements_PACA_2026:938};
assert.throws(()=>loader.creer(wrong,cog,pilote,complet),/non conforme/);
const doctored={...publication,alignements_Pactols_COG_valides_2026:[
 {...publication.alignements_Pactols_COG_valides_2026[0],code_insee:'04045'},
 publication.alignements_Pactols_COG_valides_2026[1]
]};
assert.throws(()=>loader.creer(doctored,cog,pilote,complet),/insuffisamment prouvé/);
assert.ok(fs.readFileSync(path.join(ROOT,'docs/assets/lieux-multiechelon.js'),'utf8')
 .includes('state.pacaRenommages.index'));
console.log('PACA_937_INDEX_OK — 103+832+2 ARK, 9 exceptions et zéro rétroprojection');
