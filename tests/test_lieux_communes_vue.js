'use strict';
const assert=require('node:assert/strict');
const vue=require('../docs/assets/lieux-communes-vue.js');

const sources={
 paca:[[42.8,4.2],[45.3,7.9]],
 corse:[[41.2,8.5],[43.2,9.7]],
 pdl:[[46.9,-2.7],[48.7,0.9]],
 bfc:[[46.0,2.7],[49.0,8.0]]
};
const national=[[41.2,-5.7],[51.4,10.1]];
assert.equal(vue.ZOOM_REDUCTION,7);
assert.deepEqual(vue.zonesPourVue(national,6,sources),['paca','corse','pdl','bfc'],
 'Au zoom national, ne pas masquer les quatre régions publiées');
assert.deepEqual(vue.zonesPourVue([[47.1,-1.8],[47.9,-.3]],9,sources),['pdl'],
 'Vue nantaise : charger seulement les Pays de la Loire');
assert.deepEqual(vue.zonesPourVue([[42.9,8.8],[43.1,9.5]],9,sources),['corse']);
assert.deepEqual(vue.zonesPourVue([[46.6,4.0],[47.5,6.1]],9,sources),['bfc']);
assert.deepEqual(vue.zonesPourVue([[43.4,5.1],[44.1,5.8]],9,sources),['paca']);
assert.deepEqual(vue.zonesPourVue([[48.7,2.1],[48.9,2.5]],9,sources),[],
 'Les communes franciliennes ne sont pas publiées : ne pas inventer une région chargée');
assert.deepEqual(vue.zonesPourVue([[45.0,6.1],[46.2,7.1]],9,sources),['paca','bfc'],
 'Au contact de régions, ne pas perdre les communes voisines');
assert(vue.intersecte([[42.9,5.1],[44.2,6.1]],sources.paca));
assert(!vue.intersecte([[48.1,-2.1],[48.2,-1.8]],sources.bfc));
assert.equal(vue.cle(['pdl','bfc','pdl']),vue.cle(['bfc','pdl']));
assert.throws(()=>vue.zonesPourVue(null,9,sources),/Paramètres/);
assert.throws(()=>vue.zonesPourVue(national,9,{x:[1,2]}),/Emprise/);
console.log('LIEUX_COMMUNES_VUE_OK — national conservé, ciblage spatial, bords et invalides');
