'use strict';
// Les relations validées vers une autorité hors catalogue restent navigables.
// Les cartouches de recherche demeurent strictement limités aux autorités visibles.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'docs/assets/organismes.js'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(root,'docs/data/organismes.json'),'utf8'));
const inject=[
  '  globalThis.__contextualTest={',
  '    setup:d=>{records=d.authorities;recordById=new Map(records.map(a=>[a.id,a]));',
  '      relsById=new Map();d.relations.forEach(x=>{',
  '        if(!relsById.has(x.source))relsById.set(x.source,[]);relsById.get(x.source).push(x)});',
  '      indexEvolutions(d.relations);indexServiceChildren(d.relations);',
  '    },',
  '    parentBlock,childrenBlock,evolutionBlock,card,baseCount:()=>baseRecords().length',
  '  };',
  '})();'
].join('\n');
assert.match(source,/\}\)\(\);\s*$/);
const ctx={fetch:()=>({then(){return this;},catch(){return this;}}),URL};
vm.runInNewContext(source.replace(/\}\)\(\);\s*$/,inject),ctx,{filename:'organismes.js'});
const api=ctx.__contextualTest;
api.setup(data);
const byId=new Map(data.authorities.map(a=>[a.id,a]));
const valid=new Set(['valide','validee','validée']);
const established=data.relations.filter(r=>r.type==='rattachement_service'
  && valid.has(r.validation) && byId.get(r.source)?.kind==='SER'
  && byId.get(r.source)?.presentation.visible
  && byId.has(r.target) && !byId.get(r.target).presentation.visible);
assert.equal(established.length,195,'195 rattachements validés vers des autorités hors catalogue');
assert.equal(new Set(established.map(r=>r.source)).size,175);
assert.equal(new Set(established.map(r=>r.target)).size,171);
assert.equal(data.authorities.length,934);
assert.equal(api.baseCount(),682,'La recherche ne contient que les 682 autorités visibles');
for(const rel of established){
  const sourceAuthority=byId.get(rel.source);
  const targetAuthority=byId.get(rel.target);
  const html=api.parentBlock(sourceAuthority,false);
  assert.ok(html.includes('data-detail="'+targetAuthority.id+'"'),
    'Lien contextuel manquant : '+rel.id+' '+rel.source+' → '+rel.target);
  assert.match(html,/class="attachment-item attachment-link"/);
}
const museum=byId.get('SER-0180'),ville=byId.get('ORG-0697');
assert.equal(museum.presentation.visible,true);
assert.equal(ville.presentation.visible,false);
assert.match(api.card(museum),/data-detail="ORG-0697"/);
assert.match(api.childrenBlock(ville),/data-detail="SER-0180"/,
  'Retour de la fiche contextuelle vers le service visible');
assert.doesNotMatch(api.card(museum),/data-id="ORG-0697"/,
  'Aucun cartouche autonome de la ville dans le résultat du service');
const candidate=byId.get('SER-0178');
assert.doesNotMatch(api.parentBlock(candidate),/data-detail="ORG-0700"/,
  'Rattachement à vérifier : ne pas afficher comme validé');
assert.match(source,/const baseRecords = \(\) => records\.filter\(r=>r\.presentation\.visible\)/,
  'Les fiches hors catalogue ne doivent pas rejoindre la recherche');
assert.match(source,/Autorité hors catalogue : cette fiche est consultable par les relations/);
console.log('OK — 195 rattachements navigables, 682 cartouches, 934 fiches, statut éditorial préservé');
