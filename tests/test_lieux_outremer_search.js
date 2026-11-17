/* Contrôles du contrat public COG 2026 ultramarin. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const parser=require('../docs/assets/lieux-outremer-search.js');
const src=JSON.parse(fs.readFileSync(path.join(__dirname,'../docs/data/lieux-outremer/recherche-2026.json'),'utf8'));
const entries=parser.creerIndex(src);
const communes=entries.filter(e=>e.kind==='cog2026');
const autres=entries.filter(e=>e.kind==='autre_cog2026');
assert.equal(entries.length,233);
assert.equal(communes.length,212);
assert.equal(autres.length,21);
assert.equal(new Set(entries.map(e=>e.id)).size,233);
assert.equal(communes.filter(e=>e.arkValide).length,212);
assert.equal(communes.filter(e=>e.code.startsWith('987')&&e.arkValide).length,48);
assert.equal(communes.filter(e=>e.code.startsWith('974')&&e.arkValide).length,24);
assert.equal(communes.filter(e=>e.code.startsWith('971')&&e.arkValide).length,32);
assert.equal(communes.filter(e=>e.code.startsWith('972')&&e.arkValide).length,34);
assert.equal(communes.filter(e=>e.code.startsWith('973')&&e.arkValide).length,22);
assert.equal(communes.filter(e=>e.code.startsWith('976')&&e.arkValide).length,17);
assert.equal(communes.filter(e=>e.code.startsWith('975')&&e.arkValide).length,2);
assert.equal(communes.filter(e=>e.code.startsWith('988')&&e.arkValide).length,33);
assert.equal(communes.filter(e=>e.arkConfirme).length,0);
assert.deepEqual(communes.filter(e=>e.geomStatut==='PRESENTE_INVALIDE').map(e=>e.code).sort(),['98745','98805']);
assert.ok(entries.every(e=>e.geometriePubliee===false));
assert.ok(autres.every(e=>e.kind!=='cog2026'));
const find=id=>entries.find(e=>e.id===id);
const tahaa=find('COMER:COM:98745');
assert.equal(tahaa.label,'Tahaa');
assert.equal(tahaa.parent,'Polynésie française');
assert.equal(tahaa.arkValide,'26678/pcrteZcqWgVUaT');
assert.ok(tahaa.champs.includes(parser.normaliser(tahaa.arkValide)));
assert.equal(find('COMER:COM:98711').arkValide,'26678/pcrtwSlYRcWVFw');
assert.equal(find('COMER:COM:98735').arkValide,'26678/pcrtr90gKcAXiG');
assert.equal(find('COMER:COM:98758').arkValide,'26678/pcrtRw9F7i5M8l');
assert.ok(communes.filter(e=>e.code.startsWith('987')).every(e=>e.arkValide));
assert.equal(tahaa.geomStatut,'PRESENTE_INVALIDE');
const dumbea=find('COMER:COM:98805');
assert.equal(dumbea.parent,'Nouvelle-Calédonie');
assert.equal(dumbea.geomStatut,'PRESENTE_INVALIDE');
const abymes=find('DROM:COM:97101');
assert.equal(abymes.arkValide,'26678/pcrtWDyljRng0W');
assert.equal(find('DROM:COM:97107').arkValide,'26678/pcrtIusOs61efG');
assert.equal(find('DROM:COM:97130').arkValide,'26678/crtbDafDzHnlA');
assert.equal(find('DROM:COM:97131').arkValide,'26678/crtgLT3rnkE0n');
assert.ok(abymes.champs.includes(parser.normaliser(abymes.arkValide)));
assert.ok(communes.every(e=>!['97123','97127'].includes(e.code)));
const fort=find('DROM:COM:97209');
assert.equal(fort.arkValide,'26678/pcrtCSgHEYgAcm');
assert.equal(find('DROM:COM:97229').arkValide,'26678/pcrtUDcjFgqK9r');
assert.equal(find('DROM:COM:97234').arkValide,'26678/pcrtFk4CSrgt1O');
assert.ok(fort.champs.includes(parser.normaliser(fort.arkValide)));
const cayenne=find('DROM:COM:97302');
assert.equal(cayenne.arkValide,'26678/pcrtEim2rVrqfb');
assert.ok(cayenne.champs.includes(parser.normaliser(cayenne.arkValide)));
assert.equal(find('DROM:COM:97308').arkValide,'26678/pcrtFDuzqh49Ol');
assert.equal(find('DROM:COM:97360').arkValide,'26678/pcrtlaYvADNGdY');
assert.ok(communes.every(e=>!['97351','97354','97355','97359'].includes(e.code)));
const dembeni=find('DROM:COM:97607');
assert.equal(dembeni.arkValide,'26678/crtZcuFSJVYZU');
assert.equal(dembeni.arkConfirme,null);
assert.equal(dembeni.champs.includes(parser.normaliser(dembeni.arkValide)),true);
const leport=find('DROM:COM:97407');
assert.equal(leport.arkValide,'26678/pcrtIKvRT9vwUl');
assert.equal(leport.arkConfirme,null);
assert.ok(leport.champs.includes(parser.normaliser(leport.arkValide)));
assert.equal(find('DROM:COM:97414').arkValide,'26678/pcrtBwoUOdthOV');
assert.equal(find('DROM:COM:97424').arkValide,'26678/pcrtp3m5MZ822i');
const acoua=find('DROM:COM:97601');
assert.equal(acoua.arkValide,'26678/pcrtZfYYjyoUIE');
assert.ok(acoua.champs.includes(parser.normaliser(acoua.arkValide)));
assert.equal(find('COMER:CDM:98101').type,'Condominium');
assert.equal(find('COMER:DIS:98412').parent,'Terres australes et antarctiques françaises');
assert.equal(find('COMER:COM:97701').kind,'autre_cog2026');
assert.equal(find('COMER:COM:97801').kind,'autre_cog2026');
// Ne pas assimiler validité des identifiants et homologation des contours.
assert.equal(tahaa.geomStatut,'PRESENTE_INVALIDE');
assert.equal(tahaa.geometriePubliee,false);
assert.equal(find('COMER:TERRITOIRE:987').kind,'autre_cog2026');
assert.equal(find('COMER:TERRITOIRE:987').arkValide,undefined);
const codeArks=new Map(communes.filter(e=>e.arkValide).map(e=>[e.code,e.arkValide]));
assert.equal(codeArks.size,212);
assert.equal(new Set(codeArks.values()).size,212);
// Quatre collectivités validées dans un espace distinct des 212 communes.
const collectivites={
  '977':'26678/pcrtrGdtY56gmH',
  '978':'26678/pcrty5LooX8FgU',
  '986':'26678/pcrtwFq5jKHO3k',
  '987':'26678/pcrt4K8nLVxWOP'
};
assert.deepEqual(src.pactols_collectivites_valides,collectivites);
for(const [code,ark] of Object.entries(collectivites)){
  const ent=find('COMER:TERRITOIRE:'+code);
  assert.equal(ent.nature,'TERRITOIRE');
  assert.equal(ent.arkCollectiviteValide,ark);
  assert.equal(ent.arkValide,undefined);
  assert.ok(ent.champs.includes(parser.normaliser(ark)));
}
for(const id of [
 'COMER:COM:97701','COMER:COM:97801',
 'COMER:CIR:98611','COMER:CIR:98612','COMER:CIR:98613',
 'COMER:TERRITOIRE:975','COMER:TERRITOIRE:988',
 'COMER:TERRITOIRE:989']){
  assert.equal(find(id).arkCollectiviteValide,null,'Aucun ARK transféré à '+id);
}
assert.equal(communes.filter(e=>e.arkValide).length,212);
assert.equal(autres.filter(e=>e.arkCollectiviteValide).length,4);
assert.ok(entries.every(e=>e.geometriePubliee===false));
const copy=JSON.parse(JSON.stringify(src));
copy.pactols_valides['97607']='26678/pcrtInvalide';
assert.throws(()=>parser.creerIndex(copy),/Décisions/);
copy.pactols_valides=src.pactols_valides;
copy.communes['976']='97601|Acoua';
assert.throws(()=>parser.creerIndex(copy),/Nombre de communes/);
copy.communes=src.communes;
copy.contours_invalides=[];
assert.throws(()=>parser.creerIndex(copy),/Décisions/);
const copyCollect=JSON.parse(JSON.stringify(src));
copyCollect.pactols_collectivites_valides['97701']='26678/pcrtFaux';
assert.throws(()=>parser.creerIndex(copyCollect),/collectivités/);
delete copyCollect.pactols_collectivites_valides['97701'];
copyCollect.pactols_collectivites_valides['986']=copyCollect.pactols_collectivites_valides['987'];
assert.throws(()=>parser.creerIndex(copyCollect),/collectivités/);
console.log('COG Outre-mer : 212 communes, 21 autres, 212 Pactols communaux validés, 4 collectivités distinctes — OK');
