/* Contrat de consultation publique COG / Pactols : aucun alignement par homonymie. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.AdlfiLieuxChronologieCore = api;
}(typeof window !== 'undefined' ? window : null, function () {
  'use strict';
  const SCHEMA = 'adlfi.lieux.chronologie.4regions.public-recette.v1';
  function verifier(data) {
    if (data?.schema !== SCHEMA || !Array.isArray(data.periodes_com) ||
        !Array.isArray(data.lignes_mouvements_cog) ||
        !Array.isArray(data.alignements_Pactols_COG_valides_2026) ||
        !Array.isArray(data.observations_COMA_COMD_2026) ||
        data.geometries_historiques?.length !== 0) {
      throw new Error('Contrat de données temporelles incompatible');
    }
    if (data.region !== 'paca' && data.alignements_Pactols_COG_valides_2026.length) {
      throw new Error('Alignements Pactols non autorisés dans cette recette');
    }
  }
  function dateReference(annee) {
    if (!Number.isInteger(annee) || annee < 1943 || annee > 2026)
      throw new RangeError('Année de référence hors champ');
    return String(annee) + '-01-01';
  }
  function actif(p, date) {
    return p.debut_inclus <= date && (!p.fin_exclue || date < p.fin_exclue);
  }
  function etat(data, code, annee) {
    verifier(data);
    const date = dateReference(annee);
    const etats = data.periodes_com.filter(p => p.code_insee === code &&
        p.typecom === 'COM' && actif(p, date));
    if (etats.length > 1) throw new Error('Plusieurs états COM simultanés');
    const observations = annee === 2026 ?
      data.observations_COMA_COMD_2026.filter(p => p.code_insee === code) : [];
    if (observations.length > 1) throw new Error('Statut COMA/COMD ambigu');
    const contemporain = etats[0] || observations[0] || null;
    const mouvements = data.lignes_mouvements_cog.filter(m =>
      (m.code_avant === code || m.code_apres === code) && m.date_effet <= date);
    return {
      date_reference: date, code_insee: code, etat: contemporain,
      observation_statut_millesime_2026: !etats.length && !!observations.length,
      mouvements: mouvements.slice().sort((a, b) =>
        a.date_effet.localeCompare(b.date_effet) || a.id.localeCompare(b.id)),
      geometrie_historique: null,
    };
  }
  function normaliser(text) {
    return String(text ?? '').replace(/œ/gi, 'oe').normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('fr')
      .replace(/[^a-z0-9]+/g, ' ').trim().replace(/\s+/g, ' ');
  }
  function indexer(data) {
    verifier(data);
    const grouped = new Map();
    for (const p of data.periodes_com) {
      if (p.typecom !== 'COM') continue;
      if (!grouped.has(p.code_insee)) grouped.set(p.code_insee, new Set());
      grouped.get(p.code_insee).add(p.libelle);
    }
    for (const p of data.observations_COMA_COMD_2026) {
      if (!grouped.has(p.code_insee)) grouped.set(p.code_insee, new Set());
      grouped.get(p.code_insee).add(p.libelle);
    }
    const result = [...grouped].map(([code, noms]) => ({
      kind: 'cog', id: 'cog:' + code, code, noms: [...noms].sort(),
      label: [...noms].sort((a,b)=>a.localeCompare(b,'fr'))[0],
      champs: [code, ...noms].map(normaliser),
    }));
    for (const a of data.alignements_Pactols_COG_valides_2026) {
      if (a.statut !== 'correspondance_PACA_preexistante_validee' ||
          a.millesime_validation !== 2026 || !a.ark_pactols || !a.code_insee)
        throw new Error('Lien Pactols non validé');
      result.push({
        kind: 'pactols', id: 'pactols:' + a.ark_pactols,
        code: a.code_insee, ark: a.ark_pactols,
        label: a.libelle_pactols, noms: [a.libelle_pactols],
        champs: [a.libelle_pactols, a.ark_pactols, a.code_insee].map(normaliser),
      });
    }
    return result;
  }
  function chercher(index, texte, n = 10) {
    const q = normaliser(texte);
    if (!q || n < 1) return [];
    const tokens = q.split(' ');
    const possibles = index.filter(e =>
      tokens.every(t => e.champs.some(ch => ch.includes(t))));
    possibles.sort((a,b) => {
      function score(x) {
        if (x.champs.some(ch=>ch===q)) return 0;
        if (x.champs.some(ch=>ch.startsWith(q))) return 1;
        return 2;
      }
      return score(a)-score(b) ||
        a.label.localeCompare(b.label,'fr',{sensitivity:'base'}) ||
        a.id.localeCompare(b.id);
    });
    return possibles.slice(0,n);
  }
  function nombreCommunes(data, annee) {
    const date = dateReference(annee);
    return data.periodes_com.filter(p=>p.typecom==='COM' && actif(p,date)).length;
  }
  return {verifier, dateReference, actif, etat, normaliser, indexer, chercher, nombreCommunes};
}));