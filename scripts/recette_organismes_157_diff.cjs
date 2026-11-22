#!/usr/bin/env node
"use strict";
/* A05e : reconstruire strictement le JSON publié 1.56 depuis 1.57.
   Toute modification autre que le compteur Nantes historique et la provenance est interdite. */
const fs=require("fs");
const assert=require("node:assert/strict");
const d=JSON.parse(fs.readFileSync(process.argv[2]||"docs/data/organismes.json","utf8"));
const src="AdlFI_referentiel_1-57_A05E_NANTES_GAVS_QUALIFIE_CANDIDAT.xlsx";
const sha="8408870084fc5bd2407f75a36cb308e28c220e21d1b3f03a61254bf03a87a009";
assert.equal(d.provenance.source_filename,src);
assert.equal(d.provenance.source_sha256,sha);
assert.equal(d.provenance.exported_at_utc,"2026-11-22T00:00:00+00:00");
assert.equal(d.authorities.length,934);
assert.equal(d.relations.length,600);
const n=d.authorities.find(a=>a.id==="ORG-0156");
assert.ok(n,"Université de Nantes historique manquante");
assert.deepEqual(n.usage,{affiliations_linked:3,affiliations_validated:2,source_occurrences_linked:9});
assert.equal(n.activity.end,"2021-12-31");
const next=d.authorities.find(a=>a.id==="ORG-0602");
assert.equal(next.activity.start,"2021-10-04");
const rel=d.relations.find(r=>r.id==="REL-0111");
assert.equal(rel.type,"succession_institutionnelle");
assert.equal(rel.start,"2022-01-01");
assert.equal(rel.source,"ORG-0156");
assert.equal(rel.target,"ORG-0602");
// Inversion de l'unique changement documentaire.
n.usage.affiliations_validated=1;
d.provenance.source_filename="AdlFI_referentiel_1-56_A05D_GAVS_PRETECH_QUALIFIE_CANDIDAT.xlsx";
d.provenance.source_sha256="0410751ceaea8831cac45935afc65dd71b2b187060f0641215c90ad1822ac389";
function fnv64(s){
 let h=0xcbf29ce484222325n;
 for(let i=0;i<s.length;i++)h=(h^BigInt(s.charCodeAt(i)))*0x100000001b3n&0xffffffffffffffffn;
 return h.toString(16).padStart(16,"0");
}
const actual=fnv64(JSON.stringify(d));
assert.equal(actual,"e81ea15b440106ee","Le JSON 1.57 diffère du JSON 1.56 hors A05e");
console.log("OK — version 1.56 reconstruite exactement : e81ea15b440106ee");
