(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const esc = x => String(x ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const n = v => v === null || v === undefined || String(v).trim() === '' ? null : String(v).trim();
  const unique = a => [...new Set(a.filter(x=>x!==null&&x!==undefined&&x!==''))];
  const collator = new Intl.Collator('fr',{sensitivity:'base',numeric:true});
  const countryNames = new Intl.DisplayNames(['fr'],{type:'region'});
  const country = v => {try {return v ? countryNames.of(v) : 'Non renseigné';}catch {return v||'Non renseigné';}};
  const labels = {
    LAB:'Laboratoire', MSH:'MSH', ASS:'Association', PRIV:'Entreprise privée', COL:'Collectivité',
    UNIV:'Université', MC:'Ministère de la Culture', Inrap:'Inrap', MUS:'Musée', MSH:'Maison des sciences humaines',
    scop_sarl:'SCOP SARL', association_loi_1901:'Association loi de 1901',
    public:'Public',prive:'Privé',privé:'Privé', mixte:'Mixte',
    oui:'Actif',non:'Inactif', unknown:'À confirmer', ORG:'Organisme',SER:'Service'
  };
  // Keep the descriptive raw type code when there is no editorial label.
  const natural = v => !v ? 'Non renseigné' : (labels[v] || String(v).replaceAll('_',' ').replace(/\b\w/g,s=>s.toUpperCase()));
  const safeUrl = raw => {if(!raw)return null;try{let u=new URL(raw);return ['https:','http:'].includes(u.protocol)?u.href:null}catch{return null}};
  const flagLabel = v => v === true?'Actif':v === false?'Inactif':'À confirmer';
  const state={q:'',sort:'alpha',view:'cards',page:1,pageSize:18,selected:{}};
  const facets=[
    {key:'kind',label:'Nature',open:true},
    {key:'activity',label:'Activité',open:true},
    {key:'bsr',label:'Catégorie BSR',open:true},
    {key:'sector',label:'Secteur institutionnel',open:false},
    {key:'country',label:'Pays institutionnel',open:false},
    {key:'type',label:'Type d’organisme / service',open:false},
    {key:'level',label:'Collectivités · échelon territorial',open:false},
    {key:'quality',label:'Complétude documentaire',open:false}
  ];
  facets.forEach(f=>state.selected[f.key]=new Set());
  let data,records,recordById,relsById;
  const baseRecords = () => records.filter(r=>r.presentation.visible);
  const VALID_STATES = new Set(['valide','validee','validée']);
  const RATTACHEMENT_TYPES = new Set(['rattachement_administratif','rattachement_service','rattachement_institutionnel','rattachement']);
  const BLDG = '<svg viewBox="0 0 32 32" width="32" height="32" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M5 27V11l11-6 11 6v16M9 27v-9h14v9M13 9v5M19 9v5M3 27h26"/><path d="M14 27v-5h4v5"/></svg>';
  const assetImg=(path,alt,className)=> {
    if (!path || !/^assets\/(?:organismes|logos)\/(?:ORG|SER)-\d{4}\.(?:jpg|jpeg|png|svg|webp)$/.test(path)) return null;
    return `<img class="${className}" src="../${esc(path)}" alt="${esc(alt)}" loading="lazy" decoding="async">`;
  };
  const establishedRattachements=r=>(relsById.get(r.id)||[])
    .filter(rel=>rel.source===r.id && VALID_STATES.has(rel.validation||'') && RATTACHEMENT_TYPES.has(rel.type) && recordById.has(rel.target));
  const parentVisual=(parent)=>assetImg(parent.presentation.media.logo||parent.presentation.media.image,
    'Identité visuelle : '+parent.names.preferred,'parent-logo') || `<span class="parent-picto">${BLDG}</span>`;
  function parentBlock(r,compact=false) {
    const links=establishedRattachements(r);
    if(!links.length) return '';
    const display=links.slice(0,compact?2:10).map(rel=>{
      const parent=recordById.get(rel.target);
      const type=rel.end?'Rattachement historique':(rel.type==='rattachement_service'?'Service rattaché à':'Rattachement administratif');
      const period=rel.start||rel.end?` (${rel.start?'depuis '+esc(rel.start):'date de début inconnue'}${rel.end?' ; jusqu’à '+esc(rel.end):''})`:'';
      return `<div class="attachment-item" title="${esc(type)}"><span class="parent-visual">${parentVisual(parent)}</span><span class="attachment-names"><span class="attachment-caption">${esc(type)}${period}</span><strong>${esc(parent.names.preferred)}</strong></span></div>`;
    }).join('');
    return `<div class="attachments">${display}${links.length>(compact?2:10)?`<span class="attachment-extra">+ ${links.length-(compact?2:10)} autre(s) rattachement(s)</span>`:''}</div>`;
  }

  const valueFor=(r,k)=>{
    if(k==='kind')return [r.kind];
    if(k==='activity')return [r.activity.active===true?'oui':r.activity.active===false?'non':'unknown'];
    if(k==='bsr')return [r.classification.bsr||'—'];
    if(k==='sector')return [r.classification.sector||'—'];
    if(k==='country')return [r.geography.institutional_country_iso2||'—'];
    if(k==='type')return [r.classification.type||'—'];
    if(k==='level')return r.kind==='ORG' && r.classification.type==='collectivite_territoriale' && r.classification.level
      ? [r.classification.level] : [];
    if(k==='quality'){
      const q=r.quality,a=[];
      if(q.activity_unknown)a.push('Activité à préciser');
      if(q.end_missing)a.push('Date de fin absente');
      if(q.city_unrecorded)a.push('Ville non renseignée');
      if(q.country_unrecorded)a.push('Pays non renseigné');
      if(q.no_website)a.push('Sans site officiel');
      if(r.kind==='ORG'&&!r.identifiers.ror)a.push('ROR non renseigné');
      return a.length?a:['Aucun des critères'];
    }
    return [];
  };
  const valLabel=(k,v)=>v==='—'?'Non renseigné':k==='country'?country(v):k==='type'?natural(v):natural(v);
  const searchText=r=>[
    r.id,r.names.preferred,r.names.acronym,r.names.other_acronyms.join(' '),r.names.historical_free_text,
    ...r.names.history.flatMap(h=>[h.label,h.acronym]),r.geography.cities_label,
    country(r.geography.institutional_country_iso2),r.classification.bsr,r.classification.type,
    r.identifiers.rnsr,r.identifiers.lab,r.identifiers.ror,r.website
  ].filter(Boolean).join(' ').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr');
  const textQuery=()=>state.q.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr');
  function matches(r,except=null){
    if(state.q&&!searchText(r).includes(textQuery()))return false;
    return facets.every(f=>{
      if(f.key===except)return true;
      const selected=state.selected[f.key];
      return selected.size===0||valueFor(r,f.key).some(v=>selected.has(v));
    });
  }
  function refreshFacetGroup(f){
    const counts=new Map();
    baseRecords().filter(r=>matches(r,f.key)).forEach(r=>valueFor(r,f.key).forEach(v=>counts.set(v,(counts.get(v)||0)+1)));
    const all=new Set([...baseRecords().flatMap(r=>valueFor(r,f.key)),...state.selected[f.key]]);
    let ordered=[...all].sort((a,b)=>(counts.get(b)||0)-(counts.get(a)||0)||collator.compare(valLabel(f.key,a),valLabel(f.key,b)));
    if(f.key==='kind')ordered=['ORG','SER'];
    if(f.key==='activity')ordered=['oui','non','unknown'];
    return ordered.map(v=>{
      let count=counts.get(v)||0;const checked=state.selected[f.key].has(v);
      return `<label class="facet-entry${!count&&!checked?' disabled':''}"><input type="checkbox" data-facet="${esc(f.key)}" data-value="${esc(v)}" ${checked?'checked':''} ${!count&&!checked?'disabled':''}><span class="entry-label">${esc(valLabel(f.key,v))}</span><span class="count">${count}</span></label>`;
    }).join('');
  }
  function drawFacets(){
    const container=$('#facets');
    const open=new Set([...container.querySelectorAll('details[open]')].map(el=>el.dataset.facet));
    const first=container.children.length===0;
    container.innerHTML=facets.map(f=>`<details class="facet-group" data-facet="${f.key}" ${first?(f.open?'open':''):(open.has(f.key)?'open':'')}><summary>${esc(f.label)}</summary><div class="facet-items">${refreshFacetGroup(f)}</div></details>`).join('');
  }
  function chips(){
    const el=$('#active-chips');
    const entries=facets.flatMap(f=>[...state.selected[f.key]].map(v=>({key:f.key,value:v,label:valLabel(f.key,v)})));
    if(!entries.length&&!state.q){el.innerHTML='';return;}
    el.innerHTML=(state.q?`<button type="button" class="chip" data-remove-query>Recherche : ${esc(state.q)} ×</button>`:'')+entries.map(v=>`<button type="button" class="chip" data-remove-facet="${esc(v.key)}" data-remove-value="${esc(v.value)}">${esc(v.label)} ×</button>`).join('');
  }
  function sortEntries(a){
    const sorted=[...a];
    if(state.sort==='id')sorted.sort((a,b)=>collator.compare(a.id,b.id));
    else if(state.sort==='kind')sorted.sort((a,b)=>collator.compare(a.kind,b.kind)||collator.compare(a.names.preferred,b.names.preferred));
    else if(state.sort==='mentions')sorted.sort((a,b)=>b.usage.affiliations_linked-a.usage.affiliations_linked||collator.compare(a.names.preferred,b.names.preferred));
    else sorted.sort((a,b)=>collator.compare(a.names.preferred,b.names.preferred));
    return sorted;
  }
  function card(r){
    const cat=r.classification.bsr||'Non classé';
    const typ=r.classification.type?natural(r.classification.type):'Type non précisé';
    const sector=r.classification.sector?natural(r.classification.sector):null;
    const city=r.geography.cities_label?esc(r.geography.cities_label):'<em>Ville à documenter</em>';
    const geography=city+(r.geography.institutional_country_iso2?` <span class="country-context">· pays institutionnel : ${esc(country(r.geography.institutional_country_iso2))}</span>`:'');
    const sigle=r.names.acronym?` <span class="acronym">(${esc(r.names.acronym)})</span>`:'';
    const stateclass=r.activity.active===true?'yes':r.activity.active===false?'no':'';
    const iden=[r.identifiers.lab?esc(r.identifiers.lab):null,r.identifiers.rnsr?'RNSR '+esc(r.identifiers.rnsr):null].filter(Boolean).join(' · ');
    const primary=assetImg(r.presentation.media.image||r.presentation.media.logo,'Illustration : '+r.names.preferred,'authority-image')||`<span class="image-placeholder">${BLDG}<small>Illustration à ajouter</small></span>`;
    const excluded=!r.presentation.visible?'<span class="editorial-state">Hors catalogue</span>':'';
    return `<article class="authority-card${r.presentation.visible?'':' editorial-hidden'}" data-id="${esc(r.id)}">
      <div class="card-head"><span class="kind ${r.kind==='SER'?'ser':''}">${r.kind}</span><span class="ident">${esc(r.id)}</span>${excluded}<span class="state"><span class="state-dot ${stateclass}"></span>${flagLabel(r.activity.active)}</span></div>
      <div class="card-identity"><div class="card-visual">${primary}</div><div class="card-identity-copy"><h2 class="card-title">${esc(r.names.preferred)}${sigle}</h2><div class="card-cats"><span class="cat bsr">${esc(cat)}</span><span class="cat">${esc(typ)}</span>${sector?`<span class="cat">${esc(sector)}</span>`:''}</div><p class="card-sub">${iden||'Identifiants complémentaires non renseignés'}</p></div></div>
      <div class="lineinfo"><span class="glyph" aria-hidden="true">⌖</span><span>${geography}</span></div>
      ${parentBlock(r,true)}
      <div class="card-foot"><span class="ref">${r.usage.affiliations_linked?`${r.usage.affiliations_linked} affiliation(s) source liée(s)`:'Aucune affiliation source liée'}</span><button class="details-trigger" type="button" data-detail="${r.id}">Consulter la fiche →</button></div></article>`;
  }

  function render(){
    const filtered=sortEntries(baseRecords().filter(matches));
    const total=filtered.length,pages=Math.max(1,Math.ceil(total/state.pageSize));
    state.page=Math.min(state.page,pages);
    const pageItems=filtered.slice((state.page-1)*state.pageSize,state.page*state.pageSize);
    $('#result-count').innerHTML=`<strong>${total.toLocaleString('fr-FR')}</strong> résultat${total>1?'s':''} sur ${baseRecords().length.toLocaleString('fr-FR')} autorités ${'du catalogue'}`;
    $('#cards').classList.toggle('list-mode',state.view==='list');
    $('#cards').innerHTML=pageItems.length?pageItems.map(card).join(''):'<div class="empty">Aucune autorité ne correspond à ces critères.<p>Retirez un filtre ou élargissez votre recherche.</p></div>';
    $('#pagination').innerHTML=pages>1?`<button type="button" data-page="previous" ${state.page===1?'disabled':''}>← Précédent</button><span>Page ${state.page} / ${pages}</span><button type="button" data-page="next" ${state.page===pages?'disabled':''}>Suivant →</button>`:'';
    drawFacets();chips();
  }
  function row(label,html){return html?`<dt>${esc(label)}</dt><dd>${html}</dd>`:'';}
  const link=(href,label)=>{let u=safeUrl(href);return u?`<a target="_blank" rel="noopener noreferrer" href="${esc(u)}">${esc(label)}</a>`:null};
  function relationLabel(rel){const peer=recordById.get(rel.target)||recordById.get(rel.source);return peer?.names.preferred||rel.target;}
  function updateHash(fragment){if(location.protocol==='http:'||location.protocol==='https:')history.replaceState(null,'',location.pathname+fragment);}
  function details(id,shouldUpdateHash=true){
    const r=recordById.get(id);if(!r)return;
    const verified=(relsById.get(id)||[]).filter(x=>x.source===id&&['valide','validee','validée'].includes(x.validation||''));
    const byType=Object.groupBy?Object.groupBy(verified,x=>x.type||'relation'):verified.reduce((a,x)=>{(a[x.type||'relation'] ||= []).push(x);return a},{});
    const relHtml=Object.entries(byType).map(([type,items])=>`<p><strong>${esc(natural(type))}</strong></p><ul class="subtle-list">${items.map(item=>`<li>${esc(recordById.get(item.target)?.names.preferred||item.target)} ${item.start||item.end?`<small>(${esc(item.start||'début non daté')} – ${esc(item.end||'actuel ou inconnu')})</small>`:''}</li>`).join('')}</ul>`).join('')||'<p class="detail-desc">Aucune relation validée disponible dans cette extraction.</p>';
    const historical=r.names.history.filter(x=>x.label && ['valide','validee','validée'].includes(x.validation||''));
    const others=r.names.history.filter(x=>x.label && !['valide','validee','validée'].includes(x.validation||''));
    const nameHist=historical.length?`<ul class="subtle-list">${historical.map(x=>`<li>${esc(x.label)}${x.start||x.end?` <small>(${esc(x.start||'?')}–${esc(x.end||'?')})</small>`:''}</li>`).join('')}</ul>`:'';
    const legalStates=(r.names.legal_status_history||[]);
    const legalHtml=legalStates.length?`<ul class="subtle-list">${legalStates.map(x=>{
      const period=(x.start||'?')+'–'+(x.end||'présent');
      const title=natural(x.legal_form||x.type);
      const status=['valide','validee','validée'].includes(x.validation||'')?'':' · état documentaire à vérifier';
      const source=x.source?` · ${link(x.source,'source')||''}`:'';
      return `<li><strong>${esc(title)}</strong> <small>(${esc(period)}${esc(status)})</small>${source}</li>`;
    }).join('')}</ul>`:'<p class="detail-desc">Aucun état statutaire historique distinct renseigné.</p>';
    const sigle=r.names.acronym||'Non renseigné';
    const extras=r.names.other_acronyms.length?r.names.other_acronyms.join(' · '):null;
    const kind=r.kind;
    let rnsr=r.identifiers.rnsr?link('https://rnsr.adc.education.fr/structure/'+encodeURIComponent(r.identifiers.rnsr),r.identifiers.rnsr):null;
    let content=`<div class="detail-head"><span class="kind ${kind==='SER'?'ser':''}">${kind}</span> <span class="ident">${esc(id)}</span><h2>${esc(r.names.preferred)}</h2><p class="detail-desc">${esc(natural(r.classification.type))} · ${esc(flagLabel(r.activity.active))}</p></div><div class="detail-body">
    <section class="detail-block"><h3>Identité et classification</h3><dl class="detail-dl">${row('Sigle',esc(sigle))}${row('Autres acronymes',extras?esc(extras):null)}${row('Catégorie BSR',esc(r.classification.bsr||'Non renseignée'))}${row('Secteur',esc(natural(r.classification.sector)))}${row('Type détaillé',esc(natural(r.classification.type)))}</dl></section>
    <section class="detail-block"><h3>Période d'existence</h3><dl class="detail-dl">${row('Statut',esc(flagLabel(r.activity.active)))}${row('Début',esc(r.activity.start||'Non documenté'))}${row('Fin',esc(r.activity.end||'Non documentée'))}</dl></section>
    <section class="detail-block"><h3>Localisation déclarée</h3><dl class="detail-dl">${row('Pays institutionnel',esc(country(r.geography.institutional_country_iso2)))}${row('Ville(s) d’implantation',esc(r.geography.cities_label||'Non renseignée(s)'))}</dl><p class="detail-desc" style="margin-top:9px">Les villes ne constituent pas une géolocalisation vérifiée. Les établissements multi-sites ne sont pas ramenés à un point unique.</p></section>
    <section class="detail-block"><h3>Identifiants et site web</h3><dl class="detail-dl">${row('ROR',r.identifiers.ror?link(r.identifiers.ror,r.identifiers.ror)||esc(r.identifiers.ror):'Non renseigné')}${row('RNSR',rnsr||'Non renseigné')}${row('Unité de recherche',esc(r.identifiers.lab||'Non renseigné'))}${row('IdRef',esc(r.identifiers.idref||'Non renseigné'))}${row('Wikidata',esc(r.identifiers.wikidata||'Non renseigné'))}${row('Site officiel',r.website?link(r.website,'Consulter le site officiel'):'Non renseigné')}</dl></section>
    <section class="detail-block"><h3>Dénominations historiques validées</h3>${nameHist||'<p class="detail-desc">Aucune dénomination historique validée dans le tableau dédié.</p>'}${others.length?`<p class="detail-desc" style="margin-top:8px">${others.length} autre(s) forme(s) historique(s) restent documentées avec un statut de validation distinct, sans être présentées ici comme établies.</p>`:''}</section>
    <section class="detail-block"><h3>Évolution du statut institutionnel</h3>${legalHtml}</section>
    <section class="detail-block"><h3>Rattachement institutionnel</h3>${parentBlock(r)||'<p class="detail-desc">Aucun rattachement validé à présenter.</p>'}</section><section class="detail-block"><h3>Relations institutionnelles validées</h3>${relHtml}</section>
    <section class="detail-block"><h3>Affiliations documentées</h3><dl class="detail-dl">${row('Libellés sources liés',esc(r.usage.affiliations_linked))}${row('Dont correspondances validées',esc(r.usage.affiliations_validated))}</dl><p class="detail-desc" style="margin-top:7px">Ces nombres décrivent les rapprochements du référentiel, non le nombre de notices archéologiques publiées.</p></section>
    </div>`;
    $('#detail-content').innerHTML=content;
    const d=$('#details'); if(!d.open)d.showModal();
    if(shouldUpdateHash)updateHash('#'+id);
  }
  function downloadCSV(){
    const list=sortEntries(baseRecords().filter(matches));
    const cols=['Identifiant','Nature','Nom retenu','Acronyme','Catégorie BSR','Type','Secteur','Actif','Pays institutionnel','Ville(s)','ROR','RNSR','Site officiel'];
    const dataRows=list.map(x=>[x.id,x.kind,x.names.preferred,x.names.acronym,x.classification.bsr,x.classification.type,x.classification.sector,flagLabel(x.activity.active),x.geography.institutional_country_iso2,x.geography.cities_label,x.identifiers.ror,x.identifiers.rnsr,x.website]);
    const cell=v=>'"'+String(v??'').replaceAll('"','""')+'"';
    const csv='\ufeff'+[cols,...dataRows].map(row=>row.map(cell).join(';')).join('\r\n');
    let url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='adlfi-referentiels-organismes-selection.csv';document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url);
  }
  function init(d){
    data=d;records=d.authorities;recordById=new Map(records.map(x=>[x.id,x]));relsById=new Map();
    d.relations.forEach(x=>{if(!relsById.has(x.source))relsById.set(x.source,[]);relsById.get(x.source).push(x)});
    const withCity=records.filter(x=>x.geography.cities_label).length;
    $('#summary').innerHTML=`<span class="summary-chip"><strong>${d.totals.catalog_included}</strong> autorités au catalogue</span><span class="summary-chip"><strong>${withCity}</strong> villes renseignées</span><span class="summary-chip">Référentiel AdlFI · 1.10</span>`;
    $('#query').addEventListener('input',e=>{state.q=e.target.value.trim();state.page=1;render()});
    $('#toggle-filters').addEventListener('click',e=>{const panel=$('.filter-panel');const open=panel.classList.toggle('mobile-filters-open');e.target.setAttribute('aria-expanded',String(open));e.target.textContent=open?'Masquer':'Afficher';});
    $('#sort').addEventListener('change',e=>{state.sort=e.target.value;state.page=1;render()});
    $('#facets').addEventListener('change',e=>{let box=e.target.closest('[data-facet][data-value]');if(!box)return; const key=box.dataset.facet,val=box.dataset.value;if(box.checked)state.selected[key].add(val);else state.selected[key].delete(val);state.page=1;render()});
    $('#clear-all').addEventListener('click',()=>{facets.forEach(f=>state.selected[f.key].clear());state.q='';state.page=1;$('#query').value='';render()});
    $('#active-chips').addEventListener('click',e=>{let b=e.target.closest('button');if(!b)return;if(b.hasAttribute('data-remove-query')){state.q='';$('#query').value=''}else if(b.dataset.removeFacet)state.selected[b.dataset.removeFacet].delete(b.dataset.removeValue);state.page=1;render()});
    $('#cards').addEventListener('click',e=>{let b=e.target.closest('[data-detail]');if(b)details(b.dataset.detail)});
    $('#pagination').addEventListener('click',e=>{let b=e.target.closest('[data-page]');if(!b)return;state.page += b.dataset.page==='next'?1:-1;render();$('#result-count').scrollIntoView({block:'nearest'})});
    $('#toggle-view').addEventListener('click',e=>{state.view=state.view==='cards'?'list':'cards';e.target.textContent=state.view==='cards'?'Liste':'Cartouches';e.target.setAttribute('aria-pressed',String(state.view==='list'));render()});
    $('#csv-export').addEventListener('click',downloadCSV);
    $('#close-details').addEventListener('click',()=>{$('#details').close();updateHash('')});
    $('#details').addEventListener('click',e=>{if(e.target===$('#details'))$('#details').close()});
    $('#details').addEventListener('close',()=>{if(location.hash)updateHash('')});
    render();const id=decodeURIComponent(location.hash.replace('#',''));if(recordById.has(id))details(id,false);
  }
  fetch('../data/organismes.json').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}).then(init).catch(err=>{$('#cards').innerHTML='<p class="empty">Impossible de charger les données. Lancer le site avec <code>python3 -m http.server 8000</code> depuis le dossier racine. '+esc(err.message)+'</p>'});
})();
