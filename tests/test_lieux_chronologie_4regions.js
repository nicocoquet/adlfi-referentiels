/* Contrat chronologique : tests sans navigateur et sans réseau. */
'use strict';
const assert = require('node:assert/strict');
const core = require('../docs/assets/lieux-chronologie-core.js');
const source = {
  schema:'adlfi.lieux.chronologie.4regions.public-recette.v1',
  region:'bfc',
  periodes_com:[
    {code_insee:'25368',typecom:'COM',libelle:'Marchaux',
     debut_inclus:'1943-01-01',fin_exclue:'2018-01-01'},
    {code_insee:'25368',typecom:'COM',libelle:'Marchaux-Chaudefontaine',
     debut_inclus:'2018-01-01',fin_exclue:null},
    {code_insee:'39137',typecom:'COM',libelle:'Chemilla',
     debut_inclus:'1943-01-01',fin_exclue:'2019-01-01'},
    {code_insee:'39137',typecom:'COM',libelle:'Saint-Hymetière-sur-Valouse',
     debut_inclus:'2019-01-01',fin_exclue:null},
  ],
  observations_COMA_COMD_2026:[
    {code_insee:'39012',typecom:'COMA',libelle:'Antorpe',comparent_2026:'25527'}
  ],
  lignes_mouvements_cog:[
    {id:'m1',date_effet:'2018-01-01',mod:'32',code_avant:'25368',
     code_apres:'25368',libelle_avant:'Marchaux',libelle_apres:'Marchaux-Chaudefontaine'}
  ],
  alignements_Pactols_COG_valides_2026:[],
  geometries_historiques:[]
};
assert.equal(core.etat(source,'25368',2017).etat.libelle,'Marchaux');
assert.equal(core.etat(source,'25368',2018).etat.libelle,'Marchaux-Chaudefontaine');
assert.equal(core.etat(source,'39137',2018).etat.libelle,'Chemilla');
assert.equal(core.etat(source,'39137',2019).etat.libelle,'Saint-Hymetière-sur-Valouse');
assert.equal(core.etat(source,'25368',2017).mouvements.length,0);
assert.equal(core.etat(source,'25368',2018).mouvements.length,1);
assert.equal(core.etat(source,'39012',1975).etat,null);
assert.equal(core.etat(source,'39012',2026).etat.typecom,'COMA');
assert.equal(core.nombreCommunes(source,2017),2);
assert.equal(core.nombreCommunes(source,2019),2);
assert.equal(core.dateReference(2026),'2026-01-01');
assert.throws(()=>core.dateReference(2027),RangeError);
assert.ok(core.chercher(core.indexer(source),'chemilla')[0].code==='39137');
assert.ok(core.chercher(core.indexer(source),'marchaux')[0].code==='25368');
assert.deepEqual(core.chercher(core.indexer(source),'mot inconnu'),[]);

const paca={...source,region:'paca',alignements_Pactols_COG_valides_2026:[
  {ark_pactols:'26678/pcrt-test',libelle_pactols:'Commune Pactols',
   code_insee:'06001',millesime_validation:2026,
   statut:'correspondance_PACA_preexistante_validee'}
]};
assert.ok(core.indexer(paca).some(e=>e.kind==='pactols'&&e.ark==='26678/pcrt-test'));
assert.throws(()=>core.verifier({...paca,region:'bfc'}),/Alignements Pactols/);
assert.throws(()=>core.verifier({...source,geometries_historiques:[{}]}),/Contrat/);
assert.throws(()=>core.indexer({...paca,
 alignements_Pactols_COG_valides_2026:[{...paca.alignements_Pactols_COG_valides_2026[0],
 statut:'candidat'}]}),/non validé/);

console.log('Chronologie : états au 1er janvier, COMA, noms historiques et alignements PACA OK.');
