# Pays de la Loire — 22 codes partagés : contrôle exhaustif des mouvements Insee 2026

**14 novembre 2026 — PR n°24, recette non validante.** Workflow exécuté avec succès : https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43605701680

## Sources contrôlées

Le workflow a téléchargé et vérifié par SHA-256 les trois fichiers officiels Insee du COG 2026 (`v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv`). Source : https://www.insee.fr/fr/information/8740222.

- Communes 2026 : `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`
- Couples code–libellé : `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`
- Mouvements : `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`

Le script `scripts/auditer_codes_partages_pdl_cog.py` inspecte les **22 codes déjà attestés sur deux ARK Pactols** (44 ARK). Résultats : **47 épisodes code–libellé**, **188 lignes de mouvements rattachées**, réparties en **29 groupes par code, modalité et date**. Les 188 lignes ne correspondent **pas** à 188 opérations administratives indépendantes.

## Datation issue des fichiers officiels

| Code partagé | Ancien nom / forme communale | État associé à la commune nouvelle | Opérations Insee rattachées au code (MOD, date) |
| --- | --- | --- | --- |
| 44005 | Arthon-en-Retz | Chaumes-en-Retz | 32 — 2016-01-01 |
| 44021 | Bourgneuf-en-Retz | Villeneuve-en-Retz | 32 — 2016-01-01 |
| 44087 | Machecoul | Machecoul-Saint-Même | 32 — 2016-01-01 |
| 44163 | Saint-Herblon | Vair-sur-Loire | **20 — 1950-10-11** ; 32 — 2016-01-01 |
| 49018 | Baugé | Baugé-en-Anjou | **32 — 2013-01-01 ; 32 — 2016-01-01** |
| 49021 | Beaufort-en-Vallée | Beaufort-en-Anjou | 32 — 2016-01-01 |
| 49023 | Beaupréau | Beaupréau-en-Mauges | 32 — 2015-12-15 |
| 49050 | Brissac-Quincé (précédé par Brissac) | Brissac Loire Aubance | **31 — 1964-06-01** ; 32 — 2016-12-15 |
| 49069 | Champtoceaux | Orée d'Anjou | **32 — 2015-12-15 ; 50 — 2025-01-01**, voir ci-dessous |
| 49092 | Chemillé (puis Chemillé-Melay) | Chemillé-en-Anjou | **32 — 2013-01-01 ; 32 — 2015-12-15** |
| 49125 | Doué-la-Fontaine | Doué-en-Anjou | **31 — 1964-10-01** ; 32 — 2016-12-30 |
| 49167 | Juigné-sur-Loire | Les Garennes sur Loire | 32 — 2016-12-15 |
| 49244 | La Pommeraye | Mauges-sur-Loire | 32 — 2015-12-15 |
| 49248 | Pouancé | Ombrée d'Anjou | 32 — 2016-12-15 |
| 49301 | Saint-Macaire-en-Mauges | Sèvremoine | 32 — 2015-12-15 |
| 49323 | Saint-Sylvain-d'Anjou | Verrières-en-Anjou | 32 — 2016-01-01 |
| 49331 | Segré | Segré-en-Anjou Bleu | 32 — 2016-12-15 |
| 49367 | Vern-d'Anjou | Erdre-en-Anjou | 32 — 2015-12-28 |
| 53255 | Sainte-Suzanne | Sainte-Suzanne-et-Chammes | 32 — 2016-01-01 |
| 72071 | Château-du-Loir | Montval-sur-Loir | 32 — 2016-10-01 |
| 85009 | Auzay | Auchay-sur-Vendée | 32 — 2017-01-01 |
| 85084 | Les Essarts | Essarts en Bocage / Essarts-en-Bocage | **32 — 2016-01-01 ; 21 — 2024-01-01** |

Les **22 codes** possèdent une opération `MOD=32` enregistrée dans le fichier des mouvements : les collisions ne sont donc pas de simples homonymies lexicales. L'année de l'opération archéologique ne sert jamais à dater le mouvement.

## Sept cas nécessitant une instruction renforcée

1. **44163 Saint-Herblon / Vair-sur-Loire** : le fichier de mouvements contient aussi un `MOD=20` daté du 11 octobre 1950 avec La Roche-Blanche (`44222`). Reconstituer cette séparation avant de traiter la création de 2016.
2. **49018 Baugé / Baugé-en-Anjou** : opérations de commune nouvelle en 2013 et en 2016 sous le même code `49018`. Une relation binaire unique serait insuffisante.
3. **49050 Brissac / Brissac-Quincé / Brissac Loire Aubance** : fusion simple `MOD=31` en 1964, puis création de commune nouvelle `MOD=32` en 2016.
4. **49069 Champtoceaux / Orée d'Anjou** : la période `COM 49069 Orée d'Anjou` prend fin au 1er janvier **2025** ; le mouvement `MOD=50` porte **49069 → 49126**, tandis que **`COMD 49069 Champtoceaux` subsiste au COG 2026**. Ne pas désigner `49069` comme le code actuel de la commune `Orée d'Anjou`.
5. **49092 Chemillé / Chemillé-Melay / Chemillé-en-Anjou** : trois états successifs sous `49092` avec événements `MOD=32` en 2013 et 2015.
6. **49125 Doué-la-Fontaine / Doué-en-Anjou** : mouvement `MOD=31` en 1964, puis création de commune nouvelle en 2016.
7. **85084 Les Essarts / Essarts en Bocage / Essarts-en-Bocage** : `MOD=21` daté du 1er janvier **2024**, avec mouvements vers **L'Oie (`85165`)** et **Sainte-Florence (`85212`)**. Un changement de graphie dans le libellé contemporain coexiste avec une **modification territoriale** : ne pas réduire l'événement à une correction orthotypographique.

## Suites pour le modèle historique

- Ne pas fusionner les 44 ARK Pactols au motif du code partagé.
- Identifier séparément les **épisodes d'entité administrative**, les codes, les statuts `COM/COMD/COMA`, les événements datés, les prédécesseurs et les successeurs. Les codes doivent être interprétés dans leur contexte temporel et administratif.
- Une ligne de mouvement `MOD=32` documente la participation à une opération ; elle ne suffit pas isolément à décrire toute sa composition et ses effets.
- Les géométries 2026 ne documentent pas les limites territoriales des épisodes précédents.
- Les fichiers d'audit sont archivés dans l'artefact du workflow : `codes-partages-22-cog.csv`, `periodes-codes-partages-22.csv`, `evenements-codes-partages-22.csv`, `rapport-codes-partages-22.json`.

**0 validation éditoriale nouvelle et 0 contour historique attribué. Aucune modification de `docs/data/lieux*`.**
