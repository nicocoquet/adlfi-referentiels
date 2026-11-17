# Saint-Barthélemy et Saint-Martin — audit RDF Pactols des six codes historiques/actuels

**17 novembre 2026 — recette documentaire non validante, aucun alignement public modifié.**

Après la [PR n°65](https://github.com/nicocoquet/adlfi-referentiels/pull/65), le référentiel dispose de deux successions juridiques attestées entre anciennes communes et collectivités de 2007. La présente étape vérifie **la nature des correspondances Pactols disponibles**, sans créer de lien du seul fait du transfert des droits et obligations.

## Périmètre exact

| Identité administrative | Saint-Barthélemy | Saint-Martin |
| --- | --- | --- |
| Ancienne commune (jusqu'au 23 février 2007) | `97123` | `97127` |
| Collectivité actuelle | `977` | `978` |
| Code d'application à cinq positions, non communal | `97701` | `97801` |

Ces six identifiants n'ont **pas la même nature**. En particulier, le fait qu'un export RDF porte un éventuel `skos:exactMatch` vers `http://id.insee.fr/geo/commune/97701` ne prouverait **pas** l'existence d'une commune actuelle Saint-Barthélemy ; le code à cinq chiffres sert à la codification applicative selon [l'Insee](https://www.insee.fr/fr/information/7929495).

## Sources épinglées

- Frantiq, [PACTOLS](https://github.com/frantiq/PACTOLS), export RDF Lieux `Pactols_Lieux_th17_20260722.rdf` au commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- Insee, COG 2026, fichier `v_commune_comer_2026.csv` à l'empreinte `9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8`.

Le workflow récupère le RDF par **Git LFS**, vérifie l'empreinte, lit ses concepts en flux, puis extrait les éventuelles déclarations **`skos:exactMatch`** portant exactement sur l'un des six codes. Il en conserve la famille d'URI, le libellé préféré, les variantes et les indicateurs de dépréciation/remplacement.

Les ressemblances lexicales assorties de précisions géographiques sont recensées **comme candidats non validants** ; les simples homonymes « Saint-Martin » ne sont pas transformés en correspondances.

## Politique de qualification

- `97123`/`97127` : une URI explicite est une **preuve vers une ancienne autorité communale** et ne vaut pas alignement vers la collectivité successeure.
- `977`/`978` : une URI explicite peut documenter une **autorité de collectivité d'outre-mer**, sous réserve de sa nature sémantique.
- `97701`/`97801` : tout `exactMatch`, même étiqueté comme « commune » dans son URI, demande **un examen ontologique** et ne peut être validé comme lien communal courant.
- Aucun `skos:exactMatch` historique n'est rétroprojeté, aucun ARK ne passe automatiquement d'une entité à l'autre.
- Le rapport conserve **zéro alignement publié**, **zéro contour historique**, **zéro validation automatique**, quel que soit le résultat du RDF.

Les éventuels résultats détaillés sont ajoutés ici **seulement après l'exécution sur les deux sources officielles**, et ne se déduisent pas des noms.
