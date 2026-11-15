/* Interface de recette Lieux, quatre régions. Carte = uniquement contours COG 2026. */
(function () {
  'use strict';
  const core = window.AdlfiLieuxChronologieCore;
  const $ = id => document.getElementById(id);
  const region = $('chrono-region'), year = $('chrono-year');
  const yearLabel = $('chrono-year-label'), query = $('chrono-query');
  const results = $('chrono-results'), detail = $('chrono-detail');
  const status = $('chrono-map-status'), count = $('chrono-count');
  const reference = $('chrono-reference'), scope = $('chrono-scope');
  const ROOT = '../../data/lieux-chronologie/';
  const state = { data: null, geo: null, index: [], selected: null,
    map: null, contours: null, layers: new Map(), token: 0 };
  const names = {paca: 'Provence-Alpes-Côte d’Azur', corse: 'Corse',
    pdl: 'Pays de la Loire', bfc: 'Bourgogne-Franche-Comté'};

  function text(tag, value, cls) {
    const n = document.createElement(tag);
    if (value !== undefined && value !== null) n.textContent = String(value);
    if (cls) n.className = cls;
    return n;
  }
  function ligne(container, label, value, href) {
    const row = text('div', undefined, 'chrono-detail-line');
    row.append(text('dt',label));
    const dd = text('dd');
    if (href) {
      const link = text('a',value); link.href = href;
      link.rel = 'noopener noreferrer'; link.target = '_blank';
      dd.append(link);
    } else dd.textContent = String(value ?? 'Non documenté');
    row.append(dd); container.append(row);
  }
  function resetDetail() {
    detail.replaceChildren(text('p','Sélectionnez une commune actuelle sur la carte ou recherchez un nom historique.'));
  }
  function drawDetail() {
    if (!state.data || !state.selected) return resetDetail();
    const selected = state.selected;
    const t = core.etat(state.data,selected.code,Number(year.value));
    const a = state.data.alignements_Pactols_COG_valides_2026.find(
      x=>x.code_insee===selected.code);
    const article = text('article',undefined,'chrono-fiche');
    article.append(text('div', selected.kind==='pactols' ?
      'Autorité Pactols validée en PACA (2026)' : 'Code officiel géographique',
      'lieux-fiche__type'));
    article.append(text('h2', t.etat?.libelle || selected.label ||
      ('Code INSEE '+selected.code)));
    article.append(text('p','Situation au '+t.date_reference,'chrono-date'));
    const dl = text('dl');
    ligne(dl,'Code INSEE',selected.code);
    if (t.etat) {
      ligne(dl,'Statut',t.etat.typecom);
      ligne(dl,'Libellé officiel',t.etat.libelle);
      if (t.etat.debut_inclus)
        ligne(dl,'Période du libellé',t.etat.debut_inclus+' – '+
              (t.etat.fin_exclue || 'en cours au COG 2026'));
      if (t.etat.comparent_2026)
        ligne(dl,'Commune parente en 2026',t.etat.comparent_2026);
    } else article.append(text('p',
      'Aucun état COM attesté à cette date pour ce code. Cela ne démontre pas la disparition du lieu.',
      'chrono-warning'));
    if (a) {
      const ark = a.ark_pactols;
      ligne(dl,'Concept Pactols',a.libelle_pactols,
        'https://ark.frantiq.fr/ark:/'+ark);
      ligne(dl,'ARK',ark);
      article.append(text('p',
        'Correspondance Pactols–COG validée pour 2026 seulement. La consultation '+
        'du même code à une date antérieure n’établit pas une équivalence historique.',
        'chrono-validated'));
    } else article.append(text('p',
      'Aucune correspondance Pactols–COG individuellement validée pour ce code dans ce lot.',
      'chrono-warning'));
    article.append(dl);
    const history = t.mouvements.slice(-8);
    if (history.length) {
      article.append(text('h3','Dernières lignes de mouvement COG déjà survenues'));
      const ul = text('ul',undefined,'chrono-events');
      for (const ev of history) {
        ul.append(text('li',ev.date_effet+' · MOD '+ev.mod+' : '+
          (ev.libelle_avant || 'création')+' → '+(ev.libelle_apres || 'sortie du champ')));
      }
      article.append(ul);
      article.append(text('p','Les lignes COG ne sont pas des actes juridiques indépendants.','chrono-small'));
    }
    article.append(text('p','Aucune géométrie historique n’est attribuée.','chrono-small'));
    detail.replaceChildren(article);
  }
  function afficherContours() {
    if (!state.map || !state.contours) return;
    const show = Number(year.value)===2026 || reference.checked;
    if (show && !state.map.hasLayer(state.contours)) state.contours.addTo(state.map);
    if (!show && state.map.hasLayer(state.contours)) state.map.removeLayer(state.contours);
    status.textContent = Number(year.value)===2026 ?
      'Contours des communes au COG 2026 uniquement (100 m). Les alignements AdlFI validés sont distingués en PACA.' :
      show ?
        'Attention : limites de 2026 affichées comme REPÈRES ACTUELS, sans valeur pour '+year.value+'.' :
        'Au '+year.value+' : contours 2026 masqués. Le fond OpenStreetMap est contemporain ; aucune limite ancienne n’est inventée.';
  }
  function highlight() {
    if (!state.contours) return;
    for (const [code, layer] of state.layers) {
      const selected = state.selected?.code === code;
      layer.setStyle({
        color: selected ? '#b0613a' :
          (region.value==='paca' &&
            (layer.feature.properties?.ark_pactols_valide_2026) ? '#39777b' : '#839aa2'),
        weight:selected ? 3 : 0.7,
        fillOpacity:selected ? 0.23 : 0.055,
        fillColor:selected ? '#c57a55' : '#84b5b6',
      });
      if(selected)layer.bringToFront();
    }
  }
  function select(entry) {
    state.selected=entry;
    results.hidden=true;
    query.value=entry ? entry.label : '';
    drawDetail(); highlight();
    if (entry && state.layers.has(entry.code) && state.map) {
      state.map.fitBounds(state.layers.get(entry.code).getBounds(),
        {padding:[36,36],maxZoom:11});
    }
    updateUrl();
  }
  function updateUrl() {
    const u = new URL(location.href);
    u.searchParams.set('region',region.value);
    u.searchParams.set('annee',year.value);
    if (state.selected) u.searchParams.set('code',state.selected.code);
    else u.searchParams.delete('code');
    history.replaceState(null,'',u);
  }
  function search() {
    results.replaceChildren();
    if (!state.index.length || core.normaliser(query.value).length<2) {
      results.hidden=true; return;
    }
    const hits=core.chercher(state.index,query.value,12);
    if(!hits.length)results.append(text('li','Aucun résultat dans les codes de cette région.'));
    for (const hit of hits) {
      const li = text('li');
      const btn = text('button',hit.label+' · '+(hit.kind==='pactols'?
        'Pactols validé 2026':'Insee '+hit.code));
      btn.type='button';btn.addEventListener('click',()=>select(hit));
      li.append(btn);results.append(li);
    }
    results.hidden=false;
  }
  async function json(url) {
    const r=await fetch(url);
    if(!r.ok)throw new Error('HTTP '+r.status+' : '+url);
    return r.json();
  }
  async function setRegion() {
    const seq=++state.token;
    results.hidden=true;query.value='';
    state.selected=null;state.index=[];
    count.textContent='Chargement : '+names[region.value]+'…';
    scope.textContent=names[region.value]+' · COG 2026';
    if(state.contours && state.map) state.map.removeLayer(state.contours);
    state.contours=null;state.layers.clear();
    try {
      const [data,geo]=await Promise.all([
        json(ROOT+'cog-'+region.value+'.json'),
        json(ROOT+'contours-2026-'+region.value+'.geojson'),
      ]);
      if(seq!==state.token) return;
      core.verifier(data);
      if(data.region!==region.value || geo.type!=='FeatureCollection' ||
          geo.provenance?.millesime!==2026)
        throw new Error('Données régionales ou géométries incompatibles');
      state.data=data;state.geo=geo;state.index=core.indexer(data);
      if(state.map) {
        state.contours=window.L.geoJSON(geo, {
          renderer:window.L.canvas(),
          style:{color:'#839aa2',weight:0.7,fillOpacity:0.055},
          onEachFeature(f,l) {
            const code=f.properties?.code;
            if(!code) return;
            state.layers.set(code,l);
            l.bindTooltip(f.properties.nom+' · COG '+code);
            l.on('click',()=>{
              const hit=state.index.find(x=>x.kind==='cog'&&x.code===code);
              if(hit)select(hit);
            });
          },
        });
        const bounds=state.contours.getBounds();
        if(bounds.isValid()) state.map.fitBounds(bounds,{padding:[20,20]});
      }
      const url=new URL(location.href);
      const code=url.searchParams.get('code');
      if(code) {
        const item=state.index.find(x=>x.kind==='cog'&&x.code===code);
        if(item)state.selected=item;
      }
      displayYear();
    } catch(err) {
      if(seq!==state.token)return;
      state.data=null;
      count.textContent='Données de recette indisponibles : '+err.message+
        '. Générer les fichiers avec le workflow de la PR.';
      status.textContent='Aucune géométrie chargée.';
      resetDetail();
    }
  }
  function displayYear() {
    yearLabel.textContent=year.value;
    reference.checked=false;
    afficherContours();drawDetail();highlight();
    if(state.data) {
      count.textContent=names[region.value]+' · '+core.nombreCommunes(
        state.data,Number(year.value))+' états COM au 1er janvier '+year.value+
        ' dans l’index des codes étudiés · '+
        state.data.alignements_Pactols_COG_valides_2026.length+
        ' correspondances Pactols validées au millésime 2026';
    }
    updateUrl();
  }
  function init() {
    const u=new URL(location.href);
    if(names[u.searchParams.get('region')])region.value=u.searchParams.get('region');
    const y=Number(u.searchParams.get('annee'));
    if(Number.isInteger(y)&&y>=1943&&y<=2026)year.value=String(y);
    if(window.L) {
      state.map=window.L.map('chrono-map',{scrollWheelZoom:false,preferCanvas:true})
        .setView([46.5,2.2],6);
      window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
        maxZoom:18,attribution:'© contributeurs OpenStreetMap'
      }).addTo(state.map);
    } else status.textContent='Leaflet indisponible ; la recherche et les fiches restent accessibles.';
    region.addEventListener('change',setRegion);
    year.addEventListener('input',displayYear);
    $('chrono-prev').addEventListener('click',()=>{
      year.value=String(Math.max(1943,Number(year.value)-1));displayYear();
    });
    $('chrono-next').addEventListener('click',()=>{
      year.value=String(Math.min(2026,Number(year.value)+1));displayYear();
    });
    $('chrono-now').addEventListener('click',()=>{year.value='2026';displayYear();});
    reference.addEventListener('change',afficherContours);
    query.addEventListener('input',search);
    query.addEventListener('keydown',e=>{
      if(e.key==='Escape'){results.hidden=true;}
      if(e.key==='Enter'&&!results.hidden) {
        const hit=core.chercher(state.index,query.value,1)[0];
        if(hit)select(hit);
      }
    });
    setRegion();
  }
  init();
}());