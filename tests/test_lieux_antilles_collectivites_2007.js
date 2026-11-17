/* Saint-Barthélemy et Saint-Martin : deux anciennes communes, deux COM, deux codes applicatifs. */
'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const api=require('../docs/assets/lieux-antilles-collectivites-2007.js');
const d=JSON.parse(fs.readFileSync(path.join(__dirname,
  '../docs/data/lieux-antilles-collectivites-2007/chronologie-cog-juridique-2026.json'),'utf8'));
const h=api.creer(d);
assert.equal(h.relations.length,2);
for(const [old,comm,code5,label,article] of [
 ['97123','977','97701','Saint-Barthélemy','18-X'],
 ['97127','978','97801','Saint-Martin','18-XI']
]){
 const r=h.pourCode(old);
 assert.equal(r.ancienne_commune.libelle,label);
 assert.equal(r.succession_juridique.source,'Loi organique n° 2007-223, article '+article);
 assert.strictEqual(r.mouvement_COG.COM_AP,null);
 assert.equal(r.code_cinq_positions.type,'CODE_APPLICATION_5_POSITIONS_NON_COMMUNE');
 assert.equal(h.pourCode(comm),r);
 assert.equal(h.pourCode(code5),r);
 assert.equal(h.etat(old,1946),null);
 assert.equal(h.etat(old,1947).type,'ANCIENNE_COMMUNE');
 assert.equal(h.etat(old,2007).type,'ANCIENNE_COMMUNE');
 assert.equal(h.etat(old,2008),null);
 assert.equal(h.etat(comm,2007),null);
 assert.equal(h.etat(comm,2008).type,'COLLECTIVITE');
 assert.equal(h.etat(code5,2008).type,'CODE_APPLICATION_NON_COMMUNE');
 assert.equal(h.etat(code5,2007),null);
}
assert.deepEqual([1946,1947,2007,2008,2026].map(y=>h.nombreAnciennes(y)),[0,2,2,0,0]);
assert.deepEqual([1946,1947,2007,2008,2026].map(y=>h.nombreCollectivites(y)),[0,0,0,2,2]);
assert.equal(d.nouveaux_alignements_pactols,0);
assert.equal(d.nouveaux_contours_historiques,0);
const clone=()=>JSON.parse(JSON.stringify(d));
const x1=clone();x1.relations[0].mouvement_COG.COM_AP='977';
assert.throws(()=>api.creer(x1),/violée/);
const x2=clone();x2.relations[0].code_cinq_positions.type='COMMUNE';
assert.throws(()=>api.creer(x2),/violée/);
const x3=clone();x3.relations[0].succession_juridique.identite_pactols_deduite=true;
assert.throws(()=>api.creer(x3),/violée/);
const x4=clone();x4.relations[0].succession_juridique.source='COG mod 30';
assert.throws(()=>api.creer(x4),/violée/);
const x5=clone();x5.episodes_collectivites=x5.episodes_collectivites.replace('2007-02-23','2007-02-22');
assert.throws(()=>api.creer(x5),/violée/);
const x6=clone();x6.nouveaux_alignements_pactols=1;
assert.throws(()=>api.creer(x6),/non conforme/);
console.log('Antilles : 2 anciennes communes, 2 COM, 2 codes applicatifs ; succession juridique ≠ MOD30 ≠ Pactols — OK');
