/* Tests Node.js de la logique de curseur (sans chargement du navigateur). */
'use strict';
const assert = require('node:assert/strict');
const t = require('../docs/assets/lieux-temps.js');

function demo() {
  return {
    schema: 'adlfi.lieux.temps.recette.v1',
    etat: 'recette_non_publiee',
    reference_temporelle: {
      mode: 'instant_au_1er_janvier',
      annee_min: 1943, annee_max: 2026, annee_initiale: 2026
    },
    periodes_COM: [
      { code_insee:'25368',libelle:'Marchaux',
        debut_inclus:'1943-01-01',fin_exclue:'2018-01-01' },
      { code_insee:'25368',libelle:'Marchaux-Chaudefontaine',
        debut_inclus:'2018-01-01',fin_exclue:null },
      { code_insee:'25137',libelle:'Chaudefontaine',
        debut_inclus:'1943-01-01',fin_exclue:'2018-01-01' },
      { code_insee:'39012',libelle:'Antorpe',
        debut_inclus:'1943-01-01',fin_exclue:'1974-06-01' },
    ],
    entites_complementaires_2026: [
      {code_insee:'39012',libelle:'Antorpe',typecom:'COMA',
       comparent:'25527',date_observation:'2026-01-01'}
    ],
    evenements_COG: [
      {id:'evt1974',date_effet:'1974-06-01'},
      {id:'evt2018',date_effet:'2018-01-01'},
      {id:'evt2020',date_effet:'2020-03-15'},
    ]
  };
}

const model=demo();
assert.deepEqual(t.auPremierJanvier(model,2017).etats_COM.map(x=>x.libelle),
                 ['Chaudefontaine','Marchaux']);
assert.deepEqual(t.auPremierJanvier(model,2018).etats_COM.map(x=>x.libelle),
                 ['Marchaux-Chaudefontaine']);
assert.equal(t.auPremierJanvier(model,2020).date_reference,'2020-01-01');
assert.equal(t.auPremierJanvier(model,2020).evenements_deja_survenus.length,2);
assert.equal(t.auPremierJanvier(model,2021).evenements_deja_survenus.length,3);
assert.deepEqual(t.auPremierJanvier(model,2017).entites_complementaires,[]);
assert.equal(t.auPremierJanvier(model,2026).entites_complementaires.length,1);
assert.deepEqual(t.auPremierJanvier(model,2017).geometries_historiques,[]);
assert.throws(()=>t.auPremierJanvier(model,1942),RangeError);
assert.throws(()=>t.auPremierJanvier(model,2027),RangeError);
assert.throws(()=>t.auPremierJanvier(model,'2017'),RangeError);
assert.equal(t.normaliser('Saint-Hymetière-sur-Valouse'),
             'saint hymetiere sur valouse');
const index=t.creerIndexNoms(model);
const before=t.chercherNoms(index,'Marchaux',10);
assert.equal(before.length,1);
assert.equal(before[0].code_insee,'25368');
assert.equal(before[0].formes_historiques.length,2);
assert.equal(t.chercherNoms(index,'Antorpe')[0].code_insee,'39012');
console.log('Tests du curseur Lieux : périodes, recherche et garde-fous OK.');
