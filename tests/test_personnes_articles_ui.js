/* Test Node sans navigateur : le complément Gallia reste facultatif et non publiable sans visa. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../docs/assets/personnes.js'),'utf8');

class Element {
  constructor(tag,text=''){
    this.tag=tag;this.textContent=text;this.children=[];this.dataset={};
    this.events={};this.checked=false;this.hidden=false;this.open=false;
    this.classList={add(){},toggle(){},remove(){}};
  }
  appendChild(item){this.children.push(item);return item;}
  replaceChildren(...items){this.children=items;}
  setAttribute(name,value){this[name]=value;}
  addEventListener(name,fn){this.events[name]=fn;}
  remove(){}
}
const collectText=e=>(e.textContent||'')+e.children.map(collectText).join(' ');
const collectNodes=(e,tag)=>[...(e.tag===tag?[e]:[]),...e.children.flatMap(n=>collectNodes(n,tag))];

const base=()=>{
  const journal=(id,label,present,roles)=>({
    journal:id,label,data_status:present?'present':'awaiting_relations',
    roles:roles.map(([code,label])=>({code,label,source_code:null}))
  });
  const sections=['adlfi','gallia','gallia_prehistoire'].map((journal,i)=>({
    journal,label:journal,kind:i===0?'notice':'article',
    data_status:i===0?'present':'awaiting_relations'
  }));
  return {
    publication_status:'PUBLIC_PILOT',
    totals:{authorities:1,contributions:1,notices:1},
    authorities:[{id:'PER-000001',name:'Personne Exemple',family_name:'Exemple',
                  name_idref:'',identifiers:{idref:'028293290'},name_variants:[]}],
    contributions:[{person_id:'PER-000001',journal:'adlfi',
                    handle:'20.500.13089/xyz',roles:['aut'],
                    normalized_roles:['auteur'],
                    notice:{title:'Notice AdlFI',url:'https://journals.openedition.org/adlfi/123'}}],
    role_taxonomy:[
      journal('adlfi','AdlFI',true,[['auteur','Auteur'],['responsable_operation','Responsable d’opération']]),
      journal('gallia','Gallia',false,[['auteur','Auteur'],['collaborateur','Collaborateur']]),
      journal('gallia_prehistoire','Gallia Préhistoire',false,[['auteur','Auteur'],['collaborateur','Collaborateur']])
    ],
    publication_sections:sections
  };
};
const supplement=()=>({
  schema_version:'0.1.0',
  dataset:'adlfi-referentiels/personnes-articles',
  publication_status:'PUBLIC_PILOT',
  totals:{articles:1,contributions:2,authorities:1},
  articles:[{id:'heurist:1519:73:718',journal:'gallia',title:'Article de test',
             year:2020,volume:'Gallia, 77',first_page:'1',last_page:'8',
             url:'https://www.persee.fr/doc/xyz',doi:'10.4000/test'}],
  contributions:[
    {article_id:'heurist:1519:73:718',person_id:'PER-000001',role:'auteur',position_in_role:1},
    {article_id:'heurist:1519:73:718',person_id:'PER-000001',role:'collaborateur',position_in_role:1}
  ]
});
async function renderWith(optional, status=200){
  const nodes=new Map();
  const document={
    querySelector(selector){
      if(!nodes.has(selector))nodes.set(selector,new Element(selector));
      return nodes.get(selector);
    },
    createElement(tag){return new Element(tag);},
    createTextNode(value){return new Element('#text',value);},
    addEventListener(){}
  };
  const fetch=async url=>{
    if(url.endsWith('/personnes.json'))return {ok:true,status:200,json:async()=>base()};
    if(url.endsWith('/manifest.json'))return {ok:true,status:200,json:async()=>({available:{}})};
    if(url.endsWith('/personnes-articles.json'))return {
      ok:status!==404,status,
      json:async()=>optional
    };
    throw new Error('URL fetch inattendue : '+url);
  };
  vm.runInNewContext(source,{document,fetch,URL,Intl,Promise,Set,Map,console});
  await new Promise(resolve=>setImmediate(resolve));
  return nodes;
}
(async()=>{
  const valid=await renderWith(supplement());
  const cards=valid.get('#per-cards');
  assert.equal(cards.children.length,1);
  assert.match(collectText(cards),/Article de test/);
  assert.match(collectText(cards),/Gallia, 77.*2020.*1–8/);
  assert.match(collectText(cards),/Auteur.*Collaborateur/);
  assert.match(valid.get('#per-results').textContent,/3 contributions/);
  const links=collectNodes(cards,'a');
  assert.ok(links.some(link=>link.href==='https://www.persee.fr/doc/xyz'));
  const allText=collectText(valid.get('#per-role-facets'));
  assert.match(allText,/2 contributions/);

  const notValidated=supplement();
  notValidated.publication_status='CANDIDAT_NON_VALIDE';
  const excluded=await renderWith(notValidated);
  assert.doesNotMatch(collectText(excluded.get('#per-cards')),/Article de test/);
  assert.match(excluded.get('#per-results').textContent,/1 contribution/);

  const unexpected=supplement();
  unexpected.contributions[0].role='role_non_public';
  const rejected=await renderWith(unexpected);
  assert.doesNotMatch(collectText(rejected.get('#per-cards')),/Article de test/);

  const absent=await renderWith(null,404);
  assert.match(absent.get('#per-results').textContent,/1 contribution/);
  assert.doesNotMatch(collectText(absent.get('#per-cards')),/Article de test/);
  console.log('OK : interface AdlFI, complément public, rôles, liens Persée, rejet du candidat');
})().catch(err=>{console.error(err);process.exitCode=1;});
