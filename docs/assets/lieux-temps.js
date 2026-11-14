/* Sélecteur temporel du COG : un curseur, une année, état au 1er janvier.
 * Module pur pour la recette Lieux, sans carte ni réseau ni validation ARK.
 */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.AdlfiLieuxTemps = api;
}(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  function verifier(model, annee) {
    if (!model || model.schema !== 'adlfi.lieux.temps.recette.v1' ||
        model.etat !== 'recette_non_publiee') {
      throw new Error('Couche temporelle de recette non reconnue');
    }
    const bounds = model.reference_temporelle;
    if (!Number.isInteger(annee) ||
        annee < bounds.annee_min || annee > bounds.annee_max) {
      throw new RangeError('Année hors limites de la couche COG');
    }
    return String(annee) + '-01-01';
  }

  function etatActif(periode, dateReference) {
    return periode.debut_inclus <= dateReference &&
      (periode.fin_exclue === null || dateReference < periode.fin_exclue);
  }

  function auPremierJanvier(model, annee) {
    const reference = verifier(model, annee);
    const communes = model.periodes_COM.filter(item => etatActif(item, reference))
      .sort((a, b) => a.code_insee.localeCompare(b.code_insee));
    const evenementsSurvenus = model.evenements_COG.filter(
      ev => ev.date_effet <= reference);
    return {
      annee,
      date_reference: reference,
      etats_COM: communes,
      // Pas de rétroprojection du statut COMA/COMD à des années antérieures.
      entites_complementaires: annee === 2026 ?
        model.entites_complementaires_2026 : [],
      evenements_deja_survenus: evenementsSurvenus,
      geometries_historiques: [],
      source_etats: 'insee_COG2026_v_commune_depuis_1943',
    };
  }

  function normaliser(texte) {
    return String(texte ?? '').normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('fr')
      .replace(/[^a-z0-9]+/g, ' ').trim().replace(/\s+/g, ' ');
  }

  // La recherche porte sur TOUS les noms attestés, et non seulement ceux
  // qui ont une période COM active à l'année affichée.
  function creerIndexNoms(model) {
    verifier(model, model.reference_temporelle.annee_initiale);
    const grouped = new Map();
    for (const p of model.periodes_COM) {
      if (!grouped.has(p.code_insee)) grouped.set(p.code_insee, new Map());
      const names = grouped.get(p.code_insee);
      if (!names.has(p.libelle)) names.set(p.libelle, []);
      names.get(p.libelle).push({
        debut_inclus: p.debut_inclus,
        fin_exclue: p.fin_exclue,
      });
    }
    return Array.from(grouped, ([code_insee, names]) => ({
      code_insee,
      formes_historiques: Array.from(names, ([libelle, periodes]) =>
        ({ libelle, periodes })),
      termes: [code_insee, ...Array.from(names.keys()).map(normaliser)]
    })).sort((a,b) => a.code_insee.localeCompare(b.code_insee));
  }

  function chercherNoms(index, texte, limite = 10) {
    const q = normaliser(texte);
    if (!q || !Number.isInteger(limite) || limite < 1) return [];
    return index.filter(item => item.termes.some(s => s.includes(q)))
      .sort((a,b) =>
        Number(b.code_insee === q) - Number(a.code_insee === q) ||
        Number(b.termes.includes(q)) - Number(a.termes.includes(q)) ||
        a.code_insee.localeCompare(b.code_insee)).slice(0, limite);
  }

  return {
    verifier, etatActif, auPremierJanvier,
    normaliser, creerIndexNoms, chercherNoms,
  };
}));
