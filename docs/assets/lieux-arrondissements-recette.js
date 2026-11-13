/* Prévisualisation en recette des 45 arrondissements municipaux du COG 2026.
 * Indépendante du pilote Pactols–COG PACA : aucune fusion implicite de statuts.
 */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const refs = { status: $('arm-status'), detail: $('arm-detail'), search: $('arm-search'),
    city: $('arm-ville'), form: $('arm-form'), options: $('arm-suggestions') };
  const byCode = new Map(), layers = new Map();
  let map = null, outline = null, focus = null;
  const regionStyle = { color: '#497e83', weight: 1.1, fillColor: '#69a4a8', fillOpacity: .23 };
  const selectedStyle = { color: '#a35f43', weight: 3, fillColor: '#bd7655', fillOpacity: .45 };

  function node(tag, content, cls) {
    const el = document.createElement(tag);
    if (content !== undefined) el.textContent = String(content);
    if (cls) el.className = cls;
    return el;
  }
  function norm(text) {
    return String(text ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase('fr').replace(/[^a-z0-9]+/g, ' ').trim();
  }
  function addField(dl, key, value, href) {
    dl.append(node('dt', key));
    const dd = node('dd');
    if (href) { const a=node('a', value); a.href=href; a.target='_blank'; a.rel='noopener noreferrer'; dd.append(a); }
    else dd.textContent=String(value);
    dl.append(dd);
  }
  function show(ident) {
    const a=byCode.get(ident);
    if (!a) { refs.status.textContent='Arrondissement introuvable dans ce jeu de recette.'; return; }
    focus=ident;
    for (const [code,layer] of layers) layer.setStyle(code===ident?selectedStyle:regionStyle);
    const selected=layers.get(ident);
    if (selected && map) { selected.bringToFront(); map.fitBounds(selected.getBounds(),{maxZoom:13,padding:[30,30]}); }
    refs.search.value=a.libelle;
    refs.city.value=a.commune_parente.nom;
    refs.detail.replaceChildren();
    refs.detail.append(node('p','Arrondissement municipal · COG 2026'));
    refs.detail.append(node('h2',a.libelle));
    const dl=node('dl');
    addField(dl,'Code INSEE',a.code_insee);
    addField(dl,'Nom COG',a.libelle_cog);
    addField(dl,'Commune parente',a.commune_parente.nom+' ('+a.commune_parente.code_insee+')');
    addField(dl,'Pactols (commune)',a.commune_parente.ark_pactols,
      'https://ark.frantiq.fr/ark:/'+a.commune_parente.ark_pactols);
    addField(dl,'Attestation AdlFI',a.attestation_adlfi.observe_dans_titre?'Titre de notice attesté':'Aucune mention repérée');
    addField(dl,'Géométrie','COG 2026 · contour non historique');
    refs.detail.append(dl);
    refs.status.textContent=a.libelle+' — code '+a.code_insee;
    const url=new URL(window.location.href);
    url.hash='arm='+encodeURIComponent(ident);
    window.history.replaceState(null,'',url);
  }
  function verifier(data,geo) {
    if (data.schema_version!=='0.1.0' || data.type_entite!=='arrondissement_municipal' ||
        data.autorites?.length!==45 || geo.features?.length!==45 ||
        geo.metadata?.millesime!==2026) throw new Error('Contrat de recette non respecté');
    const codes=new Set(data.autorites.map(x=>x.code_insee));
    if (codes.size!==45 || geo.features.some(x=>!codes.has(x.properties?.code_insee_arm))) {
      throw new Error('Alignement COG/contours invalide');
    }
    for (const a of data.autorites) byCode.set(a.code_insee,a);
  }
  async function getJSON(uri) {
    const r=await fetch(uri);
    if (!r.ok) throw new Error('HTTP '+r.status+' : '+uri);
    return r.json();
  }
  async function main() {
    const [data,geo]=await Promise.all([
      getJSON('../data/lieux-arrondissements.json'),
      getJSON('../data/lieux-arrondissements.geojson'),
    ]);
    verifier(data,geo);
    for (const a of data.autorites) {
      const option=node('option'); option.value=a.libelle; option.label=a.code_insee; refs.options.append(option);
    }
    refs.status.textContent='45 arrondissements · '+data.totaux.attestees_adlfi+' attestés dans les titres AdlFI · COG 2026';
    if (!window.L) { refs.status.textContent+=' · Carte indisponible (Leaflet non chargé).'; return; }
    const L=window.L;
    map=L.map('arm-map',{scrollWheelZoom:false,preferCanvas:true});
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
      maxZoom:18,attribution:'© <a href="https://www.openstreetmap.org/copyright">contributeurs OpenStreetMap</a>',
    }).addTo(map);
    map.attributionControl.addAttribution('<a href="https://www.data.gouv.fr/datasets/contours-administratifs">Contours data.gouv.fr</a> · ODbL');
    outline=L.geoJSON(geo,{
      style:regionStyle,
      onEachFeature(feature,layer) {
        const code=feature.properties.code_insee_arm;
        layers.set(code,layer);
        const a=byCode.get(code);
        const tip=node('span',a.libelle+' — '+code);
        layer.bindTooltip(tip,{sticky:true});
        layer.on('click',()=>show(code));
      },
    }).addTo(map);
    map.fitBounds(outline.getBounds(),{padding:[25,25]});
    const hash=new URLSearchParams(window.location.hash.slice(1)).get('arm');
    if (byCode.has(hash)) show(hash);
  }
  refs.form.addEventListener('submit',event=>{
    event.preventDefault();
    const q=norm(refs.search.value);
    if (!q) return;
    const city=refs.city.value;
    const found=[...byCode.values()].find(a=>(!city || a.commune_parente.nom===city)&&
      [a.code_insee,a.libelle,a.libelle_cog].some(v=>norm(v)===q)) ||
      [...byCode.values()].find(a=>(!city || a.commune_parente.nom===city)&&
      [a.libelle,a.libelle_cog,a.code_insee].some(v=>norm(v).includes(q)));
    if (found) show(found.code_insee);
    else refs.status.textContent='Aucun arrondissement ne correspond à cette recherche.';
  });
  refs.city.addEventListener('change',()=>{
    if (!map||!outline) return;
    const city=refs.city.value;
    const chosen=[...byCode.values()].filter(a=>!city||a.commune_parente.nom===city);
    const group=window.L.featureGroup(chosen.map(a=>layers.get(a.code_insee)));
    if (group.getBounds().isValid()) map.fitBounds(group.getBounds(),{padding:[25,25]});
  });
  $('arm-reset').addEventListener('click',()=>{
    focus=null; refs.search.value=''; refs.city.value='';
    refs.detail.replaceChildren(node('p','Sélectionnez un contour ou recherchez un arrondissement.'));
    for(const layer of layers.values())layer.setStyle(regionStyle);
    if(map&&outline)map.fitBounds(outline.getBounds(),{padding:[25,25]});
    refs.status.textContent='45 arrondissements · COG 2026';
    const url=new URL(window.location.href); url.hash=''; window.history.replaceState(null,'',url);
  });
  main().catch(error=>{refs.status.textContent='Recette indisponible : '+error.message;});
}());
