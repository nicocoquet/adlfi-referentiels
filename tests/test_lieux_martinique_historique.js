/* Les 34 épisodes documentés de Martinique sont vérifiés sans géométries. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('../docs/assets/lieux-martinique-historique.js');
const data=JSON.parse(fs.readFileSync(
    path.join(__dirname,'../docs/data/lieux-martinique/chronologie-cog-2026.json'),'utf8'));
const hist=api.creer(data);
assert.equal(hist.episodes.length,34);
assert.equal(new Set(hist.episodes.map(x=>x.code)).size,34);
assert.deepEqual(Object.fromEntries(
    [1943,1946,1947,1949,1950,1951,2026].map(annee=>[annee,hist.count(annee)])
),{1943:0,1946:0,1947:32,1949:32,1950:33,1951:34,2026:34});
assert.equal(hist.etat('97209',1946),null);
assert.equal(hist.etat('97209',1947).label,'Fort-de-France');
assert.equal(hist.etat('97233',1949),null);
assert.equal(hist.etat('97233',1950).label,'Le Morne-Vert');
assert.equal(hist.etat('97234',1950),null);
assert.equal(hist.etat('97234',1951).label,'Bellefontaine');
assert.equal(hist.etat('97229',2026).label,'Schœlcher');
assert.ok(hist.episodes.every(x=>x.end===null&&!Object.hasOwn(x,'geometry')));
const altered=JSON.parse(JSON.stringify(data));
altered.episodes=altered.episodes.replace('97234|Bellefontaine|1950-08-26|',
                                         '97234|Bellefontaine|1946-03-21|');
assert.throws(()=>api.creer(altered),/Épisode COG contredit/);
const altered2=JSON.parse(JSON.stringify(data));
altered2.contours_historiques_publies=1;
assert.throws(()=>api.creer(altered2),/non conforme/);
const altered3=JSON.parse(JSON.stringify(data));
altered3.mouvements_par_date[1].lignes=1;
assert.throws(()=>api.creer(altered3),/Mouvement COG inattendu/);
console.log('Martinique COG : 34 épisodes, 32 communes en 1947, 33 en 1950, 34 dès 1951 — OK');
