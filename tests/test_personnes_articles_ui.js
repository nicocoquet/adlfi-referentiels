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
                  name_idref:'',identifiers:{idref:'028293290'},contributions_count:1,name_variants:[]}],
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
async function renderWith(optional, status=200, profile=base){
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
    if(url.endsWith('/personnes.json'))return {ok:true,status:200,json:async()=>profile()};
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

  // Une nouvelle autorité Heurist peut exister avec des articles Gallia,
  // sans aucune relation et sans aucune notice AdlFI fictive.
  const galliaOnlyPersons=()=>{
    const p=base();
    p.authorities.push({
      id:'PER-000203',name:'Personne Gallia uniquement',family_name:'Gallia',
      name_idref:'',identifiers:{idref:'99000001X'},
      contributions_count:0,name_variants:[]
    });
    p.totals.authorities=2;
    return p;
  };
  const galliaOnlyArticles=()=>{
    const a=supplement();
    a.contributions.push({
      article_id:'heurist:1519:73:718',person_id:'PER-000203',
      role:'collaborateur',position_in_role:1
    });
    a.totals.contributions=3;
    a.totals.authorities=2;
    return a;
  };
  const extra=await renderWith(galliaOnlyArticles(),200,galliaOnlyPersons);
  const extendedCards=extra.get('#per-cards');
  assert.equal(extendedCards.children.length,2);
  const galliaCard=extendedCards.children.find(x=>collectText(x).includes('Personne Gallia uniquement'));
  assert.ok(galliaCard,'L’autorité sans notice AdlFI doit être affichée');
  assert.match(collectText(galliaCard),/Article de test/);
  assert.match(collectText(galliaCard),/Collaborateur/);
  assert.doesNotMatch(collectText(galliaCard),/Consulter les notices AdlFI liées/);
  assert.match(extra.get('#per-results').textContent,/2 autorités.*4 contributions/);

  const absent=await renderWith(null,404);
  assert.match(absent.get('#per-results').textContent,/1 contribution/);
  assert.doesNotMatch(collectText(absent.get('#per-cards')),/Article de test/);
  // Recette d'intégration sur les données effectivement publiées, en complément des fixtures.
  const realPeople=JSON.parse(fs.readFileSync(path.join(__dirname,'../docs/data/personnes.json'),'utf8'));
  const realArticles=JSON.parse(fs.readFileSync(path.join(__dirname,'../docs/data/personnes-articles.json'),'utf8'));
  const live=await renderWith(realArticles,200,()=>realPeople);
  const liveCards=live.get('#per-cards');
  // Les effectifs affichés doivent suivre les catalogues publiés et non rester
  // figés sur le troisième lot ; les jalons antérieurs restent contrôlés ci-dessous.
  assert.equal(liveCards.children.length,realPeople.totals.authorities);
  assert.ok(liveCards.children.length>=602,'Le quatrième lot de 160 PER doit rester publié');
  assert.ok(liveCards.children.length>=802,'Le cinquième lot de 200 PER doit rester publié');
  assert.equal(realPeople.totals.contributions,1980,'Les contributions AdlFI restent constantes');
  assert.ok(realArticles.totals.contributions>=1960,'Le quatrième lot bibliographique doit rester publié');
  const displayContributions=realPeople.totals.contributions+realArticles.totals.contributions;
  assert.match(live.get('#per-results').textContent,
               new RegExp(realPeople.totals.authorities+' autorités affichées.*'+displayContributions+' contributions'));
  const newPerson=liveCards.children.find(x=>collectText(x).includes('PER-000203'));
  assert.ok(newPerson,'Une nouvelle autorité bibliographique doit apparaître');
  assert.match(collectText(newPerson),/Christine Oberlin/);
  assert.match(collectText(newPerson),/Gallia/);
  assert.doesNotMatch(collectText(newPerson),/Consulter les notices AdlFI liées/);
  const noUrlPerson=liveCards.children.find(x=>collectText(x).includes('PER-000231'));
  assert.ok(noUrlPerson,'La fiche contenant un article dépourvu d’URL doit apparaître');
  const noUrlTitle='Découverte de la tombe d\'un oculiste à Lyon';
  assert.match(collectText(noUrlPerson),/Découverte de la tombe d'un oculiste à Lyon/);
  assert.ok(!collectNodes(noUrlPerson,'a').some(x=>(x.textContent||'').includes(noUrlTitle)),
            'Un article sans URL ne doit pas recevoir un lien artificiel');
  const secondPilot=liveCards.children.find(x=>collectText(x).includes('PER-000243'));
  assert.ok(secondPilot,'Une autorité du deuxième pilote Heurist doit apparaître');
  assert.match(collectText(secondPilot),/Frédérique Blaizot/);
  assert.match(collectText(secondPilot),/Gallia/);
  assert.doesNotMatch(collectText(secondPilot),/Consulter les notices AdlFI liées/);
  const oldNoUrl=liveCards.children.find(x=>collectText(x).includes('PER-000312'));
  assert.ok(oldNoUrl,'La fiche du nouveau pilote liée à un article sans URL doit apparaître');
  assert.match(collectText(oldNoUrl),/XIIe Circonscription \[préhistorique\]/);
  // Plusieurs articles historiques ont le même titre : cibler la notice
  // bibliographique de 1957 et non toutes les autres occurrences de ce titre.
  const unlinked1957=collectNodes(oldNoUrl,'li').find(x=>
    collectText(x).includes('XIIe Circonscription [préhistorique]') &&
    collectText(x).includes('Gallia, 15-3') && collectText(x).includes('1957'));
  assert.ok(unlinked1957,'La référence de 1957 sans URL doit être affichée');
  assert.equal(collectNodes(unlinked1957,'a').length,0,
               'La référence de 1957 sans URL ne doit pas recevoir de lien');
  const thirdPilot=liveCards.children.find(x=>collectText(x).includes('PER-000323'));
  assert.ok(thirdPilot,'La première autorité du troisième pilote Heurist doit apparaître');
  assert.match(collectText(thirdPilot),/Aurélia Borvon/);
  assert.match(collectText(thirdPilot),/Gallia/);
  assert.doesNotMatch(collectText(thirdPilot),/Consulter les notices AdlFI liées/);
  const thirdNoUrl=liveCards.children.find(x=>collectText(x).includes('PER-000442'));
  assert.ok(thirdNoUrl,'La dernière autorité du troisième pilote doit apparaître');
  const missingLinkRef=collectNodes(thirdNoUrl,'li').find(x=>
    collectText(x).includes('Recherches archéologiques en Gaule en 1954') &&
    collectText(x).includes('Gallia, 15-3') && collectText(x).includes('1957'));
  assert.ok(missingLinkRef,'L’article de 1957 sans URL doit être rendu avec sa référence');
  assert.equal(collectNodes(missingLinkRef,'a').length,0,
               'L’article sans URL ne doit pas recevoir un lien fabriqué');
  // Quatrième lot : 160 autorités bibliographiques sans création de notice AdlFI.
  const fourthAuthorities=realPeople.authorities.filter(x=>{
    const num=Number(x.id.replace('PER-',''));
    return num>=443 && num<=602;
  });
  assert.equal(fourthAuthorities.length,160);
  assert.ok(fourthAuthorities.every(x=>x.contributions_count===0));
  const fourthRelations=realArticles.contributions.filter(x=>{
    const num=Number(x.person_id.replace('PER-',''));
    return num>=443 && num<=602;
  });
  assert.equal(fourthRelations.length,551);
  const fourthFirst=liveCards.children.find(x=>collectText(x).includes('PER-000443'));
  assert.ok(fourthFirst,'La première autorité du quatrième lot doit être affichée');
  assert.match(collectText(fourthFirst),/Yves Desfossés/);
  assert.doesNotMatch(collectText(fourthFirst),/Consulter les notices AdlFI liées/);
  const fourthLast=liveCards.children.find(x=>collectText(x).includes('PER-000602'));
  assert.ok(fourthLast,'La dernière autorité du quatrième lot doit être affichée');
  assert.match(collectText(fourthLast),/Laurent Klaric/);
  assert.doesNotMatch(collectText(fourthLast),/Consulter les notices AdlFI liées/);
  // Cinquième lot : 200 autorités exclusivement bibliographiques.
  const fifthAuthorities=realPeople.authorities.filter(x=>{
    const num=Number(x.id.replace('PER-',''));
    return num>=603 && num<=802;
  });
  assert.equal(fifthAuthorities.length,200);
  assert.ok(fifthAuthorities.every(x=>x.contributions_count===0));
  const fifthRelations=realArticles.contributions.filter(x=>{
    const num=Number(x.person_id.replace('PER-',''));
    return num>=603 && num<=802;
  });
  assert.ok(fifthRelations.length>=479);
  assert.ok(fifthRelations.some(x=>x.role==='auteur'));
  assert.ok(fifthRelations.some(x=>x.role==='collaborateur'));
  const fifthFirst=liveCards.children.find(x=>collectText(x).includes('PER-000603'));
  const fifthLast=liveCards.children.find(x=>collectText(x).includes('PER-000802'));
  assert.ok(fifthFirst && fifthLast,'Les autorités extrêmes du cinquième lot doivent apparaître');
  assert.match(collectText(fifthFirst),/Claude Constantin/);
  assert.match(collectText(fifthLast),/Philippe Guillerault/);
  assert.doesNotMatch(collectText(fifthFirst),/Consulter les notices AdlFI liées/);
  assert.doesNotMatch(collectText(fifthLast),/Consulter les notices AdlFI liées/);
  // Sixième lot : 200 autorités exclusivement bibliographiques, sans notices fictives.
  const sixthAuthorities=realPeople.authorities.filter(x=>{
    const num=Number(x.id.replace('PER-',''));
    return num>=803 && num<=1002;
  });
  assert.equal(sixthAuthorities.length,200);
  assert.ok(sixthAuthorities.every(x=>x.contributions_count===0));
  const sixthRelations=realArticles.contributions.filter(x=>{
    const num=Number(x.person_id.replace('PER-',''));
    return num>=803 && num<=1002;
  });
  assert.equal(sixthRelations.length,452);
  assert.equal(sixthRelations.filter(x=>x.role==='auteur').length,388);
  assert.equal(sixthRelations.filter(x=>x.role==='collaborateur').length,64);
  const sixthFirst=liveCards.children.find(x=>collectText(x).includes('PER-000803'));
  const sixthLast=liveCards.children.find(x=>collectText(x).includes('PER-001002'));
  assert.ok(sixthFirst && sixthLast,'Les autorités extrêmes du sixième lot doivent apparaître');
  assert.match(collectText(sixthFirst),/Jean Le Gall/);
  assert.match(collectText(sixthLast),/Amable Audin/);
  assert.doesNotMatch(collectText(sixthFirst),/Consulter les notices AdlFI liées/);
  assert.doesNotMatch(collectText(sixthLast),/Consulter les notices AdlFI liées/);
  assert.match(collectText(sixthFirst),/Gallia Préhistoire/);
  // Septième lot : 200 autorités exclusivement bibliographiques, sans notices fictives.
  const seventhAuthorities=realPeople.authorities.filter(x=>{
    const num=Number(x.id.replace('PER-',''));
    return num>=1003 && num<=1202;
  });
  assert.equal(seventhAuthorities.length,200);
  assert.ok(seventhAuthorities.every(x=>x.contributions_count===0));
  const seventhRelations=realArticles.contributions.filter(x=>{
    const num=Number(x.person_id.replace('PER-',''));
    return num>=1003 && num<=1202;
  });
  assert.equal(seventhRelations.length,586);
  assert.equal(seventhRelations.filter(x=>x.role==='auteur').length,545);
  assert.equal(seventhRelations.filter(x=>x.role==='collaborateur').length,41);
  const seventhFirst=liveCards.children.find(x=>collectText(x).includes('PER-001003'));
  const seventhLast=liveCards.children.find(x=>collectText(x).includes('PER-001202'));
  assert.ok(seventhFirst && seventhLast,'Les autorités extrêmes du septième lot doivent apparaître');
  assert.match(collectText(seventhFirst),/Guillaume Asselin/);
  assert.match(collectText(seventhLast),/Sandrine Paradis-Grenouillet/);
  assert.doesNotMatch(collectText(seventhFirst),/Consulter les notices AdlFI liées/);
  assert.doesNotMatch(collectText(seventhLast),/Consulter les notices AdlFI liées/);
  assert.match(collectText(seventhFirst),/Gallia/);
  console.log('OK : interface réelle '+realPeople.totals.authorities+' PER / '+displayContributions+
              ' contributions, sept lots Heurist et références sans URL');

})().catch(err=>{console.error(err);process.exitCode=1;});
