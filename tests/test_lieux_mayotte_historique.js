/* Mayotte : les 17 identités traversent un changement de série COG en 2011. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('../docs/assets/lieux-mayotte-historique.js');
const data=JSON.parse(fs.readFileSync(
 path.join(__dirname,'../docs/data/lieux-mayotte/chronologie-cog-2026.json'),'utf8'));
const h=api.creer(data);
assert.equal(h.episodes.length,34);
assert.equal(new Set(h.episodes.map(x=>x.code)).size,17);
assert.deepEqual(Object.fromEntries(
 [1943,2007,2008,2011,2012,2025,2026].map(y=>[y,h.count(y)])),
 {1943:0,2007:0,2008:17,2011:17,2012:17,2025:17,2026:17});
for(let code=1;code<=17;code++){
  const c='976'+String(code).padStart(2,'0');
  assert.equal(h.periodes(c).length,2);
  assert.equal(h.etat(c,2007),null);
  assert.equal(h.etat(c,2008).famille,'COMER');
  assert.equal(h.etat(c,2011).famille,'COMER');
  assert.equal(h.etat(c,2012).famille,'DROM');
  assert.equal(h.etat(c,2026).famille,'DROM');
  assert.equal(h.etat(c,2011).label,h.etat(c,2012).label);
}
assert.equal(h.etat('97607',2026).label,'Dembeni');
assert.equal(h.arkDembeni.ark,'26678/crtZcuFSJVYZU');
assert.equal(h.transition.date_creation_des_communes,null);
assert.equal(h.collectivite.code_2026,'976R');
assert.equal(h.collectivite.code_2011_2025,'976D');
assert.ok(h.episodes.every(e=>!Object.hasOwn(e,'geometry')));
const clone=()=>JSON.parse(JSON.stringify(data));
const bad=clone();bad.episodes=bad.episodes.replace(
 '97607|Dembeni|COMER|2007-02-23|2011-03-31',
 '97607|Dembeni|COMER|2007-02-23|2011-02-28');
assert.throws(()=>api.creer(bad),/incohérente/);
const bad2=clone();bad2.transition_famille_cog.date_creation_des_communes='2011-03-31';
assert.throws(()=>api.creer(bad2),/faussement/);
const bad3=clone();bad3.ark_confirme_sans_alignement_valide.ark='26678/pcrtZcuFSJVYZU';
assert.throws(()=>api.creer(bad3),/Dembeni/);
const bad4=clone();bad4.nouveaux_alignements_pactols=1;
assert.throws(()=>api.creer(bad4),/non conforme/);
const bad5=clone();bad5.collectivite_statut_particulier.code_2026='976';
assert.throws(()=>api.creer(bad5),/collectivité/);
console.log('Mayotte : 17 COMER + 17 DROM, transition 2011 et Dembeni non alignée — OK');