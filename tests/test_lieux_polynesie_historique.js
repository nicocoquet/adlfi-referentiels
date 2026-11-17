/* Contrat public Polynésie : les 48 codes COG commencent en 1972 documentaire. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const api=require('../docs/assets/lieux-polynesie-historique.js');
const d=JSON.parse(fs.readFileSync(path.join(__dirname,
 '../docs/data/lieux-polynesie/chronologie-cog-2026.json'),'utf8'));
const h=api.creer(d);
assert.deepEqual([1943,1971,1972,1973,1985,2026].map(y=>h.nombreCommunes(y)),
 [0,0,0,48,48,48]);
assert.equal(h.etatTerritoire(1972),null);
assert.equal(h.etatTerritoire(1973).code,'987');
assert.equal(h.ancienClipperton(1972),null);
assert.equal(h.ancienClipperton(1973).libelle,'Clipperton');
assert.equal(h.ancienClipperton(2007).code,'98799');
assert.equal(h.ancienClipperton(2008),null);
assert.equal(h.etat('98799',2026),null);
assert.equal(h.etat('97123',2026),null);
for(let i=11;i<=58;i++){
 const code='987'+i;
 assert.equal(h.etat(code,1972),null);
 const e=h.etat(code,1973);
 assert.equal(e.code,code);
 assert.equal(e.start,'1972-05-21');
 assert.equal(e.nature,'COM');
 assert.equal(h.etat(code,2026).code,code);
}
assert.equal(h.referenceISPF.nombre_communes_associees,98);
assert.equal(h.referenceISPF.nombre_unites_de_nomenclature_fine,116);
assert.equal(d.historique_juridique.communes_preexistantes_avant_1971,4);
const clone=()=>JSON.parse(JSON.stringify(d));
let p=clone();p.episodes_communes_COG=p.episodes_communes_COG.replace('1972-05-21','1971-12-24');
assert.throws(()=>api.creer(p),/historique incompatible/);
p=clone();p.communes_associees_creees=98;
assert.throws(()=>api.creer(p),/usurpés/);
p=clone();p.decoupage_ISPF.correspondance_automatique_commune_ile=true;
assert.throws(()=>api.creer(p),/ISPF/);
p=clone();p.historique_juridique.creation_juridique_toutes_communes_deduite_1972=true;
assert.throws(()=>api.creer(p),/juridique/);
p=clone();p.ancien_code_Clipperton_COG.code_actuel=true;
assert.throws(()=>api.creer(p),/Clipperton/);
p=clone();p.nouveaux_alignements_pactols=1;
assert.throws(()=>api.creer(p),/usurpés/);
console.log('Polynésie : 48 codes COMER, 48 épisodes COG, première attestation 21 mai 1972, 98799 isolé — OK');
