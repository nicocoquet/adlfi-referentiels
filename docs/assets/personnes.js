(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const norm = x => String(x ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const create = (tag, cls, value) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (value !== undefined) node.textContent = value;
    return node;
  };
  const allowUrl = (raw, origin) => {
    try {const u = new URL(raw); return u.protocol === 'https:' && u.hostname === origin ? u.href : null;}
    catch {return null;}
  };
  const addLink = (parent, label, url, origin) => {
    const safe = allowUrl(url, origin);
    const child = create(safe ? 'a' : 'span', '', label);
    if (safe) {child.href = safe;child.target='_blank';child.rel='noopener noreferrer';}
    parent.appendChild(child);
  };
  let data;
  let articleWorks=[];
  let iconManifest={};
  // Le catalogue AdlFI reste indépendant des éventuelles contributions aux articles.
  const allContributions = () => data.contributions.concat(articleWorks);
  const allowArticleUrl = raw => {
    try {
      const hostname = new URL(raw).hostname;
      return ['journals.openedition.org','www.persee.fr'].includes(hostname) ? allowUrl(raw, hostname) : null;
    } catch {return null;}
  };
  // Chargement interdit pour les projections non visées (CANDIDAT_NON_VALIDE).
  const attachPublishedArticles = payload => {
    if (!payload || payload.publication_status!=='PUBLIC_PILOT' ||
        payload.dataset!=='adlfi-referentiels/personnes-articles' ||
        payload.schema_version!=='0.1.0' || !Array.isArray(payload.articles) ||
        !Array.isArray(payload.contributions)) throw Error('Catalogue complémentaire non publiable');
    const articles=new Map();
    for(const a of payload.articles){
      if(!['gallia','gallia_prehistoire'].includes(a.journal) || articles.has(a.id) ||
         typeof a.title!=='string' || !a.title.trim()) throw Error('Article complémentaire invalide');
      articles.set(a.id,a);
    }
    const people=new Set(data.authorities.map(p=>p.id));
    const pairs=new Set(), works=[], linkedPeople=new Set();
    for(const c of payload.contributions){
      const article=articles.get(c.article_id);
      if(!article || !people.has(c.person_id) || !['auteur','collaborateur'].includes(c.role))
        throw Error('Contribution complémentaire non publiable');
      const pair=[c.article_id,c.person_id,c.role].join('|');
      if(pairs.has(pair)) throw Error('Contribution complémentaire répétée');
      pairs.add(pair);linkedPeople.add(c.person_id);
      works.push({
        person_id:c.person_id, journal:article.journal,
        handle:c.article_id, normalized_roles:[c.role],
        notice:{title:article.title,url:article.url},
        bibliography:{volume:article.volume,year:article.year,
                      first_page:article.first_page,last_page:article.last_page}
      });
    }
    if(!payload.totals || payload.totals.articles!==articles.size ||
       payload.totals.contributions!==works.length ||
       payload.totals.authorities!==linkedPeople.size ||
       new Set(works.map(c=>c.handle)).size!==articles.size)
      throw Error('Effectifs bibliographiques incohérents');
    articleWorks=works;
    for(const item of data.role_taxonomy){
      if(item.journal!=='adlfi') item.data_status='present';
    }
    for(const item of data.publication_sections){
      if(item.journal!=='adlfi') item.data_status='present';
    }
  };
  const iconDefinitions=[
    {key:'idref',name:'IdRef',glyph:'ID',origin:'www.idref.fr',pattern:/^[0-9]{8}[0-9X]$/,url:v=>'https://www.idref.fr/'+v},
    {key:'bnf',name:'BnF',glyph:'BnF',origin:'data.bnf.fr',pattern:/^cb[0-9]{8}[0-9a-z]$/,url:v=>'https://data.bnf.fr/ark:/12148/'+v},
    {key:'orcid',name:'ORCID',glyph:'ORC',origin:'orcid.org',pattern:/^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9X]{4}$/,url:v=>'https://orcid.org/'+v},
    {key:'idhal',name:'HAL',glyph:'HAL',origin:'cv.hal.science',pattern:/^[A-Za-z0-9_-]+$/,url:v=>'https://cv.hal.science/'+encodeURIComponent(v)},
    {key:'persee',name:'Persée',glyph:'P',origin:'www.persee.fr',pattern:/^[0-9]+$/,url:v=>'https://www.persee.fr/authority/'+v},
    {key:'wikidata',name:'Wikidata',glyph:'W',origin:'www.wikidata.org',pattern:/^Q[1-9][0-9]*$/,url:v=>'https://www.wikidata.org/wiki/'+v}
  ];
  // La forme IdRef inversée fournit une clef de tri patronymique explicite.
  // Secours : patronyme déclaré, puis nom affiché ; tie-break PER stable.
  const familySortKey = person => {
    const idref=String(person.name_idref || '');
    return person.family_name || (idref.includes(',') ? idref.split(',')[0].trim() : person.name);
  };
  const surnameCollator = new Intl.Collator('fr', {sensitivity:'base', numeric:true});
  const surnameOrder = (a,b) =>
    surnameCollator.compare(familySortKey(a),familySortKey(b)) ||
    surnameCollator.compare(a.name,b.name) || a.id.localeCompare(b.id);
  const state = {q:'', selected:new Set(), expanded:new Set(['adlfi'])};
  // Une revue constitue l'union de ses rôles. Les différents filtres sont unis (OU).
  const key = (journal, role='') => journal + ':' + role;
  const isParentSelected = group => state.selected.has(key(group.journal)) || group.roles.every(r => state.selected.has(key(group.journal,r.code)));
  const checkedRole = (group, role) => state.selected.has(key(group.journal)) || state.selected.has(key(group.journal,role.code));
  const matchesSelection = c => !state.selected.size || state.selected.has(key(c.journal)) || c.normalized_roles.some(r => state.selected.has(key(c.journal,r)));
  const labelFor = c => {
    const group = data.role_taxonomy.find(x => x.journal === c.journal);
    if (!group) return c.journal;
    return group.label + ' · ' + c.normalized_roles.map(r => group.roles.find(x => x.code === r)?.label || r).join(', ');
  };
  function changeParent(group, checked) {
    for (const role of group.roles) state.selected.delete(key(group.journal,role.code));
    if (checked) state.selected.add(key(group.journal));
    else state.selected.delete(key(group.journal));
    renderFacets();render();
  }
  function changeChild(group, role, checked) {
    // En décochant un rôle d'une revue entière, conserver l'autre rôle sélectionné.
    if (state.selected.has(key(group.journal))) {
      state.selected.delete(key(group.journal));
      for (const sibling of group.roles) state.selected.add(key(group.journal,sibling.code));
    }
    const id=key(group.journal,role.code);
    if (checked) state.selected.add(id);
    else state.selected.delete(id);
    if (group.roles.every(x=>state.selected.has(key(group.journal,x.code)))) {
      for (const x of group.roles) state.selected.delete(key(group.journal,x.code));
      state.selected.add(key(group.journal));
    }
    renderFacets();render();
  }
  function renderFacets() {
    const root=$('#per-role-facets');root.replaceChildren();
    for (const group of data.role_taxonomy) {
      const block=create('div','per-role-group');
      const header=create('div','per-role-heading');
      const disclosure=create('button','per-role-expand',state.expanded.has(group.journal)?'▾':'▸');
      disclosure.type='button';
      disclosure.setAttribute('aria-label',(state.expanded.has(group.journal)?'Masquer':'Afficher')+' les rôles de '+group.label);
      disclosure.setAttribute('aria-expanded',String(state.expanded.has(group.journal)));
      const childId='per-roles-'+group.journal;
      disclosure.setAttribute('aria-controls',childId);
      disclosure.addEventListener('click',()=>{
        if (state.expanded.has(group.journal))state.expanded.delete(group.journal);
        else state.expanded.add(group.journal);
        renderFacets();
      });
      header.appendChild(disclosure);
      const journalLabel=create('label','per-role-journal-label');
      const parentInput=document.createElement('input');
      parentInput.type='checkbox';parentInput.value=key(group.journal);
      parentInput.dataset.journal=group.journal;
      parentInput.checked=isParentSelected(group);
      parentInput.indeterminate=!parentInput.checked && group.roles.some(role=>checkedRole(group,role));
      parentInput.addEventListener('change',()=>changeParent(group,parentInput.checked));
      journalLabel.appendChild(parentInput);
      journalLabel.appendChild(create('span','per-role-journal-name',group.label));
      header.appendChild(journalLabel);
      const total=allContributions().filter(c=>c.journal===group.journal).length;
      const info=create('span','per-role-status',group.data_status==='present'?`${total} contribution${total>1?'s':''}`:'Données à intégrer');
      header.appendChild(info);
      block.appendChild(header);
      const options=create('div','per-role-options');
      options.id=childId;options.hidden=!state.expanded.has(group.journal);
      for (const role of group.roles) {
        const label=create('label','per-role-option'+(group.data_status==='present'?'':' per-role-option--pending'));
        const input=document.createElement('input');input.type='checkbox';
        input.value=key(group.journal,role.code);input.dataset.role=role.code;input.dataset.journal=group.journal;
        input.disabled=group.data_status!=='present';input.checked=checkedRole(group,role);
        input.addEventListener('change',()=>changeChild(group,role,input.checked));
        label.appendChild(input);label.appendChild(create('span','',role.label));
        if (group.data_status==='present') {
          const count=allContributions().filter(c=>c.journal===group.journal&&c.normalized_roles.includes(role.code)).length;
          label.appendChild(create('span','per-role-count',`${count} contribution${count>1?'s':''}`));
        }
        options.appendChild(label);
      }
      block.appendChild(options);root.appendChild(block);
    }
    updateRoleSummary();
  }
  function updateRoleSummary() {
    const summary=$('#per-role-summary-text');
    if(!summary || !data)return;
    const selected=[];
    for(const group of data.role_taxonomy){
      if(isParentSelected(group))selected.push(group.label);
      else for(const role of group.roles){
        if(state.selected.has(key(group.journal,role.code)))selected.push(group.label+' · '+role.label);
      }
    }
    summary.textContent=selected.length===0?'Tous les rôles':selected.length===1?selected[0]:`${selected.length} filtres sélectionnés`;
    $('#per-role-menu').classList.toggle('per-role-menu--active',selected.length>0);
  }
  const appendIdentifier = (root, identifier, person) => {
    const raw=person.identifiers[identifier.key];
    if (!raw || !identifier.pattern.test(raw)) return;
    const url=identifier.url(raw);
    const safe=allowUrl(url,identifier.origin);
    if(!safe)return;
    const a=create('a','per-logo per-logo--'+identifier.key);
    a.href=safe;a.target='_blank';a.rel='noopener noreferrer';
    const tooltip=identifier.name+' · '+raw+(identifier.key==='orcid'?' (alignement documentaire non authentifié)':'');
    a.title=tooltip;
    a.dataset.tooltip=tooltip;
    a.setAttribute('aria-label','Consulter '+identifier.name+' '+raw+' (nouvel onglet)');
    const label=create('span','per-logo-fallback',identifier.glyph);
    a.appendChild(label);
    const imgPath=iconManifest[identifier.key];
    if(typeof imgPath==='string' && /^[a-z0-9-]+\.png$/.test(imgPath)){
      const img=create('img','per-logo-image');
      img.src='../assets/personnes-identifiants/'+imgPath;img.alt='';img.width=32;img.height=32;img.decoding='async';
      img.addEventListener('load',()=>a.classList.add('per-logo--image-loaded'));
      img.addEventListener('error',()=>img.remove());
      a.appendChild(img);
    }
    root.appendChild(a);
  };
  const decorateJournal = (node, section) => {
    const segments={adlfi:['Consulter les notices ','AdlFI',' liées'],gallia:['Consulter les articles ','Gallia',' liés'],gallia_prehistoire:['Consulter les articles ','Gallia Préhistoire',' liés']}[section.journal];
    if(!segments){node.appendChild(document.createTextNode(section.label));return;}
    node.appendChild(document.createTextNode(segments[0]));
    node.appendChild(create('em','',segments[1]));
    node.appendChild(document.createTextNode(segments[2]));
  };
  const renderPublicationSection = (root, section, works) => {
    const records=works.filter(x=>x.journal===section.journal);
    const byDoc=new Map();
    for(const c of records){
      const docKey=c.notice?.url || c.handle;
      if(!byDoc.has(docKey))byDoc.set(docKey,{notice:c.notice,roles:new Set(),handle:c.handle,bibliography:c.bibliography});
      for(const r of c.normalized_roles||[])byDoc.get(docKey).roles.add(r);
    }
    const count=byDoc.size;
    if(section.data_status!=='present' && !count){
      const inactive=create('div','per-doc-section per-doc-section--pending');
      const p=create('div','per-doc-pending');
      const label=create('span','per-doc-pending-label');decorateJournal(label,section);p.appendChild(label);
      p.appendChild(create('span','per-doc-soon','À venir'));
      inactive.appendChild(p);root.appendChild(inactive);return;
    }
    const details=create('details','per-doc-section');
    const summary=create('summary','per-doc-summary');decorateJournal(summary,section);
    summary.appendChild(create('span','per-doc-count',' ('+count+')'));
    details.appendChild(summary);
    const list=create('ul','per-doc-list');
    for(const row of byDoc.values()){
      const li=create('li','per-doc-item');
      const url=section.journal==='adlfi' ? allowUrl(row.notice?.url,'journals.openedition.org') : allowArticleUrl(row.notice?.url);
      const title=row.notice?.title||'Publication sans titre';
      if(url){const a=create('a','per-doc-link',title);a.href=url;a.target='_blank';a.rel='noopener noreferrer';li.appendChild(a);}
      else li.appendChild(create('span','per-doc-title',title));
      if(row.bibliography){
        const b=row.bibliography;
        const pages=b.first_page && b.last_page ? 'p. '+b.first_page+'–'+b.last_page
          : b.first_page ? 'p. '+b.first_page : '';
        const reference=[b.volume,b.year,pages].filter(Boolean).join(' · ');
        if(reference)li.appendChild(create('span','per-doc-biblio',reference));
      }
      const taxonomy=data.role_taxonomy.find(x=>x.journal===section.journal);
      const roles=[...row.roles].map(x=>taxonomy?.roles.find(r=>r.code===x)?.label||x).join(' · ');
      li.appendChild(create('span','per-doc-role',roles));
      list.appendChild(li);
    }
    details.appendChild(list);root.appendChild(details);
  };
  const renderCard = (person, matchingWorks, allWorks) => {
    const card=create('article','per-card');
    const head=create('div','per-cardhead');
    head.appendChild(create('h2','',person.name));
    head.appendChild(create('span','per-identifier',person.id));
    card.appendChild(head);
    const variants=(person.name_variants||[]).filter(x=>x && typeof x.value==='string' && x.value.trim() && x.source && x.kind);
    if(variants.length){
      const variantZone=create('div','per-variant-zone');
      variantZone.appendChild(create('span','per-variant-label',variants.length===1?'Autre forme : ':'Autres formes : '));
      variantZone.appendChild(create('span','per-variant-values',variants.map(v=>v.value.trim()).join(' · ')));
      card.appendChild(variantZone);
    }
    const logos=create('div','per-idlogos');logos.setAttribute('aria-label','Identifiants pérennes et bases d’autorité');
    for(const descriptor of iconDefinitions)appendIdentifier(logos,descriptor,person);
    card.appendChild(logos);
    for(const section of data.publication_sections){renderPublicationSection(card,section,allWorks);}
    return card;
  };
  function render() {
    if(!data)return;
    const container=$('#per-cards');container.replaceChildren();
    const works=allContributions();
    const filtered=works.filter(matchesSelection);
    const matchingByPerson=new Map(),allByPerson=new Map();
    for(const c of works){
      if(!allByPerson.has(c.person_id))allByPerson.set(c.person_id,[]);
      allByPerson.get(c.person_id).push(c);
    }
    for(const c of filtered){
      if(!matchingByPerson.has(c.person_id))matchingByPerson.set(c.person_id,[]);
      matchingByPerson.get(c.person_id).push(c);
    }
    const people=data.authorities.filter(person => {
      const matching=matchingByPerson.get(person.id)||[];
      if(!matching.length)return false;
      if(!state.q)return true;
      const all=allByPerson.get(person.id)||[];
      const haystack=[person.id,person.name,person.name_idref,...(person.name_variants||[]).map(v=>v.value),...Object.values(person.identifiers),...all.map(c=>c.notice.title)].join(' ');
      return norm(haystack).includes(norm(state.q));
    }).sort(surnameOrder);
    const visibleContributions=people.reduce((n,p)=>n+(matchingByPerson.get(p.id)||[]).length,0);
    $('#per-results').textContent=`${people.length} autorité${people.length>1?'s':''} affichée${people.length>1?'s':''} · ${visibleContributions} contribution${visibleContributions>1?'s':''} correspondant aux filtres`;
    if(!people.length){
      const pending=data.role_taxonomy.filter(g=>g.data_status!=='present' && state.selected.has(key(g.journal)));
      container.appendChild(create('p','per-empty',pending.length && !filtered.length
        ? 'Aucune contribution importée pour '+pending.map(x=>x.label).join(' et ')+'. Les relations Heurist sont encore à intégrer.'
        : 'Aucun résultat pour ces critères.'));
      return;
    }
    for(const person of people) container.appendChild(renderCard(person,matchingByPerson.get(person.id)||[],allByPerson.get(person.id)||[]));
  }
  $('#per-query').addEventListener('input',e=>{state.q=e.target.value.trim();render();});
  $('#per-reset').addEventListener('click',()=>{state.q='';state.selected.clear();$('#per-query').value='';renderFacets();render();$('#per-query').focus();});
  document.addEventListener('pointerdown',event=>{const menu=$('#per-role-menu');if(menu.open && !menu.contains(event.target))menu.open=false;});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'){$('#per-role-menu').open=false;$('#per-role-menu-trigger').focus();}});
  Promise.all([
    fetch('../data/personnes.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}),
    fetch('../assets/personnes-identifiants/manifest.json',{cache:'no-store'}).then(r=>r.ok?r.json():{available:{}}).catch(()=>({available:{}})),
    fetch('../data/personnes-articles.json',{cache:'no-store'})
      .then(r=>r.status===404?null:r.ok?r.json():Promise.reject(Error('HTTP '+r.status)))
      .catch(()=>null)
  ]).then(([json,icons,articles])=>{
    iconManifest=icons.available||{};
    if(json.publication_status!=='PUBLIC_PILOT'||json.totals.authorities!==json.authorities.length || json.totals.contributions!==json.contributions.length||!Array.isArray(json.contributions)||!Array.isArray(json.publication_sections))throw Error('Projection de recette inattendue');
    data=json;
    if(articles){
      try {attachPublishedArticles(articles);}
      catch {console.warn('Catalogue bibliographique complémentaire écarté ; données AdlFI conservées.');}
    }
    renderFacets();render();
  }).catch(()=>{$('#per-results').textContent='Données indisponibles. Ouvrez ce prototype depuis un serveur HTTP local.';});
})();
