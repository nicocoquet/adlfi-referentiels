/* Saint-Pierre-et-Miquelon : COG 2026, deux communes, un épisode territorial. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('../docs/assets/lieux-saint-pierre-miquelon-historique.js');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,
 '../docs/data/lieux-saint-pierre-miquelon/chronologie-cog-2026.json'),'utf8'));
const hist=api.creer(data);
assert.equal(hist.communes.length,2);
assert.equal(hist.collectivite.length,1);
assert.deepEqual([1943,1976,1977,1985,1986,2003,2004,2026].map(y=>hist.count(y)),
 [0,0,2,2,2,2,2,2]);
for(const code of ['97501','97502']){
 assert.equal(hist.etatCommune(code,1943),null);
 assert.equal(hist.etatCommune(code,1976),null);
 assert.equal(hist.etatCommune(code,1977).code,code);
 assert.equal(hist.etatCommune(code,1985).code,code);
 assert.equal(hist.etatCommune(code,2026).code,code);
 assert.equal(hist.etatCommune(code,2026).start,'1976-07-21');
}
assert.equal(hist.etatCommune('975',2026),null);
assert.equal(hist.etatCollectivite(1985),null);
assert.equal(hist.etatCollectivite(1986).start,'1985-06-15');
assert.equal(hist.etatCollectivite(2026).code,'975');
assert.equal(hist.statutJuridiqueAnnuel(1976),null);
assert.match(hist.statutJuridiqueAnnuel(1977),/Département d’outre-mer/);
assert.match(hist.statutJuridiqueAnnuel(1985),/Département d’outre-mer/);
assert.match(hist.statutJuridiqueAnnuel(1986),/Collectivité territoriale/);
assert.match(hist.statutJuridiqueAnnuel(2003),/Collectivité territoriale/);
assert.match(hist.statutJuridiqueAnnuel(2004),/Collectivité d’outre-mer/);
assert.equal(hist.lois.length,4);
assert.ok(hist.lois.every(x=>x.date_effet_precise_deduite===false));
assert.ok(hist.communes.every(e=>!Object.hasOwn(e,'geometry')));
assert.equal(data.contours_historiques_publies,0);
assert.equal(data.nouveaux_alignements_pactols,0);
assert.equal(data.identites_historiques_retroprojetees,0);
const clone=()=>JSON.parse(JSON.stringify(data));
const bad1=clone();bad1.episodes_communes_COMER=bad1.episodes_communes_COMER
 .replace('1976-07-21','1976-07-19');
assert.throws(()=>api.creer(bad1),/discordants/);
const bad2=clone();bad2.episodes_communes_DROM=
 '97501|Miquelon-Langlade|1976-07-21|1985-06-15';
assert.throws(()=>api.creer(bad2),/Volume/);
const bad3=clone();bad3.episodes_collectivite_COG='975|Saint-Pierre-et-Miquelon|1976-07-21|';
assert.throws(()=>api.creer(bad3),/collectivité/);
const bad4=clone();bad4.nouveaux_alignements_pactols=1;
assert.throws(()=>api.creer(bad4),/non conforme/);
const bad5=clone();bad5.famille_COG_non_equivalente_au_statut_juridique=false;
assert.throws(()=>api.creer(bad5),/non conforme/);
const bad6=clone();bad6.statuts_juridiques_reperes_annuels[0].date_effet_precise_deduite=true;
assert.throws(()=>api.creer(bad6),/confondus/);
console.log('SPM : 2 épisodes COG communaux, 1 collectivité, statuts distincts, sans ARK/contours — OK');