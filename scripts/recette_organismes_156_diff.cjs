#!/usr/bin/env node
"use strict";
// Reconstruction stricte de 1.55 depuis 1.56 ; aucun autre champ ne peut changer.
const fs=require("fs"),assert=require("node:assert/strict");
const d=JSON.parse(fs.readFileSync(process.argv[2]||"docs/data/organismes.json","utf8"));
assert.equal(d.provenance.source_filename,
  "AdlFI_referentiel_1-56_A05D_GAVS_PRETECH_QUALIFIE_CANDIDAT.xlsx");
assert.equal(d.provenance.source_sha256,
  "0410751ceaea8831cac45935afc65dd71b2b187060f0641215c90ad1822ac389");
d.provenance.source_filename="AdlFI_referentiel_1-55_A05C_GAVS_PRETECH_INRAP_CANDIDAT.xlsx";
d.provenance.source_sha256="2bd1df994401624fe84c0d696d1ecb1d13266d9b03cadb7ef76e3b65d3ae3c35";
const older={"ORG-0004":19,"ORG-0008":17,"ORG-0192":0,"ORG-0241":0,
             "ORG-0348":1,"ORG-0351":0,"ORG-0451":3,"SER-0041":0};
for(const [id,n] of Object.entries(older)){
  const x=d.authorities.find(a=>a.id===id);
  assert.ok(x,id+" absent");
  x.usage.affiliations_validated=n;
}
function fnv64(s){
 let h=0xcbf29ce484222325n;
 for(let i=0;i<s.length;i++)h=(h^BigInt(s.charCodeAt(i)))*0x100000001b3n&0xffffffffffffffffn;
 return h.toString(16).padStart(16,"0");
}
assert.equal(fnv64(JSON.stringify(d)),"78878d86e3a9e382",
  "La publication 1.56 diffère de 1.55 hors du lot A05d");
console.log("OK — publication 1.55 exactement reconstituée (78878d86e3a9e382)");
