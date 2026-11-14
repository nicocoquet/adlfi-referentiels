/* Contrat commun de consultation Pactols XML / COG national. RECETTE.
 * Un ARK et un code COG sont DEUX types de résultats. Une similarité de
 * nom ou la conservation d'un code n'autorise aucune relation entre eux.
 */
(function (root, make) {
  'use strict';
  const api = make();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.AdlfiLieuxNational = api;
}(typeof window !== 'undefined' ? window : null, function () {
  'use strict';
  const SCHEMA_PACTOLS = 'adlfi.lieux.pactols.xml.index.recette.v1';
  const SCHEMA_COG = 'adlfi.lieux.cog.national.temporel.recette.v1';

  function normaliser(value) {
    return String(value ?? '').replace(/œ/gi, c => c === 'Œ' ? 'Oe' : 'oe')
      .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase('fr').replace(/[^a-z0-9]+/g, ' ')
      .trim().replace(/\s+/g, ' ');
  }
  function verifierSources(pactols, cog) {
    if (pactols?.schema !== SCHEMA_PACTOLS ||
        cog?.schema !== SCHEMA_COG ||
        pactols.etat !== 'recette_non_publiee' ||
        cog.etat !== 'recette_non_publiee' ||
        !Array.isArray(pactols.autorites) || !Array.isArray(cog.entrees)) {
      throw new Error('Index nationaux de recette manquants ou incompatibles');
    }
  }
  function entreePactols(a) {
    const lien = a.correspondance_cog_validee_2026;
    if (lien && (a.statut !== 'validation_existante_paca' ||
        lien.type !== 'correspondance_communale_editoriale_existante' ||
        !/^[0-9A-Z]{5}$/.test(lien.code_insee))) {
      throw new Error('Correspondance COG non validée sur ' + a.ark_pactols);
    }
    if (!lien && a.statut !== 'aucune_validation_cog') {
      throw new Error('Statut Pactols incompatible avec absence de validation');
    }
    const noms = Array.from(new Set([a.libelle_documentaire, ...a.formes_attestees_xml]));
    return {
      id: 'pactols:' + a.ark_pactols,
      type: 'pactols', label: a.libelle_documentaire,
      ark: a.ark_pactols, code: lien?.code_insee || null,
      noms, lienValide: lien || null,
      champs: [a.ark_pactols, ...noms, ...(lien ? [lien.code_insee] : [])].map(normaliser),
      source: a,
    };
  }
  function entreeCOG(r) {
    return {
      id: 'cog:' + r.code_insee,
      type: 'cog', label: r.libelles_attestes.length === 1 ?
        r.libelles_attestes[0] :
        r.libelles_attestes.slice(0, 2).join(' / ') +
          (r.libelles_attestes.length > 2 ? ' …' : ''),
      code: r.code_insee, ark: null, lienValide: null,
      noms: r.libelles_attestes,
      champs: [r.code_insee, ...r.libelles_attestes].map(normaliser),
      source: r,
    };
  }
  function creerIndex(pactols, cog) {
    verifierSources(pactols,cog);
    const entries = [];
    const seen = new Set();
    for (const a of pactols.autorites) {
      const item = entreePactols(a);
      if (seen.has(item.id)) throw new Error('ARK Pactols dupliqué');
      entries.push(item);seen.add(item.id);
    }
    for (const r of cog.entrees) {
      const item = entreeCOG(r);
      if (seen.has(item.id)) throw new Error('Code COG dupliqué');
      entries.push(item);seen.add(item.id);
    }
    return entries;
  }
  function scorer(e,q,tokens) {
    if (!tokens.every(t => e.champs.some(ch => ch.includes(t)))) return null;
    const nom = e.noms.map(normaliser);
    const ident = normaliser(e.type === 'pactols' ? e.ark : e.code);
    // Pas de priorité documentaire systématique entre homonymes : afficher les deux.
    if (ident === q) return 0;
    if (nom.includes(q)) return 1;
    if (nom.some(x => x.startsWith(q))) return 2;
    if (ident.startsWith(q)) return 3;
    if (nom.some(x => x.includes(q))) return 4;
    return 5;
  }
  function chercher(index, text, limite = 12) {
    const q = normaliser(text);
    if (q.length < 2 || !Number.isInteger(limite) || limite < 1) return [];
    const tokens = q.split(' ');
    const results = [];
    for (const e of index) {
      const score=scorer(e,q,tokens);
      if (score !== null) results.push({e,score});
    }
    results.sort((a,b) => a.score-b.score ||
      a.e.label.localeCompare(b.e.label,'fr',{sensitivity:'base'}) ||
      a.e.type.localeCompare(b.e.type) || a.e.id.localeCompare(b.e.id));
    return results.slice(0,limite).map(x=>x.e);
  }
  function prefixe(code) {
    if (typeof code !== 'string' || !/^[0-9A-Z]{5}$/.test(code)) {
      throw new Error('Code COG incorrect');
    }
    return code.slice(0,2);
  }
  function verifierSegment(segment,code,annee) {
    if (segment?.schema !== SCHEMA_COG ||
        segment.etat !== 'recette_non_publiee' ||
        segment.prefixe_code !== prefixe(code) ||
        !Number.isInteger(annee) || annee < 1943 || annee > 2026) {
      throw new Error('Segment COG ou année incompatible');
    }
  }
  function projectionCOG(segment,code,annee) {
    verifierSegment(segment,code,annee);
    const reference=String(annee)+'-01-01';
    function actif(r) {
      return r.debut_inclus <= reference &&
        (r.fin_exclue === null || reference < r.fin_exclue);
    }
    const etats=[...segment.periodes_COM,...segment.periodes_ARM].filter(
      r=>r.code_insee === code && actif(r));
    if (etats.length > 1) throw new Error('États COM/ARM simultanés ambigus');
    // Une commune associée de 2026 n'a PAS un statut connu en 1975
    // seulement parce que l'événement de fusion date de 1974.
    const complement=annee===2026 ?
      segment.observations_COMA_COMD_2026.find(x=>x.code_insee===code) : null;
    if (etats.length && complement) throw new Error('Statuts COG incompatibles');
    const etat=etats[0] || complement || null;
    const mouvements=segment.mouvements.filter(m=>
      (m.code_avant===code || m.code_apres===code))
      .sort((a,b)=>a.date_effet.localeCompare(b.date_effet)||a.id.localeCompare(b.id));
    const deja=mouvements.filter(m=>m.date_effet<=reference);
    return {
      code_insee:code, date_reference:reference, annee, etat,
      qualification:etats.length ? 'COM_ARM_historique_atteste' :
        complement ? 'COMA_COMD_observe_en_2026' : 'etat_non_documente_a_cette_date',
      mouvements_connus:mouvements,
      mouvements_deja_survenus:deja,
      geometrie_historique:null,
    };
  }
  function fiche(selection,segment,annee) {
    if (!selection) return null;
    if (selection.type==='pactols') {
      const a=selection.source;
      const val=selection.lienValide;
      return {
        type:'pactols',titre:a.libelle_documentaire,ark:a.ark_pactols,
        variantes:a.formes_attestees_xml,mentions:a.occurrences_xml,
        notices:a.notice_distinctes,
        annees_operation_xml:a.annees_operation_xml,
        statut_relation:val ? 'correspondance_COG_editeur_PACA_validee' : 'aucune_correspondance_validee',
        correspondance_administrative:val && annee===2026 ?
          projectionCOG(segment,val.code_insee,annee) : null,
        consultation_COG_historique_meme_code:val && annee!==2026 ?
          projectionCOG(segment,val.code_insee,annee) : null,
        lien_COG_valide:val,
        portee_validation:val ? 'millesime_COG_2026_uniquement' : null,
        geometrie_historique:null,
      };
    }
    if (selection.type==='cog') {
      return {
        type:'cog',titre:selection.label,code_insee:selection.code,
        formes_historiques:selection.source.libelles_attestes,
        etat_admin:projectionCOG(segment,selection.code,annee),
        ark_pactols:null, // jamais déduit d'un nom ou d'un code
        lien_COG_Pactols_valide: null,
        geometrie_historique:null,
      };
    }
    throw new Error('Résultat de recherche inconnu');
  }
  return {
    normaliser,verifierSources,creerIndex,chercher,prefixe,
    projectionCOG,fiche,
  };
}));
