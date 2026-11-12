/* Index lexical du pilote Lieux : utilisable dans le navigateur et dans Node.js. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.AdlfiLieuxSearch = api;
}(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  function normaliser(value) {
    return String(value ?? '')
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase('fr')
      .replace(/[^a-z0-9]+/g, ' ')
      .trim()
      .replace(/\s+/g, ' ');
  }

  function creerIndex(autorites) {
    if (!Array.isArray(autorites)) throw new TypeError('Autorités attendues');
    return autorites.map(function (autorite) {
      const c = autorite.correspondances?.[0];
      if (!autorite.ark_pactols || !c?.code_insee) {
        throw new Error('Autorité sans ARK ou correspondance : ' + String(autorite.ark_pactols));
      }
      const libelle = autorite.libelle_pactols;
      const libelleCOG = c.libelle_cog;
      const champs = [
        normaliser(libelle),
        normaliser(libelleCOG),
        normaliser(c.code_insee),
        normaliser(autorite.ark_pactols),
      ];
      return {
        ark: autorite.ark_pactols,
        code: String(c.code_insee),
        label: libelle,
        labelCOG: libelleCOG,
        departement: c.departement,
        autorite: autorite,
        champs: [...new Set(champs.filter(Boolean))],
      };
    });
  }

  function chercher(index, requete, limite = 8) {
    const q = normaliser(requete);
    if (!q || !Number.isInteger(limite) || limite <= 0) return [];
    const termes = q.split(' ');
    const resultat = [];
    for (const lieu of index) {
      // Une recherche multi-termes peut croiser noms, codes et identifiants.
      if (!termes.every(t => lieu.champs.some(champ => champ.includes(t)))) continue;
      let score = 9;
      const nom = normaliser(lieu.label);
      const nomCOG = normaliser(lieu.labelCOG);
      const ark = normaliser(lieu.ark);
      if (nom === q || nomCOG === q || lieu.code === q || ark === q) score = 0;
      else if (nom.startsWith(q)) score = 1;
      else if (nomCOG.startsWith(q)) score = 2;
      else if (lieu.code.startsWith(q)) score = 3;
      else if (ark.startsWith(q)) score = 4;
      else if (nom.includes(q)) score = 5;
      else if (nomCOG.includes(q)) score = 6;
      resultat.push({ lieu, score });
    }
    resultat.sort((a, b) => a.score - b.score ||
      a.lieu.label.localeCompare(b.lieu.label, 'fr', { sensitivity: 'base' }) ||
      a.lieu.ark.localeCompare(b.lieu.ark));
    return resultat.slice(0, limite).map(item => item.lieu);
  }

  return { normaliser, creerIndex, chercher };
}));