# Personnes — pilote Heurist de 30 autorités : publication contrôlée

**Visa éditorial obtenu le 28 novembre 2026** sur la projection privée v1.2 après confrontation intégrale à l'export source du 27 novembre 2026. La présente recette documente exclusivement les résultats publics, sans exporter les matrices nominatives, les correspondances d'autorité Heurist ou les relations d'expertise confidentielles.

## Effectifs et conservation

| Indicateur | Avant | Ajout | Après |
|---|---:|---:|---:|
| Autorités `PER` | 1 402 | 30 | **1 432** |
| Contributions AdlFI | 1 980 | 0 | **1 980** |
| Notices AdlFI | 1 779 | 0 | **1 779** |
| Articles *Gallia* | 1 520 | 3 | **1 523** |
| Articles *Gallia Préhistoire* | 673 | 12 | **685** |
| Articles distincts | 2 193 | 15 | **2 208** |
| Relations « auteur » | 3 324 | 30 | **3 354** |
| Relations « collaborateur » | 414 | 10 | **424** |
| Relations bibliographiques | 3 738 | 40 | **3 778** |
| Autorités reliées aux articles | 1 393 | 30 | **1 423** |

Le lot apporte 30 autorités publiques `PER-001403` à `PER-001432`. Les 40 relations touchent **39 articles distincts** : **24 articles antérieurement publiés réemployés sans duplication**, et 15 nouveaux articles. Les champs source Heurist 15 (auteur) et 1057 (collaborateur), y compris l'ordre au sein de chaque rôle, ont été confrontés à la source privée.

## Traçabilité

- Source : export Heurist du 27 novembre 2026, SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`.
- Base `main` après PR #228 : commit `7a4af2f4e776e7e8e7255651260ab60b8d062720` ; blobs Personnes `ea11c26184ce5173cfe34457ef2b5d8a46ae6751`, bibliographie `c272c08c86c878a3133f0abf0bc3cdbdff253e1a`.
- 59 identifiants candidats qualifiés sans collision dans le catalogue antérieur ; un identifiant secondaire erroné a été exclu de la projection.
- Aucun DOI ni URL des 15 nouveaux articles n'entre en collision avec le catalogue publié ; toutes les 15 notices ont titre, revue, année, pagination, DOI et URL. Les DOI source ont été normalisés syntaxiquement, sans création d'informations bibliographiques.
- La publication est strictement **append-only** pour les autorités, articles et relations existants. Aucun lien fictif vers AdlFI, aucune nouvelle notice AdlFI.

## Tests permanents

`tests/test_personnes_pilote30_publication.py` verrouille par empreinte SHA-256 canonique les 30 autorités, 15 articles et 40 relations, contrôle le manifeste, les rôles, les réemplois, les collisions et la non-régression. Les tests de tous les lots antérieurs restent actifs.

**Confidentialité :** le dossier privé de recette et l'export Heurist intégral ne sont pas déposés dans ce dépôt public. L'absence de revérification externe individuelle de chaque identifiant constitue la doctrine éditoriale convenue : les identifiants validés dans Heurist sont la source de référence, avec audit transversal différé et traitement ciblé des anomalies avérées.
