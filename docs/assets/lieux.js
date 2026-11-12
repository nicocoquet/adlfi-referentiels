/* Explorateur cartographique statique des 103 lieux PACA validés. */
(function () {
  'use strict';

  const $ = selector => document.querySelector(selector);
  const search = window.AdlfiLieuxSearch;
  const input = $('#lieux-query');
  const options = $('#lieux-suggestions');
  const wrapper = $('#lieux-search-box');
  const detail = $('#lieux-detail-body');
  const counter = $('#lieux-counter');
  const mapStatus = $('#lieux-map-status');
  const reset = $('#lieux-reset');
  const DEPARTEMENTS = {
    '04': 'Alpes-de-Haute-Provence',
    '05': 'Hautes-Alpes',
    '06': 'Alpes-Maritimes',
    '13': 'Bouches-du-Rhône',
    '83': 'Var',
    '84': 'Vaucluse',
  };
  const state = {
    entries: [],
    byArk: new Map(),
    layers: new Map(),
    map: null,
    overlays: null,
    overview: null,
    selected: null,
    matches: [],
    active: -1,
  };

  function node(tag, text, className) {
    const el = document.createElement(tag);
    if (text !== undefined && text !== null) el.textContent = String(text);
    if (className) el.className = className;
    return el;
  }

  function clearNode(element) {
    element.replaceChildren();
  }

  function closeSuggestions() {
    options.hidden = true;
    state.active = -1;
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
  }

  function highlightOption() {
    const children = Array.from(options.children);
    children.forEach((li, i) => {
      li.classList.toggle('is-active', i === state.active);
      if (li.getAttribute('role') === 'option') {
        li.setAttribute('aria-selected', String(i === state.active));
      }
    });
    if (state.active < 0 || state.active >= state.matches.length) {
      input.removeAttribute('aria-activedescendant');
    } else {
      input.setAttribute('aria-activedescendant', 'lieux-option-' + state.active);
      children[state.active]?.scrollIntoView({ block: 'nearest' });
    }
  }

  function renderSuggestions() {
    const q = input.value.trim();
    clearNode(options);
    state.active = -1;
    if (!q || !state.entries.length) {
      closeSuggestions();
      return;
    }
    state.matches = search.chercher(state.entries, q, 8);
    if (!state.matches.length) {
      const li = node('li', 'Aucun lieu validé dans ce pilote pour cette recherche.', 'lieux-no-match');
      options.append(li);
    } else {
      state.matches.forEach((item, i) => {
        const li = node('li');
        li.setAttribute('role', 'option');
        li.id = 'lieux-option-' + i;
        li.setAttribute('aria-selected', 'false');
        const text = node('span');
        text.append(node('strong', item.label));
        const desc = DEPARTEMENTS[item.departement] || item.departement;
        text.append(node('small', desc +
          (item.label !== item.labelCOG ? ' · COG : ' + item.labelCOG : '')));
        li.append(text, node('span', item.code, 'lieux-suggestion-code'));
        li.addEventListener('mousedown', event => event.preventDefault());
        li.addEventListener('click', () => choisir(item.ark));
        options.append(li);
      });
    }
    options.hidden = false;
    input.setAttribute('aria-expanded', 'true');
  }

  function group(title) {
    const section = node('section', undefined, 'lieux-fiche__group');
    section.append(node('h3', title));
    const dl = node('dl', undefined, 'lieux-fiche__dl');
    section.append(dl);
    return { section, dl };
  }

  function field(dl, label, value, url) {
    dl.append(node('dt', label));
    const dd = node('dd');
    if (url) {
      const anchor = node('a', value);
      anchor.href = url;
      anchor.target = '_blank';
      anchor.rel = 'noopener noreferrer';
      dd.append(anchor);
    } else {
      dd.textContent = value === undefined || value === null ? 'Non renseigné' : String(value);
    }
    dl.append(dd);
  }

  function fiche(item) {
    clearNode(detail);
    if (!item) {
      const empty = node('div', undefined, 'lieux-empty');
      empty.append(node('h2', 'Sélectionner un lieu'));
      empty.append(node('p',
        'Recherchez une autorité Pactols ou cliquez sur une commune de la carte ' +
        'pour consulter son identifiant INSEE et sa correspondance validée.'));
      detail.append(empty);
      return;
    }
    const record = item.autorite;
    const relation = record.correspondances[0];
    const body = node('article', undefined, 'lieux-fiche');
    body.append(node('div', 'Autorité géographique Pactols', 'lieux-fiche__type'));
    body.append(node('h2', record.libelle_pactols));
    body.append(node('span', 'Correspondance éditoriale validée', 'lieux-fiche__status'));

    const identity = group('Identification documentaire');
    field(identity.dl, 'Identifiant ARK', record.ark_pactols,
      'https://ark.frantiq.fr/ark:/' + encodeURI(record.ark_pactols));
    field(identity.dl, 'Type de lieu', 'Commune');
    body.append(identity.section);

    const insee = group('Référence administrative');
    field(insee.dl, 'Nom COG', relation.libelle_cog);
    field(insee.dl, 'Code INSEE', relation.code_insee);
    field(insee.dl, 'Département', DEPARTEMENTS[relation.departement] || relation.departement);
    field(insee.dl, 'Millésime', 'COG ' + relation.millesime_cog);
    body.append(insee.section);

    const trace = group('Validation et provenance');
    field(trace.dl, 'Validation', 'AdlFI · ' + relation.validation.date);
    field(trace.dl, 'Relation', 'Correspondance communale validée');
    body.append(trace.section);
    trace.section.append(node('p', 'Source du contrôle : ' + relation.validation.source,
      'lieux-fiche__source'));

    const back = node('button', 'Revenir à la vue générale', 'lieux-fiche__back');
    back.type = 'button';
    back.addEventListener('click', () => choisir(null));
    body.append(back);
    detail.append(body);
  }

  function polygonStyle() {
    return { color: '#497e83', weight: 1.05, opacity: 0.8, fillColor: '#69a4a8',
      fillOpacity: 0.17 };
  }

  function selectedStyle() {
    return { color: '#a35f43', weight: 2.8, opacity: 1, fillColor: '#bd7655',
      fillOpacity: 0.30 };
  }

  function updateMapSelection(ark) {
    for (const [id, layer] of state.layers) {
      layer.setStyle(id === ark ? selectedStyle() : polygonStyle());
    }
    if (!state.map) return;
    if (ark && state.layers.has(ark)) {
      const selected = state.layers.get(ark);
      selected.bringToFront();
      state.map.fitBounds(selected.getBounds(), {
        animate: true,
        padding: [36, 36],
        maxZoom: 11,
      });
    } else if (!ark && state.overview?.isValid()) {
      state.map.fitBounds(state.overview, { animate: true, padding: [28, 28] });
    }
  }

  function arkFromHash() {
    if (!window.location.hash.startsWith('#ark=')) return null;
    const ark = new URLSearchParams(window.location.hash.slice(1)).get('ark');
    return state.byArk.has(ark) ? ark : null;
  }

  function choisir(ark, writeHistory = true) {
    const item = ark ? state.byArk.get(ark) : null;
    if (ark && !item) return;
    state.selected = item ? item.ark : null;
    closeSuggestions();
    state.matches = [];
    input.value = item ? item.label : '';
    fiche(item);
    updateMapSelection(state.selected);
    if (writeHistory) {
      const url = new URL(window.location.href);
      url.hash = ark ? 'ark=' + encodeURIComponent(ark) : '';
      if (url.href !== window.location.href) {
        window.history.pushState({ ark: state.selected }, '', url);
      }
    }
  }

  function setupMap(geo) {
    if (typeof window.L === 'undefined') {
      mapStatus.textContent = 'Bibliothèque cartographique indisponible. La recherche et les fiches restent accessibles.';
      return;
    }
    const L = window.L;
    const map = L.map('lieux-map', { scrollWheelZoom: false, preferCanvas: true,
      zoomControl: false });
    state.map = map;
    L.control.zoom({ position: 'topright' }).addTo(map);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">contributeurs OpenStreetMap</a>',
    }).addTo(map);
    map.attributionControl.addAttribution(
      'Contours : <a href="https://www.data.gouv.fr/datasets/contours-administratifs" target="_blank" rel="noopener noreferrer">data.gouv.fr</a> · ODbL'
    );
    const layer = L.geoJSON(geo, {
      style: polygonStyle,
      onEachFeature: function (feature, outline) {
        const ark = feature.properties.ark_pactols;
        state.layers.set(ark, outline);
        const label = state.byArk.get(ark)?.label || feature.properties.nom;
        const tooltip = document.createElement('span');
        tooltip.textContent = label;
        outline.bindTooltip(tooltip, { sticky: true, direction: 'top' });
        outline.on('click', () => choisir(ark));
        outline.on('mouseover', () => {
          if (state.selected !== ark) outline.setStyle({
            color: '#226b76', weight: 2, fillOpacity: 0.29,
          });
        });
        outline.on('mouseout', () => {
          outline.setStyle(state.selected === ark ? selectedStyle() : polygonStyle());
        });
      },
    }).addTo(map);
    state.overlays = layer;
    state.overview = layer.getBounds();
    map.fitBounds(state.overview, { padding: [28, 28], animate: false });
    mapStatus.textContent = state.layers.size +
      ' contours communaux documentés · Cliquez sur un contour pour consulter sa fiche.';
  }

  function verifierJeux(data, geo) {
    if (data.schema_version !== '0.1.0' || data.module !== 'lieux' ||
        data.perimetre !== 'PACA' || data.statut_publication !== 'pilote_valide' ||
        data.autorites?.length !== 103 ||
        geo.type !== 'FeatureCollection' || geo.features?.length !== 103) {
      throw new Error('Structure ou effectif du pilote PACA incohérent.');
    }
    const arks = new Set(), codes = new Set();
    for (const entry of data.autorites) {
      const rel = entry.correspondances?.[0];
      if (!/^26678\/[A-Za-z0-9]+$/.test(entry.ark_pactols) ||
          !/^\d{5}$/.test(rel?.code_insee || '') ||
          entry.correspondances.length !== 1 ||
          rel.validation?.statut !== 'VALIDE_EDITEUR_2026_10_18' ||
          arks.has(entry.ark_pactols) || codes.has(rel.code_insee)) {
        throw new Error('Identifiant ou validation Pactols–COG invalide.');
      }
      arks.add(entry.ark_pactols);
      codes.add(rel.code_insee);
    }
    const geocodes = new Set();
    for (const feature of geo.features) {
      const code = feature.properties?.code;
      if (!codes.has(code) || geocodes.has(code) ||
          !arks.has(feature.properties?.ark_pactols) ||
          !feature.geometry?.coordinates?.length) {
        throw new Error('Géométrie non alignée sur les autorités validées.');
      }
      geocodes.add(code);
    }
  }

  async function loadJSON(url) {
    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) throw new Error('Chargement impossible : ' + url + ' (HTTP ' + response.status + ')');
    return response.json();
  }

  async function init() {
    if (!search) throw new Error('Module de recherche manquant.');
    const [data, geo] = await Promise.all([
      loadJSON('../data/lieux.json'), loadJSON('../data/lieux-communes.geojson'),
    ]);
    verifierJeux(data, geo);
    state.entries = search.creerIndex(data.autorites);
    state.byArk = new Map(state.entries.map(e => [e.ark, e]));
    counter.textContent = state.entries.length + ' lieux validés · PACA';
    try {
      setupMap(geo);
    } catch (error) {
      mapStatus.textContent = 'Carte non disponible : ' + error.message +
        '. La recherche et les fiches restent utilisables.';
    }
    const fromLink = arkFromHash();
    if (fromLink) choisir(fromLink, false);
  }

  input.addEventListener('input', renderSuggestions);
  input.addEventListener('focus', renderSuggestions);
  input.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      closeSuggestions();
      return;
    }
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      if (options.hidden) renderSuggestions();
      if (!state.matches.length) return;
      event.preventDefault();
      const dir = event.key === 'ArrowDown' ? 1 : -1;
      state.active = (state.active + dir + state.matches.length) % state.matches.length;
      highlightOption();
      return;
    }
    if (event.key === 'Enter' && !options.hidden && state.matches.length) {
      event.preventDefault();
      choisir(state.matches[Math.max(0, state.active)].ark);
    }
  });
  document.addEventListener('pointerdown', event => {
    if (!wrapper.contains(event.target)) closeSuggestions();
  });
  reset.addEventListener('click', () => choisir(null));
  window.addEventListener('popstate', () => choisir(arkFromHash(), false));
  window.addEventListener('hashchange', () => choisir(arkFromHash(), false));

  init().catch(error => {
    counter.textContent = 'Données indisponibles';
    mapStatus.textContent = 'Impossible de charger le pilote : ' + error.message +
      '. Lancer le site depuis un serveur HTTP local pour tester les fichiers.';
    const empty = node('p', 'Le référentiel des lieux est temporairement indisponible.');
    clearNode(detail);
    detail.append(empty);
  });
}());
