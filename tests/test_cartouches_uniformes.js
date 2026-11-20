'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../docs/assets/organismes.js'),'utf8');
const apiBody=[
 '  globalThis.__cardTest={',
 '    setup:d=>{records=d.authorities;recordById=new Map(records.map(r=>[r.id,r]));',
 '      relsById=new Map();d.relations.forEach(rel=>{',
 '        if(!relsById.has(rel.source))relsById.set(rel.source,[]);relsById.get(rel.source).push(rel)});',
 '      indexEvolutions(d.relations);indexServiceChildren(d.relations);',
 '    },',
 '    card, parentBlock',
 '  };',
 '})();'
].join('\n');
assert.match(src,/\}\)\(\);\s*$/);
const instrumented=src.replace(/\}\)\(\);\s*$/,apiBody);
const context={fetch:()=>({then(){return this;},catch(){return this;}}),URL};
vm.runInNewContext(instrumented,context,{filename:'organismes.js'});
const api=context.__cardTest;
function row(id,name,{kind='ORG',type='collectivite_territoriale',bsr='COL',acronym=null,
  active=true,site=null,lab=null}={}){
 return {id,kind,names:{preferred:name,acronym,other_acronyms:[],history:[]},
  presentation:{visible:true,media:{image:null,logo:null}},
  identifiers:{lab,rnsr:null},
  classification:{type,bsr,sector:'public'},
  geography:{cities_label:'Paris',institutional_country_iso2:'FR'},
  activity:{active,start:'1900',end:null},website:site,usage:{affiliations_linked:2}};
}
const ville=row('ORG-0697','Ville de Menton');
const musee=row('SER-0180','Musée de Préhistoire régionale de Menton',{kind:'SER',type:'musee',bsr:'MUS'});
const association=row('ORG-0689','Centre de ressources de botanique appliquée',{type:'association',bsr:'ASS',acronym:'CRBA'});
const lab=row('ORG-0151','TRACES',{type:'laboratoire',bsr:'LAB',acronym:'TRACES',lab:'UMR 5608',site:'https://traces.univ-tlse2.fr/'});
api.setup({authorities:[ville,musee,association,lab],relations:[
 {id:'RSE-001',source:musee.id,target:ville.id,type:'rattachement_service',validation:'valide'},
 {id:'REL-001',source:lab.id,target:ville.id,type:'tutelle',validation:'valide'}
]});
for(const authority of [ville,musee,association,lab]){
 const html=api.card(authority);
 assert.match(html,/class="authority-card laboratory-card/,
   'Les cartouches utilisent la même structure visuelle');
 assert.match(html,/class="lab-layout"/);
 assert.match(html,/class="lab-visual"/);
 assert.match(html,/class="lab-content"/);
 assert.match(html,/Consulter la fiche/);
 assert.doesNotMatch(html,/lab-logo-band|lab-tutelle-logo/,
   'Les tutelles et rattachements ne deviennent plus un bandeau de logos');
}
const cityHtml=api.card(ville);
assert.match(cityHtml,/Services liés/, 'La collectivité affiche ses services rattachés');
assert.match(cityHtml,/data-detail="SER-0180"/,
 'La collectivité permet de naviguer vers le musée (relation entrante)');
const museumHtml=api.card(musee);
assert.match(museumHtml,/Musée/);
assert.match(museumHtml,/data-detail="ORG-0697"/,
 'Le musée permet de naviguer vers sa collectivité de rattachement');
assert.match(museumHtml,/aria-label="Consulter la fiche de Ville de Menton"/);
assert.match(api.card(lab),/href="https:\/\/traces\.univ-tlse2\.fr\/"/);
assert.match(api.card(association),/Association/);
assert.match(src,/\$\('#cards'\)\.addEventListener\('click'/,
 'Le gestionnaire de clic des cartouches reste délégué');
console.log('OK — cartouches homogènes COL/MUS/ASS/LAB et rattachements navigables');
