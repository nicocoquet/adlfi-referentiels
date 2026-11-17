/* Autorités ISPF : 98 associées, 18 unités non subdivisées, zéro ARK dérivé. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const api=require('../docs/assets/lieux-polynesie-associees.js');
const d=JSON.parse(fs.readFileSync(path.join(__dirname,
 '../docs/data/lieux-polynesie/communes-associees-ispf-2026.json'),'utf8'));
const cog=JSON.parse(fs.readFileSync(path.join(__dirname,
 '../docs/data/lieux-outremer/recherche-2026.json'),'utf8'));
const a=api.creer(d,cog),by=code=>a.byId.get('ISPF:COMAS:'+code);
assert.equal(a.entries.length,98);
assert.equal(a.byId.size,98);
assert.equal(a.parParent.size,30);
assert.equal(a.nonSub.size,18);
assert.equal(a.statistiques.unites_nomenclature_fine,116);
assert.equal(a.statistiques.alignements_Pactols_communes_conserves,176);
assert.equal(a.statistiques.alignements_Pactols_collectivites_conserves,4);
assert.equal(by('111').label,'Anaa');
assert.equal(by('111').parentCode,'98711');
assert.equal(by('112').label,'Faaite');
assert.equal(by('112').parentCode,'98711');
assert.equal(by('141').parentCode,'98714');
assert.equal(by('441').label,'Avera (Rurutu)');
assert.equal(by('441').parentCode,'98744');
assert.equal(by('501').label,'Avera (Taputapuatea)');
assert.equal(by('501').parentCode,'98750');
assert.equal(by('451').parentCode,'98745');
assert.equal(a.parParent.get('98745').length,8);
assert.equal(a.nonSub.get('98719').code_ispf,'190'); // Gambier
assert.equal(a.nonSub.get('98712').code_ispf,'120'); // Arue
assert.equal(by('190'),undefined);
assert.equal(by('120'),undefined);
assert.equal(a.anomalieGeo.ligne_base_19000_absente,true);
assert.equal(a.anomalieGeo.lignes_iles_rattachees_19001_19016,16);
assert.equal(a.statistiques.iles_rattachees_lignes_Geo,64);
assert.equal(a.statistiques.nombre_iles_rattachees_notice_ISPF,63);
assert.equal(a.entries.filter(e=>e.arkValide!==null).length,0);
assert.ok(a.entries.every(e=>e.geometriePubliee===false));
assert.ok(a.entries.every(e=>e.codeInseePropre===null));
assert.ok(a.entries.every(e=>e.validiteHistoriqueEtablie===false));
assert.equal(Object.keys(cog.pactols_valides).length,176);
assert.equal(Object.keys(cog.pactols_collectivites_valides).length,4);
const dup=()=>JSON.parse(JSON.stringify(d));
let p=dup();p.communes_associees[0].commune_parent_cog='98712';
assert.throws(()=>api.creer(p,cog),/parent COG/);
p=dup();p.communes_associees[0].code_ispf='110';
assert.throws(()=>api.creer(p,cog),/parent COG/);
p=dup();p.unites_communes_non_subdivisees[0].code_ispf='111';
assert.throws(()=>api.creer(p,cog),/parent COG/);
p=dup();p.statistiques.nouveaux_ARK_Pactols_crees=1;
assert.throws(()=>api.creer(p,cog),/Comptes/);
p=dup();p.anomalie_geo_ispf.ligne_base_19000_absente=false;
assert.throws(()=>api.creer(p,cog),/Confusion/);
p=dup();p.source_ispf.sha256='une autre source';
assert.throws(()=>api.creer(p,cog),/Source ISPF/);
console.log('ISPF Polynésie : 98 associées, 18 non subdivisées, 30 parents COG, 5 subdivisions, 0 ARK, Gambier documenté — OK');
