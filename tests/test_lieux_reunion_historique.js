/* Réunion : 24 épisodes officiels et deux mouvements de division en 1965. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('../docs/assets/lieux-reunion-historique.js');
const data=JSON.parse(fs.readFileSync(
 path.join(__dirname,'../docs/data/lieux-reunion/chronologie-cog-2026.json'),'utf8'));
const h=api.creer(data);
assert.equal(h.episodes.length,24);
assert.equal(new Set(h.episodes.map(x=>x.code)).size,24);
assert.deepEqual(Object.fromEntries(
 [1943,1946,1947,1965,1966,2026].map(y=>[y,h.count(y)])
),{1943:0,1946:0,1947:23,1965:23,1966:24,2026:24});
assert.equal(h.etat('97414',1946),null);
assert.equal(h.etat('97414',1947).label,'Saint-Louis');
assert.equal(h.etat('97414',1965).label,'Saint-Louis');
assert.equal(h.etat('97414',1966).label,'Saint-Louis');
assert.equal(h.etat('97424',1965),null);
assert.equal(h.etat('97424',1966).label,'Cilaos');
assert.equal(h.etat('97407',2026).label,'Le Port');
assert.equal(h.periodes('97414').length,1);
assert.equal(h.periodes('97424').length,1);
assert.equal(h.perimetreSaintLouis(1946),null);
assert.equal(h.perimetreSaintLouis(1965),'AVANT_DIVISION_1965');
assert.equal(h.perimetreSaintLouis(1966),'APRES_DIVISION_1965');
assert.equal(h.perimetreSaintLouis(2026),'APRES_DIVISION_1965');
assert.ok(h.episodes.every(x=>!Object.hasOwn(x,'geometry')));
assert.equal(h.division.contour_avant_1965,null);
assert.equal(h.division.contour_apres_1965,null);
const clone=()=>JSON.parse(JSON.stringify(data));
const bad=clone();bad.episodes=bad.episodes.replace(
 '97424|Cilaos|1965-02-05|','97424|Cilaos|1946-03-21|');
assert.throws(()=>api.creer(bad),/incohérents|incohérent/);
const bad2=clone();bad2.mouvement_division_1965.change_emprise_97414=false;
assert.throws(()=>api.creer(bad2),/Division/);
const bad3=clone();bad3.mouvement_division_1965.contour_avant_1965={type:'Polygon',coordinates:[]};
assert.throws(()=>api.creer(bad3),/Division/);
const bad4=clone();bad4.nouveaux_alignements_pactols=1;
assert.throws(()=>api.creer(bad4),/non conforme/);
console.log('La Réunion : 24 épisodes COG, 25 mouvements, division 1965 non géométrique — OK');