'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('../docs/assets/lieux-guyane-historique.js');
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'../docs/data/lieux-guyane/chronologie-cog-2026.json'),'utf8'));
const model=api.creer(source);
assert.equal(model.episodes.length,41);
assert.equal(new Set(model.episodes.map(x=>x.code)).size,26);
assert.equal(model.historicalIndex.length,4);
assert.deepEqual(Object.fromEntries(
 [1943,1946,1947,1953,1969,1970,1977,1989,1993,2026].map(y=>[y,model.count(y)])
),{1943:0,1946:0,1947:18,1953:23,1969:23,1970:19,1977:20,1989:21,1993:22,2026:22});
assert.equal(model.etat('97301',1969).label,'Approuague-Kaw');
assert.equal(model.etat('97301',1970).label,'Régina');
assert.equal(model.etat('97357',1976).label,'Grand-Santi-Papaichton');
assert.equal(model.etat('97357',1977).label,'Grand-Santi');
assert.equal(model.etat('97359',1969).label,'La Comté (chef-lieu Dégrad-Edmond)');
assert.equal(model.etat('97359',1970),null);
assert.equal(model.etat('97360',1976),null);
assert.equal(model.etat('97360',1977).label,'Apatou');
assert.equal(model.etat('97361',1988),null);
assert.equal(model.etat('97361',1989).label,'Awala-Yalimapo');
assert.equal(model.etat('97362',1992),null);
assert.equal(model.etat('97362',1993).label,'Papaichton');
assert.equal(model.etat('97301',1943),null);
assert.deepEqual(
 [...model.old.keys()].sort(),['97351','97354','97355','97359']);
assert.deepEqual(
 model.historicalIndex.find(x=>x.code==='97355').champs.includes(api.normalize('Mana')),true);
assert.equal(model.old.get('97355').ark_candidat,'26678/pcrtbvSjznYKWV');
assert.equal(model.old.get('97355').code_destination_mouvement_COG_1969,'97306');
assert.equal(model.old.get('97351').code_destination_mouvement_COG_1969,'97301');
assert.equal(model.old.get('97354').code_destination_mouvement_COG_1969,'97352');
assert.equal(model.old.get('97359').code_destination_mouvement_COG_1969,'97310');
assert.ok(model.episodes.every(x=>!Object.hasOwn(x,'geometry')));
const duplicate=JSON.parse(JSON.stringify(source));
duplicate.episodes+='\n97301|Nouvelle identité fabriquée|1955-01-01|1960-01-01';
assert.throws(()=>api.creer(duplicate),/Cardinalités/);
const altered=JSON.parse(JSON.stringify(source));
altered.contours_historiques_publies=1;
assert.throws(()=>api.creer(altered),/non conforme/);
const oldChanged=JSON.parse(JSON.stringify(source));
oldChanged.anciennes[0].code_destination_mouvement_COG_1969='97306';
assert.throws(()=>api.creer(oldChanged),/incohérentes/);
console.log('Guyane COG : 84 années, 41 périodes, 26 codes, 4 autorités anciennes — OK');
