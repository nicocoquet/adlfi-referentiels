'use strict';
const assert=require('node:assert/strict');
const recherche=require('../docs/assets/lieux-recherche-millesime.js');
const data={corse:{cog:{periodes_com:[
 {code_insee:'20001',typecom:'COM',libelle:'Afa',debut_inclus:'1943-01-01',fin_exclue:'1976-01-01'},
 {code_insee:'2A001',typecom:'COM',libelle:'Afa',debut_inclus:'1976-01-01',fin_exclue:null}
]}}};
const periodes=recherche.preparer(data,['corse']);
const entries=[
 {kind:'cog',id:'cog:20001',zone:'corse',code:'20001',label:'Afa',noms:['Afa']},
 {kind:'cog',id:'cog:2A001',zone:'corse',code:'2A001',label:'Afa',noms:['Afa']},
 {kind:'pactols',id:'pactols:26678/pcrtgs2LLPYow2',zone:'corse',code:'2A001',
  label:'Afa',ark:'26678/pcrtgs2LLPYow2',noms:['Afa']}
];
assert.equal(recherche.etat(entries[0],1975,periodes),'actif');
assert.equal(recherche.etat(entries[1],1975,periodes),'historique');
assert.equal(recherche.etat(entries[0],2026,periodes),'historique');
assert.equal(recherche.etat(entries[1],2026,periodes),'actif');
assert.equal(recherche.trier(entries,'Afa',2026,periodes)[0].code,'2A001');
assert.equal(recherche.trier(entries,'Afa',1975,periodes)[0].code,'20001');
assert.equal(recherche.trier(entries,'20001',2026,periodes)[0].code,'20001',
 'Une recherche par code explicite prime sur la date');
assert.equal(recherche.trier(entries,'2A001',1975,periodes)[0].code,'2A001');
assert.equal(recherche.trier(entries,'26678/pcrtgs2LLPYow2',1975,periodes)[0].kind,'pactols',
 'Un ARK explicitement demandé reste retrouvable hors de son millésime de validation');
assert.equal(recherche.trier(entries,'Afa',2026,periodes)[2].code,'20001');
const region={normandie:{cog:{periodes_com:[
 {code_insee:'50129',typecom:'COM',debut_inclus:'2016-01-01',fin_exclue:null}
]}}};
const normandie=recherche.preparer(region,['normandie']);
assert.equal(recherche.etat({kind:'cog',zone:'normandie',code:'50129'},2015,normandie),'historique');
assert.equal(recherche.etat({kind:'cog',zone:'normandie',code:'50129'},2026,normandie),'actif');
const homonymes=[
 {kind:'cog',id:'old',zone:'normandie',code:'50100',label:'Testville',noms:['Testville']},
 {kind:'cog',id:'new',zone:'normandie',code:'50129',label:'Testville',noms:['Testville']}
];
const sorted=recherche.trier(homonymes,'Testville',2026,normandie);
assert.equal(sorted[0].id,'new');
assert.equal(recherche.etat({kind:'admin',code:'50129'},2026,normandie),'hors_cog_regional');
assert.throws(()=>recherche.etat(entries[0],2027,periodes),/Millésime/);
assert.throws(()=>recherche.preparer({corse:{cog:{}}},['corse']),/Chronologie/);
console.log('LIEUX_RECHERCHE_MILLESIME_OK — codes historiques, ARK explicite, communes actives');
