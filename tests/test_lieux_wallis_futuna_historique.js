/* Wallis-et-Futuna : aucune commune, 3 CIR COG dès 1985 et loi de 1961. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('../docs/assets/lieux-wallis-futuna-historique.js');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,
 '../docs/data/lieux-wallis-futuna/chronologie-cog-2026.json'),'utf8'));
const h=api.creer(data);
assert.deepEqual([1943,1961,1962,1984,1985,2026].map(y=>h.nombreCirconscriptions(y)),
 [0,0,0,0,3,3]);
assert.equal(h.etatTerritoire(1984),null);
assert.equal(h.etatTerritoire(1985).code,'986');
assert.equal(h.etatTerritoire(2026).label,'Wallis-et-Futuna');
assert.equal(h.codeTerritoireHistorique(1961),null);
assert.equal(h.codeTerritoireHistorique(1962).code,'98609');
assert.equal(h.codeTerritoireHistorique(1984).code,'98609');
assert.equal(h.codeTerritoireHistorique(1985),null);
assert.equal(h.statutCirconscriptionsLegal(1961),null);
assert.match(h.statutCirconscriptionsLegal(1962),/1961/);
assert.match(h.statutCirconscriptionsLegal(1984),/1961/);
for(const [code,name]of [['98611','Alo'],['98612','Sigave'],['98613','Uvea']]){
 assert.equal(h.etatCirconscription(code,1962),null);
 assert.equal(h.etatCirconscription(code,1984),null);
 assert.equal(h.etatCirconscription(code,1985).label,name);
 assert.equal(h.etatCirconscription(code,2026).nature,'CIR');
 assert.equal(h.etatCirconscription(code,2026).start,'1985-01-01');
}
assert.equal(h.etatCirconscription('986',2026),null);
assert.equal(h.etatCirconscription('98609',2026),null);
assert.equal(h.etatCirconscription('98607',1943),null);
const clone=()=>JSON.parse(JSON.stringify(data));
const invalid1=clone();invalid1.territoire_courant.communes=3;
assert.throws(()=>api.creer(invalid1),/confondues/);
const invalid2=clone();invalid2.episodes_circonscriptions=
 invalid2.episodes_circonscriptions.replace('CIR|1985-01-01','COM|1985-01-01');
assert.throws(()=>api.creer(invalid2),/circonscription/);
const invalid3=clone();invalid3.ancien_code_contextuel_non_adopte.libelle='Wallis-et-Futuna';
assert.throws(()=>api.creer(invalid3),/Nouvelle-Calédonie/);
const invalid4=clone();invalid4.succession_juridique_98609_986_inferree=true;
assert.throws(()=>api.creer(invalid4),/confondues/);
const invalid5=clone();invalid5.loi_circonscriptions.entree_en_vigueur='1985-01-01';
assert.throws(()=>api.creer(invalid5),/légal/);
const invalid6=clone();invalid6.nouveaux_alignements_pactols=1;
assert.throws(()=>api.creer(invalid6),/confondues/);
console.log('Wallis-et-Futuna : 3 CIR, 0 commune, 98609→986 documentaire, loi 1961 indépendante, pas de contour/ARK — OK');
