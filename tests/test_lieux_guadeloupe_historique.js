/* Contrôle du schéma et des 35 épisodes COG Guadeloupe sans géométries. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('../docs/assets/lieux-guadeloupe-historique.js');
const data=JSON.parse(fs.readFileSync(
 path.join(__dirname,'../docs/data/lieux-guadeloupe/chronologie-cog-2026.json'),'utf8'));
const h=api.creer(data);
assert.equal(h.episodes.length,35);
assert.equal(new Set(h.episodes.map(x=>x.code)).size,34);
assert.equal(h.historicalIndex.length,2);
assert.deepEqual([...h.old.keys()].sort(),['97123','97127']);
assert.deepEqual(Object.fromEntries(
 [1943,1946,1947,1976,1977,2007,2008,2026].map(y=>[y,h.count(y)])
),{1943:0,1946:0,1947:34,1976:34,1977:34,2007:34,2008:32,2026:32});
assert.equal(h.etat('97107',1976).label,'Capesterre-de-Guadeloupe');
assert.equal(h.etat('97107',1977).label,'Capesterre-Belle-Eau');
assert.equal(h.etat('97123',2007).label,'Saint-Barthélemy');
assert.equal(h.etat('97127',2007).label,'Saint-Martin');
assert.equal(h.etat('97123',2008),null);
assert.equal(h.etat('97127',2008),null);
assert.equal(h.etat('97101',1946),null);
assert.equal(h.etat('97101',1947).label,'Les Abymes');
assert.equal(h.periodes('97107').length,2);
assert.equal(h.old.get('97123').ark_pactols_uri_insee_atteste,null);
assert.equal(h.old.get('97127').destination_com_ap,null);
assert.ok(h.episodes.every(x=>!Object.hasOwn(x,'geometry')));
assert.ok(h.historicalIndex.every(x=>x.kind==='cogHistoriqueGuadeloupe'&&!x.arkCandidat));
const invalid=JSON.parse(JSON.stringify(data));
invalid.anciens_codes[0].destination_com_ap='97701';
assert.throws(()=>api.creer(invalid),/Ancien code/);
const invalid2=JSON.parse(JSON.stringify(data));
invalid2.episodes=invalid2.episodes.replace(
 '97107|Capesterre-de-Guadeloupe|1946-03-21|1976-06-04',
 '97107|Capesterre-de-Guadeloupe|1946-03-21|1975-06-04');
assert.throws(()=>api.creer(invalid2),/discontinus|Renommage/);
const invalid3=JSON.parse(JSON.stringify(data));
invalid3.nouveaux_alignements_pactols=1;
assert.throws(()=>api.creer(invalid3),/non conforme/);
console.log('Guadeloupe COG : 35 épisodes, 34 codes, 32 actuels et deux anciens sans ARK — OK');
