# Pays de la Loire — 120 lieux imbriqués : deuxième phase, audit COG 2026

**14 novembre 2026 — PR n°24 — recette non validante.** GitHub Actions [exécution réussie](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43606353276).

## Double instruction

Les 120 concepts terminaux imbriqués par leur hiérarchie Pactols ont été répartis entre :
- **22** concepts partageant leur code Insee avec leur parent Pactols terminal, déjà contrôlés contre les mouvements officiels ; rapport : `BILAN-22-CODES-PAYS-DE-LA-LOIRE-COG-20261114.md`.
- **98** autres concepts dont les codes Pactols ne sont pas partagés par un autre ARK terminal du corpus régional, contrôlés dans ce deuxième audit grâce à `scripts/auditer_98_lieux_imbriques_pdl_cog.py`.

Les codes ne sont **pas des identifiants d'autorités historiques uniques**. Le rapprochement est non validant. Le corpus ne recense que les ARK attestés comme terminaux dans les XML, pas l'intégralité du thesaurus Pactols.

## Exécution officielle des 98 codes

La CI a téléchargé `v_commune_2026.csv`, `v_commune_depuis_1943.csv` et `v_mvt_commune_2026.csv` et vérifié les trois empreintes SHA-256 officielles déjà figées dans la branche.

| Mesure | Valeur |
| --- | ---: |
| Codes inspectés | **98** |
| Périodes code–libellé rattachées | **120** |
| Lignes de mouvements Insee rattachées aux codes | **273** |
| Codes `COMD` uniquement en 2026 | **79** |
| Codes présents en `COM` et `COMD` en 2026 | **11** |
| Codes `COM` uniquement | **2** |
| Codes `COMA` uniquement | **1** |
| Codes sans entrée dans `v_commune_2026.csv` | **5** |
| Codes avec plusieurs états historiques TYPECOM/libellé | **22** |
| Nouveaux alignements éditoriaux validés | **0** |

La somme des catégories exclusives est **79 + 11 + 2 + 1 + 5 = 98**. Ainsi **90** codes ont au moins une entrée `COMD` en 2026. Les 273 lignes de mouvement sont associées aux codes ; elles ne constituent **pas** 273 opérations administratives indépendantes.

## Les cinq codes sans entrée en 2026 : instruction prioritaire

| Concept terminal Pactols | Code Pactols | Parent hiérarchique Pactols | Mouvements repérés (MOD ; dates) |
| --- | --- | --- | --- |
| Trèves-Cunault | `49357` | Gennes-Val-de-Loire | `32`, `33` ; 1974-01-01, 2016-01-01 |
| Bazouges (Mayenne) | `53024` | Château-Gontier | `33`, `34` ; 1990-01-01, 2006-05-01 |
| Saint-Mars-sous-Ballon | `72301` | Ballon-Saint Mars | `32`, `35` ; 2016-01-01, 2020-05-28 |
| La Chapelle-Achard | `85052` | Les Achards | `32`, `35` ; 2017-01-01, 2024-01-01 |
| Fontaines (Doix lès Fontaines) | `85091` | Doix lès Fontaines | `32`, `35` ; 2016-01-01, 2026-01-01 |

Les dates et modalités ci-dessus sont celles des lignes de mouvement rattachées aux codes. **Elles ne suffisent pas, à elles seules, à qualifier la nature exhaustive de chaque événement**, ni à déclarer l'ancienne identité éteinte sans examiner les états avant/après.

## Deux codes COM seuls à ne pas interpréter comme des anciennes COMD toujours actives

- `72363` : Tuffé Val de la Chéronne au COG 2026, associé au concept terminal **Tuffé** dans la hiérarchie Pactols. Mouvements `MOD=32` en 2016 et `MOD=35` en 2021.
- `85080` : Doix lès Fontaines au COG 2026, associé au concept terminal **Doix**. Mouvements `MOD=32` en 2016 et `MOD=35` en 2026.

Ces codes correspondent aujourd'hui à des communes `COM` sans entrée distincte `COMD` sous ce code dans le fichier vérifié. Cela n'autorise pas la rétroprojection du contour actuel sur l'ancienne entité Pactols.

## Suite de l'instruction

1. Reconstituer les événements des cinq codes absents et des deux codes `COM` seuls avec les **lignes complètes avant/après** et les entités parentes.
2. Confronter les **98 enfants** aux `COMPARENT` du COG pour vérifier leur rapport à la commune parent Pactols ; ne pas confondre la parenté documentaire et le rattachement administratif.
3. Préserver les **24 enfants** dont le parent n'est pas un concept terminal dans l'extraction : son ARK est néanmoins bien attesté dans la chaîne Pactols.
4. Puis réaliser l'audit historique des 806 autorités sans changer les données publiques.

Les sorties CSV officielles (`synthese-codes-98.csv`, `periodes-codes-98.csv`, `evenements-codes-98.csv`, `rapport-codes-98.json`) sont archivées dans l'artefact GitHub Actions du lot. Aucune publication automatique dans `docs/data/lieux*`, aucun contour historique attribué.
