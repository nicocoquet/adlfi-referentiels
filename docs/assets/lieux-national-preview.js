/* Aperçu fonctionnel national Lieux ; chargé uniquement par apercu-national.html.
 * Ne modifie ni le pilote PACA public, ni ses contours 2026.
 */
(function () {
  'use strict';
  const api=window.AdlfiLieuxNational;
  if (!api) return;
  const $=q=>document.querySelector(q);
  const input=$('#nat-query'),list=$('#nat-suggestions'),year=$('#nat-year');
  const yearValue=$('#nat-year-value'),counter=$('#nat-count');
  const detail=$('#nat-detail'),mapStatus=$('#nat-map-status');
  const wrapper=$('#nat-search-box');
  const state={index:[],byId:new Map(),selected:null,suggestions:[],
    cursor:-1,segmentCache:new Map(),map:null,geoLayer:null,
    byCode:new Map(),overview:null,token:0};
  function el(tag,text,className) {
    const n=document.createElement(tag);
    if (text !== undefined && text !== null) n.textContent=String(text);
    if (className) n.className=className;
    return n;
  }
  function close() {
    list.replaceChildren();list.hidden=true;
    input.setAttribute('aria-expanded','false');
    input.removeAttribute('aria-activedescendant');
    state.cursor=-1;state.suggestions=[];
  }
  function fillResults() {
    const q=input.value;
    list.replaceChildren();state.cursor=-1;
    state.suggestions=api.chercher(state.index,q,10);
    if (!state.suggestions.length) {
      if (api.normaliser(q).length<2) return close();
      list.append(el('li','Aucun résultat dans ces deux index de recette.','lieux-no-match'));
    } else {
      state.suggestions.forEach((item,i)=>{
        const li=el('li');
        li.role='option';li.id='nat-suggestion-'+i;
        li.setAttribute('aria-selected','false');
        const text=el('span');text.append(el('strong',item.label));
        text.append(el('small',item.type==='pactols' ?
          'Pactols · '+(item.lienValide ? 'correspondance PACA validée' :
            'correspondance Insee non validée') :
          'Insee · historique des noms de commune'));
        li.append(text,el('span',item.type==='pactols'?'ARK':item.code,
                             'lieux-suggestion-code'));
        li.addEventListener('mousedown',e=>e.preventDefault());
        li.addEventListener('click',()=>choisir(item));
        list.append(li);
      });
    }
    list.hidden=false;input.setAttribute('aria-expanded','true');
  }
  function focusResult() {
    Array.from(list.children).forEach((li,i)=>{
      li.classList.toggle('is-active',i===state.cursor);
      li.setAttribute('aria-selected',String(i===state.cursor));
    });
    if(state.cursor>=0) {
      input.setAttribute('aria-activedescendant','nat-suggestion-'+state.cursor);
      list.children[state.cursor]?.scrollIntoView({block:'nearest'});
    }
  }
  async function json(url) {
    const res=await fetch(url);
    if(!res.ok) throw new Error('HTTP '+res.status+' · '+url);
    return res.json();
  }
  async function segment(code) {
    const prefix=api.prefixe(code);
    if(!state.segmentCache.has(prefix)) {
      const pending=json('data/segments/cog-'+prefix+'.json');
      state.segmentCache.set(prefix,pending);
      pending.catch(()=>state.segmentCache.delete(prefix));
    }
    return state.segmentCache.get(prefix);
  }
  function row(dl,label,value,href) {
    dl.append(el('dt',label));
    const dd=el('dd');
    if(href) {
      const a=el('a',value);a.href=href;a.target='_blank';
      a.rel='noopener noreferrer';dd.append(a);
    } else dd.textContent=value===undefined||value===null?'Non renseigné':String(value);
    dl.append(dd);
  }
  function section(parent,title) {
    const part=el('section',undefined,'lieux-fiche__group');
    part.append(el('h3',title));
    const dl=el('dl',undefined,'lieux-fiche__dl');part.append(dl);parent.append(part);
    return dl;
  }
  function zone(p,className) {return el('p',p,className||'lieux-fiche__source');}
  function render(item,info) {
    detail.replaceChildren();
    const article=el('article',undefined,'lieux-fiche');
    article.append(el('div',item.type==='pactols' ?
      'Autorité documentaire Pactols' : 'État administratif Insee',
      'lieux-fiche__type'));
    if(item.type==='pactols') {
      article.append(el('h2',info.titre));
      article.append(zone(info.lien_COG_valide ?
        'Correspondance PACA déjà validée' :
        'Aucune correspondance Pactols–COG éditorialement validée',
        info.lien_COG_valide?'nat-state-ok':'nat-state-note'));
      const id=section(article,'Identification documentaire');
      row(id,'ARK Pactols',info.ark,
        'https://ark.frantiq.fr/ark:/'+encodeURIComponent(info.ark.slice(0,5))+
        '/'+encodeURIComponent(info.ark.slice(6)));
      row(id,'Libellés XML',info.variantes.join(' · '));
      row(id,'Mentions XML',info.mentions);
      row(id,'Notices distinctes',info.notices);
      if(info.annees_operation_xml.length)
        row(id,'Années d’opération',info.annees_operation_xml.join(', '));
      if(info.lien_COG_valide) {
        const d=section(article,'Correspondance administrative validée en 2026');
        row(d,'Code Insee',info.lien_COG_valide.code_insee);
        row(d,'Nom COG 2026',info.lien_COG_valide.libelle_cog);
        row(d,'Millésime du lien',info.lien_COG_valide.millesime);
        if(info.correspondance_administrative) {
          row(d,'État au 1er janvier 2026',
              info.correspondance_administrative.etat?.libelle ||
              'Aucun état COM/ARM attesté au COG 2026');
        } else if(info.consultation_COG_historique_meme_code) {
          row(d,'État du même code au 1er janvier '+year.value,
              info.consultation_COG_historique_meme_code.etat?.libelle ||
              'État administratif non documenté');
          article.append(zone('Le lien ARK–COG a été validé au millésime 2026 uniquement. '
            +'L’état antérieur du même code est consultable à titre documentaire, '
            +'sans équivalence Pactols–COG historique établie.','nat-state-warning'));
        }
      } else {
        article.append(zone('Aucun code Insee n’est attribué par ressemblance de nom. '
          +'Les années d’opération archéologique ne datent pas l’identité administrative.'));
      }
    } else {
      article.append(el('h2',info.etat_admin.etat?.libelle ||
        'Code Insee '+info.code_insee));
      article.append(zone('Situation au '+info.etat_admin.date_reference,
                          'nat-state-note'));
      const d=section(article,'Référence administrative');
      row(d,'Code Insee',info.code_insee);
      row(d,'Noms recensés',info.formes_historiques.join(' · '));
      if(info.etat_admin.etat) {
        row(d,'Type de l’état',info.etat_admin.etat.typecom);
        row(d,'Nom à la date',info.etat_admin.etat.libelle);
        if(info.etat_admin.etat.debut_inclus)
          row(d,'Période COM/ARM',info.etat_admin.etat.debut_inclus+
            ' – '+(info.etat_admin.etat.fin_exclue || 'en cours dans COG 2026'));
        if(info.etat_admin.etat.comparent_COG_2026)
          row(d,'Commune parente 2026',info.etat_admin.etat.comparent_COG_2026);
      } else {
        article.append(zone('Aucun état COM/ARM attesté au 1er janvier choisi. '
          +'Les états COMA/COMD historiques ne sont pas entièrement reconstitués ; '
          +'cela ne démontre pas la disparition du lieu.','nat-state-warning'));
      }
      const moves=info.etat_admin.mouvements_deja_survenus;
      if(moves.length) {
        const hist=section(article,'Mouvements Insee déjà survenus');
        for(const m of moves.slice(-8)) {
          const from=m.libelle_avant||'Création administrative';
          const to=m.libelle_apres||'Sortie du champ communal';
          row(hist,m.date_effet+' · MOD '+m.MOD,from+' → '+to);
        }
        if(moves.length>8)
          article.append(zone('Seuls les huit derniers mouvements sont affichés. '
            +'La recette conserve toutes les lignes.','lieux-fiche__source'));
      }
      article.append(zone('Cette entrée Insee ne désigne pas automatiquement un ARK Pactols. '
        +'Le seul partage d’un nom ou d’un code ne constitue pas une validation.'));
    }
    article.append(zone('Aucune géométrie historique n’est attribuée à cette fiche.'));
    detail.append(article);
  }
  function clearDetail() {
    detail.replaceChildren();
    const empty=el('div',undefined,'lieux-empty');
    empty.append(el('h2','Sélectionner un lieu'),
      el('p','La recherche conserve les anciens noms indépendamment du curseur. '
        +'Les résultats Pactols et Insee demeurent distincts.'));
    detail.append(empty);
  }
  function syncMap() {
    if(!state.map) return;
    const y=Number(year.value);
    if(state.geoLayer) {
      if(y===2026 && !state.map.hasLayer(state.geoLayer))
        state.geoLayer.addTo(state.map);
      if(y!==2026 && state.map.hasLayer(state.geoLayer))
        state.map.removeLayer(state.geoLayer);
    }
    const isPaca=state.selected?.type==='pactols' && state.selected.lienValide ||
      state.selected?.type==='cog' && state.byCode.has(state.selected.code);
    const code=state.selected?.code;
    if(y===2026 && code && isPaca && state.byCode.has(code)) {
      const layer=state.byCode.get(code);
      state.map.fitBounds(layer.getBounds(),{maxZoom:11,padding:[25,25]});
    }
    mapStatus.textContent=y===2026 ?
      'Contours visibles : seules 103 correspondances PACA validées, géométries du millésime 2026. '
        +'Les autres résultats n’ont pas de contour vérifié dans cet aperçu.' :
      'Année '+y+' : les contours administratifs 2026 sont masqués. '
        +'Le fond OpenStreetMap est contemporain et ne représente pas les limites historiques.';
  }
  async function choisir(item,updateHistory=true) {
    state.selected=item;close();
    input.value=item?.label||'';
    const current=++state.token;
    if(item) {
      detail.replaceChildren(el('p','Consultation du code ou de l’autorité…'));
      try {
        const code=item.type==='cog' ? item.code : item.code;
        const src=code?await segment(code):null;
        if(current!==state.token) return;
        render(item,api.fiche(item,src,Number(year.value)));
      } catch(error) {
        if(current!==state.token) return;
        detail.replaceChildren(zone('Fiche indisponible : '+error.message,'nat-state-warning'));
      }
    } else clearDetail();
    syncMap();
    if(updateHistory) {
      const url=new URL(location.href);
      url.hash=item?'selection='+encodeURIComponent(item.id):'';
      url.searchParams.set('annee',year.value);
      window.history.replaceState({},'',url);
    }
  }
  function applyYear() {
    yearValue.textContent=year.value;
    if(state.selected) choisir(state.selected);
    else {
      syncMap();
      const url=new URL(location.href);url.searchParams.set('annee',year.value);
      history.replaceState({},'',url);
    }
  }
  async function initialiseMap() {
    if(typeof window.L==='undefined') {
      mapStatus.textContent='Leaflet indisponible. Les index et fiches restent accessibles.';
      return;
    }
    const L=window.L;
    state.map=L.map('nat-map',{scrollWheelZoom:false,preferCanvas:true})
      .setView([46.6,2.3],6);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
      maxZoom:18,
      attribution:'© contributeurs OpenStreetMap'
    }).addTo(state.map);
    try {
      const geo=await json('../../data/lieux-communes.geojson');
      const validated=new Map(state.index.filter(x=>x.type==='pactols'&&x.lienValide)
        .map(x=>[x.code,x.ark]));
      if(geo.type!=='FeatureCollection'||geo.features?.length!==103) {
        throw new Error('Pilote PACA : 103 géométries attendues');
      }
      for(const f of geo.features) {
        if(validated.get(f.properties?.code)!==f.properties?.ark_pactols) {
          throw new Error('Contours et validations PACA non concordants');
        }
      }
      state.geoLayer=L.geoJSON(geo,{
        style:{color:'#407d84',weight:1.1,fillColor:'#78a7ab',fillOpacity:0.15},
        onEachFeature(f,layer) {
          state.byCode.set(f.properties.code,layer);
          layer.bindTooltip(String(f.properties.nom||f.properties.code),{sticky:true});
          layer.on('click',()=>{
            const code=f.properties.code;
            const item=state.byId.get('pactols:'+f.properties.ark_pactols);
            if(item) choisir(item);
            else {
              const cog=state.byId.get('cog:'+code);
              if(cog) choisir(cog);
            }
          });
        }
      });
      syncMap();
    } catch(e) {
      mapStatus.textContent='Fond cartographique disponible ; aucun contour chargé : '+e.message+
        '. Les recherches restent opérationnelles.';
    }
  }
  async function init() {
    const [pactols,cog,manifest]=await Promise.all([
      json('data/index-autorites-pactols-xml.json'),
      json('data/index-toponymes-cog.json'),
      json('data/manifest-cog-national.json'),
    ]);
    if(manifest.schema!=='adlfi.lieux.cog.national.temporel.recette.v1' ||
       manifest.statut!=='recette_non_publiee')
      throw new Error('Manifeste COG de recette incompatible');
    const index=api.creerIndex(pactols,cog);
    if(index.length!==49090 ||
       index.filter(x=>x.type==='pactols'&&x.lienValide).length!==103)
      throw new Error('Volumes ou validations de sources incompatibles');
    state.index=index;
    state.byId=new Map(index.map(e=>[e.id,e]));
    counter.textContent='9 928 ARK Pactols · 39 162 codes Insee';
    const query=new URLSearchParams(location.search);
    const start=Number(query.get('annee')||2026);
    if(Number.isInteger(start)&&start>=1943&&start<=2026)year.value=String(start);
    yearValue.textContent=year.value;
    await initialiseMap();
    const sel=new URLSearchParams(location.hash.slice(1)).get('selection');
    if(sel && state.byId.has(sel)) await choisir(state.byId.get(sel),false);
    else syncMap();
  }
  input.addEventListener('input',fillResults);
  input.addEventListener('focus',fillResults);
  input.addEventListener('keydown',event=>{
    if(event.key==='Escape')return close();
    if(event.key==='ArrowDown'||event.key==='ArrowUp') {
      if(list.hidden)fillResults();
      if(!state.suggestions.length)return;
      event.preventDefault();
      state.cursor=(state.cursor+(event.key==='ArrowDown'?1:-1)+
        state.suggestions.length)%state.suggestions.length;
      focusResult();
    }
    if(event.key==='Enter'&&!list.hidden&&state.suggestions.length) {
      event.preventDefault();
      choisir(state.suggestions[Math.max(0,state.cursor)]);
    }
  });
  document.addEventListener('pointerdown',e=>{
    if(!wrapper.contains(e.target))close();
  });
  $('#nat-reset').addEventListener('click',()=>choisir(null));
  year.addEventListener('input',applyYear);
  window.addEventListener('hashchange',()=>{
    const sel=new URLSearchParams(location.hash.slice(1)).get('selection');
    choisir(sel?state.byId.get(sel)||null:null,false);
  });
  init().catch(error=>{
    counter.textContent='Données de recette indisponibles';
    detail.replaceChildren(zone('Chargement impossible : '+error.message+
      '. Utiliser le paquet de recette complet et un serveur HTTP local.',
      'nat-state-warning'));
  });
}());
