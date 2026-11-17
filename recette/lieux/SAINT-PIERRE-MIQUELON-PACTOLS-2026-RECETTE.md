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

## Résultat de la confrontation réelle — 17 novembre 2026

[GitHub Actions — rapport RDF n°44049557151](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44049557151) : le téléchargement Pactols/COG, les tests de parsing, les deux calculs reproductibles et le contrôle du rapport sont réussis.

| Code communal COG | ARK Pactols retrouvé | `skos:prefLabel` français du concept | `skos:exactMatch` INSEE | Avis |
| --- | --- | --- | --- | --- |
| `97501` Miquelon-Langlade | `26678/pcrtQAMzeGHldU` | Miquelon-Langlade | `http://id.insee.fr/geo/commune/97501` | **Éligible à validation 2026** |
| `97502` Saint-Pierre | `26678/pcrtYQmFfwxLq8` | **île Saint-Pierre (Saint-Pierre-et-Miquelon)** | `http://id.insee.fr/geo/commune/97502` | **À instruire : type d'entité différent** |

Aucun des deux concepts n'est marqué `owl:deprecated` ou `dct:isReplacedBy`, aucun code INSEE concurrent n'est déclaré sur le concept. Le rapport trouve **deux correspondances explicites**, une éligible selon notre politique et une à instruire, **zéro validation publiée**.

**Réserve majeure :** le concept Pactols [`26678/pcrtYQmFfwxLq8`](https://ark.frantiq.fr/ark:/26678/pcrtYQmFfwxLq8) a pour libellé préféré **« île Saint-Pierre (Saint-Pierre-et-Miquelon) »**. Ce libellé décrit vraisemblablement l'île, tandis que `97502` identifie la **commune administrative**. Un lien explicite `skos:exactMatch` vers le code communal ne garantit donc pas, en lui-même, l'identité sémantique entre les deux concepts. L'alignement **ne doit pas être homologué** à ce stade. Une instruction auprès de Pactols/Frantiq ou une vérification du périmètre exact du concept serait nécessaire.

Pour **Miquelon-Langlade**, l'ARK `26678/pcrtQAMzeGHldU` et le libellé concordent avec le COG 2026 ; la déclaration `exactMatch` satisfait les critères déjà retenus par l'éditeur pour les communes, sous réserve de l'opération de publication distincte.

### Point de méthode

La règle éditoriale « URI INSEE explicite = alignement communal validable » doit inclure un contrôle préalable de la **catégorie ontologique et du périmètre de l'entité**. Un alignement documenté par la source peut porter une erreur ou concerner une entité topographique insulaire plutôt qu'une autorité administrative. Cela vaut particulièrement pour les îles, quartiers, hameaux et centres-bourgs homonymes d'une commune.

Le total actuel des **128 correspondances ultramarines publiées** reste inchangé à l'issue de cette recette. Aucune correspondance rétroactive ne découle du rapport.

## Bornes

**0** nouvel alignement Pactols, **0** contour historique, **0** lien de succession. Aucun changement dans `docs/`.

La prochaine décision portera uniquement sur les éventuels couples `ARK Pactols–URI INSEE` effectivement attestés par le RDF et sur leur éligibilité, et non sur la nature institutionnelle de la collectivité `975`.
