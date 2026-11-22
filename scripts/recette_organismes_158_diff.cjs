#!/usr/bin/env node
"use strict";
/* A05f : reconstituer exactement le JSON public 1.57 depuis la version 1.58. */
const fs=require("fs"),assert=require("node:assert/strict");
const d=JSON.parse(fs.readFileSync(process.argv[2]||"docs/data/organismes.json","utf8"));
assert.equal(d.provenance.source_filename,"AdlFI_referentiel_1-58_A05F_ARCHEO_ATLANTICA_CANDIDAT.xlsx");
assert.equal(d.provenance.source_sha256,"6aa15da3019bc0a08987cd48631e95d09172d36b9fb80009b10a9636f1bf67d8");
assert.equal(d.provenance.exported_at_utc,"2026-11-22T00:00:00+00:00");
assert.equal(d.authorities.length,935);
assert.equal(d.relations.length,600);
const idx=d.authorities.findIndex(x=>x.id==="ORG-0756");
assert.equal(idx,734,"ORG-0756 doit être insérée immédiatement après ORG-0755");
const a=d.authorities[idx];
assert.deepEqual(a.validation,{status:"valide",established:true});
assert.deepEqual(a.names,{preferred:"Archéo Atlantica",acronym:null,other_acronyms:[],historical_free_text:null,history:[],legal_status_history:[]});
assert.deepEqual(a.classification,{type:"entreprise",bsr:"PRIV",sector:"prive",level:null,level_origin:null,territorial_competence:null});
assert.deepEqual(a.activity,{active:null,start:null,end:null,catalog:"inclure"});
assert.equal(a.presentation.visible,true);
assert.deepEqual(a.presentation.media,{image:null,logo:null});
assert.deepEqual(a.geography,{institutional_country_iso2:"FR",cities_label:"Batz-sur-Mer",locations:[]});
assert.deepEqual(a.usage,{affiliations_linked:1,affiliations_validated:1,source_occurrences_linked:1});
d.authorities.splice(idx,1);
assert.deepEqual([d.totals.authorities,d.totals.organismes,d.totals.catalog_included],[935,735,683]);
d.totals.authorities=934;d.totals.organismes=734;d.totals.catalog_included=682;
d.provenance.source_filename="AdlFI_referentiel_1-57_A05E_NANTES_GAVS_QUALIFIE_CANDIDAT.xlsx";
d.provenance.source_sha256="8408870084fc5bd2407f75a36cb308e28c220e21d1b3f03a61254bf03a87a009";
function fnv64(s){
 let h=0xcbf29ce484222325n;
 for(let i=0;i<s.length;i++)h=(h^BigInt(s.charCodeAt(i)))*0x100000001b3n&0xffffffffffffffffn;
 return h.toString(16).padStart(16,"0");
}
assert.equal(fnv64(JSON.stringify(d)),"ad60b33169cb47f8",
"Le JSON 1.58 diffère de 1.57 hors de l'autorité A05f et des cinq compteurs/provenances");
console.log("OK — publication 1.57 reconstituée exactement (ad60b33169cb47f8)");
