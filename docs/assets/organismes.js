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
    national:'National',interregional:'Interrégional',regional:'Régional',
    departemental:'Départemental',intercommunal:'Intercommunal',
    communal:'Communal',metropolitain:'Métropolitain',cantonal:'Cantonal',
    provincial:'Provincial',local:'Local',
    oui:'Actif',non:'Inactif', unknown:'À confirmer', ORG:'Organisme',SER:'Service'
  };
  // Keep the descriptive raw type code when there is no editorial label.
  const natural = v => !v ? 'Non renseigné' : (labels[v] || String(v).replaceAll('_',' ').replace(/\b\w/g,s=>s.toUpperCase()));
  const safeUrl = raw => {if(!raw)return null;try{let u=new URL(raw);return ['https:','http:'].includes(u.protocol)?u.href:null}catch{return null}};
  const flagLabel = v => v === true?'Actif':v === false?'Inactif':'À confirmer';
  const state={q:'',sort:'alpha',view:'cards',page:1,pageSize:18,selected:{}};
  const facets=[
    {key:'activity',label:'Activité',open:true},
    {key:'bsr',label:'Catégorie',open:true},
    {key:'sector',label:'Secteur',open:false},
    {key:'level',label:'Échelon institutionnel',open:false},
    {key:'country',label:'Pays',open:false},
    {key:'quality',label:'Complétude documentaire',open:false}
  ];
  facets.forEach(f=>state.selected[f.key]=new Set());
  let data,records,recordById,relsById;
  let childrenById=new Map();
  let federalLinksById=new Map();
  let canonicalByLegacy=new Map();
  let legacyByCanonical=new Map();

  // Ces correspondances identifient une correction éditoriale, pas une succession.
  function indexIdentityAliases(aliases=[]){
    canonicalByLegacy=new Map();
    legacyByCanonical=new Map();
    for(const item of aliases){
      if(!item || typeof item.from!=='string' || typeof item.to!=='string'
        || item.from===item.to || !recordById.has(item.to)
        || recordById.has(item.from))continue;
      canonicalByLegacy.set(item.from,item.to);
      if(!legacyByCanonical.has(item.to))legacyByCanonical.set(item.to,[]);
      legacyByCanonical.get(item.to).push(item.from);
    }
  }
  function resolveIdentityAlias(id){
    let canonical=id;
    const visited=new Set();
    while(canonicalByLegacy.has(canonical) && !visited.has(canonical)){
      visited.add(canonical);
      canonical=canonicalByLegacy.get(canonical);
    }
    return visited.has(canonical)?id:canonical;
  }
  const baseRecords = () => records.filter(r=>r.presentation.visible);
  const VALID_STATES = new Set(['valide','validee','validée']);
  const RATTACHEMENT_TYPES = new Set(['rattachement_administratif','rattachement_service','rattachement_institutionnel','rattachement','tutelle']);
  // Dates partielles : début inclusif, fin inclusive. Pas de date inventée.
  const todayISO=()=>new Date().toISOString().slice(0,10);
  function dateBound(raw,upper=false){
    if(!raw)return null;
    const s=String(raw).trim();
    if(!/^\d{4}(?:-\d{2}(?:-\d{2})?)?$/.test(s))return null;
    return s.length===4?s+(upper?'-12-31':'-01-01')
      :s.length===7?s+(upper?'-31':'-01'):s;
  }
  function currentAuthority(r,day=todayISO()){
    // Dans le JSON réel, 'actif: null' signifie activité indéterminée.
    // Ne pas convertir cette incertitude en tutelle actuelle.
    if(!r||(r.activity&&r.activity.active!==true))return false;
    const a=r.activity||{},start=dateBound(a.start),end=dateBound(a.end,true);
    if((a.start&&!start)||(a.end&&!end))return false;
    return !(start&&start>day)&&!(end&&end<day);
  }
  function currentRelation(rel,day=todayISO()){
    const start=dateBound(rel.start),end=dateBound(rel.end,true);
    if((rel.start&&!start)||(rel.end&&!end))return false;
    return !(start&&start>day)&&!(end&&end<day);
  }
  const currentRattachement=(source,target,rel,day=todayISO())=>
    currentAuthority(source,day)&&currentAuthority(target,day)&&currentRelation(rel,day);
  const BLDG = '<svg viewBox="0 0 32 32" width="32" height="32" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M5 27V11l11-6 11 6v16M9 27v-9h14v9M13 9v5M19 9v5M3 27h26"/><path d="M14 27v-5h4v5"/></svg>';
  // Un logo JPEG par identifiant stable : ORG-XXXX.jpg / SER-XXXX.jpg.
  // Aucun ancien chemin de média, ni format alternatif.
  const assetImg=(ident,alt,className)=> {
    if (!/^(?:ORG|SER)-\d{4}$/.test(ident||'')) return null;
    return `<img class="${esc(className)}" src="../assets/organismes/${esc(ident)}.jpg"
      alt="${esc(alt)}" loading="lazy" decoding="async" data-authority-logo>`;
  };
  // L'évènement error d'une image ne remonte pas par bubbling : capture obligatoire.
  // Un logo nouvellement déposé fonctionne sans rafraîchir le JSON.
  if (typeof document !== 'undefined') document.addEventListener('error',event=>{
    const img=event.target;
    if (!(img instanceof HTMLImageElement) || !img.hasAttribute('data-authority-logo')) return;
    const bandItem=img.closest('.lab-logo-item');
    if (bandItem) {
      const band=bandItem.closest('.lab-logo-band');
      bandItem.remove();
      if (band && !band.querySelector('.lab-logo-item')) band.remove();
      return;
    }
    if (img.classList.contains('detail-brand-logo')) {
      // Un logo absent ne doit pas laisser un pictogramme géant dans l'en-tête.
      img.closest('.detail-brand')?.remove();
      return;
    }
    if (img.classList.contains('parent-logo')) {
      const replacement=document.createElement('span');
      replacement.className='parent-picto';
      replacement.innerHTML=BLDG;
      img.replaceWith(replacement);
      return;
    }
    const cls=img.classList.contains('evolution-thumbnail')?'evolution-thumbnail-placeholder'
      :img.classList.contains('lab-primary-logo')?'lab-image-placeholder':'image-placeholder';
    const replacement=document.createElement('span');
    replacement.className=cls;
    replacement.innerHTML=BLDG;
    img.replaceWith(replacement);
  },true);
  const establishedRattachements=r=>(relsById.get(r.id)||[])
    .filter(rel=>rel.source===r.id && VALID_STATES.has(rel.validation||'') && RATTACHEMENT_TYPES.has(rel.type) && recordById.has(rel.target));
  const parentVisual=(parent)=>assetImg(parent.id,
    'Identité visuelle : '+parent.names.preferred,'parent-logo') || `<span class="parent-picto">${BLDG}</span>`;
  function parentBlock(r,compact=false){
  const links=establishedRattachements(r);
  if(!links.length)return '';
  const activeTutelleIds=new Set(r.kind==='ORG'&&r.classification.type==='laboratoire'
    ?laboratoryTutelles(r).map(x=>x.id):[]);
  const orderedLinks=(r.kind==='ORG'&&r.classification.type==='laboratoire')
    ? [
        ...links.filter(rel=>rel.type==='tutelle')
          .sort((a,b)=>Number(activeTutelleIds.has(b.target))-Number(activeTutelleIds.has(a.target))
             ||tutelleTextOrder(recordById.get(a.target),recordById.get(b.target))),
        ...links.filter(rel=>rel.type!=='tutelle')
      ]
    :links;
  const display=orderedLinks.slice(0,compact?2:10).map(rel=>{
    const parent=recordById.get(rel.target);
    const type=!currentRattachement(r,parent,rel)?'Rattachement historique ou non actuel'
      :(rel.type==='tutelle'?'Tutelle':rel.type==='rattachement_service'?'Service rattaché à':'Rattachement administratif');
    const period=rel.start||rel.end?` (${rel.start?'depuis '+esc(rel.start):'date de début inconnue'}${rel.end?' ; jusqu’à '+esc(rel.end):''})`:'';
    const inner=`<span class="parent-visual">${parentVisual(parent)}</span><span class="attachment-names"><span class="attachment-caption">${esc(type)}${period}</span><strong>${esc(parent.names.preferred)}</strong></span>`;
    // Le statut « hors catalogue » masque le cartouche de résultat,
    // jamais la fiche de l'autorité liée par une relation validée.
    return `<button type="button" class="attachment-item attachment-link" data-detail="${esc(parent.id)}" aria-label="Consulter la fiche de ${esc(parent.names.preferred)}">${inner}</button>`;
  }).join('');
  return `<div class="attachments">${display}${links.length>(compact?2:10)?`<span class="attachment-extra">+ ${links.length-(compact?2:10)} autre(s) rattachement(s) dans la fiche</span>`:''}</div>`;
}


  // Les affiliations fédérales sont des liens entre autorités, et non des tutelles
  // ou des rattachements de service. Elles se lisent dans les deux sens.
  function indexFederalAffiliations(relations){
    federalLinksById=new Map();
    for(const rel of relations){
      if(rel.type!=='affiliation_federale'||!VALID_STATES.has(rel.validation||'')
        ||rel.source===rel.target
        ||!recordById.has(rel.source)||!recordById.has(rel.target)
        ||recordById.get(rel.target).kind!=='ORG')continue;
      for(const [id,other,direction] of [
        [rel.source,rel.target,'federation'],
        [rel.target,rel.source,'membre']
      ]){
        if(!federalLinksById.has(id))federalLinksById.set(id,[]);
        federalLinksById.get(id).push({other,direction,relation:rel});
      }
    }
  }
  function federalAffiliationBlock(r,compact=false){
    const entries=(federalLinksById.get(r.id)||[])
      .filter(item=>recordById.has(item.other))
      .sort((a,b)=>collator.compare(recordById.get(a.other).names.preferred,
        recordById.get(b.other).names.preferred));
    if(!entries.length)return '';
    const group=(direction,title,caption)=>{
      const items=entries.filter(item=>item.direction===direction);
      if(!items.length)return '';
      const shown=items.slice(0,compact?2:10);
      const html=shown.map(item=>{
        const peer=recordById.get(item.other),rel=item.relation;
        // La présence d'une borne ne prouve pas, à elle seule, une affiliation actuelle.
        const period=rel.start&&rel.end
          ?' · Période documentée : '+esc(rel.start)+' – '+esc(rel.end)
          :rel.start?' · Début documenté : '+esc(rel.start)
          :rel.end?' · Fin documentée : '+esc(rel.end)
          :' · Dates non documentées';
        const inner=`<span class="parent-visual">${parentVisual(peer)}</span><span class="attachment-names"><span class="attachment-caption">${esc(caption)}${period}</span><strong>${esc(peer.names.preferred)}</strong></span>`;
        return `<button type="button" class="attachment-item attachment-link" data-detail="${esc(peer.id)}" aria-label="Consulter la fiche de ${esc(peer.names.preferred)}">${inner}</button>`;
      }).join('');
      return `<div class="children-block"><p class="children-label">${esc(title)}</p><div class="attachments">${html}</div>${items.length>shown.length?`<p class="detail-desc">+ ${items.length-shown.length} autre(s) affiliation(s) dans la fiche</p>`:''}</div>`;
    };
    return group('federation','Affiliation fédérale','Affilié à')
      +group('membre','Organisations affiliées','Organisation affiliée');
  }

  function indexServiceChildren(relations){
  childrenById=new Map();
  for(const rel of relations){
    if(rel.type!=='rattachement_service'||!VALID_STATES.has(rel.validation||'')
       ||!recordById.has(rel.source)||!recordById.has(rel.target)
       ||recordById.get(rel.source).kind!=='SER')continue;
    if(!childrenById.has(rel.target))childrenById.set(rel.target,[]);
    childrenById.get(rel.target).push(rel);
  }
}
  function childrenBlock(r,compact=false){
  const links=(childrenById.get(r.id)||[])
    .sort((a,b)=>Number(currentRattachement(recordById.get(b.source),r,b))
      -Number(currentRattachement(recordById.get(a.source),r,a))
      ||collator.compare(recordById.get(a.source).names.preferred,recordById.get(b.source).names.preferred));
  if(!links.length)return '';
  const shown=links.slice(0,compact?2:10);
  const display=shown.map(rel=>{
    const child=recordById.get(rel.source);
    const current=currentRattachement(child,r,rel);
    const type=current?'Service rattaché':'Service historiquement rattaché ou statut actuel indéterminé';
    const date=rel.start||rel.end?` (${rel.start?'depuis '+esc(rel.start):'début non documenté'}${rel.end?' ; jusqu’à '+esc(rel.end):''})`:'';
    const inner=`<span class="parent-visual">${parentVisual(child)}</span><span class="attachment-names"><span class="attachment-caption">${esc(type)}${date}</span><strong>${esc(child.names.preferred)}</strong></span>`;
    return `<button type="button" class="attachment-item attachment-link" data-detail="${esc(child.id)}" aria-label="Consulter la fiche de ${esc(child.names.preferred)}">${inner}</button>`;
  }).join('');
  return `<div class="children-block"><p class="children-label">Services liés</p><div class="attachments">${display}${links.length>shown.length?`<span class="attachment-extra">+ ${links.length-shown.length} autre(s) service(s) dans la fiche</span>`:''}</div></div>`;
}

  // Cartouche éditorial des laboratoires : uniquement les tutelles validées
  // sans date de fin, jamais les relations proposées ou historiques.
  // Classement éditorial : les noms sont toujours alphabétiques.
  const tutelleTextOrder=(a,b)=>collator.compare(a.names.preferred,b.names.preferred)
    || collator.compare(a.id,b.id);
  // Les logos suivent une priorité institutionnelle propre, indépendante du texte :
  // ministère de la Culture, puis CNRS, puis autres tutelles par nom.
  const LOGO_ORDER=new Map([['ORG-0023',0],['ORG-0004',1]]);
  const tutelleLogoOrder=(a,b)=>(LOGO_ORDER.get(a.id)??2)-(LOGO_ORDER.get(b.id)??2)
    || tutelleTextOrder(a,b);

  function laboratoryTutelles(r,asOf=todayISO()) {
    if(!currentAuthority(r,asOf))return [];
    const seen=new Set();
    return (relsById.get(r.id)||[])
      .filter(rel=>rel.source===r.id && rel.type==='tutelle'
        && VALID_STATES.has(rel.validation||'') && recordById.has(rel.target)
        && currentRattachement(r,recordById.get(rel.target),rel,asOf))
      .filter(rel=>{if(seen.has(rel.target))return false;seen.add(rel.target);return true})
      .map(rel=>recordById.get(rel.target))
      .sort(tutelleTextOrder);
  }

  // Les filiations sont orientées du prédécesseur/contributeur vers l'autorité issue
  // de l'évolution, y compris SER → ORG. Elles ne prouvent pas une succession totale.
  const SUCCESSION_TYPES=new Set([
    'succession_institutionnelle','succession_service','succession',
    'fusion_constitutive','scission_constitutive',
    'succession_partielle','filiation_partielle'
  ]);
  const TOTAL_SUCCESSION_TYPES=new Set(['succession_institutionnelle','succession_service','succession']);
  let evolutionById=new Map();
  const EVOLUTION_MONTHS=['janvier','février','mars','avril','mai','juin',
    'juillet','août','septembre','octobre','novembre','décembre'];
  function evolutionDate(raw){
    if(!raw)return null;
    const value=String(raw),m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    if(!m)return value;
    const month=Number(m[2]),day=Number(m[3]);
    if(month<1||month>12||day<1||day>31)return value;
    return (day===1?'1er':String(day))+' '+EVOLUTION_MONTHS[month-1]+' '+m[1];
  }
  function indexEvolutions(relations){
    evolutionById=new Map();
    for(const x of relations){
      if(!SUCCESSION_TYPES.has(x.type)||!VALID_STATES.has(x.validation||'')
        ||!recordById.has(x.source)||!recordById.has(x.target))continue;
      if(!evolutionById.has(x.source))evolutionById.set(x.source,[]);
      if(!evolutionById.has(x.target))evolutionById.set(x.target,[]);
      evolutionById.get(x.source).push({other:x.target,direction:'successor',relation:x});
      evolutionById.get(x.target).push({other:x.source,direction:'predecessor',relation:x});
    }
  }
  function evolutionEntries(r){
    return (evolutionById.get(r.id)||[]).map(item=>{
      const partner=recordById.get(item.other);
      return partner?{...item,partner}:null;
    }).filter(Boolean).sort((a,b)=>a.direction!==b.direction
      ?(a.direction==='successor'?-1:1)
      :collator.compare(a.partner.names.preferred,b.partner.names.preferred));
  }
  const EVOLUTION_TYPE_LABELS={
    succession_institutionnelle:'Succession institutionnelle',
    succession_service:'Succession de service',
    succession:'Succession',
    fusion_constitutive:'Fusion constitutive',
    scission_constitutive:'Scission constitutive',
    succession_partielle:'Succession partielle',
    filiation_partielle:'Filiation partielle'
  };
  const evolutionTypeLabel=type=>EVOLUTION_TYPE_LABELS[type]||'Évolution institutionnelle';
  function evolutionGroupLabel(r,direction,count,items=[]){
    if(items.some(x=>!TOTAL_SUCCESSION_TYPES.has(x.relation.type)))
      return direction==='predecessor'?'Origines et filiations antérieures':'Évolutions et filiations ultérieures';
    if(direction==='predecessor')return count===1?'Structure antérieure':'Structures antérieures';
    const suffix=r.kind==='SER'?'à ce service':r.classification.type==='laboratoire'
      ?'à ce laboratoire':'à cet organisme';
    return (count===1?'Structure ayant succédé ':'Structures ayant succédé ')+suffix;
  }
  function evolutionLink(item){
    const p=item.partner;
    const name=p.names.preferred;
    // Le titre est le nom éditorial normalisé, jamais le seul acronyme.
    // L'acronyme demeure une aide à l'identification, sous le titre.
    const context=[p.id,
      p.names.acronym && p.names.acronym.toLocaleLowerCase('fr')!==name.toLocaleLowerCase('fr')
        ?p.names.acronym:null,
      p.identifiers?.lab].filter(Boolean).join(' · ');
    const visual=assetImg(p.id,
      'Identité visuelle : '+p.names.preferred,'evolution-thumbnail')
      ||`<span class="evolution-thumbnail-placeholder">${BLDG}</span>`;
    const date=evolutionDate(item.relation.start);
    const label=evolutionTypeLabel(item.relation.type)+(date?' · '+date:'');
    const content=`<span class="evolution-thumbnail-wrap">${visual}</span>
      <span class="evolution-link-content"><strong title="${esc(p.names.preferred)}">${esc(name)}</strong>
        <span>${esc(context)}</span><small>${esc(label)}</small></span>
      <span class="evolution-link-symbol" aria-hidden="true">↗</span>`;
    return `<button type="button" class="evolution-link" data-detail="${esc(p.id)}"
      aria-label="Consulter la fiche de ${esc(p.names.preferred)}">${content}</button>`;
  }
  function evolutionBlock(r,compact=false){
    const entries=evolutionEntries(r);
    if(!entries.length)return '';
    const shown=compact?entries.slice(0,2):entries;
    const groups=[];
    for(const direction of ['successor','predecessor']){
      const all=entries.filter(e=>e.direction===direction);
      const list=shown.filter(e=>e.direction===direction);
      if(!list.length)continue;
      groups.push(`<div class="evolution-group"><div class="evolution-group-label">${esc(evolutionGroupLabel(r,direction,all.length,all))}</div>
        ${list.map(evolutionLink).join('')}</div>`);
    }
    const remaining=entries.length-shown.length;
    return `<section class="evolution-panel${compact?' evolution-compact':''}"
      aria-label="Évolution institutionnelle">${compact?'':'<h3>Évolution institutionnelle</h3>'}
      ${groups.join('')}
      ${remaining?`<p class="evolution-more">+ ${remaining} autre(s) relation(s) dans la fiche</p>`:''}
      ${compact?'':`<p class="evolution-note">Ces relations concernent des autorités distinctes :
      elles ne fusionnent pas leurs notices ni leurs affiliations historiques.
      Une fusion constitutive ou une filiation partielle ne prouve pas une succession juridique intégrale.</p>`}</section>`;
  }

  function unifiedCard(r){
  const isLab=r.kind==='ORG'&&r.classification.type==='laboratoire';
  const category=isLab?'Laboratoire':natural(r.classification.bsr||r.kind);
  const stateclass=r.activity.active===true?'yes':r.activity.active===false?'no':'';
  const typ=r.classification.type?natural(r.classification.type):null;
  const sector=r.classification.sector?natural(r.classification.sector):null;
  const meta=[r.names.acronym,isLab?r.identifiers.lab:typ,!isLab?sector:null]
    .filter(Boolean).filter((x,i,a)=>a.indexOf(x)===i).map(esc).join(' · ');
  const place=[r.geography.cities_label,country(r.geography.institutional_country_iso2)]
    .filter((v,i)=>i===0?Boolean(v):Boolean(r.geography.institutional_country_iso2))
    .map(esc).join(' · ')||'Localisation à documenter';
  const website=safeUrl(r.website);
  const visual=assetImg(r.id,'Logo : '+r.names.preferred,'lab-primary-logo');
  const count=r.usage.affiliations_linked;
  const usage=count===1?'1 affiliation source liée':count>1?`${count} affiliations sources liées`:'Aucune affiliation source liée';
  const excluded=!r.presentation.visible?'<span class="editorial-state">Hors catalogue</span>':'';
  const provisional=r.validation?.status==='a_verifier'?'<span class="editorial-state">À vérifier</span>':'';
  return `<article class="authority-card laboratory-card${r.presentation.visible?'':' editorial-hidden'}" data-id="${esc(r.id)}">
    <div class="card-head lab-head"><span class="kind lab-kind">${esc(category)}</span><span class="ident">${esc(r.id)}</span>${excluded}${provisional}<span class="state"><span class="state-dot ${stateclass}"></span>${flagLabel(r.activity.active)}</span></div>
    <div class="lab-layout">
      <div class="lab-visual">${visual}</div>
      <div class="lab-content"><h2 class="card-title lab-title">${esc(r.names.preferred)}</h2>
        ${meta?`<p class="lab-meta">${meta}</p>`:''}
        <p class="lab-place" title="Ville de référence et pays de rattachement institutionnel">${place}</p>
        ${website?`<a class="lab-website" href="${esc(website)}" target="_blank" rel="noopener noreferrer">Site officiel <span aria-hidden="true">↗</span></a>`:''}
      </div>
    </div>
    ${parentBlock(r,true)}
    ${childrenBlock(r,true)}
    ${federalAffiliationBlock(r,true)}
    ${evolutionBlock(r,true)}
    <div class="card-foot lab-foot"><span class="ref">${usage}</span><button class="details-trigger" type="button" data-detail="${esc(r.id)}">Consulter la fiche →</button></div>
  </article>`;
}
  function laboratoryCard(r){return unifiedCard(r);}

  // Les niveaux institutionnels sont documentés pour certaines ORG seulement.
  // Ne pas inférer ici l'échelon des SER, des associations, des entreprises ni des
  // syndicats mixtes dont la composition territoriale reste à instruire.
  const INSTITUTIONAL_LEVEL_TYPES=new Set([
    'collectivite_territoriale','epci','musee','etablissement_public',
    'etablissement_public_administratif','agence_federale'
  ]);

  const valueFor=(r,k)=>{
    if(k==='kind')return [r.kind];
    if(k==='activity')return [r.activity.active===true?'oui':r.activity.active===false?'non':'unknown'];
    if(k==='bsr')return [r.classification.bsr||'—'];
    if(k==='sector')return [r.classification.sector||'—'];
    if(k==='country')return [r.geography.institutional_country_iso2||'—'];
    if(k==='type')return [r.classification.type||'—'];
    if(k==='level')return r.classification.level ? [r.classification.level] : [];
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
  // Libellés éditoriaux des facettes, sans altérer les codes du JSON.
  const bsrFacetLabels={COL:'Collectivité territoriale',PRIV:'Entreprise'};
  const levelFacetLabels={
    national:'National',regional:'Régional',departemental:'Départemental',
    communal:'Communal',intercommunal:'Intercommunal',
    metropole:'Métropole (forme)',metropolitain:'Métropolitain (statut particulier)',
    cantonal:'Cantonal',provincial:'Provincial'
  };
  const valLabel=(k,v)=>{
    if(v==='—')return 'Non renseigné';
    if(k==='country')return country(v);
    if(k==='bsr')return bsrFacetLabels[v]||natural(v);
    if(k==='level')return levelFacetLabels[v]||natural(v);
    return natural(v);
  };
  const searchText=r=>[
    r.id,...(legacyByCanonical.get(r.id)||[]),r.names.preferred,r.names.acronym,r.names.other_acronyms.join(' '),r.names.historical_free_text,
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
  function card(r){return unifiedCard(r);}

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
    id=resolveIdentityAlias(id);
    const r=recordById.get(id);if(!r)return;
    const verified=(relsById.get(id)||[]).filter(x=>x.source===id&&VALID_STATES.has(x.validation||'')&&x.type!=='affiliation_federale');
    const byType=Object.groupBy?Object.groupBy(verified,x=>x.type||'relation'):verified.reduce((a,x)=>{(a[x.type||'relation'] ||= []).push(x);return a},{});
    const relHtml=Object.entries(byType).map(([type,items])=>`<p><strong>${esc(natural(type))}</strong></p><ul class="subtle-list">${(type==='tutelle'?[...items].sort((a,b)=>tutelleTextOrder(recordById.get(a.target),recordById.get(b.target))):items).map(item=>`<li>${esc(recordById.get(item.target)?.names.preferred||item.target)} ${item.start||item.end?`<small>(${esc(item.start||'début non daté')} – ${esc(item.end||'fin non documentée')})</small>`:''}</li>`).join('')}</ul>`).join('')||'<p class="detail-desc">Aucune relation validée disponible dans cette extraction.</p>';
    const historicalForms={denominations:[],organes:[],variantes:[],nonValidees:[]};
    for (const item of r.names.history||[]) {
      if (!item.label) continue;
      if (!VALID_STATES.has(item.validation||'')) {
        historicalForms.nonValidees.push(item);
      } else if (item.type==='designation_historique_organe') {
        historicalForms.organes.push(item);
      } else if (item.type==='variante_denomination') {
        historicalForms.variantes.push(item);
      } else {
        historicalForms.denominations.push(item);
      }
    }
    const historicalList=items=>items.length
      ? `<ul class="subtle-list">${items.map(x=>{
          const period=x.start&&x.end
            ? `<small>(${esc(evolutionDate(x.start))} – ${esc(evolutionDate(x.end))})</small>`
            : x.end ? `<small>(jusqu’au ${esc(evolutionDate(x.end))})</small>`
            : x.start ? `<small>(à partir du ${esc(evolutionDate(x.start))})</small>` : '';
          const source=x.source&&safeUrl(x.source)?` · ${link(x.source,'source')||''}`:'';
          return `<li>${esc(x.label)}${period?` ${period}`:''}${source}</li>`;
        }).join('')}</ul>`
      : '';
    const nameHist=historicalList(historicalForms.denominations);
    const organeHist=historicalForms.organes.length
      ? `<ul class="subtle-list">${historicalForms.organes.map(x=>`<li>${esc(x.label)}${x.end?` <small>(jusqu’au ${esc(evolutionDate(x.end))} ; début non documenté)</small>`:''}${x.source && safeUrl(x.source)?` · ${link(x.source,'source')||''}`:''}</li>`).join('')}</ul>`
      : '';
    const varianteHist=historicalList(historicalForms.variantes);
    const others=historicalForms.nonValidees;
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
    const headerLogo=r.presentation?.media?.logo
      ? `<div class="detail-brand">${assetImg(id,'Logo de '+r.names.preferred,'detail-brand-logo')}</div>` : '';
    const validationNotice=r.validation?.status==='a_verifier'
      ? '<p class="detail-context-note">Qualification documentaire à vérifier : certains attributs de cette autorité restent à instruire. Sa présence au catalogue ne signifie pas que ces informations sont définitivement validées.</p>' : '';
    const contextNotice=r.presentation?.visible ? ''
      : '<p class="detail-context-note">Autorité hors catalogue : cette fiche est consultable par les relations institutionnelles, mais aucun cartouche autonome ne figure dans les résultats de recherche.</p>';
    let content=`<div class="detail-head"><div class="detail-head-inner">
      <div class="detail-head-copy"><span class="kind ${kind==='SER'?'ser':''}">${kind}</span>
      <span class="ident">${esc(id)}</span><h2>${esc(r.names.preferred)}</h2>
      <p class="detail-desc">${esc(natural(r.classification.type))} · ${esc(flagLabel(r.activity.active))}</p>
      ${contextNotice}${validationNotice}</div>
      ${headerLogo}</div></div><div class="detail-body">
    <section class="detail-block"><h3>Identité et classification</h3><dl class="detail-dl">${row('Sigle',esc(sigle))}${row('Autres acronymes',extras?esc(extras):null)}${row('Validation documentaire',esc(r.validation?.status==='a_verifier'?'À vérifier':r.validation?.established===true?'Validée':'Non précisée dans cette extraction'))}${row('Catégorie BSR',esc(r.classification.bsr||'Non renseignée'))}${row('Secteur',esc(natural(r.classification.sector)))}${row('Échelon institutionnel',esc(natural(r.classification.level)))}${r.classification.territorial_competence?row('Périmètre de compétence',esc(natural(r.classification.territorial_competence))):''}${row('Type détaillé',esc(natural(r.classification.type)))}</dl></section>
    <section class="detail-block"><h3>Période d'existence</h3><dl class="detail-dl">${row('Statut',esc(flagLabel(r.activity.active)))}${row('Début',esc(r.activity.start||'Non documenté'))}${row('Fin',esc(r.activity.end||'Non documentée'))}</dl></section>
    <section class="detail-block"><h3>Localisation déclarée</h3><dl class="detail-dl">${row('Pays institutionnel',esc(country(r.geography.institutional_country_iso2)))}${row('Ville(s) d’implantation',esc(r.geography.cities_label||'Non renseignée(s)'))}</dl><p class="detail-desc" style="margin-top:9px">Les villes ne constituent pas une géolocalisation vérifiée. Les établissements multi-sites ne sont pas ramenés à un point unique.</p></section>
    <section class="detail-block"><h3>Identifiants et site web</h3><dl class="detail-dl">${row('ROR',r.identifiers.ror?link(r.identifiers.ror,r.identifiers.ror)||esc(r.identifiers.ror):'Non renseigné')}${row('RNSR',rnsr||'Non renseigné')}${row('Unité de recherche',esc(r.identifiers.lab||'Non renseigné'))}${row('IdRef',esc(r.identifiers.idref||'Non renseigné'))}${row('Wikidata',esc(r.identifiers.wikidata||'Non renseigné'))}${row('Site officiel',r.website?link(r.website,'Consulter le site officiel'):'Non renseigné')}</dl></section>
    <section class="detail-block"><h3>Anciennes dénominations et formes historiques</h3>${nameHist||'<p class="detail-desc">Aucune ancienne dénomination validée dans le tableau dédié.</p>'}${others.length?`<p class="detail-desc" style="margin-top:8px">${others.length} autre(s) forme(s) restent documentées avec un statut de validation distinct, sans être présentées ici comme établies.</p>`:''}</section>
    ${organeHist?`<section class="detail-block"><h3>Désignations historiques d’organes</h3><p class="detail-desc">Ces appellations concernent un organe de l’autorité (par exemple son assemblée délibérante), et non un changement d’identité juridique de l’autorité elle-même.</p>${organeHist}</section>`:''}
    ${varianteHist?`<section class="detail-block"><h3>Variantes de dénomination</h3>${varianteHist}</section>`:''}
    <section class="detail-block"><h3>Évolution du statut institutionnel</h3>${legalHtml}</section>
    <section class="detail-block"><h3>Rattachement institutionnel</h3>${parentBlock(r)||'<p class="detail-desc">Aucun rattachement validé à présenter.</p>'}</section>${childrenBlock(r)?`<section class="detail-block"><h3>Services rattachés</h3>${childrenBlock(r)}</section>`:''}<section class="detail-block"><h3>Relations institutionnelles validées</h3>${relHtml}</section>
    ${federalAffiliationBlock(r)?`<section class="detail-block"><h3>Affiliations fédérales</h3>${federalAffiliationBlock(r)}</section>`:''}
    ${evolutionBlock(r,false)?`<section class="detail-block">${evolutionBlock(r,false)}</section>`:''}
    <section class="detail-block"><h3>Affiliations documentées</h3><dl class="detail-dl">${row('Libellés sources liés',esc(r.usage.affiliations_linked))}${row('Dont correspondances validées',esc(r.usage.affiliations_validated))}</dl><p class="detail-desc" style="margin-top:7px">Ces nombres décrivent les rapprochements du référentiel, non le nombre de notices archéologiques publiées.</p></section>
    </div>`;
    $('#detail-content').innerHTML=content;
    const d=$('#details'); if(!d.open)d.showModal();
    if(shouldUpdateHash)updateHash('#'+id);
  }
  function downloadCSV(){
    const list=sortEntries(baseRecords().filter(matches));
    const cols=['Identifiant','Nature','Nom retenu','Acronyme','Catégorie BSR','Type','Secteur','Échelon institutionnel','Périmètre de compétence','Actif','Pays institutionnel','Ville(s)','ROR','RNSR','Site officiel'];
    const dataRows=list.map(x=>[x.id,x.kind,x.names.preferred,x.names.acronym,x.classification.bsr,x.classification.type,x.classification.sector,x.classification.level,x.classification.territorial_competence,flagLabel(x.activity.active),x.geography.institutional_country_iso2,x.geography.cities_label,x.identifiers.ror,x.identifiers.rnsr,x.website]);
    const cell=v=>'"'+String(v??'').replaceAll('"','""')+'"';
    const csv='\ufeff'+[cols,...dataRows].map(row=>row.map(cell).join(';')).join('\r\n');
    let url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='adlfi-referentiels-organismes-selection.csv';document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url);
  }
  function init(d){
    data=d;records=d.authorities;recordById=new Map(records.map(x=>[x.id,x]));relsById=new Map();
    indexIdentityAliases(d.aliases||[]);
    d.relations.forEach(x=>{if(!relsById.has(x.source))relsById.set(x.source,[]);relsById.get(x.source).push(x)});
    indexEvolutions(d.relations);
    indexServiceChildren(d.relations);
    indexFederalAffiliations(d.relations);

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
    $('#details').addEventListener('click',e=>{
      const trigger=e.target.closest?.('button[data-detail]');
      if(trigger){details(trigger.dataset.detail);return;}
      if(e.target===$('#details'))$('#details').close();
    });
    $('#details').addEventListener('close',()=>{if(location.hash)updateHash('')});
    render();const id=decodeURIComponent(location.hash.replace('#',''));
    const canonical=resolveIdentityAlias(id);
    if(recordById.has(canonical))details(canonical,canonical!==id);
  }
  fetch('../data/organismes.json').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}).then(init).catch(err=>{$('#cards').innerHTML='<p class="empty">Impossible de charger les données. Lancer le site avec <code>python3 -m http.server 8000</code> depuis le dossier racine. '+esc(err.message)+'</p>'});
})();
