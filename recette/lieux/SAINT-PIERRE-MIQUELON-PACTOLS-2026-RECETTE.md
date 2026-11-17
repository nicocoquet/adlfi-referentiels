# Saint-Pierre-et-Miquelon — audit Pactols–COG 2026

**17 novembre 2026 — recette non validante, sans publication de nouveaux alignements.**

## Périmètre

La [PR n°63](https://github.com/nicocoquet/adlfi-referentiels/pull/63) a publié les périodes COG documentaires des deux communes, **Miquelon-Langlade (`97501`) et Saint-Pierre (`97502`)**, et les a séparées de la collectivité `975`.

Le fichier public `docs/data/lieux-outremer/recherche-2026.json` ne contient **aucune correspondance Pactols–COG déjà validée** pour ces deux communes ; **cela ne signifie pas que Pactols n'a aucun concept correspondant**. Seul l'examen RDF peut trancher la présence de liens explicites et de candidats éditoriaux.

## Sources contrôlées

- **Pactols-Lieux th17, 22 juillet 2026**, dépôt [Frantiq/PACTOLS](https://github.com/frantiq/PACTOLS), commit `69bf9697e24cefd645a69465bbd271702786285a`, chemin `pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf` ; SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- **Insee, COG 2026**, `v_commune_comer_2026.csv`, [édition officielle](https://www.insee.fr/fr/information/8740222) ; SHA-256 `9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8`.

Le workflow récupère le dépôt RDF avec **Git LFS**, compare les empreintes exactes, effectue une extraction XML en flux, puis produit deux rapports identiques contrôlés par `cmp`.

## Règles de qualification

1. **`skos:exactMatch` explicite** du concept Pactols vers `http(s)://id.insee.fr/geo/commune/97501` ou `97502` : preuve documentaire directe d'une correspondance déclarée dans le thésaurus.
2. Pour être **éligible** à l'arbitrage éditorial AdlFI : un seul candidat pour le code, un seul code INSEE exactMatch sur le concept, `skos:prefLabel` français cohérent avec le libellé COG (ou désambiguïsation Saint-Pierre-et-Miquelon), concept non déprécié et sans remplacement déclaré.
3. **Correspondance uniquement lexicale** : candidat à instruire, jamais alignement automatique. Le nom « Saint-Pierre » étant très homonyme, tout concept homonyme sans URI correspondante demeure exclu de la validation.
4. **`skos:altLabel` et autres URI** conservés comme éléments de preuve, non comme équivalence admise.
5. Les éventuels résultats éligibles de l'audit **ne modifient ni le total des 128 liens 2026 publiés ni aucune période antérieure à 2026**. Ils appellent une décision de publication spécifique.

Le rapport indique séparément les deux codes, leurs éventuels `exactMatch`, leurs candidats lexicaux et les homonymes rejetés. **Aucun nom, identifiant Pactols ou résultat chiffré n'est préjugé avant l'exécution sur le RDF officiel.**

## Bornes

**0** nouvel alignement Pactols, **0** contour historique, **0** lien de succession. Aucun changement dans `docs/`.

La prochaine décision portera uniquement sur les éventuels couples `ARK Pactols–URI INSEE` effectivement attestés par le RDF et sur leur éligibilité, et non sur la nature institutionnelle de la collectivité `975`.
