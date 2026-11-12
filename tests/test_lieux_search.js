/* Non-régression de l'autocomplétion, sans navigateur ni dépendances. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { normaliser, creerIndex, chercher } = require('../docs/assets/lieux-search.js');

const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'docs/data/lieux.json'), 'utf8'));
const contours = JSON.parse(fs.readFileSync(path.join(root, 'docs/data/lieux-communes.geojson'), 'utf8'));
const index = creerIndex(data.autorites);
const codes = new Set(index.map(x => x.code));
const arks = new Set(index.map(x => x.ark));

assert.equal(index.length, 103);
assert.equal(codes.size, 103);
assert.equal(arks.size, 103);
assert.equal(contours.features.length, 103);

// La comparaison est insensible aux accents, tirets, apostrophes et à la casse.
assert.equal(normaliser('ÉVENOS'), 'evenos');
assert.equal(normaliser('  AIX–en—Provence  '), 'aix en provence');
assert.equal(normaliser("L’Île-d’Yeu"), 'l ile d yeu');

let result = chercher(index, 'Aix en Provence');
assert.equal(result[0].code, '13001');
assert.equal(chercher(index, '13001')[0].label, 'Aix-en-Provence');
assert.equal(chercher(index, '26678/pcrtD12duBekzn')[0].code, '06001');
assert.equal(chercher(index, 'Aiglun Alpes Maritimes')[0].code, '06001');
assert.equal(chercher(index, 'Draix')[0].code, '04072');

// Recherche sur nom COG y compris lorsqu'il diffère du libellé Pactols.
assert.ok(chercher(index, 'Les Mees').some(x => x.code === '04116'));
assert.equal(chercher(index, 'Le Castellet Var')[0].code, '83035');

// Les propositions ou géométries non validées ne doivent jamais être suggérées.
for (const code of ['06088', '13055', '83069']) {
  assert.ok(!codes.has(code), code + ' ne doit pas figurer parmi les codes validés');
  assert.deepEqual(chercher(index, code), []);
}
for (const nom of ['Nice', 'Marseille', 'Hyères']) {
  assert.deepEqual(chercher(index, nom), []);
}

assert.deepEqual(chercher(index, ''), []);
assert.deepEqual(chercher(index, '___'), []);
assert.equal(chercher(index, 'a', 3).length, 3);
assert.ok(chercher(index, 'a', 3).every(x => arks.has(x.ark)));
assert.ok(chercher(index, 'x', 0).length === 0);

// Chaque contour renvoie bien vers l'ARK validé du même code communal.
const byCode = new Map(index.map(x => [x.code, x.ark]));
for (const f of contours.features) {
  assert.equal(f.properties.ark_pactols, byCode.get(f.properties.code));
}
console.log('Lieux : index, recherche, exclusions et 103 correspondances géométriques OK.');
