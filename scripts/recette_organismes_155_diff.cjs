#!/usr/bin/env node
"use strict";
/* Recette A05c : toute différence hors des cinq fiches et de la provenance est interdite.
   On reconstitue exactement l'instantané 1.54 et compare sa signature canonique
   JSON.stringify (code-unités UTF-16), sans dépendance réseau. */
const fs = require("fs");
const assert = require("node:assert/strict");
const filename = process.argv[2] || "docs/data/organismes.json";
const data = JSON.parse(fs.readFileSync(filename, "utf8"));
assert.equal(data.provenance.source_filename,
  "AdlFI_referentiel_1-55_A05C_GAVS_PRETECH_INRAP_CANDIDAT.xlsx");
assert.equal(data.provenance.source_sha256,
  "2bd1df994401624fe84c0d696d1ecb1d13266d9b03cadb7ef76e3b65d3ae3c35");
data.provenance.source_filename = "AdlFI_referentiel_1-54_A05B_CNRS_INRAP_LABOS_CANDIDAT.xlsx";
data.provenance.source_sha256 = "32e69ba481331a0f1470c93ae40827e69dbb58cca20d739921459be30b218f15";
data.provenance.exported_at_utc = "2026-11-21T00:00:00+00:00";
const old = {
  "ORG-0004": [173, 18, 326],
  "ORG-0008": [46, 14, 270],
  "ORG-0078": [46, 4, 120],
  "ORG-0348": [9, 0, 9],
  "ORG-0451": [5, 0, 5],
};
for (const [id, arr] of Object.entries(old)) {
  const a = data.authorities.find(x => x.id === id);
  assert.ok(a, "Identifiant absent: " + id);
  a.usage = {
    affiliations_linked: arr[0],
    affiliations_validated: arr[1],
    source_occurrences_linked: arr[2]
  };
  if (id === "ORG-0451") {
    a.validation = {status: "a_verifier", established: false};
    a.activity.active = null;
    a.activity.start = null;
    a.geography.cities_label = null;
    a.quality.activity_unknown = true;
    a.quality.city_unrecorded = true;
  }
}
function fnv64(str) {
  let h = 0xcbf29ce484222325n;
  for (let i=0; i<str.length; i++) {
    h ^= BigInt(str.charCodeAt(i));
    h = (h * 0x100000001b3n) & 0xffffffffffffffffn;
  }
  return h.toString(16).padStart(16,"0");
}
assert.equal(fnv64(JSON.stringify(data)), "5e2d45664dca0fae",
  "Différences imprévues dans le JSON au-delà du lot A05c");
console.log("OK — reconstruction exacte du JSON 1.54, signature 5e2d45664dca0fae");
